Below is a Python function that, given a `SENDERCOMPID` and optional routing parameters (`currency`, `targetsubid`, `etf`, `countrycode`), returns the appropriate destination (desk) based on the `alias_AutoRouteCRD.csv` file. The function uses a most‑specific‑match logic (exact matches take precedence over wildcards) and falls back to the fully wildcard entry if nothing else matches.

Additionally, a helper function is provided to retrieve the `ACCOUNT` number associated with a `SENDERCOMPID` using the `enrichment_CRDAccountMapping.csv` file.

```python
import csv
from typing import Optional, Dict, List, Any

def load_alias_routes(filepath: str) -> List[Dict[str, str]]:
    """
    Load the routing alias CSV into a list of dictionaries.
    Expected columns: SENDERCOMPID, CURRENCY, TARGETSUBID, ETF, COUNTRYCODE, DESTINATION
    """
    routes = []
    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            # Strip whitespace from all values (as per .ini trim directives)
            cleaned = {k: v.strip() for k, v in row.items()}
            routes.append(cleaned)
    return routes

def load_account_mapping(filepath: str) -> Dict[str, str]:
    """
    Load the enrichment CSV mapping SENDERCOMPID to ACCOUNT.
    The file has two columns: SENDERCOMPID;ACCOUNT
    """
    mapping = {}
    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            if len(row) >= 2:
                sender = row[0].strip()
                account = row[1].strip()
                mapping[sender] = account
    return mapping

def get_destination_for_crd(
    sendercompid: str,
    currency: str = '*',
    targetsubid: str = '*',
    etf: str = '*',
    countrycode: str = '*',
    alias_file: str = 'alias_AutoRouteCRD.csv'
) -> Optional[str]:
    """
    Returns the destination (desk) for a given SENDERCOMPID and optional routing attributes.
    The matching follows a most‑specific match: among all rows that match the input
    (allowing wildcards), the row with the highest number of exact (non‑wildcard) matches
    is selected. If multiple rows have the same specificity, the first one encountered
    in the file is returned.

    Args:
        sendercompid (str): The sender comp ID (e.g., 'BPGICRD').
        currency (str): Currency code (default '*').
        targetsubid (str): Target sub ID (default '*').
        etf (str): ETF flag (default '*').
        countrycode (str): Country code (default '*').
        alias_file (str): Path to the alias CSV file.

    Returns:
        str or None: The destination string, or None if no match (should not happen
                     because the file contains a fully wildcard row).
    """
    routes = load_alias_routes(alias_file)

    best_match = None
    best_score = -1

    for route in routes:
        # Check if all fields match (exact or wildcard)
        if not (route['SENDERCOMPID'] in (sendercompid, '*')):
            continue
        if not (route['CURRENCY'] in (currency, '*')):
            continue
        if not (route['TARGETSUBID'] in (targetsubid, '*')):
            continue
        if not (route['ETF'] in (etf, '*')):
            continue
        if not (route['COUNTRYCODE'] in (countrycode, '*')):
            continue

        # Compute specificity score: count of fields that are exact matches (not wildcard)
        score = 0
        if route['SENDERCOMPID'] != '*':
            score += 1
        if route['CURRENCY'] != '*':
            score += 1
        if route['TARGETSUBID'] != '*':
            score += 1
        if route['ETF'] != '*':
            score += 1
        if route['COUNTRYCODE'] != '*':
            score += 1

        if score > best_score:
            best_score = score
            best_match = route['DESTINATION']
        # If equal score, keep the first (order in file acts as tie‑breaker)

    return best_match

def get_account_for_crd(
    sendercompid: str,
    enrichment_file: str = 'enrichment_CRDAccountMapping.csv'
) -> Optional[str]:
    """
    Returns the ACCOUNT number associated with a given SENDERCOMPID.

    Args:
        sendercompid (str): The sender comp ID.
        enrichment_file (str): Path to the enrichment CSV.

    Returns:
        str or None: The account number if found, else None.
    """
    mapping = load_account_mapping(enrichment_file)
    return mapping.get(sendercompid)

# Example usage:
if __name__ == '__main__':
    # Get destination for BPGICRD with USD currency
    dest = get_destination_for_crd('BPGICRD', currency='USD')
    print(f"Destination for BPGICRD (USD): {dest}")

    # Get destination for BPGICRD with any currency (default '*')
    dest2 = get_destination_for_crd('BPGICRD')
    print(f"Destination for BPGICRD (any): {dest2}")

    # Get account number for BPGICRD
    acc = get_account_for_crd('BPGICRD')
    print(f"Account for BPGICRD: {acc}")
```

### Explanation

- **`load_alias_routes`** reads the alias CSV and strips whitespace from every field, as indicated by the `.ini` `[trim]` section.
- **`get_destination_for_crd`** performs a most‑specific match:
  - It iterates over all rows, keeping those where every field either matches the input exactly or is a wildcard (`*`).
  - For each matching row, it counts how many fields are **not** wildcards (i.e., exact constraints).
  - The row with the highest count is selected; if multiple rows have the same count, the first one encountered (the order in the file) is returned.
  - Because the alias file ends with a fully wildcard row (`*;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42`), there will always be a match.
- **`get_account_for_crd`** provides a simple lookup of the account number from the enrichment mapping.

### Notes

- The function expects the CSV files to be in the same directory as the script, or you can provide full paths.
- All parameters are treated as strings; the matching is case‑sensitive (as per the file contents).
- If you need to match on additional fields (e.g., `ETF` with value `'yes'`), simply pass them as arguments.