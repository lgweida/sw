import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

@dataclass
class FIXMessage:
    timestamp: str
    thread_id: str
    connection: str
    direction: str  # I_ (Incoming) or O_ (Outgoing)
    msg_type: str
    msg_type_code: str
    fields: Dict[str, str]
    raw_message: str
    
class FIXParser:
    def __init__(self):
        # FIX message type mappings
        self.msg_types = {
            'D': 'New Order Single',
            'G': 'Order Cancel/Replace Request', 
            'F': 'Order Cancel Request',
            '8': 'Execution Report',
            '9': 'Order Cancel Reject'
        }
        
        # FIX field mappings (commonly used fields)
        self.field_names = {
            '1': 'Account',
            '6': 'AvgPx',
            '8': 'BeginString',
            '9': 'BodyLength',
            '11': 'ClOrdID',
            '14': 'CumQty',
            '15': 'Currency',
            '17': 'ExecID',
            '20': 'ExecTransType',
            '21': 'HandlInst',
            '22': 'SecurityIDSource',
            '29': 'LastCapacity',
            '30': 'LastMkt',
            '31': 'LastPx',
            '32': 'LastQty',
            '34': 'MsgSeqNum',
            '35': 'MsgType',
            '37': 'OrderID',
            '38': 'OrderQty',
            '39': 'OrdStatus',
            '40': 'OrdType',
            '41': 'OrigClOrdID',
            '48': 'SecurityID',
            '49': 'SenderCompID',
            '50': 'SenderSubID',
            '52': 'SendingTime',
            '54': 'Side',
            '55': 'Symbol',
            '56': 'TargetCompID',
            '57': 'TargetSubID',
            '60': 'TransactTime',
            '63': 'SettlType',
            '75': 'TradeDate',
            '116': 'OnBehalfOfSubID'
        }
        
        # Order status mappings
        self.order_status = {
            '0': 'New',
            '1': 'Partially Filled',
            '2': 'Filled',
            '4': 'Canceled',
            '8': 'Rejected',
            'A': 'Pending New',
            'E': 'Pending Replace'
        }
        
        # Order type mappings
        self.order_types = {
            '1': 'Market',
            '2': 'Limit',
            '3': 'Stop',
            '4': 'Stop Limit'
        }
        
    def parse_fix_message(self, fix_string: str) -> Dict[str, str]:
        """Parse FIX message string into field dictionary"""
        fields = {}
        if not fix_string:
            return fields
            
        # Split by SOH character (|) or actual SOH if present
        parts = fix_string.split('|')
        
        for part in parts:
            if '=' in part:
                try:
                    tag, value = part.split('=', 1)
                    fields[tag] = value
                except ValueError:
                    continue
                    
        return fields
    
    def parse_log_line(self, line: str) -> Optional[FIXMessage]:
        """Parse a single log line and extract FIX message"""
        # Extract timestamp
        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)', line)
        if not timestamp_match:
            return None
        timestamp = timestamp_match.group(1)
        
        # Extract thread and connection info
        thread_match = re.search(r'\[([^\]]+)\]', line)
        thread_id = thread_match.group(1) if thread_match else ""
        
        # Extract connection info
        connection_match = re.search(r'\[([^\]]+)\].*?\[([^\]]+)\]', line)
        connection = connection_match.group(2) if connection_match else ""
        
        # Determine direction
        direction = "Incoming" if "Receiving" in line else "Outgoing" if "Sending" in line else "Unknown"
        
        # Extract FIX message
        fix_match = re.search(r'(8=FIX[^|]*(?:\|[^|]*)*)', line)
        if not fix_match:
            return None
        fix_string = fix_match.group(1)
        
        # Parse FIX fields
        fields = self.parse_fix_message(fix_string)
        
        # Get message type
        msg_type_code = fields.get('35', '')
        msg_type = self.msg_types.get(msg_type_code, f'Unknown ({msg_type_code})')
        
        return FIXMessage(
            timestamp=timestamp,
            thread_id=thread_id,
            connection=connection,
            direction=direction,
            msg_type=msg_type,
            msg_type_code=msg_type_code,
            fields=fields,
            raw_message=fix_string
        )
    
    def get_field_name(self, tag: str) -> str:
        """Get human-readable field name"""
        return self.field_names.get(tag, f'Tag_{tag}')
    
    def format_field_value(self, tag: str, value: str) -> str:
        """Format field value based on tag type"""
        if tag == '39':  # OrdStatus
            return self.order_status.get(value, value)
        elif tag == '40':  # OrdType
            return self.order_types.get(value, value)
        elif tag == '54':  # Side
            return 'Buy' if value == '1' else 'Sell' if value == '2' else value
        else:
            return value

def analyze_order_replacements(messages: List[FIXMessage]) -> List[Dict[str, Any]]:
    """Analyze order replacements and track field changes"""
    replacements = []
    
    # Group messages by ClOrdID to track order chain
    order_chain = {}
    replace_messages = []
    
    for msg in messages:
        if msg.msg_type_code == 'G':  # Order Cancel/Replace Request
            replace_messages.append(msg)
            
    for replace_msg in replace_messages:
        orig_cl_ord_id = replace_msg.fields.get('41', '')  # OrigClOrdID
        new_cl_ord_id = replace_msg.fields.get('11', '')   # ClOrdID
        
        if orig_cl_ord_id and new_cl_ord_id:
            # Find the original order or previous replacement
            original_order = None
            for msg in messages:
                if (msg.fields.get('11') == orig_cl_ord_id and 
                    msg.msg_type_code in ['D', 'G']):  # New Order or Replace
                    original_order = msg
                    break
            
            if original_order:
                changes = compare_order_fields(original_order, replace_msg)
                replacements.append({
                    'timestamp': replace_msg.timestamp,
                    'original_cl_ord_id': orig_cl_ord_id,
                    'new_cl_ord_id': new_cl_ord_id,
                    'changes': changes,
                    'original_fields': {tag: value for tag, value in original_order.fields.items()},
                    'new_fields': {tag: value for tag, value in replace_msg.fields.items()}
                })
    
    return replacements

