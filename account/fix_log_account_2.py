import dash
from dash import dcc, html, dash_table, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import base64
import io
import re
import os
from urllib.parse import quote

# Initialize the Dash app with callback exception suppression
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Ullink FIX Log & Account Viewer"

# Define FIX tag mappings for common fields
FIX_TAG_MAP = {
    "8": "BeginString",
    "9": "BodyLength",
    "35": "MsgType",
    "34": "MsgSeqNum",
    "49": "SenderCompID",
    "56": "TargetCompID",
    "52": "SendingTime",
    "10": "CheckSum",
    "11": "ClOrdID",
    "14": "CumQty",
    "17": "ExecID",
    "20": "ExecTransType",
    "31": "LastPx",
    "32": "LastQty",
    "37": "OrderID",
    "38": "OrderQty",
    "39": "OrdStatus",
    "40": "OrdType",
    "44": "Price",
    "54": "Side",
    "55": "Symbol",
    "58": "Text",
    "59": "TimeInForce",
    "150": "ExecType",
    "151": "LeavesQty"
}

# MsgType mappings
MSG_TYPE_MAP = {
    "D": "New Order Single",
    "8": "Execution Report",
    "F": "Order Cancel Request",
    "G": "Order Cancel/Replace Request",
    "0": "Heartbeat",
    "1": "Test Request",
    "2": "Resend Request",
    "3": "Reject",
    "4": "Sequence Reset",
    "5": "Logout",
    "A": "Logon"
}

# List of networks for Account Mapping
NETWORKS = {
    'total': 'Total',
    'bloomberg': 'Bloomberg',
    'itg': 'ITG',
    'fidessa': 'Fidessa',
    'tradeweb': 'TradeWeb',
    'tradeware': 'TradeWare',
    'nyfix': 'NYFIX',
    'crd': 'CRD'
}


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


# Function to load all CSV files for Account Mapping
def load_all_network_files_1():
    """Load all network CSV files"""
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
                
                all_data[network_key] = df
                print(f"Loaded {filename}: {len(df)} rows")
                
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")
        else:
            print(f"Warning: File {filename} not found")
    
    # Create combined dataframe for 'total' tab
    if all_data:
        total_df = pd.concat(all_data.values(), ignore_index=True)
        all_data['total'] = total_df
        print(f"Total combined rows: {len(total_df)}")
    
    return all_data

# Load account data at startup
print(f"Loading account data at {datetime.now()}")
network_data = load_all_network_files()

def parse_fix_message(fix_string):
    """Parse a single FIX message string into a dictionary"""
    if not fix_string:
        return {}
    
    fields = {}
    # Split by SOH character (ASCII 1)
    parts = re.split(r'[\x01|;]', fix_string)
    
    for part in parts:
        if '=' in part:
            tag, value = part.split('=', 1)
            if tag in FIX_TAG_MAP:
                field_name = FIX_TAG_MAP[tag]
                
                # Special handling for certain fields
                if tag == "35":  # MsgType
                    value = MSG_TYPE_MAP.get(value, value)
                elif tag == "52":  # SendingTime
                    # Try to parse timestamp
                    try:
                        dt = datetime.strptime(value, "%Y%m%d-%H:%M:%S.%f")
                        value = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    except:
                        pass
                elif tag == "54":  # Side
                    side_map = {"1": "Buy", "2": "Sell"}
                    value = side_map.get(value, value)
                elif tag == "39":  # OrdStatus
                    status_map = {
                        "0": "New",
                        "1": "Partially Filled",
                        "2": "Filled",
                        "4": "Canceled",
                        "5": "Replaced",
                        "6": "Pending Cancel",
                        "8": "Rejected",
                        "9": "Suspended"
                    }
                    value = status_map.get(value, value)
                elif tag == "150":  # ExecType
                    exec_map = {
                        "0": "New",
                        "1": "Partial Fill",
                        "2": "Fill",
                        "3": "Done for Day",
                        "4": "Canceled",
                        "5": "Replace",
                        "6": "Pending Cancel",
                        "7": "Stopped",
                        "8": "Rejected",
                        "9": "Suspended",
                        "A": "Pending New",
                        "B": "Calculated",
                        "C": "Expired",
                        "D": "Restated",
                        "E": "Pending Replace",
                        "F": "Trade",
                        "G": "Trade Correct",
                        "H": "Trade Cancel",
                        "I": "Order Status"
                    }
                    value = exec_map.get(value, value)
                
                fields[field_name] = value
            else:
                fields[f"Tag_{tag}"] = value
    
    return fields

def parse_fix_text(text_content):
    """Parse FIX log text content directly"""
    try:
        messages = []
        lines = text_content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                # Try to find FIX messages in the line
                # Look for pattern like "8=FIX.4.4" or contains SOH character
                if '8=FIX' in line or '\x01' in line:
                    # Clean up the line
                    line = line.replace('', '\x01')  # Replace SOH representation
                    
                    # Parse the FIX message
                    parsed_msg = parse_fix_message(line)
                    if parsed_msg:
                        parsed_msg['_LineNumber'] = i + 1
                        parsed_msg['_RawMessage'] = line[:200] + "..." if len(line) > 200 else line
                        messages.append(parsed_msg)
        
        if messages:
            df = pd.DataFrame(messages)
            # Reorder columns to put common fields first
            common_fields = ['_LineNumber', 'MsgType', 'MsgSeqNum', 'SendingTime', 
                           'SenderCompID', 'TargetCompID', 'ClOrdID', 'Symbol',
                           'Side', 'OrdStatus', 'ExecType', 'LastPx', 'LastQty',
                           'OrderQty', 'CumQty', 'LeavesQty', 'Price']
            
            # Get actual columns that exist in dataframe
            existing_common = [f for f in common_fields if f in df.columns]
            other_cols = [col for col in df.columns if col not in existing_common + ['_LineNumber', '_RawMessage']]
            
            final_order = ['_LineNumber'] + existing_common + other_cols + ['_RawMessage']
            # Only include columns that exist
            final_order = [col for col in final_order if col in df.columns]
            
            df = df[final_order]
            return df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error parsing text: {e}")
        return pd.DataFrame()

def parse_fix_log_file(contents):
    """Parse FIX log file content from uploaded file"""
    try:
        # Decode the base64 content
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Try different encodings
        try:
            text = decoded.decode('utf-8')
        except:
            text = decoded.decode('latin-1')
        
        return parse_fix_text(text)
            
    except Exception as e:
        print(f"Error parsing file: {e}")
        return pd.DataFrame()

