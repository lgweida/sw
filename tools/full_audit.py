#!/usr/bin/env python3
"""
FIX Order Audit Trail Generator
Tracks order lifecycle and modifications using ClOrdID (11) and OrigClOrdID (41) links
"""

import os
import re
import csv
import argparse
from datetime import datetime
from collections import defaultdict, OrderedDict
import glob

class FIXOrderAuditTrail:
    def __init__(self):
        # FIX 4.2 tag definitions
        self.tag_definitions = {
            '35': 'MsgType',          # Message Type
            '54': 'Side',             # 1=Buy, 2=Sell
            '59': 'TimeInForce',      # Time In Force
            '40': 'OrdType',          # Order Type
            '38': 'OrderQty',         # Quantity
            '44': 'Price',            # Price
            '99': 'StopPx',           # Stop Price
            '55': 'Symbol',           # Security symbol
            '11': 'ClOrdID',          # Client Order ID (current)
            '41': 'OrigClOrdID',      # Original Client Order ID (for mods/cancels)
            '37': 'OrderID',          # Order ID (exchange/broker)
            '17': 'ExecID',           # Execution ID
            '150': 'ExecType',        # Execution type
            '39': 'OrdStatus',        # Order status
            '6': 'AvgPx',             # Average price
            '14': 'CumQty',           # Cumulative quantity
            '151': 'LeavesQty',       # Leaves quantity
            '60': 'TransactTime',     # Transaction time
            '1': 'Account',           # Account
            '58': 'Text',             # Text message
            '434': 'CxlRejResponseTo',# Cancel Reject Response To
        }
        
        # Message types for order lifecycle
        self.order_msg_types = {
            'D': 'NewOrder',
            '8': 'ExecutionReport',
            'F': 'OrderCancel',
            'G': 'OrderReplace',
            '9': 'OrderReject',
            '3': 'OrderCancelReject',
        }
        
        # Execution types
        self.exec_types = {
            '0': 'New',
            '4': 'Canceled',
            '5': 'Replaced',
            '8': 'Rejected',
            'F': 'Trade',
            'I': 'OrderStatus'
        }
        
        # Order status mapping
        self.order_status = {
            '0': 'New',
            '1': 'PartiallyFilled',
            '2': 'Filled',
            '4': 'Canceled',
            '5': 'Replaced',
            '6': 'PendingCancel',
            '7': 'Stopped',
            '8': 'Rejected',
            '9': 'Suspended',
            'A': 'PendingNew',
            'B': 'Calculated',
            'C': 'Expired',
            'D': 'AcceptedForBidding',
            'E': 'PendingReplace'
        }

    def parse_fix_message(self, message):
        """Parse a single FIX message into a dictionary"""
        parsed = {}
        
        # Handle different delimiters
        if '\x01' in message:
            fields = message.split('\x01')
        elif '|' in message:
            fields = message.split('|')
        else:
            # Try to split on any non-alphanumeric delimiter followed by '='
            fields = re.split(r'(?<=\=)[^a-zA-Z0-9]', message)
        
        for field in fields:
            if '=' in field:
                parts = field.split('=', 1)
                if len(parts) == 2:
                    tag, value = parts
                    if tag in self.tag_definitions:
                        parsed[self.tag_definitions[tag]] = value
                    else:
                        parsed[tag] = value
        
        return parsed

    def build_order_audit_trail(self, log_files, target_order_id=None, target_account=None, target_clordid=None):
        """Build audit trail for orders, optionally filtered by criteria"""
        # Store all messages by ClOrdID and OrderID
        orders_by_clordid = defaultdict(list)
        orders_by_orderid = defaultdict(list)
        all_messages = []
        
        # Process all log files
        for log_file in log_files:
            print(f"Processing: {os.path.basename(log_file)}")
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line or '8=FIX.4.2' not in line:
                            continue
                        
                        try:
                            parsed = self.parse_fix_message(line)
                            msg_type = parsed.get('MsgType', '')
                            
                            # Only process order-related messages
                            if msg_type in self.order_msg_types:
                                # Add timestamp if not present
                                if 'TransactTime' not in parsed:
                                    parsed['TransactTime'] = datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]
                                
                                # Store message
                                all_messages.append(parsed)
                                
                                # Index by ClOrdID
                                clordid = parsed.get('ClOrdID')
                                if clordid:
                                    orders_by_clordid[clordid].append(parsed)
                                
                                # Index by OrderID
                                orderid = parsed.get('OrderID')
                                if orderid:
                                    orders_by_orderid[orderid].append(parsed)
                                
                        except Exception as e:
                            print(f"Error parsing line {line_num}: {e}")
                            continue
                            
            except Exception as e:
                print(f"Error reading file {log_file}: {e}")
                continue
        
        # Build audit trails
        audit_trails = []
        
        if target_order_id or target_account or target_clordid:
            # Find specific orders matching criteria
            matching_orders = self._find_matching_orders(
                all_messages, target_order_id, target_account, target_clordid
            )
            
            for order_info in matching_orders:
                audit_trail = self._build_single_audit_trail(order_info, orders_by_clordid, orders_by_orderid)
                if audit_trail:
                    audit_trails.append(audit_trail)
        else:
            # Build audit trails for all orders
            processed_orders = set()
            for msg in all_messages:
                clordid = msg.get('ClOrdID')
                orderid = msg.get('OrderID')
                
                if clordid and clordid not in processed_orders:
                    audit_trail = self._build_single_audit_trail(
                        {'ClOrdID': clordid, 'OrderID': orderid},
                        orders_by_clordid,
                        orders_by_orderid
                    )
                    if audit_trail:
                        audit_trails.append(audit_trail)
                        processed_orders.add(clordid)
        
        return audit_trails

    def _find_matching_orders(self, messages, order_id=None, account=None, clordid=None):
        """Find orders matching the specified criteria"""
        matching_orders = []
        seen_orders = set()
        
        for msg in messages:
            current_order_id = msg.get('OrderID')
            current_account = msg.get('Account')
            current_clordid = msg.get('ClOrdID')
            
            # Check if this message matches our criteria
            matches = True
            if order_id and current_order_id != order_id:
                matches = False
            if account and current_account != account:
                matches = False
            if clordid and current_clordid != clordid:
                matches = False
            
            if matches and current_clordid and current_clordid not in seen_orders:
                matching_orders.append({
                    'ClOrdID': current_clordid,
                    'OrderID': current_order_id,
                    'Account': current_account
                })
                seen_orders.add(current_clordid)
        
        return matching_orders

    def _build_single_audit_trail(self, order_info, orders_by_clordid, orders_by_orderid):
        """Build audit trail for a single order"""
        clordid = order_info['ClOrdID']
        orderid = order_info['OrderID']
        
        # Get all messages for this ClOrdID
        clordid_messages = orders_by_clordid.get(clordid, [])
        
        # Get all messages for this OrderID (might include related orders)
        orderid_messages = orders_by_orderid.get(orderid, [])
        
        # Combine and sort by time
        all_related_messages = clordid_messages + orderid_messages
        all_related_messages.sort(key=lambda x: x.get('TransactTime', ''))
        
        # Build the audit trail
        audit_trail = {
            'ClOrdID': clordid,
            'OrderID': orderid,
            'Account': order_info.get('Account'),
            'events': [],
            'modification_chain': self._build_modification_chain(clordid, orders_by_clordid)
        }
        
        # Add each event to the trail
        for msg in all_related_messages:
            event = self._create_event_description(msg)
            audit_trail['events'].append(event)
        
        return audit_trail

    def _build_modification_chain(self, clordid, orders_by_clordid):
        """Build the chain of order modifications using OrigClOrdID"""
        modification_chain = []
        current_clordid = clordid
        
        while current_clordid:
            messages = orders_by_clordid.get(current_clordid, [])
            if not messages:
                break
            
            # Find the message that references this ClOrdID as OrigClOrdID
            found_previous = False
            for other_clordid, other_messages in orders_by_clordid.items():
                for msg in other_messages:
                    if msg.get('OrigClOrdID') == current_clordid:
                        modification_chain.insert(0, {
                            'ClOrdID': current_clordid,
                            'ModifiedBy': other_clordid,
                            'ModificationType': self._get_modification_type(msg)
                        })
                        current_clordid = other_clordid
                        found_previous = True
                        break
                if found_previous:
                    break
            
            if not found_previous:
                break
        
        return modification_chain

    def _get_modification_type(self, msg):
        """Determine the type of modification"""
        msg_type = msg.get('MsgType', '')
        exec_type = msg.get('ExecType', '')
        
        if msg_type == 'G' or exec_type == '5':
            return 'REPLACE'
        elif msg_type == 'F' or exec_type == '4':
            return 'CANCEL'
        elif msg_type == '9' or exec_type == '8':
            return 'REJECT'
        else:
            return 'UNKNOWN'

    def _create_event_description(self, msg):
        """Create human-readable event description"""
        msg_type = self.order_msg_types.get(msg.get('MsgType', ''), 'Unknown')
        exec_type = self.exec_types.get(msg.get('ExecType', ''), '')
        ord_status = self.order_status.get(msg.get('OrdStatus', ''), '')
        
        event = {
            'timestamp': msg.get('TransactTime', 'N/A'),
            'message_type': msg_type,
            'exec_type': exec_type,
            'order_status': ord_status,
            'clordid': msg.get('ClOrdID', ''),
            'orig_clordid': msg.get('OrigClOrdID', ''),
            'order_id': msg.get('OrderID', ''),
            'symbol': msg.get('Symbol', ''),
            'side': self._parse_side(msg.get('Side', '')),
            'quantity': msg.get('OrderQty', ''),
            'price': msg.get('Price', ''),
            'leaves_qty': msg.get('LeavesQty', ''),
            'cum_qty': msg.get('CumQty', ''),
            'avg_px': msg.get('AvgPx', ''),
            'text': msg.get('Text', '')
        }
        
        return event

    def _parse_side(self, side_code):
        side_map = {'1': 'Buy', '2': 'Sell'}
        return side_map.get(side_code, f'Unknown({side_code})')

    def generate_audit_report(self, audit_trails, output_file=None):
        """Generate human-readable audit report"""
        reports = []
        
        for trail in audit_trails:
            report = self._generate_single_order_report(trail)
            reports.append(report)
        
        full_report = "\n\n" + "="*80 + "\n\n".join(reports)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(full_report)
        
        print(full_report)
        return full_report

    def _generate_single_order_report(self, trail):
        """Generate report for a single order"""
        report = []
        
        report.append("=" * 80)
        report.append(f"ORDER AUDIT TRAIL")
        report.append("=" * 80)
        report.append(f"Client Order ID: {trail['ClOrdID']}")
        report.append(f"Order ID: {trail['OrderID']}")
        report.append(f"Account: {trail.get('Account', 'N/A')}")
        report.append("")
        
        # Modification chain
        if trail['modification_chain']:
            report.append("MODIFICATION CHAIN:")
            report.append("-" * 40)
            for mod in trail['modification_chain']:
                report.append(f"{mod['ClOrdID']} -> {mod['ModifiedBy']} ({mod['ModificationType']})")
            report.append("")
        
        # Events timeline
        report.append("EVENTS TIMELINE:")
        report.append("-" * 40)
        for event in trail['events']:
            report.append(f"{event['timestamp']} - {event['message_type']}")
            report.append(f"  Status: {event['order_status']}, Exec: {event['exec_type']}")
            report.append(f"  Symbol: {event['symbol']}, Side: {event['side']}")
            report.append(f"  Qty: {event['quantity']}, Price: {event['price']}")
            report.append(f"  Leaves: {event['leaves_qty']}, CumQty: {event['cum_qty']}")
            if event['orig_clordid']:
                report.append(f"  OrigClOrdID: {event['orig_clordid']}")
            if event['text']:
                report.append(f"  Text: {event['text']}")
            report.append("")
        
        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description='FIX Order Audit Trail Generator')
    parser.add_argument('log_dir', help='Directory containing log files')
    parser.add_argument('--order-id', help='Filter by OrderID')
    parser.add_argument('--account', help='Filter by Account')
    parser.add_argument('--clordid', help='Filter by ClOrdID')
    parser.add_argument('-o', '--output', help='Output report file', default='fix_audit_trail.txt')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.log_dir):
        print(f"Error: Directory '{args.log_dir}' does not exist")
        return
    
    # Find log files
    log_patterns = ['*.log', '*.txt', '*.fix', '*.dat']
    log_files = []
    for pattern in log_patterns:
        log_files.extend(glob.glob(os.path.join(args.log_dir, pattern)))
    
    if not log_files:
        print("No log files found")
        return
    
    # Generate audit trail
    auditor = FIXOrderAuditTrail()
    audit_trails = auditor.build_order_audit_trail(
        log_files, 
        target_order_id=args.order_id,
        target_account=args.account,
        target_clordid=args.clordid
    )
    
    if audit_trails:
        auditor.generate_audit_report(audit_trails, args.output)
        print(f"\nGenerated audit trail for {len(audit_trails)} orders")
    else:
        print("No orders found matching the criteria")

if __name__ == "__main__":
    main()