def compare_order_fields(original: FIXMessage, replacement: FIXMessage) -> List[Dict[str, str]]:
    """Compare fields between original and replacement orders"""
    changes = []
    parser = FIXParser()
    
    # Get all unique field tags from both messages
    all_tags = set(original.fields.keys()) | set(replacement.fields.keys())
    
    # Compare each field
    for tag in sorted(all_tags):
        orig_value = original.fields.get(tag, '')
        new_value = replacement.fields.get(tag, '')
        
        if orig_value != new_value:
            field_name = parser.get_field_name(tag)
            changes.append({
                'field_tag': tag,
                'field_name': field_name,
                'original_value': parser.format_field_value(tag, orig_value) if orig_value else 'N/A',
                'new_value': parser.format_field_value(tag, new_value) if new_value else 'N/A',
                'change_type': 'Added' if not orig_value else 'Removed' if not new_value else 'Modified'
            })
    
    return changes

def safe_float(value: str, default: float = 0.0) -> float:
    """Safely convert string to float, handling empty strings and invalid values"""
    if not value or value.strip() == '':
        return default
    try:
        return float(value.strip())
    except (ValueError, TypeError):
        return default

def safe_int(value: str, default: int = 0) -> int:
    """Safely convert string to int, handling empty strings and invalid values"""
    if not value or value.strip() == '':
        return default
    try:
        return int(float(value.strip()))  # Handle cases like "100.0"
    except (ValueError, TypeError):
        return default

def create_audit_trail(log_data: str) -> Dict[str, Any]:
    """Create comprehensive audit trail from FIX log data"""
    parser = FIXParser()
    messages = []
    
    # Parse all log lines
    for line in log_data.strip().split('\n'):
        msg = parser.parse_log_line(line)
        if msg:
            messages.append(msg)
    
    # Sort by timestamp
    messages.sort(key=lambda x: x.timestamp)
    
    # Analyze order replacements
    replacements = analyze_order_replacements(messages)
    
    # Create execution summary
    executions = []
    total_qty = 0
    total_value = 0
    
    for msg in messages:
        if msg.msg_type_code == '8':  # Execution Report
            last_qty = safe_float(msg.fields.get('32', '0'))
            last_px = safe_float(msg.fields.get('31', '0'))
            cum_qty = safe_float(msg.fields.get('14', '0'))
            avg_px = safe_float(msg.fields.get('6', '0'))
            
            # Use avg_px if last_px is 0 (common in some execution reports)
            if last_px == 0 and avg_px > 0:
                last_px = avg_px
            
            # Only add to executions if we have meaningful data
            if cum_qty > 0:  # Changed from last_qty > 0 to cum_qty > 0
                executions.append({
                    'timestamp': msg.timestamp,
                    'cl_ord_id': msg.fields.get('11', ''),
                    'exec_id': msg.fields.get('17', ''),
                    'last_qty': last_qty,
                    'last_px': last_px,
                    'cum_qty': cum_qty,
                    'avg_px': avg_px,
                    'last_mkt': msg.fields.get('30', ''),
                    'symbol': msg.fields.get('55', msg.fields.get('48', ''))
                })
                
                total_qty = max(total_qty, cum_qty)
                if last_px > 0 and last_qty > 0:
                    total_value += last_qty * last_px
    
    # Calculate VWAP
    total_executed_qty = sum(exec['last_qty'] for exec in executions if exec['last_qty'] > 0)
    vwap = total_value / total_executed_qty if total_executed_qty > 0 else 0
    
    # Get order details from first order
    first_order = next((msg for msg in messages if msg.msg_type_code == 'D'), None)
    original_qty = safe_float(first_order.fields.get('38', '0')) if first_order else 0
    
    # Build audit trail
    audit_trail = {
        'summary': {
            'total_messages': len(messages),
            'order_date': messages[0].timestamp.split()[0] if messages else '',
            'start_time': messages[0].timestamp if messages else '',
            'end_time': messages[-1].timestamp if messages else '',
            'original_quantity': original_qty,
            'filled_quantity': total_qty,
            'remaining_quantity': original_qty - total_qty,
            'fill_percentage': (total_qty / original_qty * 100) if original_qty > 0 else 0,
            'vwap': round(vwap, 4),
            'total_executions': len(executions),
            'total_replacements': len(replacements),
            'symbol': executions[0]['symbol'] if executions else '',
            'venues': list(set(exec['last_mkt'] for exec in executions if exec['last_mkt']))
        },
        'messages': [
            {
                'timestamp': msg.timestamp,
                'direction': msg.direction,
                'connection': msg.connection,
                'msg_type': msg.msg_type,
                'msg_type_code': msg.msg_type_code,
                'fields': {
                    parser.get_field_name(tag): parser.format_field_value(tag, value)
                    for tag, value in msg.fields.items()
                },
                'raw_fields': msg.fields,
                'raw_message': msg.raw_message
            }
            for msg in messages
        ],
        'executions': executions,
        'replacements': replacements
    }
    
    return audit_trail

