import pandas as pd
# import dash_cytoscape as cyto
import json
import load_ulbridge_properties
import convert_time

adapter_columns = [
    "session_name",
    "session_ip_port",
    "session_type",
    "session_sendercompid",
    "session_targetcompid",
    "session_version",
    "session_prefix",
    "category_name",
    "routing_destination",
    "note_comment",
    "category",
    "session_ip_machine",
    "session_ip_machine_backup",
    "Start Time",
    "End Time"
]


def load_adapter_data():
    try:
        with open('grouped_sessions.json', 'r') as f:
            data = json.load(f)
        dfs = []
        print(
            f"Loading grouped_sessions.json data... {len(data)} categories found.")
        for key, value in data.items():
            # if (key == "session_name"):
                # print(f"{key}: {value}")
            if isinstance(value, list):
                for item in value:
                    # temp_df = pd.json_normalize(value, sep='_')
                    temp_df = pd.json_normalize(item, sep='_')
                    temp_df['category'] = key
                    dfs.append(temp_df)
        df = pd.concat(dfs, ignore_index=True)
        all_columns = df.columns
        # for name in all_columns:
            # print(name)
        # print(df.shape)
        df = apply_properties(df)
        return df
    except FileNotFoundError:
        print("Warning: grouped_sessions.json not found. Using sample data.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading grouped_sessions.json: {e}")
        return pd.DataFrame()


def load_ullink_properties():
    adpater_properties = load_ulbridge_properties.parse_property_file(
        load_ulbridge_properties.PROPERTY_FILE_PATH)
    return adpater_properties


def apply_properties(df):
    adapter_df = df
    ap = load_ullink_properties()
    adapter_df.replace(ap, inplace=True)
    adapter_df['Start Time'] = adapter_df['timers/doStart_trigger'].apply(
        convert_time.parse_cron_line)
    adapter_df['End Time'] = adapter_df['timers/doStopdoReset_trigger'].apply(
        convert_time.parse_cron_line)

    adapter_df = adapter_df[adapter_columns]
    # print(adapter_df.to_string())
    return adapter_df


if __name__ == "__main__":
    df = load_adapter_data()
    # df = apply_properties(df)
    print(df.to_string())
