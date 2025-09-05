#!/usr/bin/env python3
"""
FIX 4.2 Log File Analyzer
Extracts order characteristics from FIX protocol log files
"""

import os
import re
import csv
import argparse
from datetime import datetime
from collections import defaultdict, Counter
import glob

class FIXLogAnalyzer:
    def __init__(self):
        # FIX 4.2 tag definitions for order characteristics
        self.tag_definitions = {
            '35': 'MsgType',          # Message Type
            '54': 'Side',             # 1=Buy, 2=Sell
            '59': 'TimeInForce',      # 0=Day, 1=GTC, 3=IOC, 4=FOK
            '40': 'OrdType',          # 1=Market, 2=Limit, 3=Stop, 4=Stop Limit
            '38': 'OrderQty',         # Quantity
            '44': 'Price',            # Price
            '99': 'StopPx',           # Stop Price
            '55': 'Symbol',           # Security symbol
            '11': 'ClOrdID',          # Client Order ID
            '37': 'OrderID',          # Order ID
            '17': 'ExecID',           # Execution ID
            '150': 'ExecType',        # Execution type
            '39': 'OrdStatus',        # Order status
            '6': 'AvgPx',             # Average price
            '14': 'CumQty',           # Cumulative quantity
            '151': 'LeavesQty',       # Leaves quantity
            '60': 'TransactTime',     # Transaction time
            '1': 'Account',           # Account
            '58': 'Text',             # Text message
        }
        
        # Reverse lookup for tag names
        self.tag_names = {v: k for k, v in self.tag_definitions.items()}
        
        # Message types we're interested in
        self.order_msgs = ['D', '8', 'F', 'G']  # New Order, Execution Report, Order Cancel, Order Replace
        
    def parse_fix_message(self, message):
        """Parse a single FIX message into a dictionary"""
        parsed = {}
        # Split on SOH character (ASCII 1) or pipe if SOH isn't preserved
        if '\x01' in message:
            fields = message.split('\x01')
        else:
            # Try common delimiters
            fields = re.split(r'[|=]', message)
        
        for field in fields:
            if '=' in field:
                tag, value = field.split('=', 1)
                if tag in self.tag_definitions:
                    parsed[self.tag_definitions[tag]] = value
                else:
                    parsed[tag] = value
        
        return parsed
    
    def extract_order_characteristics(self, parsed_msg):
        """Extract order characteristics from parsed message"""
        if parsed_msg.get('MsgType') not in self.order_msgs:
            return None
        
        characteristics = {
            'MsgType': parsed_msg.get('MsgType', ''),
            'Side': self._parse_side(parsed_msg.get('Side', '')),
            'TimeInForce': self._parse_tif(parsed_msg.get('TimeInForce', '')),
            'OrdType': self._parse_ord_type(parsed_msg.get('OrdType', '')),
            'Symbol': parsed_msg.get('Symbol', ''),
            'OrderQty': parsed_msg.get('OrderQty', ''),
            'Price': parsed_msg.get('Price', ''),
            'StopPx': parsed_msg.get('StopPx', ''),
            'Account': parsed_msg.get('Account', ''),
            'ClOrdID': parsed_msg.get('ClOrdID', ''),
            'OrderID': parsed_msg.get('OrderID', ''),
            'TransactTime': parsed_msg.get('TransactTime', ''),
            'OrdStatus': parsed_msg.get('OrdStatus', ''),
            'ExecType': parsed_msg.get('ExecType', ''),
        }
        
        return characteristics
    
    def _parse_side(self, side_code):
        """Convert side code to human-readable format"""
        side_map = {
            '1': 'Buy',
            '2': 'Sell',
            '3': 'BuyMinus',
            '4': 'SellPlus',
            '5': 'SellShort',
            '6': 'SellShortExempt',
            '7': 'Undisclosed',
            '8': 'Cross',
            '9': 'CrossShort',
        }
        return side_map.get(side_code, f'Unknown({side_code})')
    
    def _parse_tif(self, tif_code):
        """Convert TimeInForce code to human-readable format"""
        tif_map = {
            '0': 'Day',
            '1': 'GTC',
            '2': 'OPG',
            '3': 'IOC',
            '4': 'FOK',
            '5': 'GTX',
            '6': 'GTD',
            '7': 'ATC',
        }
        return tif_map.get(tif_code, f'Unknown({tif_code})')
    
    def _parse_ord_type(self, ord_type_code):
        """Convert order type code to human-readable format"""
        ord_type_map = {
            '1': 'Market',
            '2': 'Limit',
            '3': 'Stop',
            '4': 'StopLimit',
            '5': 'MarketOnClose',
            '6': 'WithOrWithout',
            '7': 'LimitOrBetter',
            '8': 'LimitWithOrWithout',
            '9': 'OnBasis',
            'D': 'PreviouslyQuoted',
            'E': 'PreviouslyIndicated',
            'G': 'ForexSwap',
            'I': 'Funari',
            'P': 'Pegged',
        }
        return ord_type_map.get(ord_type_code, f'Unknown({ord_type_code})')
    
    def scan_log_files(self, log_directory, output_file=None):
        """Scan all log files in directory and extract order characteristics"""
        all_orders = []
        stats = defaultdict(Counter)
        
        # Find all log files (common extensions)
        log_patterns = ['*.log', '*.txt', '*.fix', '*.dat']
        log_files = []
        
        for pattern in log_patterns:
            log_files.extend(glob.glob(os.path.join(log_directory, pattern)))
        
        print(f"Found {len(log_files)} log files to process")
        
        for log_file in log_files:
            print(f"Processing: {os.path.basename(log_file)}")
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Look for FIX messages (typically start with 8=FIX.4.2)
                        if '8=FIX.4.2' in line:
                            try:
                                parsed = self.parse_fix_message(line)
                                order_chars = self.extract_order_characteristics(parsed)
                                
                                if order_chars:
                                    all_orders.append(order_chars)
                                    
                                    # Update statistics
                                    stats['by_side'][order_chars['Side']] += 1
                                    stats['by_tif'][order_chars['TimeInForce']] += 1
                                    stats['by_type'][order_chars['OrdType']] += 1
                                    stats['by_symbol'][order_chars['Symbol']] += 1
                                    stats['by_account'][order_chars['Account']] += 1
                                    
                            except Exception as e:
                                print(f"Error parsing line {line_num} in {log_file}: {e}")
                                continue
                                
            except Exception as e:
                print(f"Error reading file {log_file}: {e}")
                continue
        
        # Generate summary report
        self.generate_report(all_orders, stats, output_file)
        
        return all_orders, stats
    
    def generate_report(self, orders, stats, output_file=None):
        """Generate comprehensive report"""
        report = []
        
        # Summary statistics
        report.append("=" * 60)
        report.append("FIX 4.2 LOG ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Total Orders Found: {len(orders)}")
        report.append("")
        
        # Order distribution by side
        report.append("ORDER DISTRIBUTION BY SIDE:")
        report.append("-" * 30)
        for side, count in stats['by_side'].most_common():
            report.append(f"{side:15}: {count:6} ({count/len(orders)*100:.1f}%)")
        report.append("")
        
        # Order distribution by TimeInForce
        report.append("ORDER DISTRIBUTION BY TIME IN FORCE:")
        report.append("-" * 40)
        for tif, count in stats['by_tif'].most_common():
            report.append(f"{tif:15}: {count:6} ({count/len(orders)*100:.1f}%)")
        report.append("")
        
        # Order distribution by type
        report.append("ORDER DISTRIBUTION BY ORDER TYPE:")
        report.append("-" * 35)
        for ord_type, count in stats['by_type'].most_common():
            report.append(f"{ord_type:15}: {count:6} ({count/len(orders)*100:.1f}%)")
        report.append("")
        
        # Top symbols
        report.append("TOP 10 SYMBOLS:")
        report.append("-" * 25)
        for symbol, count in stats['by_symbol'].most_common(10):
            report.append(f"{symbol:15}: {count:6}")
        report.append("")
        
        # Write to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write('\n'.join(report))
            
            # Also export raw data to CSV
            csv_file = output_file.replace('.txt', '.csv').replace('.log', '.csv')
            if orders:
                self.export_to_csv(orders, csv_file)
        
        # Print to console
        print('\n'.join(report))
    
    def export_to_csv(self, orders, csv_file):
        """Export order data to CSV file"""
        if not orders:
            return
        
        fieldnames = list(orders[0].keys())
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(orders)
        
        print(f"Order data exported to: {csv_file}")

def main():
    parser = argparse.ArgumentParser(description='Analyze FIX 4.2 log files for order characteristics')
    parser.add_argument('log_dir', help='Directory containing log files')
    parser.add_argument('-o', '--output', help='Output report file', default='fix_analysis_report.txt')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.log_dir):
        print(f"Error: Directory '{args.log_dir}' does not exist")
        return
    
    analyzer = FIXLogAnalyzer()
    analyzer.scan_log_files(args.log_dir, args.output)

if __name__ == "__main__":
    main()