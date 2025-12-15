import pandas as pd
import sys

def get_consolidated_routing_rules_by_priority(file_path: str, sender_comp_id: str) -> pd.DataFrame:
    """
    Reads routing rules, filters them by SENDERCOMPID, consolidates rules 
    with the same routing criteria, and maintains the high-to-low priority 
    order based on the rule's original position in the file.

    Args:
        file_path (str): The path to the routing CSV file.
        sender_comp_id (str): The SENDERCOMPID to filter the rules by.

    Returns:
        pd.DataFrame: A DataFrame of the consolidated routing rules, 
                      ordered by their highest priority (lowest original index).
    """
    
    # 1. Read the CSV file with the correct delimiter
    try:
        df = pd.read_csv(file_path, delimiter=';')
    except FileNotFoundError:
        # Instead of returning a DataFrame with an error message, raise an exception
        # or handle it within main for cleaner separation.
        raise FileNotFoundError(f"Error: File not found at: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading file: {e}")
    
    # 2. Filter the rules by the provided SENDERCOMPID 
    filtered_df = df[df['SENDERCOMPID'] == sender_comp_id].copy()
    
    if filtered_df.empty:
        # Return empty DataFrame if no rules are found
        return pd.DataFrame()

    # Add a column to store the priority based on original row index
    # Lower index = Higher priority
    filtered_df['_priority'] = filtered_df.index
    
    # 3. Define grouping columns (all criteria except CURRENCY and SENDERCOMPID)
    grouping_columns = [
        'TARGETSUBID', 
        'ETF', 
        'COUNTRYCODE', 
        'DESTINATION'
    ]
    
    # 4. Group and consolidate currencies, taking the minimum priority index
    consolidated_df = filtered_df.groupby(grouping_columns).agg(
        # Consolidate currencies as a sorted, comma-separated string
        CURRENCIES=('CURRENCY', lambda x: ', '.join(sorted(x.unique()))),
        # Find the highest priority (lowest index) within the group
        _min_priority=('_priority', 'min')
    ).reset_index()
    
    # 5. Add SENDERCOMPID back and clean up
    consolidated_df.insert(0, 'SENDERCOMPID', sender_comp_id)

    # 6. Sort by the minimum priority index to maintain original high-to-low order
    consolidated_df = consolidated_df.sort_values(by='_min_priority', ascending=True)
    
    # 7. Clean up and reorder columns
    column_order = [
        'SENDERCOMPID', 'CURRENCIES', 'TARGETSUBID', 
        'ETF', 'COUNTRYCODE', 'DESTINATION'
    ]
    
    return consolidated_df[column_order]

def main(file_path: str = "routing.csv"):
    """
    Main function to load the routing rules, consolidate them, and print the results.
    
    Accepts SENDERCOMPID as a command-line argument.
    """
    
    # Check for command-line argument for SENDERCOMPID
    if len(sys.argv) > 1:
        # Use the first argument after the script name as the SENDERCOMPID
        sender_comp_id = sys.argv[1]
    else:
        # Default SENDERCOMPID if no argument is provided
        sender_comp_id = "BPGICRD"
    
    print(f"--- Consolidated Routing Rules for SENDERCOMPID: {sender_comp_id} ---")
    
    try:
        consolidated_rules = get_consolidated_routing_rules_by_priority(file_path, sender_comp_id)
    except Exception as e:
        print(e, file=sys.stderr)
        return

    if not consolidated_rules.empty:
        print("\nRules are sorted by priority (high to low, based on original row index):\n")
        # Print the DataFrame in Markdown format
        print(consolidated_rules.to_markdown(index=False, numalign="left", stralign="left"))
    else:
        # This handles the case where rules are not found, which is already printed by get_consolidated_routing_rules_by_priority
        # but since we changed it to return an empty DataFrame, we'll re-add the print here.
        if sender_comp_id in get_consolidated_routing_rules_by_priority(file_path, sender_comp_id).columns:
            # If the column is SENDERCOMPID, it means it returned a valid empty df, which is already handled by the prior print.
            pass
        else:
            print(f"No rules found for SENDERCOMPID: {sender_comp_id}", file=sys.stdout)


if __name__ == '__main__':
    main(file_path="routing.csv")