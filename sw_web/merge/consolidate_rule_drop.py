import pandas as pd
import sys

def get_consolidated_routing_rules_by_priority(file_path: str, sender_comp_id: str) -> pd.DataFrame:
    """
    Reads routing rules, filters them by SENDERCOMPID, consolidates rules 
    with the same routing criteria, maintains high-to-low priority, and 
    drops columns where all resulting consolidated values are the wildcard character (*).

    Args:
        file_path (str): The path to the routing CSV file.
        sender_comp_id (str): The SENDERCOMPID to filter the rules by.

    Returns:
        pd.DataFrame: A DataFrame of the consolidated routing rules.
    """
    
    # 1. Read the CSV file with the correct delimiter
    try:
        df = pd.read_csv(file_path, delimiter=';')
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File not found at: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading file: {e}")
    
    # 2. Filter the rules by the provided SENDERCOMPID 
    filtered_df = df[df['SENDERCOMPID'] == sender_comp_id].copy()
    
    if filtered_df.empty:
        return pd.DataFrame()

    # Add a column to store the priority based on original row index
    filtered_df['_priority'] = filtered_df.index
    
    # 3. Define grouping columns (all criteria except CURRENCY)
    grouping_columns = [
        'TARGETSUBID', 
        'ETF', 
        'COUNTRYCODE', 
        'DESTINATION'
    ]
    
    # 4. Group and consolidate currencies, taking the minimum priority index
    consolidated_df = filtered_df.groupby(grouping_columns).agg(
        CURRENCIES=('CURRENCY', lambda x: ', '.join(sorted(x.unique()))),
        _min_priority=('_priority', 'min')
    ).reset_index()
    
    # 5. Add SENDERCOMPID back
    consolidated_df.insert(0, 'SENDERCOMPID', sender_comp_id)

    # 6. Sort by the minimum priority index to maintain original high-to-low order
    consolidated_df = consolidated_df.sort_values(by='_min_priority', ascending=True)
    
    # 7. Identify and drop columns that only contain '*'
    columns_to_check_for_wildcard = ['TARGETSUBID', 'ETF', 'COUNTRYCODE']
    columns_to_drop = []
    
    for col in columns_to_check_for_wildcard:
        # Check if all unique non-null values in the column are exactly '*'
        if col in consolidated_df.columns and (consolidated_df[col].unique() == ['*']).all():
            columns_to_drop.append(col)

    if columns_to_drop:
        consolidated_df = consolidated_df.drop(columns=columns_to_drop)

    # 8. Clean up and reorder columns
    all_final_columns = ['SENDERCOMPID', 'CURRENCIES', 'TARGETSUBID', 'ETF', 'COUNTRYCODE', 'DESTINATION']
    
    column_order = [col for col in all_final_columns if col in consolidated_df.columns]
    
    return consolidated_df[column_order]

def main(file_path: str = "routing.csv"):
    """
    Main function to load the routing rules, consolidate them, and print the results.
    
    Accepts SENDERCOMPID as a command-line argument.
    """
    
    # Check for command-line argument for SENDERCOMPID
    if len(sys.argv) > 1:
        sender_comp_id = sys.argv[1]
    else:
        sender_comp_id = "BPGICRD"
    
    print(f"--- Consolidated Routing Rules for SENDERCOMPID: {sender_comp_id} (Wildcard Columns Dropped) ---")
    
    try:
        consolidated_rules = get_consolidated_routing_rules_by_priority(file_path, sender_comp_id)
    except Exception as e:
        print(e, file=sys.stderr)
        return

    if not consolidated_rules.empty:
        print("\nRules are sorted by priority (high to low, based on original row index):\n")
        print(consolidated_rules.to_markdown(index=False, numalign="left", stralign="left"))
    else:
        print(f"No rules found for SENDERCOMPID: {sender_comp_id}", file=sys.stdout)

if __name__ == '__main__':
    main(file_path="routing.csv")