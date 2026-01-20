# create_csv_files.py
import pandas as pd
import numpy as np

# Function to create random account data
def create_account_data(network_name, num_rows):
    # Sample ACRONAMEs (3-8 character strings)
    base_acronames = ['ABC', 'XYZ', 'DEF', 'GHI', 'JKL', 'MNO', 'PQR', 'STU', 'VWX', 'YZA',
                     'BETA', 'GAMMA', 'DELTA', 'OMEGA', 'ALPHA', 'SIGMA', 'THETA', 'ZETA',
                     'TRADER', 'INVEST', 'CAPITAL', 'FUND', 'EQUITY', 'BOND', 'TRUST']
    
    # Generate unique ACRONAMEs for this network
    acronames = []
    while len(acronames) < num_rows:
        base = np.random.choice(base_acronames)
        suffix = str(np.random.randint(1, 999)) if np.random.random() > 0.5 else ''
        acroname = f"{base}{suffix}"
        if len(acroname) >= 3 and len(acroname) <= 8 and acroname not in acronames:
            acronames.append(acroname)
    
    # Generate unique account numbers starting with 200
    account_numbers = []
    base_num = 2000000
    for i in range(num_rows):
        account_numbers.append(str(base_num + i * 111))
    
    # Create DataFrame
    df = pd.DataFrame({
        'ACRONAME': acronames,
        'ACCOUNT_NUMBER': account_numbers,
        'NETWORK': network_name  # Add network column
    })
    
    return df

# Create data for each network
networks = ['Bloomberg', 'ITG', 'Fidessa', 'TradeWeb', 'TradeWare', 'NYFIX', 'CRD']
network_data = {}

for network in networks:
    # Generate 3-8 rows for each network
    num_rows = np.random.randint(3, 9)
    df = create_account_data(network, num_rows)
    network_data[network] = df
    
    # Save to CSV
    filename = f"account_mapping_{network.lower()}.csv"
    df.to_csv(filename, index=False)
    print(f"Created {filename} with {num_rows} rows")

# Create a combined file with all data
all_data = pd.concat([network_data[network] for network in networks], ignore_index=True)
all_data.to_csv("account_mapping_all.csv", index=False)
print(f"\nCreated account_mapping_all.csv with {len(all_data)} total rows")

# Display sample data
print("\nSample data from each network:")
for network in networks:
    print(f"\n{network}:")
    print(network_data[network][['ACRONAME', 'ACCOUNT_NUMBER']].head())