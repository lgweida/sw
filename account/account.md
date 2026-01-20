The error is occurring because you're trying to store `pd.DataFrame` objects directly in a Dash `dcc.Store` component. Dash stores can only store JSON-serializable data (dicts, lists, strings, numbers, etc.), not pandas DataFrames.

Specifically, the issue is in this line:
```python
dcc.Store(id='account-network-data', data=network_data),
```

Where `network_data` contains DataFrame objects. You need to convert the DataFrames to JSON-serializable format before storing them.

Here's the fix:

1. **Update the `load_all_network_files` function** to store data in JSON format:

```python
def load_all_network_files():
    """Load all network CSV files and convert to JSON-serializable format"""
    all_data = {}
    
    for network_key, network_name in NETWORKS.items():
        if network_key == 'total':
            continue
            
        filename = f"account_mapping_{network_key}.csv"
        
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename)
                # Clean column names
                df.columns = [col.strip().upper() for col in df.columns]
                
                # Ensure required columns exist
                if 'ACRONAME' not in df.columns or 'ACCOUNT_NUMBER' not in df.columns:
                    print(f"Warning: Missing required columns in {filename}")
                    continue
                
                # Ensure proper data types
                df['ACCOUNT_NUMBER'] = df['ACCOUNT_NUMBER'].astype(str)
                df['ACRONAME'] = df['ACRONAME'].astype(str)
                
                # Add network column if not present
                if 'NETWORK' not in df.columns:
                    df['NETWORK'] = network_name
                
                # Convert DataFrame to dict for JSON serialization
                all_data[network_key] = df.to_dict('records')
                print(f"Loaded {filename}: {len(df)} rows")
                
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")
        else:
            print(f"Warning: File {filename} not found")
    
    # Create combined dataframe for 'total' tab
    if all_data:
        # Recreate DataFrames for combination
        dfs_to_combine = []
        for network_key, data_dict in all_data.items():
            if data_dict:  # Check if not empty
                df = pd.DataFrame(data_dict)
                dfs_to_combine.append(df)
        
        if dfs_to_combine:
            total_df = pd.concat(dfs_to_combine, ignore_index=True)
            all_data['total'] = total_df.to_dict('records')
            print(f"Total combined rows: {len(total_df)}")
    
    return all_data
```

2. **Update how you access the data in callbacks**. In the `update_account_display` callback, change:

```python
# Convert stored data back to DataFrames
network_data_loaded = {}
for key, df_dict in network_data_dict.items():
    if df_dict:  # Check if not empty list
        network_data_loaded[key] = pd.DataFrame(df_dict)
```

3. **Also update the `download_account_data` callback**:

```python
def download_account_data(n_clicks, tab_value, search_term, network_data_dict):
    if n_clicks and network_data_dict and tab_value in network_data_dict:
        # Get data for current tab and convert to DataFrame
        data_list = network_data_dict[tab_value]
        if data_list:  # Check if not empty
            current_df = pd.DataFrame(data_list)
            
            # Apply filtering if search term exists
            if search_term and str(search_term).strip():
                filtered_df = filter_account_dataframe(current_df, search_term)
            else:
                filtered_df = current_df
            
            if not filtered_df.empty:
                # Create CSV string
                csv_string = filtered_df.to_csv(index=False, encoding='utf-8')
                filename = f"account_mapping_{tab_value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                
                return dict(content=csv_string, filename=filename)
    
    return None
```

4. **Update the `filter_account_dataframe` function** to handle both DataFrame and dict list inputs:

```python
def filter_account_dataframe(df, search_term=None):
    """Filter dataframe by multiple search terms separated by spaces"""
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        return pd.DataFrame()
    
    # Ensure we're working with a DataFrame
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    
    # Rest of the function remains the same...
    # If no search term, return original dataframe
    if not search_term or not str(search_term).strip():
        return df.copy()
    
    # ... rest of your existing code ...
```

5. **Update the startup printing section**:

```python
print(f"\nLoaded Account Networks:")
for network_key in NETWORKS.keys():
    if network_key in network_data and network_data[network_key]:
        record_count = len(network_data[network_key])
        print(f"  • {NETWORKS[network_key]:12} - {record_count:3} records")
    else:
        print(f"  • {NETWORKS[network_key]:12} -   0 records")
```

The key change is that `network_data` should now contain lists of dictionaries (from `df.to_dict('records')`) instead of DataFrames directly, which makes it JSON-serializable for Dash to store.