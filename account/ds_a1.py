import pandas as pd
import random

# List of sample company names
companies = [
    "BLACKROCK INC", "JP MORGAN CHASE", "GOLDMAN SACHS", "MORGAN STANLEY", 
    "BANK OF AMERICA", "WELLS FARGO", "CITIGROUP", "STATE STREET CORP",
    "FIDELITY INVESTMENTS", "VANGUARD GROUP", "CHARLES SCHWAB", "PRUDENTIAL FINANCIAL",
    "CAPITAL GROUP", "WELLINGTON MANAGEMENT", "NORTHERN TRUST", "T. ROWE PRICE",
    "INVESCO", "FRANKLIN TEMPLETON", "LEGG MASON", "ALLIANCEBERNSTEIN"
]

# Generate account data
account_data = []
for i in range(20):
    account_id = 20000000 + i + 1
    company = companies[i]
    account_data.append([account_id, company])

# Create accounts DataFrame and save to CSV
accounts_df = pd.DataFrame(account_data, columns=['account_id', 'account_name'])
accounts_df.to_csv('account.csv', index=False, header=False)

# Generate subaccount data
subaccount_data = []
first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa", 
               "James", "Jennifer", "William", "Maria", "Richard", "Susan", "Thomas", 
               "Karen", "Charles", "Nancy", "Christopher", "Betty", "Daniel", "Helen"]

last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", 
              "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", 
              "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

subaccount_id_start = 30000000

for account in account_data:
    account_id = account[0]
    # Generate 1-3 subaccounts per account
    num_subaccounts = random.randint(1, 3)
    
    for j in range(num_subaccounts):
        subaccount_id = subaccount_id_start + len(subaccount_data) + 1
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        subaccount_name = f"{first_name} {last_name}"
        
        subaccount_data.append([subaccount_id, account_id, subaccount_name])

# Create subaccounts DataFrame and save to CSV
subaccounts_df = pd.DataFrame(subaccount_data, columns=['subaccount_id', 'account_id', 'subaccount_name'])
subaccounts_df.to_csv('subaccount.csv', index=False, header=False)

print("Generated account.csv with 20 accounts")
print("Generated subaccount.csv with", len(subaccount_data), "subaccounts")