# New function for multi-term search
def search_dataframe(df, search_text):
    """
    Search DataFrame for multiple terms separated by spaces.
    Returns rows where any column contains ALL search terms (in any order).
    """
    if not search_text or not search_text.strip():
        return df
    
    # Split search text into individual terms
    search_terms = [term.strip().lower() for term in search_text.split() if term.strip()]
    if not search_terms:
        return df
    
    # Initialize mask - start with all True
    mask = pd.Series([True] * len(df))
    
    # For each search term, find rows that contain it
    for term in search_terms:
        term_mask = pd.Series([False] * len(df))
        
        # Search in all string columns
        for col in df.columns:
            try:
                # Skip non-string columns or columns with no data
                if df[col].dtype == 'object' and len(df[col]) > 0:
                    # Check if the term exists in this column
                    col_mask = df[col].astype(str).str.lower().str.contains(term, na=False)
                    term_mask = term_mask | col_mask
            except Exception as e:
                # Skip columns that can't be converted to string
                continue
        
        # Combine with AND logic - row must contain ALL terms
        mask = mask & term_mask
    
    return df[mask] if mask.any() else pd.DataFrame()

# Function for filtering account data
def filter_account_dataframe(df, search_term=None):
    """Filter dataframe by multiple search terms separated by spaces"""
    if df is None or df.empty:
        return pd.DataFrame()
    
    # If no search term, return original dataframe
    if not search_term or not str(search_term).strip():
        return df.copy()
    
    # Clean and split search terms
    search_terms = str(search_term).strip().lower()
    if not search_terms:
        return df.copy()
    
    # Split by spaces and filter out empty strings
    search_list = [term.strip() for term in search_terms.split() if term.strip()]
    
    if not search_list:
        return df.copy()
    
    # Create a copy of the dataframe
    df_copy = df.copy()
    
    # Ensure columns are strings for comparison
    if 'ACCOUNT_NUMBER' in df_copy.columns:
        df_copy['ACCOUNT_NUMBER'] = df_copy['ACCOUNT_NUMBER'].astype(str).str.lower()
    if 'ACRONAME' in df_copy.columns:
        df_copy['ACRONAME'] = df_copy['ACRONAME'].astype(str).str.lower()
    
    # Initialize mask to True for all rows
    mask = pd.Series([True] * len(df_copy), index=df_copy.index)
    
    # Apply each search term with AND logic
    for term in search_list:
        # Check if term exists in either column
        term_mask = pd.Series([False] * len(df_copy), index=df_copy.index)
        
        if 'ACCOUNT_NUMBER' in df_copy.columns:
            term_mask = term_mask | (df_copy['ACCOUNT_NUMBER'].str.contains(term, na=False, regex=False))
        if 'ACRONAME' in df_copy.columns:
            term_mask = term_mask | (df_copy['ACRONAME'].str.contains(term, na=False, regex=False))
        
        mask = mask & term_mask
    
    # Apply the combined mask
    return df[mask].copy()

