import re
from collections import defaultdict
from datetime import datetime

def parse_fix_message(line):
    """Parse a FIX message line and return a dictionary of tag-value pairs."""
    fix_data = {}
    # Extract the FIX message part (after "Sending : " or "Receiving : ")
    fix_part = line.split(':', 2)[-1].strip()
    
    # Split by pipe and parse tag=value pairs
    for field in fix_part.split('|'):
        if '=' in field:
            tag, value = field.split('=', 1)
            try:
                fix_data[int(tag)] = value
            except ValueError:
                fix_data[tag] = value
    
    return fix_data

def parse_log_file(filename):
    """Parse the log file and extract order events."""
    orders = defaultdict(list)
    current_replacements = {}  # Track current replacement chains
    
    with open(filename, 'r') as file:
        for line in file:
            if any(x in line for x in ['Sending : ', 'Receiving : ']) and '35=' in line:
                try:
                    # Extract timestamp - it's at the beginning of the line
                    timestamp_str = line.split(' ')[0] + '.' + line.split(' ')[1].split('_')[0]
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d.%H:%M:%S.%f')
                    
                    direction = 'OUT' if 'Sending : ' in line else 'IN'
                    connector = line.split(']')[1].strip().strip('[]')
                    
                    fix_data = parse_fix_message(line)
                    msg_type = fix_data.get(35, '')
                    
                    if msg_type in ['D', 'G', 'F', '8']:  # New order, replace, cancel, execution
                        cl_ord_id = fix_data.get(11, '')
                        orig_cl_ord_id = fix_data.get(41, '')
                        order_qty = fix_data.get(38, '')
                        cum_qty = fix_data.get(14, '')
                        price = fix_data.get(6, '')
                        exec_type = fix_data.get(150, '0')  # 0 = New
                        ord_status = fix_data.get(39, '0')  # 0 = New
                        
                        # For execution reports, get exec type and order status
                        if msg_type == '8':
                            exec_type = fix_data.get(150, exec_type)
                            ord_status = fix_data.get(39, ord_status)
                        
                        event = {
                            'timestamp': timestamp,
                            'direction': direction,
                            'connector': connector,
                            'msg_type': msg_type,
                            'cl_ord_id': cl_ord_id,
                            'orig_cl_ord_id': orig_cl_ord_id,
                            'order_qty': order_qty,
                            'cum_qty': cum_qty,
                            'price': price,
                            'exec_type': exec_type,
                            'ord_status': ord_status,
                            'raw_line': line.strip()
                        }
                        
                        # Track replacement chains
                        if msg_type in ['G', 'F'] and orig_cl_ord_id:  # Replace request
                            current_replacements[cl_ord_id] = orig_cl_ord_id
                        
                        if cl_ord_id:  # Only add if we have a ClOrdID
                            orders[cl_ord_id].append(event)
                        
                        # Also track by original order ID for replacement chains
                        if orig_cl_ord_id and orig_cl_ord_id in orders:
                            orders[orig_cl_ord_id].append(event)
                            
                except (IndexError, ValueError) as e:
                    print(f"Error parsing line: {line.strip()}")
                    print(f"Error: {e}")
                    continue
    
    return orders, current_replacements

def build_replacement_chains(orders, current_replacements):
    """Build complete replacement chains from the orders data."""
    chains = defaultdict(list)
    processed = set()
    
    # Start from the end of replacement chains and work backwards
    for final_cl_ord_id, orig_cl_ord_id in current_replacements.items():
        if final_cl_ord_id in processed:
            continue
            
        chain = []
        current_id = final_cl_ord_id
        
        # Follow the chain backwards
        while current_id:
            if current_id in orders:
                chain.append(current_id)
            
            if current_id in current_replacements:
                current_id = current_replacements[current_id]
            else:
                break
        
        # Reverse to get chronological order
        chain.reverse()
        if chain:
            # Use the original order ID as the key
            original_id = chain[0]
            chains[original_id] = chain
            processed.update(chain)
    
    return chains