def print_replacement_changes(audit_trail: Dict[str, Any]) -> None:
    """Print detailed replacement analysis"""
    replacements = audit_trail.get('replacements', [])
    
    print(f"\n=== ORDER REPLACEMENT ANALYSIS ===")
    print(f"Total Replacements: {len(replacements)}\n")
    
    for i, replacement in enumerate(replacements, 1):
        print(f"Replacement #{i}")
        print(f"Time: {replacement['timestamp']}")
        print(f"Original Order ID: {replacement['original_cl_ord_id']}")
        print(f"New Order ID: {replacement['new_cl_ord_id']}")
        print(f"Changes ({len(replacement['changes'])} fields modified):")
        
        for change in replacement['changes']:
            print(f"  • {change['field_name']} ({change['field_tag']}): "
                  f"{change['original_value']} → {change['new_value']} "
                  f"[{change['change_type']}]")
        print("-" * 60)

# Function to read log data from file or use provided data
def read_log_data(file_path: str = None) -> str:
    """Read log data from file or return sample data"""
    if file_path:
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print(f"File {file_path} not found. Using provided data.")
    
    # Complete log data from the document
    return """2026-09-18 09:41:30.187_326 [15583-48bd94d4:985fd603ca:1829] [I_BloombergAlgoFix42] (INFO) Receiving : 8=FIX.4.2|9=0202|35=D|49=BLP|56=1MET|34=1829|52=20250918-13:41:30|50=32646470|57=ULB|60=20250918-13:41:30|1=MS_PB|63=0|38=23818|40=1|11=5DLY0000030001|15=USD|75=20250
2025-09-18 09:41:30.190_864 [15583-48bd94d4:985fd603ca:1829] [O_METClearpoolFix42] (INFO) Sending : 8=FIX.4.2|9=233|35=D|49=ET|56=METCPEX3|34=1302|52=20250918-13:41:30|50=32646470|57=ULB|116=Steven Bardong|1=EISLE-LT|11=B6_5DLY0000030001|15=USD|21=1|22=2|38=23818|40=1|
2025-09-18 09:41:30.193_632 [16926-48bd94e2:985fd603d0:5814] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=253|35=8|34=5814|49=METCPEX3|52=20250918-13:41:30.192|56=ET|57=32646470|1=EISLE-LT|6=0|11=B6_5DLY0000030001|14=0|17=711250918000206315|20=0|37=205250918000
2025-09-18 09:41:30.194_045 [16926-48bd94e2:985fd603d0:5814] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=324|35=8|49=1MET|56=BLP|34=1873|52=20250918-13:41:30.193|50=ULB|57=32646470|1=MS_PB|6=0|11=5DLY0000030001|14=0|15=USD|17=711250918000206315|20=0|22=2|31=0|3
2025-09-18 09:41:30.194_727 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=371|35=8|49=DC_MET|56=LINKMIZINT|34=400|52=20250918-13:41:30|50=ULB|57=32646470|1=20012048|6=0|11=5DLY0000030001|14=0|15=USD|17=711250918000206315|20=0|22=2|31=0|32=0|37=205250918
2025-09-18 09:41:30.198_013 [16926-48bd94e2:985fd603d5:5815] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=302|35=8|34=5815|49=METCPEX3|52=20250918-13:41:30.196|56=ET|57=32646470|1=EISLE-LT|6=28.75|11=B6_5DLY0000030001|14=100|17=205250918000046635|20=0|29=1|30=C
2025-09-18 09:41:30.198_322 [16926-48bd94e2:985fd603d5:5815] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=363|35=8|49=1MET|56=BLP|34=1874|52=20250918-13:41:30.197|50=ULB|57=32646470|1=MS_PB|6=28.75|11=5DLY0000030001|14=100|15=USD|17=205250918000046635|20=0|22=2|
2025-09-18 09:41:30.199_188 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=410|35=8|49=DC_MET|56=LINKMIZINT|34=401|52=20250918-13:41:30|50=ULB|57=32646470|1=20012048|6=28.75|11=5DLY0000030001|14=100|15=USD|17=205250918000046635|20=0|22=2|29=1|30=CDED|31=
2025-09-18 09:44:46.047_400 [16926-48bd94e2:985fd900de:6715] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=308|35=8|34=6715|49=METCPEX3|52=20250918-13:44:46.045|56=ET|57=32646470|1=EISLE-LT|6=28.6|11=B6_5DLY0000030001|14=200|17=205250918000054289|20=0|29=1|30=JS
2025-09-18 09:44:46.047_818 [16926-48bd94e2:985fd900de:6715] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=369|35=8|49=1MET|56=BLP|34=1894|52=20250918-13:44:46.046|50=ULB|57=32646470|1=MS_PB|6=28.6|11=5DLY0000030001|14=200|15=USD|17=205250918000054289|20=0|22=2|2
2025-09-18 09:44:46.049_200 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=416|35=8|49=DC_MET|56=LINKMIZINT|34=425|52=20250918-13:44:46|50=ULB|57=32646470|1=20012048|6=28.6|11=5DLY0000030001|14=200|15=USD|17=205250918000054289|20=0|22=2|29=1|30=JSJX|31=2
2025-09-18 09:45:08.111_287 [16926-48bd94e2:985fd9570e:6876] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=309|35=8|34=6876|49=METCPEX3|52=20250918-13:45:08.109|56=ET|57=32646470|1=EISLE-LT|6=28.47|11=B6_5DLY0000030001|14=400|17=205250918000054985|20=0|29=1|30=X
2025-09-18 09:45:08.111_729 [16926-48bd94e2:985fd9570e:6876] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=370|35=8|49=1MET|56=BLP|34=1901|52=20250918-13:45:08.110|50=ULB|57=32646470|1=MS_PB|6=28.47|11=5DLY0000030001|14=400|15=USD|17=205250918000054985|20=0|22=2|
2025-09-18 09:45:08.112_457 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=417|35=8|49=DC_MET|56=LINKMIZINT|34=427|52=20250918-13:45:08|50=ULB|57=32646470|1=20012048|6=28.47|11=5DLY0000030001|14=400|15=USD|17=205250918000054985|20=0|22=2|29=1|30=XNAS|31=
2025-09-18 09:47:07.284_489 [16926-48bd94e2:985fdb2893:7523] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=310|35=8|34=7523|49=METCPEX3|52=20250918-13:47:07.282|56=ET|57=32646470|1=EISLE-LT|6=28.546|11=B6_5DLY0000030001|14=500|17=205250918000059249|20=0|29=1|30=
2025-09-18 09:47:07.284_917 [16926-48bd94e2:985fdb2893:7523] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=371|35=8|49=1MET|56=BLP|34=1910|52=20250918-13:47:07.284|50=ULB|57=32646470|1=MS_PB|6=28.546|11=5DLY0000030001|14=500|15=USD|17=205250918000059249|20=0|22=2
2025-09-18 09:47:07.285_735 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=418|35=8|49=DC_MET|56=LINKMIZINT|34=440|52=20250918-13:47:07|50=ULB|57=32646470|1=20012048|6=28.546|11=5DLY0000030001|14=500|15=USD|17=205250918000059249|20=0|22=2|29=1|30=XNAS|31
2025-09-18 09:48:20.665_119 [16926-48bd94e2:985fdc4738:7951] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=319|35=8|34=7951|49=METCPEX3|52=20250918-13:48:20.663|56=ET|57=32646470|1=EISLE-LT|6=28.55299212598425|11=B6_5DLY0000030001|14=508|17=205250918000061259|20
2025-09-18 09:48:20.665_711 [16926-48bd94e2:985fdc4738:7951] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=380|35=8|49=1MET|56=BLP|34=1920|52=20250918-13:48:20.664|50=ULB|57=32646470|1=MS_PB|6=28.55299212598425|11=5DLY0000030001|14=508|15=USD|17=20525091800006125
2025-09-18 09:48:20.665_843 [16926-48bd94e2:985fdc4739:7952] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=320|35=8|34=7952|49=METCPEX3|52=20250918-13:48:20.663|56=ET|57=32646470|1=EISLE-LT|6=28.56225433526011|11=B6_5DLY0000030001|14=519|17=205250918000061261|20
2025-09-18 09:48:20.666_182 [16926-48bd94e2:985fdc4739:7952] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=381|35=8|49=1MET|56=BLP|34=1921|52=20250918-13:48:20.665|50=ULB|57=32646470|1=MS_PB|6=28.56225433526011|11=5DLY0000030001|14=519|15=USD|17=20525091800006126
2025-09-18 09:48:20.666_258 [16926-48bd94e2:985fdc4739:7953] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=320|35=8|34=7953|49=METCPEX3|52=20250918-13:48:20.663|56=ET|57=32646470|1=EISLE-LT|6=28.57964879852126|11=B6_5DLY0000030001|14=541|17=205250918000061263|20
2025-09-18 09:48:20.666_268 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=427|35=8|49=DC_MET|56=LINKMIZINT|34=445|52=20250918-13:48:20|50=ULB|57=32646470|1=20012048|6=28.55299212598425|11=5DLY0000030001|14=508|15=USD|17=205250918000061259|20=0|22=2|29=1
2025-09-18 09:48:20.666_497 [16926-48bd94e2:985fdc4739:7953] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=381|35=8|49=1MET|56=BLP|34=1922|52=20250918-13:48:20.665|50=ULB|57=32646470|1=MS_PB|6=28.57964879852126|11=5DLY0000030001|14=541|15=USD|17=20525091800006126
2025-09-18 09:48:20.666_564 [16926-48bd94e2:985fdc4739:7954] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=308|35=8|34=7954|49=METCPEX3|52=20250918-13:48:20.663|56=ET|57=32646470|1=EISLE-LT|6=28.62|11=B6_5DLY0000030001|14=600|17=205250918000061265|20=0|29=1|30=X
2025-09-18 09:48:20.666_762 [16926-48bd94e2:985fdc4739:7954] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=369|35=8|49=1MET|56=BLP|34=1923|52=20250918-13:48:20.665|50=ULB|57=32646470|1=MS_PB|6=28.62|11=5DLY0000030001|14=600|15=USD|17=205250918000061265|20=0|22=2|
2025-09-18 09:48:20.667_431 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=428|35=8|49=DC_MET|56=LINKMIZINT|34=446|52=20250918-13:48:20|50=ULB|57=32646470|1=20012048|6=28.56225433526011|11=5DLY0000030001|14=519|15=USD|17=205250918000061261|20=0|22=2|29=1
2025-09-18 09:48:20.667_504 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=428|35=8|49=DC_MET|56=LINKMIZINT|34=447|52=20250918-13:48:20|50=ULB|57=32646470|1=20012048|6=28.57964879852126|11=5DLY0000030001|14=541|15=USD|17=205250918000061263|20=0|22=2|29=1
2025-09-18 09:48:20.667_550 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=416|35=8|49=DC_MET|56=LINKMIZINT|34=448|52=20250918-13:48:20|50=ULB|57=32646470|1=20012048|6=28.62|11=5DLY0000030001|14=600|15=USD|17=205250918000061265|20=0|22=2|29=1|30=XNAS|31=
2025-09-18 09:49:20.293_086 [15583-48bd94d4:985fdd3024:1845] [I_BloombergAlgoFix42] (INFO) Receiving : 8=FIX.4.2|9=0233|35=G|49=BLP|56=1MET|34=1845|52=20250918-13:49:20|50=32646470|57=ULB|60=20250918-13:49:20|1=MS_PB|63=0|38=23818|40=2|11=5DLY000003000B|41=5DLY00000300
2025-09-18 09:49:20.295_442 [15583-48bd94d4:985fdd3024:1845] [O_METClearpoolFix42] (INFO) Sending : 8=FIX.4.2|9=289|35=G|49=ET|56=METCPEX3|34=1340|52=20250918-13:49:20|50=32646470|57=ULB|116=Steven Bardong|1=EISLE-LT|11=B6_5DLY000003000B|15=USD|21=1|22=2|37=20525091800
2025-09-18 09:49:20.297_916 [16926-48bd94e2:985fdd3029:8311] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=286|35=8|34=8311|49=METCPEX3|52=20250918-13:49:20.296|56=ET|57=32646470|1=EISLE-LT|6=28.62|11=B6_5DLY000003000B|14=600|17=711250918000311030|20=0|37=205250
2025-09-18 09:49:20.298_401 [16926-48bd94e2:985fdd3029:8311] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=354|35=8|49=1MET|56=BLP|34=1934|52=20250918-13:49:20.297|50=ULB|57=32646470|1=MS_PB|6=28.62|11=5DLY000003000B|14=600|15=USD|17=711250918000311030|20=0|22=2|
2025-09-18 09:49:20.299_397 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=401|35=8|49=DC_MET|56=LINKMIZINT|34=456|52=20250918-13:49:20|50=ULB|57=32646470|1=20012048|6=28.62|11=5DLY000003000B|14=600|15=USD|17=711250918000311030|20=0|22=2|31=0|32=0|37=205
2025-09-18 09:49:20.302_335 [16926-48bd94e2:985fdd302d:8312] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=315|35=8|34=8312|49=METCPEX3|52=20250918-13:49:20.300|56=ET|57=32646470|1=EISLE-LT|6=28.72|11=B6_5DLY000003000B|14=700|17=205250918000063197|20=0|29=1|30=X
2025-09-18 09:49:20.302_739 [16926-48bd94e2:985fdd302d:8312] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=376|35=8|49=1MET|56=BLP|34=1935|52=20250918-13:49:20.301|50=ULB|57=32646470|1=MS_PB|6=28.72|11=5DLY000003000B|14=700|15=USD|17=205250918000063197|20=0|22=2|
2025-09-18 09:49:20.303_761 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=423|35=8|49=DC_MET|56=LINKMIZINT|34=457|52=20250918-13:49:20|50=ULB|57=32646470|1=20012048|6=28.72|11=5DLY000003000B|14=700|15=USD|17=205250918000063197|20=0|22=2|29=1|30=XBOS|31=
2025-09-18 09:50:19.545_699 [15583-48bd94d4:985fde1798:1847] [I_BloombergAlgoFix42] (INFO) Receiving : 8=FIX.4.2|9=0233|35=G|49=BLP|56=1MET|34=1847|52=20250918-13:50:19|50=32646470|57=ULB|60=20250918-13:50:19|1=MS_PB|63=0|38=23818|40=2|11=5DLY000003000E|41=5DLY00000300
2025-09-18 09:50:19.546_374 [15583-48bd94d4:985fde1798:1847] [O_METClearpoolFix42] (INFO) Sending : 8=FIX.4.2|9=289|35=G|49=ET|56=METCPEX3|34=1346|52=20250918-13:50:19|50=32646470|57=ULB|116=Steven Bardong|1=EISLE-LT|11=B6_5DLY000003000E|15=USD|21=1|22=2|37=20525091800
2025-09-18 09:51:27.902_268 [16926-48bd94e2:985fdf229d:8962] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=317|35=8|34=8962|49=METCPEX3|52=20250918-13:51:27.900|56=ET|57=32646470|1=EISLE-LT|6=28.7625|11=B6_5DLY000003000B|14=800|17=205250918000068055|20=0|29=1|30
2025-09-18 09:51:27.902_668 [16926-48bd94e2:985fdf229d:8962] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=378|35=8|49=1MET|56=BLP|34=1952|52=20250918-13:51:27.901|50=ULB|57=32646470|1=MS_PB|6=28.7625|11=5DLY000003000B|14=800|15=USD|17=205250918000068055|20=0|22=
2025-09-18 09:51:27.904_074 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=425|35=8|49=DC_MET|56=LINKMIZINT|34=466|52=20250918-13:51:27|50=ULB|57=32646470|1=20012048|6=28.7625|11=5DLY000003000B|14=800|15=USD|17=205250918000068055|20=0|22=2|29=1|30=XNAS|3
2025-09-18 09:51:42.546_279 [15583-48bd94d4:985fdf5bd1:1850] [I_BloombergAlgoFix42] (INFO) Receiving : 8=FIX.4.2|9=0233|35=G|49=BLP|56=1MET|34=1850|52=20250918-13:51:42|50=32646470|57=ULB|60=20250918-13:51:42|1=MS_PB|63=0|38=23818|40=2|11=5DLY000003000H|41=5DLY00000300
2025-09-18 09:51:42.546_963 [15583-48bd94d4:985fdf5bd1:1850] [O_METClearpoolFix42] (INFO) Sending : 8=FIX.4.2|9=289|35=G|49=ET|56=METCPEX3|34=1354|52=20250918-13:51:42|50=32646470|57=ULB|116=Steven Bardong|1=EISLE-LT|11=B6_5DLY000003000H|15=USD|21=1|22=2|37=20525091800
2025-09-18 09:51:42.550_423 [16926-48bd94e2:985fdf5bd5:9052] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=288|35=8|34=9052|49=METCPEX3|52=20250918-13:51:42.548|56=ET|57=32646470|1=EISLE-LT|6=28.7625|11=B6_5DLY000003000H|14=800|17=711250918000340240|20=0|37=2052
2025-09-18 09:51:42.550_870 [16926-48bd94e2:985fdf5bd5:9052] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=356|35=8|49=1MET|56=BLP|34=1953|52=20250918-13:51:42.550|50=ULB|57=32646470|1=MS_PB|6=28.7625|11=5DLY000003000H|14=800|15=USD|17=711250918000340240|20=0|22=
2025-09-18 09:51:42.551_295 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=403|35=8|49=DC_MET|56=LINKMIZINT|34=467|52=20250918-13:51:42|50=ULB|57=32646470|1=20012048|6=28.7625|11=5DLY000003000H|14=800|15=USD|17=711250918000340240|20=0|22=2|31=0|32=0|37=2
2025-09-18 09:51:51.832_484 [16926-48bd94e2:985fdf8017:9110] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=324|35=8|34=9110|49=METCPEX3|52=20250918-13:51:51.830|56=ET|57=32646470|1=EISLE-LT|6=28.78888888888889|11=B6_5DLY000003000H|14=900|17=205250918000069075|20
2025-09-18 09:51:51.832_885 [16926-48bd94e2:985fdf8017:9110] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=385|35=8|49=1MET|56=BLP|34=1955|52=20250918-13:51:51.832|50=ULB|57=32646470|1=MS_PB|6=28.78888888888889|11=5DLY000003000H|14=900|15=USD|17=20525091800006907
2025-09-18 09:51:51.833_641 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=432|35=8|49=DC_MET|56=LINKMIZINT|34=469|52=20250918-13:51:51|50=ULB|57=32646470|1=20012048|6=28.78888888888889|11=5DLY000003000H|14=900|15=USD|17=205250918000069075|20=0|22=2|29=1
2025-09-18 09:54:55.353_721 [16926-48bd94e2:985fe24cf8:10022] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=328|35=8|34=10022|49=METCPEX3|52=20250918-13:54:55.352|56=ET|57=32646470|1=EISLE-LT|6=28.82762645914397|11=B6_5DLY000003000H|14=1028|17=205250918000076139
2025-09-18 09:54:55.354_207 [16926-48bd94e2:985fe24cf8:10022] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=388|35=8|49=1MET|56=BLP|34=1975|52=20250918-13:54:55.353|50=ULB|57=32646470|1=MS_PB|6=28.82762645914397|11=5DLY000003000H|14=1028|15=USD|17=205250918000076
2025-09-18 09:54:55.354_288 [16926-48bd94e2:985fe24cf9:10023] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=327|35=8|34=10023|49=METCPEX3|52=20250918-13:54:55.352|56=ET|57=32646470|1=EISLE-LT|6=28.84545454545454|11=B6_5DLY000003000H|14=1100|17=205250918000076141
2025-09-18 09:54:55.354_495 [16926-48bd94e2:985fe24cf9:10023] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=387|35=8|49=1MET|56=BLP|34=1976|52=20250918-13:54:55.353|50=ULB|57=32646470|1=MS_PB|6=28.84545454545454|11=5DLY000003000H|14=1100|15=USD|17=205250918000076
2025-09-18 09:54:55.354_741 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=435|35=8|49=DC_MET|56=LINKMIZINT|34=480|52=20250918-13:54:55|50=ULB|57=32646470|1=20012048|6=28.82762645914397|11=5DLY000003000H|14=1028|15=USD|17=205250918000076139|20=0|22=2|29=
2025-09-18 09:54:55.354_853 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=434|35=8|49=DC_MET|56=LINKMIZINT|34=481|52=20250918-13:54:55|50=ULB|57=32646470|1=20012048|6=28.84545454545454|11=5DLY000003000H|14=1100|15=USD|17=205250918000076141|20=0|22=2|29=
2025-09-18 09:58:43.687_847 [16926-48bd94e2:985fe5c8e7:11077] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=326|35=8|34=11077|49=METCPEX3|52=20250918-13:58:43.686|56=ET|57=32646470|1=EISLE-LT|6=28.86923076923077|11=B6_5DLY000003000H|14=1300|17=205250918000081857
2025-09-18 09:58:43.688_342 [16926-48bd94e2:985fe5c8e7:11077] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=386|35=8|49=1MET|56=BLP|34=2010|52=20250918-13:58:43.687|50=ULB|57=32646470|1=MS_PB|6=28.86923076923077|11=5DLY000003000H|14=1300|15=USD|17=205250918000081
2025-09-18 09:58:43.689_647 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=433|35=8|49=DC_MET|56=LINKMIZINT|34=503|52=20250918-13:58:43|50=ULB|57=32646470|1=20012048|6=28.86923076923077|11=5DLY000003000H|14=1300|15=USD|17=205250918000081857|20=0|22=2|29=
2025-09-18 10:00:47.305_679 [16926-48bd94e2:985fe7abc8:11716] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=328|35=8|34=11716|49=METCPEX3|52=20250918-14:00:47.304|56=ET|57=32646470|1=EISLE-LT|6=28.92666666666667|11=B6_5DLY000003000H|14=1500|17=205250918000088791
2025-09-18 10:00:47.306_161 [16926-48bd94e2:985fe7abc8:11716] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=388|35=8|49=1MET|56=BLP|34=2024|52=20250918-14:00:47.305|50=ULB|57=32646470|1=MS_PB|6=28.92666666666667|11=5DLY000003000H|14=1500|15=USD|17=205250918000088
2025-09-18 10:00:47.307_162 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=435|35=8|49=DC_MET|56=LINKMIZINT|34=512|52=20250918-14:00:47|50=ULB|57=32646470|1=20012048|6=28.92666666666667|11=5DLY000003000H|14=1500|15=USD|17=205250918000088791|20=0|22=2|29=
2025-09-18 10:01:52.573_911 [16926-48bd94e2:985fe8aabd:11935] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=321|35=8|34=11935|49=METCPEX3|52=20250918-14:01:52.572|56=ET|57=32646470|1=EISLE-LT|6=28.959375|11=B6_5DLY000003000H|14=1600|17=205250918000092689|20=0|29
2025-09-18 10:01:52.574_336 [16926-48bd94e2:985fe8aabd:11935] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=381|35=8|49=1MET|56=BLP|34=2027|52=20250918-14:01:52.573|50=ULB|57=32646470|1=MS_PB|6=28.959375|11=5DLY000003000H|14=1600|15=USD|17=205250918000092689|20=0
2025-09-18 10:01:52.575_250 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=428|35=8|49=DC_MET|56=LINKMIZINT|34=515|52=20250918-14:01:52|50=ULB|57=32646470|1=20012048|6=28.959375|11=5DLY000003000H|14=1600|15=USD|17=205250918000092689|20=0|22=2|29=1|30=XNA
2025-09-18 10:03:29.212_859 [15583-48bd94d4:985fea243c:1874] [I_BloombergAlgoFix42] (INFO) Receiving : 8=FIX.4.2|9=0190|35=F|49=BLP|56=1MET|34=1874|52=20250918-14:03:29|50=32646470|57=ULB|60=20250918-14:03:29|38=23818|40=2|11=5DLY000003000P|41=5DLY000003000H|48=BRXYZ91
2025-09-18 10:03:29.213_481 [15583-48bd94d4:985fea243c:1874] [O_METClearpoolFix42] (INFO) Sending : 8=FIX.4.2|9=231|35=F|49=ET|56=METCPEX3|34=1410|52=20250918-14:03:29|50=32646470|57=ULB|116=Steven Bardong|1=20012048|11=B6_5DLY000003000P|22=2|37=205250918000046629|38=2
2025-09-18 10:03:29.214_935 [16926-48bd94e2:985fea243e:12402] [O_METClearpoolFix42] (INFO) Receiving : 8=FIX.4.2|9=288|35=8|34=12402|49=METCPEX3|52=20250918-14:03:29.213|56=ET|57=32646470|1=EISLE-LT|6=28.959375|11=B6_5DLY000003000P|14=1600|17=711250918000466971|20=0|37
2025-09-18 10:03:29.215_283 [16926-48bd94e2:985fea243e:12402] [I_BloombergAlgoFix42] (INFO) Sending : 8=FIX.4.2|9=355|35=8|49=1MET|56=BLP|34=2051|52=20250918-14:03:29.214|50=ULB|57=32646470|1=MS_PB|6=28.959375|11=5DLY000003000P|14=1600|15=USD|17=711250918000466971|20=0
2025-09-18 10:03:29.216_566 [3753] [DC_MET_TO_FLEX_IS_FIX42] (INFO) Sending : 8=FIX.4.2|9=384|35=8|49=DC_MET|56=LINKMIZINT|34=529|52=20250918-14:03:29|50=ULB|57=32646470|1=20012048|6=28.959375|11=5DLY000003000H|14=1600|15=USD|17=711250918000466971|20=0|22=2|31=0|32=0|37=205250918000046629"""

