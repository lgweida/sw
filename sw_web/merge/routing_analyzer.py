import pandas as pd
from io import StringIO

def get_routing_matrix(account, csv_file_path=None, csv_data=None):
    # Read the CSV data
    if csv_file_path:
        df = pd.read_csv(csv_file_path)
    elif csv_data:
        df = pd.read_csv(StringIO(csv_data))
    else:
        raise ValueError("Either csv_file_path or csv_data must be provided")
    
    # Filter by account - try both string and int comparison
    df_account = df[(df['ACCOUNT'] == str(account)) | (df['ACCOUNT'] == int(account))].copy()
    
    if df_account.empty:
        # Debug: show what accounts are available
        available_accounts = df['ACCOUNT'].unique()
        raise ValueError(f"No routing rules found for account {account}. Available accounts: {available_accounts}")
    
    # Build the routing matrix
    matrix_data = []
    for idx, row in df_account.iterrows():
        conditions = []
        for col in df_account.columns[:-1]:  # Exclude DESK column
            if row[col] != '*' and col != 'ACCOUNT':  # Skip wildcards and ACCOUNT
                conditions.append(f"{col}={row[col]}")
        
        matrix_data.append({
            'Rule': len(matrix_data) + 1,
            'Conditions': ' AND '.join(conditions) if conditions else 'All other cases',
            'Destination': row['DESK']
        })
    
    return pd.DataFrame(matrix_data)


def print_routing_matrix(account, csv_file_path=None, csv_data=None):
    matrix_df = get_routing_matrix(account, csv_file_path, csv_data)
    
    print("=" * 100)
    print(f"ROUTING RULE TABLE FOR ACCOUNT {account}")
    print("=" * 100)
    print()
    print(matrix_df.to_string(index=False))
    print()
    print("=" * 100)
    
    return matrix_df


# Example usage
if __name__ == "__main__":
    # Sample CSV data
    sample_csv = """ACCOUNT,#ACCOUNT,#SENDERSUBID,#TARGETSUBID,TARGETSUBID,FIX.5847,DELIVERTOSUBID,ONBEHALFOFSUBID,ETF,CURRENCY,ONBEHALFOFCOMPID,DESK
20010783,*,*,*,*,*,*,*,yes,*,*,ETF17
20010783,*,*,PROG,*,*,*,*,*,*,*,PT17
20010783,*,*,PROG,*,*,*,*,yes,*,*,PT17
20010784,*,*,*,*,*,*,*,*,USD,*,USD_DESK
20010784,*,*,ALGO,*,*,*,*,*,*,*,ALGO_DESK"""
    
    print("-" * 100)
    routing_df = get_routing_matrix(20010783, csv_data=sample_csv)
    print(routing_df)
    print()
    
    print_routing_matrix(20010783, csv_data=sample_csv)
