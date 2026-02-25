import pandas as pd

def compare_dataframes_by_columns(df1, df2, keys, dropna=True, return_rows=False):
    """
    Compare two DataFrames based on one or more key columns, identifying records that are:
    - Only in df1
    - Common to both (based on the combination of key columns)
    - Only in df2
    """

    # Ensure keys is a list
    if isinstance(keys, str):
        keys = [keys]

    # Check that all key columns exist in both DataFrames
    for col in keys:
        if col not in df1.columns or col not in df2.columns:
            raise ValueError(f"Column '{col}' must exist in both DataFrames.")

    # Make a copy of the DataFrames to avoid modifying originals,
    # and optionally drop rows with NaN in any key column
    if dropna:
        df1_clean = df1.dropna(subset=keys).copy()
        df2_clean = df2.dropna(subset=keys).copy()
    else:
        df1_clean = df1.copy()
        df2_clean = df2.copy()

    # Create a Series of tuples representing the composite key for each row
    key1 = df1_clean[keys].apply(tuple, axis=1)
    key2 = df2_clean[keys].apply(tuple, axis=1)

    # Get unique sets of key tuples
    set1 = set(key1.unique())
    set2 = set(key2.unique())

    # Compute categories
    only_A = set1 - set2
    common = set1 & set2
    only_B = set2 - set1

    # Build the result dictionary
    result = {
        'only_A_set': only_A,
        'common_set': common,
        'only_B_set': only_B,
        'only_A_count': len(only_A),
        'common_count': len(common),
        'only_B_count': len(only_B)
    }

    # If rows are requested, filter and add them
    if return_rows:
        # Use .isin() on the tuple Series to filter rows
        result['only_A_rows'] = df1_clean[key1.isin(only_A)]
        result['only_B_rows'] = df2_clean[key2.isin(only_B)]
        result['common_A_rows'] = df1_clean[key1.isin(common)]
        result['common_B_rows'] = df2_clean[key2.isin(common)]

    return result