# Main execution
def main():
    # Read the log data
    log_data = read_log_data('order_log.txt')
    
    # Create audit trail
    print("Parsing FIX log data...")
    audit_trail = create_audit_trail(log_data)
    
    # Save to JSON file
    with open('audit_trail.json', 'w', encoding='utf-8') as f:
        json.dump(audit_trail, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Audit trail saved to 'audit_trail.json'")
    print(f"📊 Summary:")
    print(f"   • Total Messages: {audit_trail['summary']['total_messages']}")
    print(f"   • Order Date: {audit_trail['summary']['order_date']}")
    print(f"   • Original Quantity: {audit_trail['summary']['original_quantity']:,.0f}")
    print(f"   • Filled Quantity: {audit_trail['summary']['filled_quantity']:,.0f}")
    print(f"   • Fill Percentage: {audit_trail['summary']['fill_percentage']:.1f}%")
    print(f"   • VWAP: ${audit_trail['summary']['vwap']:.4f}")
    print(f"   • Total Executions: {audit_trail['summary']['total_executions']}")
    print(f"   • Total Replacements: {audit_trail['summary']['total_replacements']}")
    print(f"   • Symbol: {audit_trail['summary']['symbol']}")
    print(f"   • Venues: {', '.join(audit_trail['summary']['venues'])}")
    
    # Print replacement analysis
    print_replacement_changes(audit_trail)
    
    return audit_trail

def analyze_replacement_changes_detailed(audit_trail: Dict[str, Any]) -> None:
    """
    Detailed function to analyze which fields changed with each replacement
    This function provides granular analysis of order modifications
    """
    replacements = audit_trail.get('replacements', [])
    
    if not replacements:
        print("No order replacements found in the audit trail.")
        return
    
    print(f"\n{'='*80}")
    print(f"DETAILED ORDER REPLACEMENT FIELD CHANGE ANALYSIS")
    print(f"{'='*80}")
    
    # Summary statistics
    total_changes = sum(len(r['changes']) for r in replacements)
    field_change_frequency = defaultdict(int)
    
    # Collect field change statistics
    for replacement in replacements:
        for change in replacement['changes']:
            field_change_frequency[change['field_name']] += 1
    
    print(f"\n📈 REPLACEMENT STATISTICS:")
    print(f"   • Total Replacements: {len(replacements)}")
    print(f"   • Total Field Changes: {total_changes}")
    print(f"   • Average Changes per Replacement: {total_changes/len(replacements):.1f}")
    
    print(f"\n📊 MOST FREQUENTLY CHANGED FIELDS:")
    for field, count in sorted(field_change_frequency.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {field}: {count} times")
    
    print(f"\n🔍 DETAILED REPLACEMENT BREAKDOWN:")
    
    for i, replacement in enumerate(replacements, 1):
        print(f"\n{'-'*60}")
        print(f"REPLACEMENT #{i}")
        print(f"{'-'*60}")
        print(f"⏰ Timestamp: {replacement['timestamp']}")
        print(f"🔄 Order ID Chain: {replacement['original_cl_ord_id']} → {replacement['new_cl_ord_id']}")
        print(f"📝 Fields Changed: {len(replacement['changes'])}")
        
        if replacement['changes']:
            print(f"\n🔧 FIELD MODIFICATIONS:")
            for j, change in enumerate(replacement['changes'], 1):
                change_icon = {
                    'Added': '➕',
                    'Removed': '➖', 
                    'Modified': '🔄'
                }.get(change['change_type'], '❓')
                
                print(f"   {j:2d}. {change_icon} {change['field_name']} (Tag {change['field_tag']})")
                print(f"       Before: {change['original_value']}")
                print(f"       After:  {change['new_value']}")
                print(f"       Type:   {change['change_type']}")
                
                # Special handling for important fields
                if change['field_tag'] == '40':  # OrdType
                    print(f"       💡 Order type changed from {change['original_value']} to {change['new_value']}")
                elif change['field_tag'] == '38':  # OrderQty
                    print(f"       💡 Order quantity modification")
                elif change['field_tag'] == '44':  # Price
                    print(f"       💡 Price level adjustment")
                elif change['field_tag'] == '59':  # TimeInForce
                    print(f"       💡 Time in force parameter changed")
                
                print()
        else:
            print(f"   ℹ️  No field changes detected (possible system-level replacement)")
    
    print(f"\n{'='*80}")

# Utility function to export specific data views
def export_executions_only(audit_trail: Dict[str, Any], filename: str = 'executions_only.json'):
    """Export only execution data for analysis"""
    executions_data = {
        'summary': audit_trail['summary'],
        'executions': audit_trail['executions']
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(executions_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Executions data exported to '{filename}'")

def export_replacements_only(audit_trail: Dict[str, Any], filename: str = 'replacements_only.json'):
    """Export only replacement data for analysis"""
    replacements_data = {
        'summary': {
            'total_replacements': audit_trail['summary']['total_replacements'],
            'order_date': audit_trail['summary']['order_date']
        },
        'replacements': audit_trail['replacements']
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(replacements_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Replacements data exported to '{filename}'")

# Advanced analysis functions
def calculate_execution_metrics(audit_trail: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate advanced execution metrics"""
    executions = audit_trail.get('executions', [])
    
    if not executions:
        return {}
    
    # Calculate metrics
    prices = [exec['last_px'] for exec in executions if exec['last_px'] > 0]
    quantities = [exec['last_qty'] for exec in executions if exec['last_qty'] > 0]
    
    metrics = {
        'total_executions': len(executions),
        'total_quantity': sum(quantities),
        'total_value': sum(exec['last_px'] * exec['last_qty'] for exec in executions if exec['last_px'] > 0),
        'price_range': {
            'min': min(prices) if prices else 0,
            'max': max(prices) if prices else 0,
            'range': max(prices) - min(prices) if prices else 0
        },
        'quantity_range': {
            'min': min(quantities) if quantities else 0,
            'max': max(quantities) if quantities else 0,
            'average': sum(quantities) / len(quantities) if quantities else 0
        },
        'venues': list(set(exec['last_mkt'] for exec in executions if exec['last_mkt'])),
        'venue_distribution': {}
    }
    
    # Calculate venue distribution
    venue_qty = defaultdict(float)
    for exec in executions:
        if exec['last_mkt'] and exec['last_qty'] > 0:
            venue_qty[exec['last_mkt']] += exec['last_qty']
    
    metrics['venue_distribution'] = dict(venue_qty)
    
    return metrics

if __name__ == "__main__":
    # Run the main parser
    audit_trail = main()
    
    # Run detailed replacement analysis
    analyze_replacement_changes_detailed(audit_trail)
    
    # Export additional views
    export_executions_only(audit_trail)
    export_replacements_only(audit_trail)
    
    # Calculate and display execution metrics
    exec_metrics = calculate_execution_metrics(audit_trail)
    if exec_metrics:
        print(f"\n📊 EXECUTION METRICS:")
        print(f"   • Price Range: ${exec_metrics['price_range']['min']:.2f} - ${exec_metrics['price_range']['max']:.2f}")
        print(f"   • Price Impact: ${exec_metrics['price_range']['range']:.2f}")
        print(f"   • Average Execution Size: {exec_metrics['quantity_range']['average']:.0f} shares")
        print(f"   • Venue Distribution:")
        for venue, qty in exec_metrics['venue_distribution'].items():
            percentage = (qty / exec_metrics['total_quantity']) * 100
            print(f"     - {venue}: {qty:,.0f} shares ({percentage:.1f}%)")
    
    print(f"\n✅ Analysis complete! Check the generated JSON files for detailed data.")
