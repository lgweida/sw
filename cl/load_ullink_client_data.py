import re
import pandas as pd
from pprint import pprint

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

    # Print the parsed result
    df = pd.DataFrame(parsed_data)
    print(f"the original df shape : {df.shape}")
    # print(df)
    is_duplicate = df.duplicated(
        subset=['Client', 'Account', 'Network', 'Identifier'])
    duplicated_rows = df[is_duplicate]
    if not duplicated_rows.empty:
        print("Duplicate rows found:")
        pprint(duplicated_rows)
    df = df.drop_duplicates()
    # print(df)
    print(f"the removed  df shape : {df.shape}")
    parsed_data = df.to_dict('records')
    return parsed_data


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