def print_order_audit_trail(orders, chains):
    """Print audit trail for each replacement chain."""
    for original_order_id, chain in chains.items():
        print(f"\n{'='*100}")
        print(f"ORDER REPLACEMENT CHAIN AUDIT TRAIL")
        print(f"Original Order ID: {original_order_id}")
        print(f"Replacement Chain: {' -> '.join(chain)}")
        print(f"{'='*100}")
        
        all_events = []
        for order_id in chain:
            if order_id in orders:
                all_events.extend(orders[order_id])
        
        # Sort events by timestamp
        all_events.sort(key=lambda x: x['timestamp'])
        
        for i, event in enumerate(all_events):
            print(f"\nEvent {i+1}:")
            print(f"  Time: {event['timestamp']}")
            print(f"  Direction: {event['direction']}")
            print(f"  Connector: {event['connector']}")
            print(f"  Msg Type: {event['msg_type']} ({get_msg_type_desc(event['msg_type'])})")
            print(f"  ClOrdID: {event['cl_ord_id']}")
            if event['orig_cl_ord_id']:
                print(f"  OrigClOrdID: {event['orig_cl_ord_id']}")
            if event['order_qty']:
                print(f"  OrderQty: {event['order_qty']}")
            if event['cum_qty']:
                print(f"  CumQty: {event['cum_qty']}")
            if event['price']:
                print(f"  Price: {event['price']}")
            print(f"  ExecType: {event['exec_type']} ({get_exec_type_desc(event['exec_type'])})")
            print(f"  OrdStatus: {event['ord_status']} ({get_ord_status_desc(event['ord_status'])})")
            print(f"  {'-'*50}")

def get_msg_type_desc(msg_type):
    """Get description for FIX message type."""
    msg_types = {
        'D': 'New Order Single',
        'G': 'Order Replace Request',
        'F': 'Order Cancel Request',
        '8': 'Execution Report'
    }
    return msg_types.get(msg_type, f'Unknown ({msg_type})')

def get_exec_type_desc(exec_type):
    """Get description for FIX execution type."""
    exec_types = {
        '0': 'New',
        '4': 'Canceled',
        '5': 'Replaced',
        'F': 'Trade (Partial Fill or Fill)',
        '1': 'Partial Fill',
        '2': 'Fill'
    }
    return exec_types.get(exec_type, f'Unknown ({exec_type})')

def get_ord_status_desc(ord_status):
    """Get description for FIX order status."""
    ord_statuses = {
        '0': 'New',
        '1': 'Partially filled',
        '2': 'Filled',
        '4': 'Canceled',
        '5': 'Replaced',
        '8': 'Rejected',
        'A': 'Pending New',
        'E': 'Pending Replace',
        '6': 'Pending Cancel'
    }
    return ord_statuses.get(ord_status, f'Unknown ({ord_status})')

def main():
    filename = 'order_log.txt'
    
    print("Parsing order log file...")
    orders, current_replacements = parse_log_file(filename)
    chains = build_replacement_chains(orders, current_replacements)
    
    print(f"Found {len(chains)} replacement chains")
    print(f"Total orders tracked: {len(orders)}")
    
    # Print audit trails
    if chains:
        print_order_audit_trail(orders, chains)
    else:
        print("No replacement chains found")
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY:")
    print(f"{'='*80}")
    for original_id, chain in chains.items():
        print(f"Chain starting with {original_id}: {len(chain)} orders in chain")
        for order_id in chain:
            if order_id in orders:
                exec_reports = [e for e in orders[order_id] if e['msg_type'] == '8']
                fills = [e for e in exec_reports if e['exec_type'] in ['F', '1', '2']]
                print(f"  {order_id}: {len(exec_reports)} execution reports, {len(fills)} fills")

if __name__ == "__main__":
    main()