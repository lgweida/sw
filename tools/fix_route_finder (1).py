import csv
import os
import argparse
from collections import defaultdict

class FixRouteFinder:
    def __init__(self, rules_dir):
        """Initialize the route finder and load all routing rules from the specified directory"""
        self.rules_dir = rules_dir
        self.routing_rules = defaultdict(list)  # Organize rules by network name
        self.field_mapping = {
            # Add FIX tag to field name mappings if needed
            # Example: '35': 'MSG_TYPE',
        }
        self.load_all_rules()
        
    def load_all_rules(self):
        """Load all routing rule CSV files from the directory"""
        try:
            # Get all files starting with 'alias_' and ending with '.csv'
            for filename in os.listdir(self.rules_dir):
                if filename.startswith('alias_') and filename.endswith('.csv'):
                    network_name = filename[len('alias_'):-len('.csv')]
                    file_path = os.path.join(self.rules_dir, filename)
                    self._load_rules_from_file(network_name, file_path)
                    
            print(f"Successfully loaded routing rules for {len(self.routing_rules)} networks")
            
        except Exception as e:
            print(f"Error loading routing rules: {str(e)}")
            raise
    
    def _load_rules_from_file(self, network, file_path):
        """Load routing rules from a single CSV file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                # Detect CSV delimiter (comma or semicolon)
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
                csvfile.seek(0)
                
                reader = csv.DictReader(csvfile, dialect=dialect)
                rules_count = 0
                
                for row in reader:
                    # Extract destination
                    destination = row.get('DESTINATION')
                    if not destination:
                        continue
                        
                    # Build rule conditions (exclude DESTINATION itself)
                    conditions = {k: v.strip() for k, v in row.items() if k != 'DESTINATION' and v.strip()}
                    
                    # Add to rules collection
                    self.routing_rules[network].append({
                        'conditions': conditions,
                        'destination': destination
                    })
                    rules_count += 1
                
                print(f"Loaded {rules_count} rules from {file_path} (Network: {network})")
                
        except Exception as e:
            print(f"Error loading file {file_path}: {str(e)}")
    
    def _parse_fix_message(self, fix_string):
        """Parse a FIX message string into a dictionary"""
        # Simple FIX message parsing - assumes fields are separated by | in tag=value format
        # More complex parsing may be needed for production use
        fix_fields = {}
        for field in fix_string.split('|'):
            if '=' in field:
                tag, value = field.split('=', 1)
                # Convert tag to name using mapping if available
                field_name = self.field_mapping.get(tag, tag)
                fix_fields[field_name] = value.strip()
        return fix_fields
    
    def _calculate_match_score(self, fix_message, rule_conditions):
        """Calculate matching score between FIX message and rule conditions"""
        score = 0
        total_conditions = len(rule_conditions)
        
        if total_conditions == 0:
            return 0  # Rules with no conditions don't participate in matching
        
        for field, required_value in rule_conditions.items():
            # Get corresponding field value from FIX message
            message_value = fix_message.get(field)
            
            if message_value is None:
                # Message doesn't contain this field, can't match
                continue
                
            if required_value == '*':
                # Wildcard match, give base score
                score += 1
            elif required_value == message_value:
                # Exact match, give higher score
                score += 3
            elif '*' in required_value:
                # Partial wildcard match (e.g., ABC*)
                pattern = required_value.replace('*', '')
                if message_value.startswith(pattern) or message_value.endswith(pattern):
                    score += 2
        
        # Calculate match percentage
        return (score / (total_conditions * 3)) * 100 if total_conditions > 0 else 0
    
    def find_best_route(self, fix_input):
        """
        Find the best route for a given FIX message
        fix_input can be either a string or a parsed dictionary
        """
        # Parse string input to dictionary if needed
        if isinstance(fix_input, str):
            fix_message = self._parse_fix_message(fix_input)
        else:
            fix_message = fix_input
            
        best_route = None
        highest_score = 0
        
        # Check all rules across all networks
        for network, rules in self.routing_rules.items():
            for rule in rules:
                score = self._calculate_match_score(fix_message, rule['conditions'])
                
                # Update best route if current score is higher
                if score > highest_score and score > 0:
                    highest_score = score
                    best_route = {
                        'network': network,
                        'destination': rule['destination'],
                        'match_score': round(score, 2),
                        'conditions_matched': rule['conditions']
                    }
        
        return best_route

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='FIX Message Route Finder')
    parser.add_argument('rules_directory', help='Path to directory containing routing rule CSV files')
    args = parser.parse_args()
    
    # Validate directory exists
    if not os.path.isdir(args.rules_directory):
        print(f"Error: Directory {args.rules_directory} does not exist")
        return
    
    # Initialize route finder
    try:
        route_finder = FixRouteFinder(args.rules_directory)
    except Exception as e:
        print(f"Failed to initialize route finder: {str(e)}")
        return
    
    # Example 1: Using dictionary format FIX message
    example_fix_dict = {
        'ULFOMSESSIONNAME': 'Session123',
        'HANDLINST': 'FlextradeAlgoFix42',
        'FIX.5847': 'broker',
        'TARGETSUBID': 'FROG',
        'CURRENCY': 'USD',
        'ONBEHALFOFCOMPID': 'MHFEUAG',
        'SENDERCOMPID': 'BFGICRD',
        'ETF': 'yes',
        'COUNTRYCODE': 'US'
    }
    
    print("\n=== Testing Example 1 (Dictionary Format FIX Message) ===")
    best_route = route_finder.find_best_route(example_fix_dict)
    if best_route:
        print(f"Best Route Network: {best_route['network']}")
        print(f"Destination: {best_route['destination']}")
        print(f"Match Score: {best_route['match_score']}%")
        print("Matched Conditions:")
        for k, v in best_route['conditions_matched'].items():
            print(f"  {k}: {v}")
    else:
        print("No matching routing rules found")
    
    # Example 2: Using FIX string format message
    example_fix_string = (
        "ULFOMSESSIONNAME=Session456|HANDLINST=FlextradeAlgoFix42|FIX.5847=broker|"
        "TARGETSUBID=FROG|CURRENCY=USD|ONBEHALFOFCOMPID=SomeComp|SENDERCOMPID=BFGICRD|"
        "ETF=yes|COUNTRYCODE=US"
    )
    
    print("\n=== Testing Example 2 (FIX String Format Message) ===")
    best_route = route_finder.find_best_route(example_fix_string)
    if best_route:
        print(f"Best Route Network: {best_route['network']}")
        print(f"Destination: {best_route['destination']}")
        print(f"Match Score: {best_route['match_score']}%")
        print("Matched Conditions:")
        for k, v in best_route['conditions_matched'].items():
            print(f"  {k}: {v}")
    else:
        print("No matching routing rules found")

if __name__ == "__main__":
    main()
    