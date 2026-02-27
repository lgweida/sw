import csv

def load_enrichment_map(filepath):
    """
    Load the enrichment CSV into a dictionary mapping SENDERSUBID to its fields.
    Columns: 0=SENDERSUBID, 1=ACCOUNT, 2=ONBEHALFOFSUBID, 3=CLIENTFULLNAME, 4=ULACCOUNT
    """
    enrichment = {}
    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            if len(row) >= 5:
                sender = row[0].strip()
                enrichment[sender] = {
                    'ACCOUNT': row[1].strip(),
                    'ONBEHALFOFSUBID': row[2].strip(),
                    'CLIENTFULLNAME': row[3].strip(),
                    'ULACCOUNT': row[4].strip()
                }
    return enrichment

def load_alias_map(filepath):
    """
    Load the routing alias CSV.
    Returns a dict mapping ACCOUNT (numeric) to DESTINATION, and a default destination.
    """
    account_to_dest = {}
    default_dest = None
    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            if len(row) >= 6:
                sender_subid = row[0].strip()
                account = row[1].strip()
                currency = row[2].strip()
                etf = row[3].strip()
                fix5847 = row[4].strip()
                dest = row[5].strip()
                if account == '*':
                    # Use the first fully wildcard row as default
                    if default_dest is None:
                        default_dest = dest
                else:
                    account_to_dest[account] = dest
    return account_to_dest, default_dest

def get_destination(sender_sub_id,
                    enrichment_file='enrichment_BloombergOPTAccountMap.csv',
                    alias_file='alias_Bloomberg_OPT_routing.csv'):
    """
    Returns the destination for a given sender sub ID by:
    1. Looking up the sender in the enrichment file to obtain the ULACCOUNT.
    2. Using the ULACCOUNT to find the destination in the routing alias file.
    3. Falling back to the default destination if the ULACCOUNT is not explicitly listed.

    Args:
        sender_sub_id (str): The sender sub ID (e.g., '7914854').
        enrichment_file (str): Path to the enrichment CSV.
        alias_file (str): Path to the routing alias CSV.

    Returns:
        str or None: The destination (e.g., 'O_AGENCY_OPTIONS_WEX_FIX44') or None if
                     the sender sub ID is not found.
    """
    enrichment = load_enrichment_map(enrichment_file)
    alias, default = load_alias_map(alias_file)

    if sender_sub_id not in enrichment:
        return None

    ulaccount = enrichment[sender_sub_id]['ULACCOUNT']
    return alias.get(ulaccount, default)


dest = get_destination('7914854')
print(dest)  # Output: O_AGENCY_OPTIONS_WEX_FIX44