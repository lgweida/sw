import os
import glob
import pandas as pd
from typing import Dict, List, Optional, Any

class FIXRouter:
    def __init__(self, csv_directory: str = "."):
        self.routing_rules = {}
        self.load_routing_rules(csv_directory)
    
    def load_routing_rules(self, directory: str):
        """Load all routing rule CSV files from the directory"""
        csv_files = glob.glob(os.path.join(directory, "alias_*.csv"))
        
        for csv_file in csv_files:
            # Extract network name from filename
            filename = os.path.basename(csv_file)
            network_name = filename.replace("alias_", "").replace(".csv", "")
            
            try:
                # Try different delimiters since files use different separators
                for delimiter in [';', ',']:
                    try:
                        df = pd.read_csv(csv_file, delimiter=delimiter)
                        if not df.empty:
                            self.routing_rules[network_name] = {
                                'columns': df.columns.tolist(),
                                'rules': df.to_dict('records')
                            }
                            break
                    except:
                        continue
            except Exception as e:
                print(f"Error loading {csv_file}: {e}")
    
    def parse_fix_message(self, fix_message: str) -> Dict[str, str]:
        """Parse FIX message into a dictionary of tag=value pairs"""
        fix_fields = {}
        try:
            # Split by SOH character (ASCII 1) or by pipe if SOH not present
            if '\x01' in fix_message:
                pairs = fix_message.split('\x01')
            else:
                pairs = fix_message.split('|')
            
            for pair in pairs:
                if '=' in pair:
                    tag, value = pair.split('=', 1)
                    fix_fields[tag.strip()] = value.strip()
        except Exception as e:
            print(f"Error parsing FIX message: {e}")
        
        return fix_fields
    
    def match_rule(self, rule: Dict[str, Any], fix_fields: Dict[str, str]) -> bool:
        """Check if a rule matches the given FIX message fields"""
        for field, pattern in rule.items():
            if pd.isna(pattern) or pattern in ['*', '']:
                continue
                
            # Handle special field mappings
            actual_value = None
            
            # Map CSV column names to FIX tags
            if field == 'SENDERCOMPID':
                actual_value = fix_fields.get('49')  # SenderCompID
            elif field == 'ONBEHALFOFCOMPID':
                actual_value = fix_fields.get('116')  # OnBehalfOfCompID
            elif field == 'TARGETSUBID':
                actual_value = fix_fields.get('57')  # TargetSubID
            elif field == 'DELIVERTOSUBID':
                actual_value = fix_fields.get('128')  # DeliverToSubID
            elif field == 'CURRENCY':
                actual_value = fix_fields.get('15')  # Currency
            elif field == 'ACCOUNT':
                actual_value = fix_fields.get('1')   # Account
            elif field == 'HANDLINST':
                actual_value = fix_fields.get('21')  # HandlInst
            elif field == 'ETF':
                # ETF might be in custom tag 5847 or other field
                actual_value = fix_fields.get('5847') or fix_fields.get('n')  # Adjust as needed
            elif field == 'COUNTRYCODE':
                actual_value = fix_fields.get('421')  # Country
            elif field == 'FIX.5847':
                actual_value = fix_fields.get('5847')  # Custom tag
            elif field == 'ULFOMSESSIONNAME':
                actual_value = fix_fields.get('n')    # Adjust based on your implementation
            elif field == 'ELECTRONIC_TRADING':
                actual_value = fix_fields.get('n')    # Adjust based on your implementation
            elif field.startswith('#'):
                # Custom identifier field (like #ACCOUNT)
                identifier_name = field[1:]
                actual_value = fix_fields.get(identifier_name)
            else:
                # Try direct tag mapping
                actual_value = fix_fields.get(field)
            
            # If we have a pattern but no actual value, no match
            if actual_value is None:
                return False
            
            # Handle wildcard patterns
            if pattern == '*':
                continue
            
            # Handle account number patterns like 200xxxxx
            if str(pattern).startswith('200') and 'x' in str(pattern):
                pattern_str = str(pattern).replace('x', '.')
                import re
                if not re.match(pattern_str, str(actual_value)):
                    return False
            # Exact match for other cases
            elif str(actual_value) != str(pattern):
                return False
        
        return True
    
    def find_routing_path(self, fix_message: str) -> Optional[str]:
        """Find the routing destination for a given FIX message"""
        fix_fields = self.parse_fix_message(fix_message)
        
        for network_name, network_data in self.routing_rules.items():
            for rule in network_data['rules']:
                if self.match_rule(rule, fix_fields):
                    destination = rule.get('DESTINATION')
                    if destination and not pd.isna(destination):
                        return destination
        
        return None
    
    def get_all_possible_routes(self, fix_message: str) -> List[Dict[str, str]]:
        """Get all possible routing paths for a given FIX message"""
        fix_fields = self.parse_fix_message(fix_message)
        routes = []
        
        for network_name, network_data in self.routing_rules.items():
            for rule in network_data['rules']:
                if self.match_rule(rule, fix_fields):
                    destination = rule.get('DESTINATION')
                    if destination and not pd.isna(destination):
                        routes.append({
                            'network': network_name,
                            'destination': destination,
                            'matched_rule': {k: v for k, v in rule.items() if k != 'DESTINATION'}
                        })
        
        return routes

# Example usage
def main():
    # Initialize the router with CSV files in current directory
    router = FIXRouter()
    
    # Example FIX messages for testing
    test_messages = [
        # Example 1: Match based on account pattern
        "8=FIX.4.2|9=length|35=D|49=FlextradeAlgoFix42|56=broker|1=20012345|15=USD|21=1|55=AAPL|54=1|38=100|40=2|10=checksum",
        
        # Example 2: Match based on specific identifiers
        "8=FIX.4.2|9=length|35=D|49=BFGICRD|56=broker|1=30012345|15=USD|57=FROG|55=MSFT|54=1|38=200|40=1|10=checksum",
        
        # Example 3: Match with custom tag 5847
        "8=FIX.4.2|9=length|35=D|49=SomeSender|56=broker|1=40012345|15=USD|57=FROG|5847=yes|55=GOOG|54=2|38=150|40=2|10=checksum"
    ]
    
    print("Routing Rule Analysis:")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\nTest Message {i}:")
        print("-" * 30)
        
        # Get all possible routes
        routes = router.get_all_possible_routes(message)
        
        if routes:
            for route in routes:
                print(f"Network: {route['network']}")
                print(f"Destination: {route['destination']}")
                print(f"Matched Conditions: {route['matched_rule']}")
                print()
        else:
            print("No matching route found")
        
        # Get single best route
        destination = router.find_routing_path(message)
        if destination:
            print(f"Primary Route: {destination}")
        else:
            print("No primary route found")

if __name__ == "__main__":
    main()