import csv
import configparser
from pathlib import Path
from collections import defaultdict
import pandas as pd


def load_nyfix_account_mapping(mapping_file_path, ini_file_path):
    """
    Load the NYFIX account mapping file using the INI configuration.
    
    Args:
        mapping_file_path (str): Path to the enrichment_NYFIXAccountMapping.csv file
        ini_file_path (str): Path to the enrichment_NYFIXAccountMapping.ini file
    
    Returns:
        dict: Dictionary mapping ONBEHALFOFCOMPID to ACCOUNT
    """
    # Parse the INI file
    config = configparser.ConfigParser()
    with open(ini_file_path, 'r') as ini_file:
        config.read_file(ini_file)
    
    # Get column mappings from INI
    lookup_col = None
    result_col = None
    
    if 'lookup' in config:
        for key, value in config['lookup'].items():
            if value == 'ONBEHALFOFCOMPID':
                lookup_col = int(key)
    
    if 'result' in config:
        for key, value in config['result'].items():
            if value == 'ACCOUNT':
                result_col = int(key)
    
    lookup_col = lookup_col if lookup_col is not None else 0  
    result_col = result_col if result_col is not None else 1
    if lookup_col is None or result_col is None:
        raise ValueError("Could not determine column mappings from INI file")
    
    # Read the mapping file
    onbehalf_to_account = {}
    
    with open(mapping_file_path, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        for row in reader:
            if not row or len(row) <= max(lookup_col, result_col):
                continue
            
            onbehalf = row[lookup_col].strip()
            account = row[result_col].strip()
            
            if onbehalf and account and onbehalf != '*' and account != '*':
                onbehalf_to_account[onbehalf] = account
    
    return onbehalf_to_account


def load_nyfix_routing(routing_file_path):
    """
    Load the NYFIX routing file (alias_AutoRouteNYFIX.csv) and extract ONBEHALFOFCOMPID to DESTINATION mappings.
    
    Args:
        routing_file_path (str): Path to the alias_AutoRouteNYFIX.csv file
    
    Returns:
        dict: Dictionary mapping ONBEHALFOFCOMPID to set of destinations
    """
    onbehalf_to_destinations = defaultdict(set)
    
    with open(routing_file_path, 'r') as csv_file:
        # Read the header to find column indices
        header = csv_file.readline().strip().split(';')
        
        # Find column indices
        try:
            onbehalf_idx = header.index('ONBEHALFOFCOMPID')
            dest_idx = header.index('DESTINATION')
        except ValueError as e:
            # If header doesn't match, assume first column is ONBEHALFOFCOMPID and last is DESTINATION
            print(f"Warning: Could not find expected columns in header: {e}")
            print("Assuming first column is ONBEHALFOFCOMPID and last column is DESTINATION")
            onbehalf_idx = 0
            dest_idx = -1
        
        # Reset file pointer to beginning
        csv_file.seek(0)
        reader = csv.reader(csv_file, delimiter=';')
        
        # Skip header
        next(reader)
        
        for row in reader:
            if not row:
                continue
            
            # Get ONBEHALFOFCOMPID (handle both positive and negative indices)
            if onbehalf_idx >= 0 and onbehalf_idx < len(row):
                onbehalf = row[onbehalf_idx].strip()
            else:
                onbehalf = None
            
            # Get DESTINATION
            if dest_idx >= 0 and dest_idx < len(row):
                destination = row[dest_idx].strip()
            elif dest_idx == -1 and len(row) > 0:
                destination = row[-1].strip()
            else:
                destination = None
            
            # Only add if both are valid and ONBEHALFOFCOMPID is not '*'
            if onbehalf and destination and onbehalf != '*':
                onbehalf_to_destinations[onbehalf].add(destination)
    
    return onbehalf_to_destinations


def link_accounts_to_destinations(mapping_file_path, mapping_ini_path, routing_file_path):
    """
    Link accounts to destinations using the mapping and routing files.
    
    This function:
    1. Loads the mapping from ONBEHALFOFCOMPID to ACCOUNT from the mapping file
    2. Loads the mapping from ONBEHALFOFCOMPID to DESTINATIONS from the routing file
    3. Joins them to create a mapping from ACCOUNT to DESTINATIONS
    
    Args:
        mapping_file_path (str): Path to the enrichment_NYFIXAccountMapping.csv file
        mapping_ini_path (str): Path to the enrichment_NYFIXAccountMapping.ini file
        routing_file_path (str): Path to the alias_AutoRouteNYFIX.csv file
    
    Returns:
        dict: Dictionary with ACCOUNT as key and list of unique DESTINATIONS as value
    """
    
    print("Loading account mappings...")
    onbehalf_to_account = load_nyfix_account_mapping(mapping_file_path, mapping_ini_path)
    print(f"Loaded {len(onbehalf_to_account)} ONBEHALFOFCOMPID to ACCOUNT mappings")
    
    print("\nLoading routing mappings...")
    onbehalf_to_destinations = load_nyfix_routing(routing_file_path)
    print(f"Loaded {len(onbehalf_to_destinations)} ONBEHALFOFCOMPID to DESTINATION mappings")
    
    # Join the mappings
    account_to_destinations = defaultdict(set)
    unmatched_onbehalf = []
    
    for onbehalf, destinations in onbehalf_to_destinations.items():
        if onbehalf in onbehalf_to_account:
            account = onbehalf_to_account[onbehalf]
            account_to_destinations[account].update(destinations)
        else:
            unmatched_onbehalf.append(onbehalf)
    
    # Convert sets to sorted lists
    result = {account: sorted(list(destinations)) 
              for account, destinations in account_to_destinations.items()}
    
    print(f"\nLinked {len(result)} accounts to destinations")
    print(f"Found {len(unmatched_onbehalf)} ONBEHALFOFCOMPID(s) in routing file without a matching account in mapping file")
    if unmatched_onbehalf:
        print(f"Warning: {len(unmatched_onbehalf)} ONBEHALFOFCOMPID(s) in routing file not found in mapping file")
        print(f"unmatched ONBEHALFOFCOMPID(s): {unmatched_onbehalf}")

    return result, unmatched_onbehalf


def get_destinations_for_account(account, account_to_destinations):
    """
    Get all destinations for a specific account.
    
    Args:
        account (str): Account number to look up
        account_to_destinations (dict): Dictionary from account to destinations
    
    Returns:
        list: List of destinations for the account
    """
    return account_to_destinations.get(account, [])


def save_account_destinations_to_file(account_to_destinations, output_file_path, 
                                       include_unmatched=False, unmatched_list=None):
    """
    Save the account to destinations mappings to a file.
    
    Args:
        account_to_destinations (dict): Dictionary with account as key and destinations as value
        output_file_path (str): Path to the output file
        include_unmatched (bool): Whether to include unmatched ONBEHALFOFCOMPIDs
        unmatched_list (list): List of unmatched ONBEHALFOFCOMPIDs
    """
    
    with open(output_file_path, 'w') as out_file:
        # Write header
        out_file.write("ACCOUNT,DESTINATION\n")
        
        # Write mappings
        for account in sorted(account_to_destinations.keys()):
            destinations = account_to_destinations[account]
            for dest in destinations:
                out_file.write(f"{account},{dest}\n")
    
    print(f"Saved {len(account_to_destinations)} account mappings to {output_file_path}")


def print_mapping_summary(account_to_destinations, unmatched_onbehalf):
    """
    Print a summary of the account to destination mappings.
    
    Args:
        account_to_destinations (dict): Dictionary with account as key and destinations as value
        unmatched_onbehalf (list): List of unmatched ONBEHALFOFCOMPIDs
    """
    
    print(f"\n{'='*70}")
    print(f"ACCOUNT TO DESTINATION MAPPING SUMMARY")
    print(f"{'='*70}")
    
    print(f"Total accounts mapped: {len(account_to_destinations)}")
    
    # Count total mappings
    total_mappings = sum(len(dests) for dests in account_to_destinations.values())
    print(f"Total account-destination pairs: {total_mappings}")
    
    # Show distribution
    dest_counts = {}
    for account, destinations in account_to_destinations.items():
        count = len(destinations)
        dest_counts[count] = dest_counts.get(count, 0) + 1
    
    print(f"\nDistribution:")
    for count, num_accounts in sorted(dest_counts.items()):
        print(f"  {num_accounts} account(s) have {count} destination(s)")
    
    # Show unmatched
    if unmatched_onbehalf:
        print(f"\nUnmatched ONBEHALFOFCOMPIDs (in routing but not in mapping): {len(unmatched_onbehalf)}")
        if len(unmatched_onbehalf) <= 20:
            print(f"  {', '.join(unmatched_onbehalf[:20])}")
        else:
            print(f"  First 20: {', '.join(unmatched_onbehalf[:20])}")
            print(f"  ... and {len(unmatched_onbehalf) - 20} more")
    
    # Show sample mappings
    print(f"\nSample account mappings (first 10 accounts):")
    print(f"{'ACCOUNT':<12} {'DESTINATIONS':<30}")
    print(f"{'-'*12} {'-'*30}")
    
    for i, (account, destinations) in enumerate(sorted(account_to_destinations.items())):
        if i >= 10:
            break
        dest_str = ', '.join(destinations)
        # Truncate if too long
        if len(dest_str) > 30:
            dest_str = dest_str[:27] + "..."
        print(f"{account:<12} {dest_str:<30}")


def main():
    """
    Main function to demonstrate the usage of the account to destination linking.
    """
    
    root_dir = "client_data"  # Update this to your actual root directory containing the files
    # File paths (update these to your actual file paths)
    mapping_file = f"{root_dir}/enrichments/enrichment_NYFIXAccountMapping.csv"
    mapping_ini = f"{root_dir}/enrichments/enrichment_NYFIXAccountMapping.ini"
    routing_file = f"{root_dir}/conf/aliases/alias_AutoRouteNYFIX.csv"
    
    # Check if files exist
    files_to_check = [
        (mapping_file, "Mapping CSV"),
        (mapping_ini, "Mapping INI"),
        (routing_file, "Routing CSV")
    ]
    
    all_files_exist = True
    for file_path, file_desc in files_to_check:
        if not Path(file_path).exists():
            print(f"Error: {file_desc} file '{file_path}' not found!")
            all_files_exist = False
    
    if not all_files_exist:
        print("\nPlease make sure all files are in the current directory.")
        return
    
    try:
        # Link accounts to destinations
        print("Linking accounts to destinations...")
        account_to_destinations, unmatched = link_accounts_to_destinations(
            mapping_file, mapping_ini, routing_file
        )
        
        # Print summary
        print_mapping_summary(account_to_destinations, unmatched)
        
        # Save to file
        output_file = "account_destination_mapping.csv"
        save_account_destinations_to_file(account_to_destinations, output_file)
        
        # Example: Get destinations for a specific account
        if account_to_destinations:
            sample_account = next(iter(account_to_destinations.keys()))
            destinations = get_destinations_for_account(sample_account, account_to_destinations)
            print(f"\nExample: Account {sample_account} -> Destinations: {destinations}")
            df = pd.DataFrame({"Account": list(account_to_destinations.keys()), 
                               "Destinations": [', '.join(dests) for dests in account_to_destinations.values()]})
            print("\nFull account to destination mapping:")
            df['Adapter'] = 'NYFIX'  # Add a column to indicate the source adapter
            print(df)
        
    except Exception as e:
        print(f"Error processing files: {e}")
        import traceback
        traceback.print_exc()


# If you want to use the functions in your own code
if __name__ == "__main__":
    main()
else:
    # Export the main functions for use in other modules
    __all__ = [
        'load_nyfix_account_mapping',
        'load_nyfix_routing',
        'link_accounts_to_destinations',
        'get_destinations_for_account',
        'save_account_destinations_to_file',
        'print_mapping_summary'
    ]