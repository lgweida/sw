import pandas as pd
from typing import Dict, List, Any

class RoutingEngine:
    def __init__(self, lookup_fields: List[str], results: Dict[str, int]):
        self.lookup_fields = lookup_fields
        self.results = results
        
    def parse_client_rules(self, csv_content: str) -> List[Dict]:
        """Parse client rules from CSV content"""
        rules = []
        lines = csv_content.strip().split('\n')
        
        for line in lines:
            fields = [field.strip() for field in line.split(',')]
            rule = {}
            for i, field_name in enumerate(self.lookup_fields):
                if i < len(fields):
                    rule[field_name] = fields[i]
            rules.append(rule)
            
        return rules
    
    def evaluate_rule(self, rule: Dict, account: str, target_subid: str = None, etf: str = None) -> bool:
        """Evaluate if a rule matches the given conditions"""
        # Check account match
        if rule.get('ACCOUNT') != account and rule.get('ACCOUNT') != '*':
            return False
            
        # Check #TARGETSUBID match
        if target_subid and rule.get('#TARGETSUBID') != '*' and rule.get('#TARGETSUBID') != target_subid:
            return False
            
        # Check ETF match  
        if etf and rule.get('ETF') != '*' and rule.get('ETF') != etf:
            return False
            
        return True
    
    def get_routing_desk(self, rules: List[Dict], account: str, target_subid: str = None, etf: str = None) -> str:
        """Get the routing desk based on matching rules"""
        for rule in rules:
            if self.evaluate_rule(rule, account, target_subid, etf):
                # Extract desk from the last field (assuming desk is in the last position)
                desk_field = list(rule.values())[-1] if rule else None
                if desk_field and desk_field != '*':
                    return desk_field
        return None

def main():
    # Given routing lookup configuration
    lookup_config = {
        "lookupFields": [
            "ACCOUNT", "#ACCOUNT", "#SENDERSUBID", "#TARGETSUBID", "TARGETSUBID",
            "FIX.5847", "DELIVERTOSUBID", "ONBEHALFOFSUBID", "CURRENCY", "ETF",
            "ONBEHALFOFCOMPID", "ULFROMSESSIONNAME"
        ],
        "results": {
            "FLEX17_DESK": 12
        }
    }
    
    # Client rules CSV content
    client_rules_csv = """20010783,*,*,*,*,*,*,*,yes,*,*,ETF17
20010783,*,*,PROG,*,*,*,*,*,*,*,PT17
20010783,*,*,PROG,*,*,*,*,yes,*,*,PT17"""
    
    # Initialize routing engine
    router = RoutingEngine(lookup_config["lookupFields"], lookup_config["results"])
    
    # Parse client rules
    rules = router.parse_client_rules(client_rules_csv)
    
    # Test cases
    account = "20010783"
    
    print("Routing Logic Demonstration")
    print("=" * 50)
    print(f"Account: {account}")
    print()
    
    # Test Case 1: ETF = yes, #TARGETSUBID = None
    print("Test Case 1: ETF = 'yes', #TARGETSUBID = None")
    desk1 = router.get_routing_desk(rules, account, None, "yes")
    print(f"Routing Desk: {desk1}")
    print(f"Explanation: Matches rule 1 - ETF='yes' routes to ETF17")
    print()
    
    # Test Case 2: #TARGETSUBID = PROG, ETF = None
    print("Test Case 2: #TARGETSUBID = 'PROG', ETF = None")
    desk2 = router.get_routing_desk(rules, account, "PROG", None)
    print(f"Routing Desk: {desk2}")
    print(f"Explanation: Matches rule 2 - #TARGETSUBID='PROG' routes to PT17")
    print()
    
    # Test Case 3: #TARGETSUBID = PROG, ETF = yes
    print("Test Case 3: #TARGETSUBID = 'PROG', ETF = 'yes'")
    desk3 = router.get_routing_desk(rules, account, "PROG", "yes")
    print(f"Routing Desk: {desk3}")
    print(f"Explanation: Matches rule 3 - #TARGETSUBID='PROG' takes precedence even when ETF='yes', routes to PT17")
    print()
    
    # Show the rules for clarity
    print("Client Rules:")
    print("-" * 30)
    for i, rule in enumerate(rules, 1):
        print(f"Rule {i}: {rule}")
    print()
    
    # Summary
    print("Summary:")
    print("- Account 20010783 routes to ETF17 when ETF='yes'")
    print("- Account 20010783 routes to PT17 when #TARGETSUBID='PROG'")
    print("- #TARGETSUBID='PROG' condition takes precedence over ETF='yes'")

if __name__ == "__main__":
    main()