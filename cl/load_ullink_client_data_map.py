import json
import re
import pandas as pd
from pprint import pprint
import adapter
import load_snow_client_data
import compare_df

ullink_clients = ["aut", "bbg", "crd", "fid",
                  "itg", "nfx", "sgd",  "tdw", "tkgor"]
pattern = r"^(.*?)\s+\((\d+)\)\s+/ (.*?)\s+(.*)$"


def load_ullink_client_data():
    parsed_data = []
    for ullink_client in ullink_clients:
        account_path = f"./client_data/data/{ullink_client}"
        names_path = f"./client_data/data/{ullink_client}_names"
        with open(account_path, 'r') as f:
            account_list = f.read().splitlines()
        with open(names_path, 'r') as f:
            text = f.read()
        for line in text.strip().split("\n"):
            match = re.match(pattern, line.strip())
            if match:
                entity_name = match.group(1).strip()
                entity_id = match.group(2)
                network = match.group(3).strip()
                codes = [code.strip("()")
                         for code in re.findall(r"\((.*?)\)", match.group(4))]
                codes = list(set(codes))
                codes.sort()
                if f"{entity_id}" in account_list:
                    parsed_data.append({
                        "Client": entity_name,
                        "Account": entity_id,
                        "Network": network,
                        "Identifier": ','.join(codes),
                        "Count": len(codes)
                    })

    df = pd.DataFrame(parsed_data)
    is_duplicate = df.duplicated(
        subset=['Client', 'Account', 'Network', 'Identifier'])
    duplicated_rows = df[is_duplicate]
    if not duplicated_rows.empty:
        print("Duplicate rows found:")
        pprint(duplicated_rows)
    df = df.drop_duplicates()
    df.rename(columns={
        'Client': 'Client Name',
        'Account': 'Account',
        'Network': 'Network',
        'Identifier': 'Identifier'
    }, inplace=True)

    # List of all target columns (in the order you prefer)
    target_columns = [
        'Client Name', 'Account', 'OMS', 'Network', 'Identifier',
        'High Touch', 'Low Touch', 'PT', 'ETF', 'IS', 'Japan', 'CB',
        'Options', 'Direct Tokyo', 'Start Time', 'End Time', 'Adapter Name'
    ]

    target_columns = [
        'Client Name',
        'Account',
        'Network',
        'Identifier'
    ]
    df['Network'] = df['Network'].str.lower().replace({'autex': 'Tradeweb',
                                                       'Charles': 'Charles River',
                                                       'tk gor': 'MIZUHO TK',
                                                       'quattro tk': 'MIZUHO TK'
                                                       }).str.upper()

    # Reorder columns to match the target list (optional)
    df['Identifier'] = df['Identifier'].str.split(',')   # splits into list
    # explodes list into rows
    df = df.explode('Identifier')
    df.reset_index(drop=True, inplace=True)

    df = df[target_columns]
    df = add_adapter_name(df)

    pd.set_option('display.max_rows', None)      # Show all rows
    pd.set_option('display.max_columns', None)   # Show all columns
    df = add_oms_name(df)
    pd.set_option('display.max_rows', None)      # Show all rows
    pd.set_option('display.max_columns', None)   # Show all columns

    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')

    parsed_data = df.to_dict('records')
    return parsed_data


def add_oms_name(df):
    df_snow = load_snow_client_data.load_snow_client_data()
    df_snow.rename(columns={'u_mizuho_account_number': 'Account',
                   'u_oms_provider': 'OMS', 'u_network_provider': 'Network'}, inplace=True)
    df_snow['Account'] = df_snow['Account'].astype(str)

    columns_to_drop = ['u_number', 'u_requested_for', 'u_closed', 'u_flow_type']

    df_snow = df_snow.drop(columns=columns_to_drop)
    is_duplicate = df.duplicated(
        subset=['Account', 'Network'])
    duplicated_rows = df_snow[is_duplicate]
    if not duplicated_rows.empty:
        print("Duplicate rows found:")
        pprint(duplicated_rows.to_string())
    df_snow = df_snow.drop_duplicates()
    mapping = {'quattro tk': 'tk gor', 'charles': 'charles river', 'autex': 'tradeweb', 'tk': 'tk gor'}
    mapping_lower = {k.lower(): v.upper() for k, v in mapping.items()}  # map to uppercase results

    df['Network'] = df['Network'].apply(lambda x: mapping_lower.get(x.lower(), x)).str.upper()
    df_snow['Network'] = df_snow['Network'].apply(lambda x: mapping_lower.get(x.lower(), x)).str.upper()
    df_detail = compare_df.compare_dataframes_by_columns(df, df_snow, keys=['Account', 'Network'], dropna=False, return_rows=True)
    with open('comparison_detail.txt', 'w') as f:
        f.write("Only in client data:\n")
        f.write(df_detail['only_A_rows'].to_string(index=False))
        f.write("\n\nOnly in snow data:\n")
        f.write(df_detail['only_B_rows'].to_string(index=False))
        f.write("\n\nCommon to both:\n")
        f.write(df_detail['common_A_rows'].to_string(index=False))
    df_detail['summary'] = {
        'only_in_client_data_count': df_detail['only_A_count'],
        'only_in_snow_data_count': df_detail['only_B_count'],
        'common_to_both_count': df_detail['common_count']
    }       
    with open('comparison_detail.json', 'w') as f:
        json.dump({
            "only_in_client_data": df_detail['only_A_rows'].to_dict(orient='records'),
            "only_in_snow_data": df_detail['only_B_rows'].to_dict(orient='records'),
            "common_to_both": df_detail['common_A_rows'].to_dict(orient='records'),
            "summary": df_detail['summary']
        }, f, indent=4)

    df_merged = df.merge(df_snow, on=['Account','Network'], how='left')
    df_merged.sort_values(by=['Account', 'Network','Identifier'], inplace=True)
    return (df_merged)


def add_adapter_name(df):
    df_adapter = adapter.load_adapter_data()
    df_adapter = df_adapter[['session_targetcompid',
                             'session_name', 'Start Time', 'End Time', 'routing_destination']]
    df_adapter.rename(
        columns={'session_targetcompid': 'Identifier', 'session_name': 'Adapter Name'}, inplace=True)
    df_adapter_cr = df_adapter[df_adapter['routing_destination'].str.contains('CRD', na=False)]
    df_merged = df.merge(df_adapter_cr, on=['Identifier'], how='left')
    return (df_merged)


def get_file_timestamp():
    import os
    import time
    name_file_list = []
    for ullink_client in ullink_clients:
        names_path = f"./client_data/data/{ullink_client}_names"
        t = os.path.getmtime(names_path)
        name_file_list.append(
            f" {names_path} {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))}")

    return '\n'.join(name_file_list)


if __name__ == "__main__":
    client_data = load_ullink_client_data()
    with open('ullink_client_data.json', 'w') as f:
        json.dump(client_data, f, indent=4) 