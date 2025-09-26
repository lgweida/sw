import csv
import os
import re
from typing import Dict, List, Optional, Tuple
import simplefix

class FIXRouter:
    def __init__(self, routing_files_directory: str):
        """
        Initialize the FIX Router with routing configuration files.
        
        Args:
            routing_files_directory: Directory containing routing CSV files
        """
        self.routing_files_directory = routing_files_directory
        self.routing_rules = {}
        self.load_routing_rules()
    
    def load_routing_rules(self):
        """Load all routing rules from CSV files in the directory."""
        if not os.path.exists(self.routing_files_directory):
            print(f"Directory {self.routing_files_directory} does not exist")
            return
            
        for filename in os.listdir(self.routing_files_directory):
            if filename.endswith('.csv'):
                network_name = self.extract_network_name(filename)
                file_path = os.path.join(self.routing_files_directory, filename)
                self.routing_rules[network_name] = self.parse_routing_file(file_path)
                print(f"Loaded routing rules for {network_name}")
    
    def extract_network_name(self, filename: str) -> str:
        """Extract network name from filename."""
        # Remove .csv extension and any prefixes like 'alias_AutoRoute'
        name = filename.replace('.csv', '')
        if 'AutoRoute' in name:
            return name.split('AutoRoute')[-1]
        return name
    
    def parse_routing_file(self, file_path: str) -> List[Dict]:
        """
        Parse a routing CSV file and return routing rules.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of routing rules as dictionaries
        """
        rules = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # Parse the routing rules from the file content
                lines = content.strip().split('\n')
                for line in lines:
                    if '==>' in line and 'alias_' in line:
                        rule = self.parse_routing_line(line)
                        if rule:
                            rules.append(rule)
                            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            
        return rules
    
    def parse_routing_line(self, line: str) -> Optional[Dict]:
        """
        Parse a single routing rule line.
        
        Args:
            line: Raw line from CSV file
            
        Returns:
            Dictionary containing routing rule or None if parsing fails
        """
        try:
            # Split by '==>' to separate source and destination
            if '==>' not in line:
                return None
                
            parts = line.split('==>')
            if len(parts) != 2:
                return None
                
            source = parts[0].strip()
            destination = parts[1].strip()
            
            # Extract routing criteria from source
            rule = {
                'source': source,
                'destination': destination,
                'criteria': {}
            }
            
            # Parse various criteria from the source part
            if 'ACCOUNT' in source:
                account_match = re.search(r'ACCOUNT[;:]\s*([^;]+)', source)
                if account_match:
                    rule['criteria']['account'] = account_match.group(1).strip()
            
            if 'CURRENCY' in source:
                currency_match = re.search(r'CURRENCY[;:]\s*([^;]+)', source)
                if currency_match:
                    rule['criteria']['currency'] = currency_match.group(1).strip()
            
            if 'TARGETSUBID' in source:
                target_match = re.search(r'TARGETSUBID[;:]\s*([^;]+)', source)
                if target_match:
                    rule['criteria']['target_sub_id'] = target_match.group(1).strip()
            
            if 'DELIVERTOSUBID' in source:
                deliver_match = re.search(r'DELIVERTOSUBID[;:]\s*([^;]+)', source)
                if deliver_match:
                    rule['criteria']['deliver_to_sub_id'] = deliver_match.group(1).strip()
            
            # Extract destination information
            if 'DESTINATION' in destination:
                dest_match = re.search(r'DESTINATION[^;]*?([A-Z_]+)', destination)
                if dest_match:
                    rule['route_to'] = dest_match.group(1).strip()
            
            return rule
            
        except Exception as e:
            print(f"Error parsing line: {line}, Error: {e}")
            return None
    
    def parse_fix_message(self, fix_message: str) -> Dict:
        """
        Parse a FIX message and extract relevant routing fields.
        
        Args:
            fix_message: Raw FIX message string
            
        Returns:
            Dictionary containing parsed FIX fields
        """
        try:
            msg = simplefix.FixMessage()
            msg.append_buffer(fix_message.encode())
            
            parsed = {}
            
            # Extract common routing fields
            if msg.get(1):  # Account
                parsed['account'] = msg.get(1).decode()
            
            if msg.get(15):  # Currency
                parsed['currency'] = msg.get(15).decode()
            
            if msg.get(57):  # TargetSubID
                parsed['target_sub_id'] = msg.get(57).decode()
            
            if msg.get(128):  # DeliverToSubID
                parsed['deliver_to_sub_id'] = msg.get(128).decode()
            
            if msg.get(55):  # Symbol
                parsed['symbol'] = msg.get(55).decode()
            
            if msg.get(54):  # Side
                parsed['side'] = msg.get(54).decode()
            
            if msg.get(38):  # OrderQty
                parsed['order_qty'] = msg.get(38).decode()
            
            if msg.get(40):  # OrdType
                parsed['ord_type'] = msg.get(40).decode()
            
            return parsed
            
        except Exception as e:
            print(f"Error parsing FIX message: {e}")
            return {}
    
    def find_routing_path(self, fix_message: str, preferred_networks: List[str] = None) -> List[Dict]:
        """
        Find the routing path for a given FIX message.
        
        Args:
            fix_message: FIX message string
            preferred_networks: List of preferred networks to check first
            
        Returns:
            List of matching routing rules with network information
        """
        parsed_msg = self.parse_fix_message(fix_message)
        if not parsed_msg:
            return []
        
        matching_routes = []
        
        # Check preferred networks first
        networks_to_check = []
        if preferred_networks:
            networks_to_check.extend(preferred_networks)
        
        # Add all other networks
        for network in self.routing_rules.keys():
            if network not in networks_to_check:
                networks_to_check.append(network)
        
        for network in networks_to_check:
            rules = self.routing_rules.get(network, [])
            
            for rule in rules:
                if self.matches_criteria(parsed_msg, rule['criteria']):
                    route_info = {
                        'network': network,
                        'rule': rule,
                        'match_score': self.calculate_match_score(parsed_msg, rule['criteria'])
                    }
                    matching_routes.append(route_info)
        
        # Sort by match score (higher is better)
        matching_routes.sort(key=lambda x: x['match_score'], reverse=True)
        
        return matching_routes
    
    def matches_criteria(self, message_fields: Dict, criteria: Dict) -> bool:
        """
        Check if message fields match the routing criteria.
        
        Args:
            message_fields: Parsed FIX message fields
            criteria: Routing rule criteria
            
        Returns:
            True if message matches criteria
        """
        for key, expected_value in criteria.items():
            if key not in message_fields:
                continue
                
            message_value = message_fields[key]
            
            # Handle wildcards and patterns
            if expected_value == '*' or expected_value == '*:*:*:*':
                continue
            
            # Handle account number patterns (e.g., 200xxxxx)
            if key == 'account' and 'x' in expected_value.lower():
                pattern = expected_value.replace('x', '\\d').replace('X', '\\d')
                if not re.match(pattern, message_value):
                    return False
            elif message_value != expected_value:
                return False
        
        return len(criteria) > 0  # Only match if there are actual criteria
    
    def calculate_match_score(self, message_fields: Dict, criteria: Dict) -> int:
        """
        Calculate a match score based on how many criteria match.
        More specific matches get higher scores.
        
        Args:
            message_fields: Parsed FIX message fields
            criteria: Routing rule criteria
            
        Returns:
            Match score (higher is better)
        """
        score = 0
        for key, expected_value in criteria.items():
            if key in message_fields and message_fields[key] == expected_value:
                # Exact matches get higher scores
                if expected_value not in ['*', '*:*:*:*']:
                    score += 10
                else:
                    score += 1
        return score
    
    def get_routing_summary(self) -> Dict:
        """Get a summary of all loaded routing rules."""
        summary = {}
        for network, rules in self.routing_rules.items():
            summary[network] = {
                'rule_count': len(rules),
                'sample_rules': rules[:3] if rules else []
            }
        return summary

# Example usage
def main():
    # Initialize router with routing files directory
    router = FIXRouter('/path/to/routing/files')
    
    # Example FIX message (you would replace this with actual FIX message)
    sample_fix_message = "8=FIX.4.2\x019=154\x0135=D\x0149=SENDER\x0156=TARGET\x0134=1\x0152=20241001-12:30:00\x011=2001234\x0115=USD\x0155=AAPL\x0154=1\x0138=100\x0140=2\x01"
    
    # Find routing path
    routes = router.find_routing_path(sample_fix_message)
    
    # Display results
    if routes:
        print("Found routing options:")
        for i, route in enumerate(routes[:5], 1):  # Show top 5 matches
            print(f"\n{i}. Network: {route['network']}")
            print(f"   Destination: {route['rule'].get('route_to', 'Unknown')}")
            print(f"   Match Score: {route['match_score']}")
            print(f"   Criteria: {route['rule']['criteria']}")
    else:
        print("No routing rules matched the FIX message")
    
    # Show routing summary
    print("\nRouting Rules Summary:")
    summary = router.get_routing_summary()
    for network, info in summary.items():
        print(f"{network}: {info['rule_count']} rules")

if __name__ == "__main__":
    main()