# Main layout with sidebar navigation
app.layout = html.Div([
    # Navigation Sidebar
    html.Div([
        html.Div([
            html.Div([
                html.I(className="fas fa-chart-line text-2xl text-blue-500 mb-6"),
                html.H2("Ullink Tools", className="text-xl font-bold text-white mb-8")
            ], className="text-center mb-8"),
            
            html.Div([
                html.Button([
                    html.I(className="fas fa-file-alt mr-3"),
                    html.Span("FIX Log Viewer", className="font-medium")
                ], id="nav-fix-log", n_clicks=0,
                   className="nav-button w-full text-left px-4 py-3 rounded-lg mb-2 bg-blue-700 text-white"),
                
                html.Button([
                    html.I(className="fas fa-address-book mr-3"),
                    html.Span("Account Mapping", className="font-medium")
                ], id="nav-account-mapping", n_clicks=0,
                   className="nav-button w-full text-left px-4 py-3 rounded-lg bg-gray-700 text-white hover:bg-gray-600"),
            ], className="space-y-2"),
            
            html.Div([
                html.P("v1.0.0", className="text-gray-400 text-xs text-center mt-8")
            ])
        ], className="p-4")
    ], id="sidebar", className="fixed left-0 top-0 h-screen w-64 bg-gray-800 shadow-lg z-10"),
    
    # Main Content Area
    html.Div([
        # Header
        html.Div([
            html.Div([
                html.Div([
                    html.I(className="fas fa-chart-line text-3xl text-blue-600 mr-3"),
                    html.Div([
                        html.H1("Ullink FIX Log Viewer", id="main-title", 
                               className="text-2xl font-bold text-gray-800"),
                        html.P("Upload or paste FIX protocol log files", 
                               id="main-subtitle",
                               className="text-gray-600")
                    ])
                ], className="flex items-center"),
                
                html.Div([
                    html.Span("FIX Protocol Analyzer", 
                             className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full"),
                    html.Span("Real-time Parser", 
                             className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full ml-2"),
                ], className="flex items-center")
            ], className="flex justify-between items-center")
        ], id="main-header", className="bg-white shadow-sm border-b px-8 py-6 ml-64"),
        
        # Main Content (changes based on navigation)
        html.Div(id="main-content", className="ml-64 min-h-screen bg-gray-50"),
        
        # Footer
        html.Div([
            html.Div([
                html.P("Ullink Tools v1.0", className="text-gray-600"),
                html.P([
                    "Powered by ",
                    html.Span("Dash & Plotly", className="text-blue-600 font-medium")
                ], className="text-gray-600 text-sm")
            ], className="text-center py-4")
        ], id="main-footer", className="border-t border-gray-200 mt-6 ml-64"),
    ], id="content-wrapper"),
    
    # Hidden storage for data
    dcc.Store(id='parsed-data-store'),
    dcc.Store(id='data-source-store', data={'source': 'none', 'filename': ''}),
    dcc.Store(id='current-page', data='fix-log'),
    dcc.Store(id='account-network-data', data=network_data),
    dcc.Store(id='account-last-updated', data=datetime.now().isoformat()),
    
    # Download components
    dcc.Download(id="download-dataframe-csv"),
    dcc.Download(id="download-account-csv"),
], className="min-h-screen bg-gray-50")

# Callback to switch between pages
@app.callback(
    [Output('main-content', 'children'),
     Output('main-title', 'children'),
     Output('main-subtitle', 'children'),
     Output('nav-fix-log', 'className'),
     Output('nav-account-mapping', 'className'),
     Output('current-page', 'data')],
    [Input('nav-fix-log', 'n_clicks'),
     Input('nav-account-mapping', 'n_clicks')],
    [State('current-page', 'data')]
)
def switch_page(fix_clicks, account_clicks, current_page):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        # Default to FIX Log Viewer
        return get_fix_log_layout(), "Ullink FIX Log Viewer", "Upload or paste FIX protocol log files", \
               "nav-button w-full text-left px-4 py-3 rounded-lg mb-2 bg-blue-700 text-white", \
               "nav-button w-full text-left px-4 py-3 rounded-lg bg-gray-700 text-white hover:bg-gray-600", \
               "fix-log"
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'nav-fix-log':
        return get_fix_log_layout(), "Ullink FIX Log Viewer", "Upload or paste FIX protocol log files", \
               "nav-button w-full text-left px-4 py-3 rounded-lg mb-2 bg-blue-700 text-white", \
               "nav-button w-full text-left px-4 py-3 rounded-lg bg-gray-700 text-white hover:bg-gray-600", \
               "fix-log"
    else:  # nav-account-mapping
        return get_account_mapping_layout(), "Account Mapping Viewer", "View and search account mappings across different trading networks", \
               "nav-button w-full text-left px-4 py-3 rounded-lg mb-2 bg-gray-700 text-white hover:bg-gray-600", \
               "nav-button w-full text-left px-4 py-3 rounded-lg bg-blue-700 text-white", \
               "account-mapping"

# Function to get FIX Log layout
def get_fix_log_layout():
    return html.Div([
        # Main Content
        html.Div([
            # Left sidebar for file upload and filters
            html.Div([
                # Input Method Selection
                html.Div([
                    html.H3("Input Method", className="text-lg font-semibold text-gray-800 mb-4"),
                    
                    # Tabs for input method
                    html.Div([
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-upload mr-2"),
                                "Upload File"
                            ], id="upload-tab-btn", n_clicks=0,
                               className="tab-button px-4 py-2 rounded-t-lg bg-blue-600 text-white"),
                            
                            html.Button([
                                html.I(className="fas fa-paste mr-2"),
                                "Paste Log"
                            ], id="paste-tab-btn", n_clicks=0,
                               className="tab-button px-4 py-2 rounded-t-lg bg-gray-100 text-gray-700 hover:bg-gray-200"),
                        ], className="flex border-b border-gray-200")
                    ], className="mb-4"),
                    
                    # Upload File Section (initially visible)
                    html.Div([
                        html.H3("Upload FIX Log File", className="text-lg font-semibold text-gray-800 mb-4"),
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                html.Div([
                                    html.I(className="fas fa-cloud-upload-alt text-3xl text-blue-500 mb-2"),
                                    html.P("Drag and drop your FIX log file", className="font-medium"),
                                    html.P("or click to browse", className="text-sm text-gray-500 mt-1"),
                                ], className="text-center")
                            ]),
                            className="upload-container border-2 border-dashed border-gray-300 rounded-xl p-8 hover:border-blue-500 transition-colors bg-gray-50"
                        ),
                        html.Div(id='file-info', className="mt-4"),
                        html.Div([
                            html.P("Supported formats:", className="text-sm font-medium text-gray-700 mt-4"),
                            html.Ul([
                                html.Li("Text files (.txt, .log)", className="text-sm text-gray-600"),
                                html.Li("CSV files with FIX messages", className="text-sm text-gray-600"),
                                html.Li("Any file containing FIX protocol messages", className="text-sm text-gray-600")
                            ], className="list-disc pl-5 mt-2 space-y-1")
                        ])
                    ], id='upload-section', className="mb-6"),
                    
                    # Paste Text Section (initially hidden)
                    html.Div([
                        html.H3("Paste FIX Log Content", className="text-lg font-semibold text-gray-800 mb-4"),
                        html.Div([
                            html.Label("FIX Log Content", className="block text-sm font-medium text-gray-700 mb-2"),
                            dcc.Textarea(
                                id='paste-text',
                                placeholder='Paste your FIX log content here...\nExample:\n8=FIX.4.4|9=123|35=D|49=SENDER|56=TARGET|...\n8=FIX.4.4|9=456|35=8|49=SENDER|56=TARGET|...',
                                value='',
                                className="code-textarea w-full h-64 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-vertical",
                                style={'fontFamily': 'monospace', 'whiteSpace': 'pre'}
                            ),
                            html.Div([
                                html.Button([
                                    html.I(className="fas fa-play mr-2"),
                                    "Parse Log"
                                ], id='parse-btn', n_clicks=0,
                                   className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors mt-3"),
                                html.Button([
                                    html.I(className="fas fa-eraser mr-2"),
                                    "Clear"
                                ], id='clear-paste-btn', n_clicks=0,
                                   className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors mt-3 ml-2"),
                            ], className="flex"),
                        ]),
                        html.Div(id='paste-info', className="mt-4"),
                        html.Div([
                            html.P("Tips for pasting:", className="text-sm font-medium text-gray-700 mt-4"),
                            html.Ul([
                                html.Li("Copy FIX messages directly from logs or monitoring tools", className="text-sm text-gray-600"),
                                html.Li("Support for SOH (ASCII 1) delimiters (shown as | or ^A)", className="text-sm text-gray-600"),
                                html.Li("Can parse multiple messages separated by newlines", className="text-sm text-gray-600"),
                                html.Li("Comments starting with # are ignored", className="text-sm text-gray-600")
                            ], className="list-disc pl-5 mt-2 space-y-1")
                        ])
                    ], id='paste-section', className="mb-6", style={'display': 'none'}),
                ], id='input-method-container'),
                
                # Filters Card
                html.Div([
                    html.H3("Filters", className="text-lg font-semibold text-gray-800 mb-4 flex items-center"),
                    
                    html.Div([
                        html.Label("Message Type", className="block text-sm font-medium text-gray-700 mb-2"),
                        dcc.Dropdown(
                            id='msgtype-filter',
                            multi=True,
                            placeholder="Select message types...",
                            className="mb-4"
                        ),
                    ]),
                    
                    html.Div([
                        html.Label("Sender/Target", className="block text-sm font-medium text-gray-700 mb-2"),
                        html.Div([
                            dcc.Input(
                                id='sender-filter',
                                type='text',
                                placeholder='Sender ID',
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            ),
                            dcc.Input(
                                id='target-filter',
                                type='text',
                                placeholder='Target ID',
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 mt-2"
                            ),
                        ]),
                    ], className="mb-4"),

                    html.Div([
                        html.Label("Symbol Filter", className="block text-sm font-medium text-gray-700 mb-2"),
                        dcc.Dropdown(
                            id='symbol-filter',
                            placeholder="Select symbol(s)...",
                            multi=True,  # Allow multiple selections
                            className="mb-4"
                        ),
                    ], className="mb-4"),
                    
                    html.Div([
                        html.Label("Global Search", className="block text-sm font-medium text-gray-700 mb-2"),
                        html.Div([
                            dcc.Input(
                                id='global-search',
                                type='text',
                                placeholder='Search terms separated by spaces (AND search)',
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            ),
                            html.Small("Example: 'AAPL Buy' finds rows containing both 'AAPL' AND 'Buy'", 
                                      className="text-gray-500 text-xs mt-1 block")
                        ]),
                    ], className="mb-6"),
                    
                    html.Div([
                        html.Button([
                            html.I(className="fas fa-filter-circle-xmark mr-2"),
                            "Clear Filters"
                        ], id='clear-filters', n_clicks=0,
                           className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors mr-3"),
                        html.Button([
                            html.I(className="fas fa-file-export mr-2"),
                            "Export CSV"
                        ], id='export-btn', n_clicks=0,
                           className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors")
                    ], className="flex"),
                ], className="bg-white rounded-xl shadow-sm p-6")
            ], className="lg:w-1/4 pr-6"),
            
            # Main content area
            html.Div([
                # Statistics Cards
                html.Div(id='summary-stats', className="mb-6"),
                
                # Data Table
                html.Div([
                    html.Div([
                        html.H3("FIX Messages", className="text-lg font-semibold text-gray-800"),
                        html.Div([
                            html.Span("Live", className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"),
                            html.Span("Parsed", className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 ml-2")
                        ])
                    ], className="flex justify-between items-center mb-4"),
                    
                    dcc.Loading(
                        id="loading",
                        type="circle",
                        children=[
                            html.Div(id='data-table-container', className="bg-white rounded-xl shadow-sm overflow-hidden")
                        ],
                        className="loading-spinner"
                    )
                ], className="mb-8"),
                
                # Charts
                html.Div([
                    html.Div([
                        html.H3("Message Type Distribution", className="text-lg font-semibold text-gray-800 mb-4"),
                        dcc.Graph(id='msgtype-chart', 
                                 className="bg-white rounded-xl shadow-sm p-4",
                                 config={'displayModeBar': True, 'responsive': True})
                    ], className="w-full")
                ])
            ], className="lg:w-3/4")
        ], className="px-8 py-6 flex flex-col lg:flex-row"),
    ], className="min-h-screen")

# Function to get Account Mapping layout
def get_account_mapping_layout():
    return html.Div([
        html.Div([
            # Last updated timestamp
            html.Div(id='account-last-updated-display', style={
                'textAlign': 'center',
                'color': '#888',
                'fontSize': '12px',
                'marginBottom': '10px'
            }),
            
            # Stats summary
            html.Div(id='account-stats-summary', style={
                'textAlign': 'center',
                'color': '#444',
                'fontSize': '14px',
                'marginBottom': '20px'
            }),
            
            # Search input with improved UI
            html.Div([
                html.Div([
                    html.Div([
                        html.Label("🔍 Advanced Search:", 
                                  style={'fontWeight': 'bold', 'marginRight': '10px', 'fontSize': '16px'}),
                        html.Span("(Separate multiple terms with spaces)", 
                                 style={'color': '#666', 'fontSize': '12px', 'fontStyle': 'italic'})
                    ], style={'marginBottom': '5px'}),
                    
                    html.Div([
                        dcc.Input(
                            id='account-search-input',
                            type='text',
                            placeholder='Example: "bank 1234" searches for records containing both "bank" and "1234"',
                            style={
                                'width': '500px', 
                                'marginRight': '10px', 
                                'padding': '10px',
                                'borderRadius': '5px',
                                'border': '1px solid #ddd',
                                'fontSize': '14px'
                            },
                            debounce=True
                        ),
                        html.Button('Clear', id='account-clear-button', n_clicks=0,
                                   style={
                                       'padding': '10px 20px',
                                       'backgroundColor': '#f8f9fa',
                                       'border': '1px solid #ddd',
                                       'borderRadius': '5px',
                                       'cursor': 'pointer'
                                   }),
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                    
                    html.Div([
                        html.Span("Search Logic:", style={'fontWeight': 'bold', 'marginRight': '5px'}),
                        html.Span("All terms must match (AND logic)", style={'color': '#444'}),
                        html.Span(" • ", style={'margin': '0 5px'}),
                        html.Span("Searches in both ACRONAME and ACCOUNT_NUMBER", style={'color': '#444'}),
                        html.Span(" • ", style={'margin': '0 5px'}),
                        html.Span("Case-insensitive", style={'color': '#444'})
                    ], style={'marginTop': '8px', 'fontSize': '12px', 'color': '#666'})
                ], style={
                    'padding': '20px',
                    'backgroundColor': '#f8f9fa',
                    'borderRadius': '8px',
                    'marginBottom': '20px'
                })
            ]),
            
            # Search terms display
            html.Div(id='account-search-terms-display', style={
                'textAlign': 'center',
                'marginBottom': '15px',
                'fontSize': '13px',
                'color': '#555'
            }),
            
            # Tabs
            html.Div([
                dcc.Tabs(
                    id='account-tabs', 
                    value='total', 
                    children=[
                        dcc.Tab(
                            label=f'{NETWORKS[network]} ({len(network_data.get(network, pd.DataFrame()))})' 
                                  if network in network_data else NETWORKS[network],
                            value=network,
                            style={
                                'padding': '10px',
                                'fontWeight': 'bold'
                            },
                            selected_style={
                                'backgroundColor': '#007bff',
                                'color': 'white',
                                'border': 'none'
                            }
                        ) for network in NETWORKS.keys()
                    ],
                    style={
                        'fontSize': '14px',
                        'marginBottom': '20px'
                    }
                )
            ]),
            
            # Data table container
            html.Div(id='account-table-container', style={'marginTop': '20px'}),
            
            # Download button (added to layout)
            html.Div([
                html.Button([
                    html.I(className="fas fa-download mr-2"),
                    "Download CSV"
                ], id='account-download-btn', n_clicks=0,
                   className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"),
            ], id='account-download-container', style={'display': 'none', 'marginTop': '20px'}),
        ], className="px-8 py-6")
    ])

# Add Tailwind CSS CDN and styles
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ullink FIX Log & Account Viewer</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Inter', sans-serif;
            }
            .card {
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .fix-table {
                font-family: 'Courier New', monospace;
                font-size: 0.875rem;
            }
            .status-new { background-color: #dbeafe; color: #1e40af; }
            .status-filled { background-color: #dcfce7; color: #166534; }
            .status-rejected { background-color: #fee2e2; color: #991b1b; }
            .status-partial { background-color: #fef3c7; color: #92400e; }
            .scrollbar-hide::-webkit-scrollbar {
                display: none;
            }
            .scrollbar-hide {
                -ms-overflow-style: none;
                scrollbar-width: none;
            }
            .code-textarea {
                font-family: 'Courier New', monospace;
                font-size: 0.875rem;
                line-height: 1.5;
            }
            .upload-container {
                cursor: pointer;
            }
            .upload-container:hover {
                background-color: #f0f9ff;
            }
            .nav-button {
                transition: all 0.2s ease-in-out;
            }
            .nav-button:hover {
                transform: translateX(5px);
            }
            .tab-button {
                transition: all 0.2s ease-in-out;
            }
        </style>
    </head>
    <body class="bg-gray-50">
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Callback to switch between upload and paste sections (FIX Log)
@app.callback(
    [Output('upload-section', 'style'),
     Output('paste-section', 'style'),
     Output('upload-tab-btn', 'className'),
     Output('paste-tab-btn', 'className')],
    [Input('upload-tab-btn', 'n_clicks'),
     Input('paste-tab-btn', 'n_clicks')]
)
def switch_input_method(upload_clicks, paste_clicks):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        # Default to upload section
        return ({'display': 'block'}, {'display': 'none'},
                "tab-button px-4 py-2 rounded-t-lg bg-blue-600 text-white",
                "tab-button px-4 py-2 rounded-t-lg bg-gray-100 text-gray-700 hover:bg-gray-200")
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'upload-tab-btn':
        return ({'display': 'block'}, {'display': 'none'},
                "tab-button px-4 py-2 rounded-t-lg bg-blue-600 text-white",
                "tab-button px-4 py-2 rounded-t-lg bg-gray-100 text-gray-700 hover:bg-gray-200")
    else:  # paste-tab-btn
        return ({'display': 'none'}, {'display': 'block'},
                "tab-button px-4 py-2 rounded-t-lg bg-gray-100 text-gray-700 hover:bg-gray-200",
                "tab-button px-4 py-2 rounded-t-lg bg-blue-600 text-white")

# Callback to handle data parsing from both sources (FIX Log)
@app.callback(
    [Output('parsed-data-store', 'data'),
     Output('data-source-store', 'data'),
     Output('file-info', 'children'),
     Output('paste-info', 'children')],
    [Input('upload-data', 'contents'),
     Input('parse-btn', 'n_clicks'),
     Input('clear-paste-btn', 'n_clicks')],
    [State('upload-data', 'filename'),
     State('paste-text', 'value'),
     State('data-source-store', 'data')]
)
def parse_data(upload_contents, parse_clicks, clear_paste_clicks, filename, paste_text, current_source):
    ctx = dash.callback_context
    
    # Initialize outputs
    file_info = ""
    paste_info = ""
    
    if not ctx.triggered:
        return dash.no_update, dash.no_update, file_info, paste_info
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Handle clear paste button
    if trigger_id == 'clear-paste-btn':
        # Return empty data and clear info displays
        return {'data': [], 'columns': []}, {'source': 'none', 'filename': ''}, "", ""
    
    if trigger_id == 'upload-data' and upload_contents:
        # Parse from uploaded file
        df = parse_fix_log_file(upload_contents)
        if not df.empty:
            # Convert DataFrame to JSON for storage
            data = df.to_dict('records')
            columns = list(df.columns)
            
            # Create file info
            file_info = html.Div([
                html.Div([
                    html.I(className="fas fa-file-alt text-blue-500 mr-3"),
                    html.Div([
                        html.H4(f"{filename}", className="font-medium text-gray-800"),
                        html.Div([
                            html.Span(f"{len(df)} messages parsed", 
                                     className="text-sm text-gray-600"),
                            html.I(className="fas fa-circle text-xs mx-2 text-gray-400"),
                            html.Span(f"{df['MsgType'].nunique() if 'MsgType' in df.columns else 0} message types",
                                     className="text-sm text-gray-600")
                        ], className="flex items-center")
                    ])
                ], className="flex items-center")
            ])
            
            return {'data': data, 'columns': columns}, {'source': 'file', 'filename': filename}, file_info, paste_info
    
    elif trigger_id == 'parse-btn' and paste_text:
        # Parse from pasted text
        df = parse_fix_text(paste_text)
        if not df.empty:
            # Convert DataFrame to JSON for storage
            data = df.to_dict('records')
            columns = list(df.columns)
            
            # Create paste info
            paste_info = html.Div([
                html.Div([
                    html.I(className="fas fa-clipboard text-green-500 mr-3"),
                    html.Div([
                        html.H4("Pasted Content", className="font-medium text-gray-800"),
                        html.Div([
                            html.Span(f"{len(df)} messages parsed", 
                                     className="text-sm text-gray-600"),
                            html.I(className="fas fa-circle text-xs mx-2 text-gray-400"),
                            html.Span(f"{df['MsgType'].nunique() if 'MsgType' in df.columns else 0} message types",
                                     className="text-sm text-gray-600")
                        ], className="flex items-center")
                    ])
                ], className="flex items-center")
            ])
            
            return {'data': data, 'columns': columns}, {'source': 'paste', 'filename': 'Pasted Content'}, file_info, paste_info
    
    # Return empty data if parsing failed
    return {'data': [], 'columns': []}, {'source': 'none', 'filename': ''}, file_info, paste_info

# Callback to clear the paste text area (FIX Log)
@app.callback(
    Output('paste-text', 'value'),
    [Input('clear-paste-btn', 'n_clicks')],
    prevent_initial_call=True
)
def clear_paste_text(n_clicks):
    """Clear the paste text area when the clear button is clicked"""
    if n_clicks:
        return ''
    return dash.no_update

# Main callback to update the display (FIX Log)
@app.callback(
    [Output('data-table-container', 'children'),
     Output('msgtype-filter', 'options'),
     Output('summary-stats', 'children'),
     Output('msgtype-chart', 'figure')],
    [Input('parsed-data-store', 'data'),
     Input('msgtype-filter', 'value'),
     Input('sender-filter', 'value'),
     Input('target-filter', 'value'),
     Input('symbol-filter', 'value'),
     Input('global-search', 'value'),
     Input('clear-filters', 'n_clicks')],
    [State('data-source-store', 'data')]
)
def update_display(parsed_data, msgtype_filter, sender_filter, target_filter, 
                   symbol_filter, global_search, clear_clicks, source_data):
    
    # Check if we have data
    if not parsed_data or not parsed_data['data']:
        # Return empty state
        empty_state = html.Div([
            html.Div([
                html.I(className="fas fa-chart-bar text-5xl text-gray-300 mb-4"),
                html.H3("No Data Loaded", className="text-xl font-semibold text-gray-700 mb-2"),
                html.P("Upload a file or paste FIX log content to start analyzing", className="text-gray-500"),
            ], className="text-center py-12")
        ], className="bg-white rounded-xl shadow-sm")
        return empty_state, [], None, go.Figure()
    
    # Convert stored data back to DataFrame
    df = pd.DataFrame(parsed_data['data'])
    
    # Store original unfiltered dataframe
    original_df = df.copy()
    
    # Apply filters
    if msgtype_filter:
        df = df[df['MsgType'].isin(msgtype_filter)]
    if sender_filter:
        df = df[df['SenderCompID'].astype(str).str.contains(sender_filter, case=False, na=False)]
    if target_filter:
        df = df[df['TargetCompID'].astype(str).str.contains(target_filter, case=False, na=False)]
    
    if symbol_filter:
        df = df[df['Symbol'].isin(symbol_filter)]

    # Apply multi-term global search using the new function
    if global_search and global_search.strip():
        df = search_dataframe(df, global_search)
    
    # Create message type options for dropdown
    msgtype_options = []
    if 'MsgType' in original_df.columns and not original_df.empty:
        msgtype_counts = original_df['MsgType'].value_counts()
        msgtype_options = [{'label': f"{msg} ({count})", 'value': msg} 
                          for msg, count in msgtype_counts.items()]
    
    # Create data table if we have data
    if not df.empty:
        # Determine status-based styling
        status_conditions = []
        if 'OrdStatus' in df.columns:
            for status, style_class in [
                ('New', 'status-new'),
                ('Filled', 'status-filled'),
                ('Rejected', 'status-rejected'),
                ('Partially Filled', 'status-partial'),
                ('Canceled', 'status-rejected')
            ]:
                status_conditions.append({
                    'if': {
                        'filter_query': f'{{OrdStatus}} = "{status}"',
                        'column_id': 'OrdStatus'
                    },
                    'className': f'px-2 py-1 rounded-full text-xs font-medium {style_class}'
                })
        
        table = dash_table.DataTable(
            id='fix-data-table',
            columns=[
                {"name": col.replace('_', ' ').title(), 
                 "id": col, 
                 "hideable": True,
                 "type": "text"}
                for col in df.columns
            ],
            data=df.to_dict('records'),
            page_size=20,
            page_current=0,
            page_action='native',
            filter_action='native',
            sort_action='native',
            sort_mode='multi',
            column_selectable='single',
            row_selectable='multi',
            selected_columns=[],
            selected_rows=[],
            style_table={
                'overflowX': 'auto',
                'borderRadius': '0.5rem',
                'border': '1px solid #e5e7eb'
            },
            style_header={
                'backgroundColor': '#f9fafb',
                'color': '#374151',
                'fontWeight': '600',
                'borderBottom': '1px solid #e5e7eb',
                'padding': '12px 16px'
            },
            style_data={
                'backgroundColor': 'white',
                'color': '#1f2937',
                'borderBottom': '1px solid #f3f4f6'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f9fafb'
                },
                {
                    'if': {'column_id': 'MsgType'},
                    'fontWeight': '600',
                    'color': '#1e40af'
                },
                {
                    'if': {'column_id': 'ClOrdID'},
                    'fontFamily': 'monospace',
                    'fontSize': '0.875rem'
                },
                {
                    'if': {'column_id': 'Symbol'},
                    'fontWeight': '600',
                    'color': '#059669'
                },
                *status_conditions
            ],
            style_cell={
                'textAlign': 'left',
                'padding': '12px 16px',
                'fontFamily': "'Inter', sans-serif",
                'fontSize': '0.875rem',
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth': '120px',
                'border': 'none'
            },
            style_filter={
                'backgroundColor': '#f9fafb',
                'border': '1px solid #e5e7eb',
                'padding': '8px'
            },
            tooltip_data=[
                {
                    column: {'value': str(value), 'type': 'markdown'}
                    for column, value in row.items()
                } for row in df.to_dict('records')
            ],
            tooltip_duration=None,
            export_format='csv',
            export_headers='display'
        )
    else:
        table = html.Div([
            html.Div([
                html.I(className="fas fa-search text-4xl text-gray-300 mb-4"),
                html.H4("No matching messages found", className="text-lg font-semibold text-gray-700 mb-2"),
                html.P("Try adjusting your filter criteria", className="text-gray-600"),
            ], className="text-center py-12")
        ], className="bg-white rounded-xl shadow-sm")
    
    # Create summary statistics cards
    summary_stats = None
    if 'MsgType' in original_df.columns and not original_df.empty:
        # Get top message types
        msgtype_counts = original_df['MsgType'].value_counts().head(6)
        
        stats_cards = []
        for msg_type, count in msgtype_counts.items():
            # Assign icon based on message type
            if "Execution" in msg_type:
                icon = "fa-chart-line"
                color = "text-green-600"
                bg_color = "bg-green-50"
            elif "Order" in msg_type:
                icon = "fa-shopping-cart"
                color = "text-blue-600"
                bg_color = "bg-blue-50"
            elif "Cancel" in msg_type:
                icon = "fa-ban"
                color = "text-red-600"
                bg_color = "bg-red-50"
            elif "Log" in msg_type:
                icon = "fa-sign-in-alt"
                color = "text-purple-600"
                bg_color = "bg-purple-50"
            else:
                icon = "fa-envelope"
                color = "text-gray-600"
                bg_color = "bg-gray-50"
            
            stats_cards.append(
                html.Div([
                    html.Div([
                        html.I(className=f"fas {icon} text-xl {color}"),
                        html.Div([
                            html.P(msg_type[:20] + ("..." if len(msg_type) > 20 else ""), 
                                  className="text-sm font-medium text-gray-700 truncate"),
                            html.P(f"{count}", className="text-2xl font-bold text-gray-800")
                        ], className="ml-4")
                    ], className="flex items-center")
                ], className=f"{bg_color} rounded-xl p-4")
            )
        
        # Add totals card
        total_messages = len(original_df)
        filtered_messages = len(df) if not df.empty else 0
        
        stats_cards.append(
            html.Div([
                html.Div([
                    html.I(className="fas fa-database text-xl text-indigo-600"),
                    html.Div([
                        html.P("Messages", className="text-sm font-medium text-gray-700"),
                        html.Div([
                            html.Span(f"{filtered_messages}", className="text-2xl font-bold text-gray-800"),
                            html.Span(f" / {total_messages}", className="text-lg text-gray-500")
                        ], className="flex items-baseline")
                    ], className="ml-4")
                ], className="flex items-center")
            ], className="bg-indigo-50 rounded-xl p-4")
        )
        
        summary_stats = html.Div([
            html.H3("Statistics", className="text-lg font-semibold text-gray-800 mb-4"),
            html.Div(stats_cards, className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4")
        ])
    
    # Create message type distribution chart
    fig = go.Figure()
    if 'MsgType' in original_df.columns and not original_df.empty:
        msgtype_counts = original_df['MsgType'].value_counts().reset_index()
        msgtype_counts.columns = ['MsgType', 'Count']
        
        # Create a nice color palette
        colors = ['#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#ec4899']
        
        fig = go.Figure(data=[go.Bar(
            x=msgtype_counts['MsgType'],
            y=msgtype_counts['Count'],
            marker_color=colors[:len(msgtype_counts)],
            text=msgtype_counts['Count'],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )])
        
        fig.update_layout(
            title=None,
            xaxis_title='Message Type',
            yaxis_title='Count',
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(family='Inter', size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Inter"
            ),
            xaxis=dict(
                showgrid=False,
                tickangle=45
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#f3f4f6',
                zeroline=False
            )
        )
    
    return table, msgtype_options, summary_stats, fig

# Callback to clear all filter inputs when the clear button is clicked (FIX Log)
@app.callback(
    [Output('msgtype-filter', 'value'),
     Output('sender-filter', 'value'),
     Output('target-filter', 'value'),
     Output('symbol-filter', 'value'),  # ADD THIS
     Output('global-search', 'value')],
    [Input('clear-filters', 'n_clicks')],
    prevent_initial_call=True
)
def clear_filter_inputs(n_clicks):
    """Clear all filter inputs when the clear button is clicked"""
    if n_clicks:
        # Return empty values for all filter inputs
        return None, '', '', None, ''
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Callback for FIX Log export functionality
@app.callback(
    Output("download-dataframe-csv", "data"),
    [Input("export-btn", "n_clicks")],
    [State('parsed-data-store', 'data')],
    prevent_initial_call=True
)
def export_fix_data(n_clicks, parsed_data):
    if n_clicks and parsed_data and parsed_data['data']:
        # Convert stored data back to DataFrame
        df = pd.DataFrame(parsed_data['data'])
        
        # Create CSV string
        csv_string = df.to_csv(index=False, encoding='utf-8')
        
        # Return the CSV file for download
        return dict(content=csv_string, filename="fix_log_export.csv")
    
    return None



@app.callback(
    Output('symbol-filter', 'options'),
    [Input('parsed-data-store', 'data')]
)
def update_symbol_options(parsed_data):
    """Dynamically populate symbol dropdown from parsed data"""
    if not parsed_data or not parsed_data['data']:
        return []
    
    df = pd.DataFrame(parsed_data['data'])
    
    # Check if Symbol column exists
    if 'Symbol' in df.columns and not df['Symbol'].empty:
        # Get unique symbols, sorted alphabetically
        symbols = sorted(df['Symbol'].dropna().astype(str).unique())
        
        # Create options with counts
        options = []
        for symbol in symbols:
            count = len(df[df['Symbol'] == symbol])
            options.append({
                'label': f"{symbol} ({count})",
                'value': symbol
            })
        return options
    
    return []


# Combined callback for Account Mapping page (without download output)
@app.callback(
    [Output('account-table-container', 'children'),
     Output('account-search-input', 'value'),
     Output('account-last-updated-display', 'children'),
     Output('account-stats-summary', 'children'),
     Output('account-tabs', 'children'),
     Output('account-search-terms-display', 'children'),
     Output('account-download-container', 'style')],
    [Input('account-tabs', 'value'),
     Input('account-search-input', 'value'),
     Input('account-clear-button', 'n_clicks')],
    [State('account-network-data', 'data'),
     State('account-last-updated', 'data')]
)
def update_account_display(tab_value, search_term, clear_clicks, network_data_dict, last_updated_str):
    ctx = dash.callback_context
    
    # Initialize variables
    table_content = html.Div()
    search_value = search_term or ''
    last_updated = f"Last updated: {datetime.fromisoformat(last_updated_str).strftime('%Y-%m-%d %H:%M:%S')}"
    stats_summary = ""
    tab_children = []
    search_terms_display = ""
    download_container_style = {'display': 'none'}
    
    # Handle clear button click
    if ctx.triggered and ctx.triggered[0]['prop_id'] == 'account-clear-button.n_clicks':
        search_value = ''
        search_term = ''
    
    # Parse search terms for display
    if search_term and str(search_term).strip():
        search_terms = [term for term in str(search_term).strip().split() if term]
        if search_terms:
            search_terms_display = html.Div([
                html.Span("Searching for: ", style={'fontWeight': 'bold'}),
                html.Span(" AND ".join([f'"{term}"' for term in search_terms]))
            ])
    
    # Check if data is loaded
    if not network_data_dict:
        table_content = html.Div([
            html.H3("No data loaded", style={'color': 'red', 'textAlign': 'center'}),
            html.P("Please ensure the CSV files are in the same directory as this app", 
                   style={'textAlign': 'center'})
        ], className="bg-white rounded-xl shadow-sm p-8")
        stats_summary = "No data available"
    else:
        # Convert stored data back to DataFrames
        network_data_loaded = {}
        for key, df_dict in network_data_dict.items():
            if df_dict:
                network_data_loaded[key] = pd.DataFrame(df_dict)
        
        # Get data for current tab
        current_df = network_data_loaded.get(tab_value)
        
        if current_df is None or current_df.empty:
            table_content = html.Div([
                html.H3(f"No data available for {NETWORKS[tab_value]}", 
                       style={'textAlign': 'center', 'color': '#666'})
            ], className="bg-white rounded-xl shadow-sm p-8")
            stats_summary = f"{NETWORKS[tab_value]}: 0 records"
        else:
            # Apply filtering
            filtered_df = filter_account_dataframe(current_df, search_term)
            
            if filtered_df.empty:
                table_content = html.Div([
                    html.H3(f"No matching records found in {NETWORKS[tab_value]}", 
                           style={'textAlign': 'center', 'color': '#666'}),
                    html.P(f"Search terms: {search_term}" if search_term else "", 
                           style={'textAlign': 'center'})
                ], className="bg-white rounded-xl shadow-sm p-8")
                stats_summary = f"{NETWORKS[tab_value]}: 0 of {len(current_df)} records match"
            else:
                # Create data table
                columns = [
                    {"name": "ACRONAME", "id": "ACRONAME"},
                    {"name": "ACCOUNT_NUMBER", "id": "ACCOUNT_NUMBER"}
                ]
                
                # Add NETWORK column only for total tab
                if tab_value == 'total' and 'NETWORK' in filtered_df.columns:
                    columns.insert(0, {"name": "NETWORK", "id": "NETWORK"})
                
                table = dash_table.DataTable(
                    id='account-data-table',
                    columns=columns,
                    data=filtered_df.to_dict('records'),
                    page_size=15,
                    page_current=0,
                    page_action='native',
                    sort_action='native',
                    sort_mode='single',
                    filter_action='none',
                    style_table={
                        'overflowX': 'auto',
                        'borderRadius': '8px',
                        'border': '1px solid #ddd'
                    },
                    style_header={
                        'backgroundColor': '#007bff',
                        'color': 'white',
                        'fontWeight': 'bold',
                        'fontSize': '14px',
                        'border': 'none'
                    },
                    style_cell={
                        'textAlign': 'left',
                        'padding': '12px',
                        'fontSize': '13px',
                        'borderBottom': '1px solid #eee'
                    },
                    style_data={
                        'border': 'none'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f8f9fa'
                        },
                        {
                            'if': {'state': 'selected'},
                            'backgroundColor': 'rgba(0, 123, 255, 0.1)',
                            'border': '1px solid #007bff'
                        }
                    ]
                )
                
                # Calculate statistics
                if search_term and str(search_term).strip():
                    search_terms_list = [term for term in str(search_term).strip().split() if term]
                    search_display = f" ({len(search_terms_list)} search term{'s' if len(search_terms_list) > 1 else ''})"
                else:
                    search_display = ""
                
                stats_summary = (
                    f"{NETWORKS[tab_value]}: Showing {len(filtered_df)} of {len(current_df)} records{search_display}"
                )
                
                # Show download button
                download_container_style = {'display': 'block', 'marginTop': '20px', 'textAlign': 'center'}
                
                # Create table container with download button
                table_content = html.Div([
                    html.Div([
                        html.H4(f"{NETWORKS[tab_value]} - Account Mappings", 
                               className="text-lg font-semibold text-gray-800 mb-2"),
                        html.P(f"Showing {len(filtered_df)} records (out of {len(current_df)} total)",
                              className="text-gray-600 mb-4")
                    ], className="mb-4"),
                    
                    html.Hr(className="my-4"),
                    
                    table
                ], className="bg-white rounded-xl shadow-sm p-6")
    
    # Update tab labels with counts
    tab_children = []
    for network in NETWORKS.keys():
        count = 0
        if network in network_data_dict and network_data_dict[network]:
            df = pd.DataFrame(network_data_dict[network])
            count = len(df)
        
        tab_children.append(
            dcc.Tab(
                label=f'{NETWORKS[network]} ({count})',
                value=network,
                style={
                    'padding': '12px 20px',
                    'fontWeight': 'bold',
                    'border': '1px solid #ddd',
                    'borderBottom': 'none',
                    'backgroundColor': '#f8f9fa'
                },
                selected_style={
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'border': '1px solid #007bff',
                    'borderBottom': 'none'
                }
            )
        )
    
    return table_content, search_value, last_updated, stats_summary, tab_children, search_terms_display, download_container_style

# Separate callback for Account Mapping download functionality
@app.callback(
    Output("download-account-csv", "data"),
    [Input("account-download-btn", "n_clicks")],
    [State('account-tabs', 'value'),
     State('account-search-input', 'value'),
     State('account-network-data', 'data')],
    prevent_initial_call=True
)
def download_account_data(n_clicks, tab_value, search_term, network_data_dict):
    if n_clicks and network_data_dict and tab_value in network_data_dict:
        # Get data for current tab
        current_df = pd.DataFrame(network_data_dict[tab_value])
        
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

# Additional callback to update tab counts when search is performed (Account Mapping)
@app.callback(
    Output('account-tabs', 'value'),
    [Input('account-search-input', 'n_submit')],
    [State('account-tabs', 'value')]
)
def maintain_tab_on_search(n_submit, current_tab):
    """Keep current tab when search is performed"""
    return current_tab

if __name__ == '__main__':
    # Print startup information
    print("\n" + "="*60)
    print("Ullink FIX Log & Account Viewer - Starting Server")
    print("="*60)
    
    print(f"\nLoaded Account Networks:")
    for network_key in NETWORKS.keys():
        if network_key in network_data:
            df = network_data[network_key]
            print(f"  • {NETWORKS[network_key]:12} - {len(df):3} records")
    
    total_records = len(network_data.get('total', pd.DataFrame()))
    print(f"\nTotal account records across all networks: {total_records}")
    print("\nApplication Features:")
    print("  • FIX Log Viewer: Upload/paste and analyze FIX protocol logs")
    print("  • Account Mapping: View and search account mappings")
    print("\nAccess the application at: http://localhost:8060")
    print("="*60 + "\n")
    
    app.run(debug=False, port=8060)