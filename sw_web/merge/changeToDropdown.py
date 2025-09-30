import dash
from dash import State, dcc, html, Input, Output, dash_table
import pandas as pd
import dash_cytoscape as cyto
import json

# Load data from external JSON file
def load_client_data():
    try:
        with open('client.json', 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    except FileNotFoundError:
        # Fallback to sample data if file doesn't exist
        print("Warning: client.json not found. Using sample data.")
        sample_data = [
            {
                "Client Name": "N/A",
                "Account": "JEFFERIESOTD_OMNI",
                "OMS": "",
                "Network": "TRADEWARE",
                "Identifier": "JEFFOTD",
                "High Touch": "",
                "Low Touch": "",
                "PT": "",
                "ETF": "",
                "IS": "",
                "Japan": "",
                "CB": "",
                "Options": "OPT",
                "Direct Tokyo": "",
                "Start Time": "07:00 MON-FRI",
                "End Time": "17:00 MON-FRI"
            },
            {
                "Client Name": "Client A",
                "Account": "ACME_123",
                "OMS": "OMS_A",
                "Network": "TRADEWARE",
                "Identifier": "JEFFOTD",
                "High Touch": "Yes",
                "Low Touch": "",
                "PT": "",
                "ETF": "",
                "IS": "",
                "Japan": "",
                "CB": "",
                "Options": "OPT",
                "Direct Tokyo": "",
                "Start Time": "08:00 MON-FRI",
                "End Time": "16:00 MON-FRI"
            },
            {
                "Client Name": "Client B",
                "Account": "CORP_456",
                "OMS": "OMS_B",
                "Network": "NEWTWORK_X",
                "Identifier": "OTHER_ID",
                "High Touch": "",
                "Low Touch": "Yes",
                "PT": "",
                "ETF": "",
                "IS": "",
                "Japan": "",
                "CB": "",
                "Options": "OPT",
                "Direct Tokyo": "",
                "Start Time": "09:00 MON-FRI",
                "End Time": "15:00 MON-FRI"
            },
            {
                "Client Name": "Client C",
                "Account": "JEFFERIESOTD_OMNI",
                "OMS": "OMS_C",
                "Network": "TRADEWARE",
                "Identifier": "OTHER_ID",
                "High Touch": "",
                "Low Touch": "",
                "PT": "",
                "ETF": "",
                "IS": "",
                "Japan": "",
                "CB": "",
                "Options": "OPT",
                "Direct Tokyo": "",
                "Start Time": "10:00 MON-FRI",
                "End Time": "14:00 MON-FRI"
            }
        ]
        return pd.DataFrame(sample_data)
    except Exception as e:
        print(f"Error loading client.json: {e}")
        return pd.DataFrame()

# Load adapter data from JSON file
def load_adapter_data():
    try:
        with open('adapters.json', 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("Warning: adapters.json not found. Using sample adapter data.")
        # Sample adapter data structure based on your JSON
        return {
            "BLOOMBERG": [
                "I_BLOOMBERG_HYBRID_FIX42",
                "I_BLOOMBERG_PT_FIX42", 
                "BloombergSellSide42",
                "I_BBG_OPT_FIX42"
            ],
            "CHARLES RIVER": [
                "CRD"
            ],
            "FIDESSA": [
                "I_FIDESSA_IPC"
            ],
            "ITG": [
                "ITGGSDHubSellSide42",
                "I_TRITON_USHUB_ITG_FIX42"
            ],
            "MIZUHO TK": [
                "MZTKGORSellSide42"
            ],
            "NYFIX": [
                "NYFIXSellSide42"
            ],
            "SUNGARD": [
                "I_RICEHALL_SUNGARD_FIX40",
                "SungardSellSide42"
            ],
            "TRADEWARE": [
                "TradeWareSellSide42",
                "I_TRADEWARE_OPT_FIX42"
            ],
            "TRADEWEB": [
                "TradewebSellSide42",
                "I_TRADEWEB_RFQF_FIX42"
            ]
        }
    except Exception as e:
        print(f"Error loading adapters.json: {e}")
        return {}

# --- New Data Loading for Accounts and Sub-accounts ---
def load_accounts_data():
    """Loads parent account data from account.csv."""
    try:
        # Load data and name columns
        df_acc = pd.read_csv('account.csv', header=None)
        df_acc.columns = ['Account', 'Parent Account Name']
        return df_acc
    except FileNotFoundError:
        print("Warning: account.csv not found. Using sample data.")
        account_sample = {
            'Account': [20000001, 20000002, 20000003],
            'Parent Account Name': ['BLACKROCK INC', 'JP MORGAN CHASE', 'GOLDMAN SACHS']
        }
        return pd.DataFrame(account_sample)
    except Exception as e:
        print(f"Error loading account.csv: {e}")
        return pd.DataFrame(columns=['Account', 'Parent Account Name'])

def load_subaccounts_data():
    """Loads sub-account data from subaccount.csv."""
    try:
        # Load data and name columns
        df_sub = pd.read_csv('subaccount.csv', header=None)
        df_sub.columns = ['Sub Account', 'Account', 'Sub-account Name']
        return df_sub
    except FileNotFoundError:
        print("Warning: subaccount.csv not found. Using sample data.")
        subaccount_sample = {
            'Sub Account': [30000001, 30000002, 30000003],
            'Account': [20000001, 20000001, 20000002],
            'Sub-account Name': ['John Garcia', 'Sarah Miller', 'Daniel Johnson']
        }
        return pd.DataFrame(subaccount_sample)
    except Exception as e:
        print(f"Error loading subaccount.csv: {e}")
        return pd.DataFrame(columns=['Sub Account', 'Account', 'Sub-account Name'])

def get_merged_accounts():
    """Merges parent and sub-account data."""
    df_accounts = load_accounts_data()
    df_subaccounts = load_subaccounts_data()
    
    if df_accounts.empty or df_subaccounts.empty:
        return pd.DataFrame()
        
    # Merge the two dataframes on the parent account ID
    merged_df = pd.merge(df_subaccounts, df_accounts, on='Account', how='left')
    return merged_df

# Load the data
df = load_client_data()

# Reformat time columns to be more readable
def reformat_time_str(time_str):
    """Converts strings like '07:00 MON-FRI' to 'MON-FRI 07:00'."""
    if isinstance(time_str, str) and ' ' in time_str:
        parts = time_str.split(' ', 1)
        if len(parts) == 2:
            return f"{parts[1]} {parts[0]}"
    return time_str

if 'Start Time' in df.columns:
    df['Start Time'] = df['Start Time'].apply(reformat_time_str)
if 'End Time' in df.columns:
    df['End Time'] = df['End Time'].apply(reformat_time_str)

# Add 'Actions' column for the modal trigger
if not df.empty:
    df['Actions'] = '...'

merged_accounts_df = get_merged_accounts()

adapter_data = load_adapter_data()

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Service type mapping
service_type_mapping = {
    'HT': 'High Touch',
    'LT': 'Low Touch', 
    'PT': 'PT',
    'ETF': 'ETF',
    'IS': 'IS',
    'JPBD': 'Japan',
    'CB': 'CB',
    'OPT': 'Options',
    'TK': 'Direct Tokyo'
}

service_types = ['HT', 'LT', 'PT', 'ETF', 'IS', 'JPBD', 'CB', 'OPT', 'TK']

# Add Tailwind CSS and custom styles
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .custom-tab {
                background-color: #f3f4f6 !important;
                border: 1px solid #e5e7eb !important;
                border-bottom: none !important;
                padding: 6px 12px !important;
                margin-right: 5px !important;
                margin-bottom: -1px !important;
                border-top-left-radius: 8px !important;
                border-top-right-radius: 8px !important;
                color: #374151 !important;
                cursor: pointer !important;
                font-size: 0.8rem !important;
                font-weight: 500 !important;
                min-width: 90px !important;
                text-align: center !important;
            }
            
            .custom-tab--selected {
                background-color: #2563eb !important;
                color: white !important;
                border: 1px solid #2563eb !important;
                border-bottom: none !important;
            }
            
            .custom-tab:hover:not(.custom-tab--selected) {
                background-color: #e5e7eb !important;
            }
            
            .sticky-header {
                position: sticky;
                top: 0;
                z-index: 1000;
                backdrop-filter: blur(10px);
                border-bottom: 1px solid #e5e7eb;
            }
            
            .sidebar {
                height: calc(100vh - 80px);
                position: sticky;
                top: 80px;
                overflow-y: auto;
            }
            
            .main-content {
                height: calc(100vh - 80px);
                overflow-y: auto;
            }
            
            .sidebar::-webkit-scrollbar {
                width: 4px;
            }
            
            .sidebar::-webkit-scrollbar-track {
                background: #f1f5f9;
            }
            
            .sidebar::-webkit-scrollbar-thumb {
                background: #cbd5e1;
                border-radius: 4px;
            }
            
            .nav-btn {
                transition: all 0.3s ease;
                border: 2px solid transparent;
            }
            
            .nav-btn-active {
                background-color: #2563eb !important;
                color: white !important;
                border-color: #1d4ed8 !important;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
            }
            
            .nav-btn:hover:not(.nav-btn-active) {
                background-color: #e5e7eb !important;
                border-color: #d1d5db !important;
            }
            
            /* Enhanced Checkbox Container Styling */
            .checkbox-container {
                display: flex !important;
                flex-wrap: nowrap !important;
                overflow-x: auto !important;
                overflow-y: hidden !important;
                gap: 8px !important;
                padding: 8px !important;
                background: #f1f5f9 !important;
                border-radius: 16px;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
                margin: 4px 0;
                border: 1px solid #e5e7eb;
                scrollbar-width: thin;
                scrollbar-color: #cbd5e1 #f1f5f9;
            }
            .checkbox-container::-webkit-scrollbar {
                height: 4px;
            }
            .checkbox-container::-webkit-scrollbar-track {
                background: #f1f5f9;
            }
            .checkbox-container::-webkit-scrollbar-thumb {
                background: #cbd5e1;
            }
            
            /* Enhanced Checkbox Item Styling */
            .checkbox-item {
                display: flex !important;
                align-items: center !important;
                background: white !important;
                backdrop-filter: blur(5px) !important;
                padding: 4px 8px !important;
                border-radius: 12px !important;
                border: 1px solid #e5e7eb !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                cursor: pointer !important;
                position: relative !important;
                overflow: hidden !important;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
                min-height: 32px !important;
                justify-content: flex-start !important;
            }
            
            /* Gradient overlay effect */
            .checkbox-item::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg, transparent, rgba(37, 99, 235, 0.05), transparent);
                opacity: 0;
                transition: opacity 0.3s ease;
                pointer-events: none;
            }
            
            .checkbox-item:hover::before {
                opacity: 1;
            }
            
            /* Enhanced hover and focus states */
            .checkbox-item:hover {
                border-color: #3b82f6 !important;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1) !important;
                transform: translateY(-2px) !important;
                background: white !important;
            }
            
            .checkbox-item:active {
                transform: translateY(0) !important;
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
            }
            
            /* Checkbox styling */
            .checkbox-item input[type="checkbox"] {
                width: 14px !important;
                height: 14px !important;
                margin-right: 6px !important;
                accent-color: #2563eb !important;
                cursor: pointer !important;
                border-radius: 6px !important;
                border: 2px solid #d1d5db !important;
                transition: all 0.2s ease !important;
                position: relative !important;
            }
            
            .checkbox-item input[type="checkbox"]:checked {
                background-color: #2563eb !important;
                border-color: #2563eb !important;
                box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
            }
            
            .checkbox-item input[type="checkbox"]:hover {
                border-color: #2563eb !important;
                box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
            }
            
            /* Label styling */
            .checkbox-item label {
                cursor: pointer !important;
                font-size: 0.75rem !important;
                color: #374151 !important;
                font-weight: 500 !important;
                letter-spacing: 0.025em !important;
                user-select: none !important;
                flex: 1 !important;
                transition: color 0.2s ease !important;
            }
            
            .checkbox-item:hover label {
                color: #3b82f6 !important;
            }
            
            /* Selected state styling */
            .checkbox-item:has(input:checked) {
                background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
                border-color: #1d4ed8 !important;
                box-shadow: 0 8px 25px rgba(37, 99, 235, 0.25) !important;
                color: white !important;
            }
            
            .checkbox-item:has(input:checked) label {
                color: white !important;
                font-weight: 600 !important;
            }
            
            .checkbox-item:has(input:checked)::before {
                background: linear-gradient(45deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1));
                opacity: 1;
            }
            
            /* Enhanced Clear Button Styling */
            .clear-service-btn {
                background: transparent !important;
                color: #16a34a !important; /* green-600 */
                border: 1px solid #86efac !important; /* green-300 */
                padding: 6px 12px !important;
                border-radius: 10px !important;
                font-size: 0.75rem !important;
                font-weight: 600 !important;
                cursor: pointer !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                text-transform: uppercase !important;
                letter-spacing: 0.05em !important;
                position: relative !important;
                overflow: hidden !important;
            }
            
            .clear-service-btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
                transition: left 0.5s ease;
            }
            
            .clear-service-btn:hover::before {
                left: 100%;
            }
            
            .clear-service-btn:hover {
                background: #16a34a !important; /* green-600 */
                color: white !important;
                box-shadow: 0 4px 12px rgba(22, 163, 74, 0.2) !important;
            }
            
            .clear-service-btn:active {
                transform: translateY(0) !important;
                box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3) !important;
            }
            
            /* Side Navigation Bar Styling */
            .side-nav {
                width: 70px;
                height: 100vh;
                position: fixed;
                left: 0;
                top: 0;
                background: #f3f4f6; /* Light gray background */
                box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
                z-index: 1100;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px 0;
                transition: width 0.3s ease;
            }
            
            .side-nav:hover {
                width: 200px;
            }
            
            .side-nav-logo {
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 1.2rem;
                margin-bottom: 30px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .side-nav:hover .side-nav-logo {
                width: 160px;
                justify-content: flex-start;
                padding-left: 15px;
            }
            
            .side-nav-item {
                width: 50px;
                height: 50px;
                margin: 5px 0;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: flex-start;
                color: #64748b; /* Darker icon color for light background */
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
                text-decoration: none;
                padding-left: 15px; /* Add padding to center the icon */
            }
            
            .side-nav:hover .side-nav-item {
                width: 160px;
                justify-content: flex-start;
                padding-left: 15px;
            }
            
            .side-nav-item:hover {
                background: rgba(59, 130, 246, 0.1);
                color: #3b82f6;
                transform: translateX(5px);
            }
            
            .side-nav-item.active {
                background-color: #d1d5db; /* Medium gray */
                color: #1f2937; /* Dark gray for icon */
                box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
            }
            
            .side-nav-item .icon {
                font-size: 1.3rem;
                min-width: 20px;
            }
            
            .side-nav-item .label {
                margin-left: 12px;
                font-weight: 500;
                font-size: 0.9rem;
                display: none; /* Hide label completely when collapsed */
                opacity: 0; /* For fade-in transition */
                transition: opacity 0.2s ease;
                white-space: nowrap;
            }
            
            .side-nav:hover .side-nav-item .label {
                display: inline; /* Show label on expand */
                opacity: 1;
            }
            
            /* Tooltip styling for collapsed state */
            .nav-tooltip {
                position: absolute;
                left: 65px;
                background: white;
                color: #1f2937;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 0.8rem;
                white-space: nowrap;
                opacity: 0;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                pointer-events: none;
                transform: translateY(-50%);
                transition: opacity 0.2s ease;
                z-index: 1200;
            }
            
            .nav-tooltip::before {
                content: '';
                position: absolute;
                left: -4px;
                top: 50%;
                transform: translateY(-50%);
                border: 4px solid transparent;
                border-right-color: white;
            }
            
            .side-nav-item:hover .nav-tooltip {
                opacity: 1;
            }
            
            .side-nav:hover .nav-tooltip {
                display: none;
            }
            
            /* Main content adjustment */
            .main-app-container {
                margin-left: 70px;
                transition: margin-left 0.3s ease;
            }

            /* Custom Modal Styles */
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1200;
            }

            .modal-content-wrapper {
                background: white;
                position: relative; /* Needed for absolute positioning of the close button */
                border-top-right-radius: 12px;
                border-bottom-right-radius: 12px;
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                width: 90%;
                max-width: 800px;
                max-height: 90vh;
                overflow-y: auto;
                transform: scale(0.95);
                opacity: 0;
                transition: all 0.2s ease-in-out;
            }

            .modal-open .modal-content-wrapper {
                transform: scale(1);
                opacity: 1;
            }

            .modal-list-item {
                display: flex;
                justify-content: flex-start;
                padding: 0.5rem 0;
                border-bottom: 1px solid #e5e7eb;
            }
            
            .modal-body-container {
                display: flex;
                gap: 24px; /* Space between details and graph */
            }
            .modal-details-column {
                flex: 1; /* This will be 1/3 of the space */
            }
            .modal-graph-column {
                flex: 2; /* This will be 2/3 of the space */
                min-height: 450px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
            
            .modal-edit-input {
                width: 100%;
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
            }

            /* Responsive design for checkboxes */
            @media (max-width: 768px) {
                .checkbox-container {
                    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
                    gap: 12px;
                    padding: 16px;
                }
                
                .checkbox-item {
                    padding: 10px 12px !important;
                    min-height: 44px !important;
                }
                
                .checkbox-item label {
                    font-size: 0.85rem !important;
                }
            }
            
            /* Animation for checkbox changes */
            @keyframes checkboxPop {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }
            
            .checkbox-item input[type="checkbox"]:checked {
                animation: checkboxPop 0.3s ease;
            }
        </style>
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        colors: {
                            primary: '#2563eb',
                            secondary: '#64748b',
                            accent: '#f59e0b',
                        }
                    }
                }
            }
        </script>
    </head>
    <body class="bg-gray-100">
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

predefined_networks = ['ALL', 'BLOOMBERG', 'FIDESSA', 'ITG', 'TRADEWARE', 'TRADEWEB', 'NYFIX']

networks = predefined_networks

def create_dashboard_layout():
    return html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Search", className="text-lg font-semibold mb-4 text-primary flex items-center"),
                        
                        html.Div([
                            html.Label("Client Name:", className="block text-sm font-medium text-gray-700 mb-1"),
                            dcc.Input(
                                id="client-search",
                                type="text",
                                placeholder="Enter partial client name...",
                                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                            ),
                        ], className="mb-4"),
                        
                        html.Div([
                            html.Label("Account Number:", className="block text-sm font-medium text-gray-700 mb-1"),
                            dcc.Input(
                                id="account-search",
                                type="number",
                                placeholder="Enter partial account...",
                                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                            ),
                        ], className="mb-4"),
                        
                        html.Button(
                            "CLEAR",
                            id="clear-search-btn",
                            n_clicks=0,
                            className="w-full px-4 py-2 text-sm font-semibold text-green-600 bg-transparent border-2 border-green-300 rounded-md hover:bg-green-600 hover:text-white hover:border-transparent transition-colors"
                        ),
                    ], className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200"),
                    
                    # Summary output moved to sidebar
                    html.Div([
                        html.H3("Summary", className="text-lg font-semibold mb-4 text-primary"),
                        html.Div(id="summary-output", className="text-sm text-gray-700 h-full")
                    ], className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200"),

                ], className="p-4")
            ], className="sidebar bg-white shadow-lg w-80 min-w-80"),
            
            html.Div([
                # Flex container for Network Filter and Adapters
                html.Div([
                    html.Div([
                        html.H3("Network", className="text-xl font-semibold mb-2 text-primary"),
                        dcc.Tabs(
                            id="network-tabs",
                            value='ALL',
                            children=[
                                dcc.Tab(
                                    label=network,
                                    value=network,
                                    className="custom-tab",
                                    selected_className="custom-tab--selected"
                                ) for network in networks
                            ],
                            className="mb-4"
                        ),
                    ], className="w-2/3 p-3 bg-blue-50 rounded-lg border border-blue-200"),

                    # New container for Adapters - now with dropdown
                    html.Div([
                        html.H3("Adapters", className="text-xl font-semibold mb-2 text-primary"),
                        html.Div(id="adapter-dropdown-container", children=[
                            html.Div("Please select a specific network to see available adapters.",
                                     className="text-gray-500 italic text-sm p-3 bg-gray-50 rounded-lg border border-gray-200 h-full")
                        ]),
                    ], className="w-1/3 p-3 bg-blue-50 rounded-lg border border-blue-200"),
                ], className="flex space-x-2 mb-2"),
                
                # Flex container for Service Types and OMS Filter
                html.Div([
                    # Enhanced Summary Section with Service Type Checkboxes
                    html.Div([
                        html.H3("Services", className="text-xl font-semibold mb-2 text-primary"),
                        html.Div([
                            dcc.Checklist(
                                id="service-type-checklist",
                                options=[{"label": st, "value": st} for st in service_types],
                                value=[],
                                className="checkbox-container",
                                labelClassName="checkbox-item",
                                inputClassName="mr-2"
                            ),
                            html.Button(
                                "CLEAR",
                                id="clear-service-btn",
                                n_clicks=0,
                                className="clear-service-btn ml-4 self-center"
                            )
                        ], className="flex items-center")
                    ], className="w-2/3 mb-1 p-2 bg-blue-50 rounded-lg border border-blue-200"),

                    # OMS Filter moved from sidebar
                    html.Div([
                        html.H3("OMS", className="text-xl font-semibold mb-2 text-primary"),
                        dcc.Dropdown(
                            id="value-dropdown",
                            clearable=False,
                            className="w-full text-sm"
                        ),
                    ], className="w-1/3 mb-1 p-3 bg-blue-50 rounded-lg border border-blue-200"),
                ], className="flex space-x-2 mb-1"),
                
                # Data table
                html.Div([
                    html.H3("Client Data", className="text-xl font-semibold mb-2 text-primary"),
                    html.Div(id="table-container", children=[
                        dash_table.DataTable(
                            id="data-table",
                            columns=([
                                {"name": col, "id": col} for col in df.columns if col != 'Actions'
                            ] + [
                                # Ensure Actions column is last and styled
                                {"name": "Actions", "id": "Actions"}
                            ]) if not df.empty else [],
                            data=df.to_dict("records") if len(df) > 0 else [],
                            page_size=15,
                            style_table={"overflowX": "auto", "minWidth": "100%"},
                            style_cell={
                                'padding': '12px', 
                                'textAlign': 'center', 
                                'border': '1px solid #e5e7eb', 
                                'fontSize': '14px'
                            },
                            style_header={
                                'backgroundColor': '#f8fafc',
                                'fontWeight': 'bold',
                                'border': '1px solid #e5e7eb',
                                'color': '#374151'
                            },
                            style_data={
                                'backgroundColor': 'white',
                                'border': '1px solid #e5e7eb'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': '#f9fafb'
                                }
                            ],
                            style_cell_conditional=[
                                {
                                    'if': {'column_id': 'Client Name'},
                                    'textAlign': 'left',
                                },
                                {
                                    'if': {'column_id': 'Actions'},
                                    'cursor': 'pointer',
                                    'font-weight': 'bold',
                                    'font-size': '18px',
                                    'color': '#3b82f6'
                                }
                            ],
                            sort_action="native",
                            filter_action="native",
                            export_format="xlsx",
                            export_headers="display"
                        )
                    ])
                ], className="bg-white p-4 rounded-lg shadow-md"),

                # Custom Modal built with Divs, with structure present at startup
                html.Div(
                    id="row-data-modal",
                    className="modal-overlay",
                    style={'display': 'none'}, # Hidden by default
                    children=html.Div( # modal-content-wrapper
                        className="modal-content-wrapper", 
                        children=html.Div( # p-6 container
                            className="p-6",
                            children=[ 
                                # New 'X' close button
                                html.Button("×", id="modal-close-x-button", className="absolute top-2 right-4 text-gray-500 hover:text-gray-800 text-3xl font-light leading-none"),
                                html.H4("Details", className="text-2xl font-semibold text-primary mb-4"),
                                html.Div(id="modal-content-container"), # Dynamic content will go here
                                html.Button("Close", id="modal-close-button", className="mt-6 px-4 py-2 bg-gray-300 text-gray-800 rounded-md hover:bg-gray-400 transition-colors")
                            ]
                        )
                    )
                ),

            ], className="main-content flex-1 p-4"),

            # Store to hold data for the selected row
            dcc.Store(id='selected-row-store'),
            
        ], className="flex min-h-screen"),
    ])



# Function to create the Stats page layout
def create_stats_layout():
    if len(df) == 0:
        return html.Div([
            html.Div([
                html.H2("Advanced Statistics", className="text-3xl font-bold text-primary mb-6"),
                html.Div("No data available. Please check if client.json exists.", className="text-red-600 text-center p-8"),
            ], className="p-8")
        ])
    
    # Calculate comprehensive statistics for the stats page
    total_clients = len(df)
    
    # Safe calculation for networks - handle NaN values
    if 'Network' in df.columns:
        network_counts = df['Network'].dropna().value_counts()
        network_data = {}
        for network, count in network_counts.items():
            percentage = round((count / total_clients * 100), 1) if total_clients > 0 else 0
            network_data[str(network)] = {'count': count, 'percentage': percentage}
    else:
        network_data = {}
    
    # Safe calculation for OMS - handle NaN values
    if 'OMS' in df.columns:
        oms_counts = df['OMS'].dropna().value_counts()
        oms_data = {}
        for oms, count in oms_counts.items():
            percentage = round((count / total_clients * 100), 1) if total_clients > 0 else 0
            oms_data[str(oms)] = {'count': count, 'percentage': percentage}
    else:
        oms_data = {}
    
    # Calculate service type statistics with percentages
    service_columns = ['High Touch', 'Low Touch', 'PT', 'ETF', 'IS', 'Japan', 'CB', 'Options', 'Direct Tokyo']
    active_services = {}
    for col in service_columns:
        if col in df.columns:
            # Count non-null and non-empty values
            active_count = len(df[df[col].notna() & (df[col].astype(str) != '')])
            if active_count > 0:
                percentage = round((active_count / total_clients * 100), 1) if total_clients > 0 else 0
                active_services[col] = {'count': active_count, 'percentage': percentage}
    
    # Calculate time statistics
    if 'Start Time' in df.columns:
        start_time_counts = df['Start Time'].dropna().value_counts()
        start_time_data = {}
        for time, count in start_time_counts.items():
            percentage = round((count / total_clients * 100), 1) if total_clients > 0 else 0
            start_time_data[str(time)] = {'count': count, 'percentage': percentage}
    else:
        start_time_data = {}
    
    if 'End Time' in df.columns:
        end_time_counts = df['End Time'].dropna().value_counts()
        end_time_data = {}
        for time, count in end_time_counts.items():
            percentage = round((count / total_clients * 100), 1) if total_clients > 0 else 0
            end_time_data[str(time)] = {'count': count, 'percentage': percentage}
    else:
        end_time_data = {}
    
    return html.Div([
        html.Div([
            html.H2("Advanced Statistics", className="text-3xl font-bold text-primary mb-6"),
            
            # Overall statistics cards
            html.Div([
                html.Div([
                    html.H3("Total Clients", className="text-lg font-semibold text-gray-700 mb-2"),
                    html.P(f"{total_clients}", className="text-3xl font-bold text-primary")
                ], className="bg-white p-6 rounded-lg shadow-md text-center"),
                
                html.Div([
                    html.H3("Active Networks", className="text-lg font-semibold text-gray-700 mb-2"),
                    html.P(f"{len(network_data)}", className="text-3xl font-bold text-primary")
                ], className="bg-white p-6 rounded-lg shadow-md text-center"),
                
                html.Div([
                    html.H3("Active OMS", className="text-lg font-semibold text-gray-700 mb-2"),
                    html.P(f"{len(oms_data)}", className="text-3xl font-bold text-primary")
                ], className="bg-white p-6 rounded-lg shadow-md text-center"),
                
                html.Div([
                    html.H3("Active Services", className="text-lg font-semibold text-gray-700 mb-2"),
                    html.P(f"{len(active_services)}", className="text-3xl font-bold text-primary")
                ], className="bg-white p-6 rounded-lg shadow-md text-center"),
            ], className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"),
            
            # Network Statistics
            html.Div([
                html.H3("Network Distribution", className="text-xl font-semibold text-primary mb-4"),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span(network, className="font-medium text-gray-700"),
                            html.Span(f" ({data['count']} - {data['percentage']}%)", 
                                    className="text-sm text-gray-500 ml-2")
                        ], className="flex justify-between items-center mb-2")
                    ] for network, data in network_data.items())
                ], className="bg-white p-6 rounded-lg shadow-md")
            ], className="mb-8"),
            
            # OMS Statistics
            html.Div([
                html.H3("OMS Distribution", className="text-xl font-semibold text-primary mb-4"),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span(oms, className="font-medium text-gray-700"),
                            html.Span(f" ({data['count']} - {data['percentage']}%)", 
                                    className="text-sm text-gray-500 ml-2")
                        ], className="flex justify-between items-center mb-2")
                    ] for oms, data in oms_data.items())
                ], className="bg-white p-6 rounded-lg shadow-md")
            ], className="mb-8"),
            
            # Service Type Statistics
            html.Div([
                html.H3("Service Type Distribution", className="text-xl font-semibold text-primary mb-4"),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span(service, className="font-medium text-gray-700"),
                            html.Span(f" ({data['count']} - {data['percentage']}%)", 
                                    className="text-sm text-gray-500 ml-2")
                        ], className="flex justify-between items-center mb-2")
                    ] for service, data in active_services.items())
                ], className="bg-white p-6 rounded-lg shadow-md")
            ], className="mb-8"),
            
            # Time Statistics
            html.Div([
                html.H3("Start Time Distribution", className="text-xl font-semibold text-primary mb-4"),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span(time, className="font-medium text-gray-700"),
                            html.Span(f" ({data['count']} - {data['percentage']}%)", 
                                    className="text-sm text-gray-500 ml-2")
                        ], className="flex justify-between items-center mb-2")
                    ] for time, data in start_time_data.items())
                ], className="bg-white p-6 rounded-lg shadow-md mb-6"),
                
                html.H3("End Time Distribution", className="text-xl font-semibold text-primary mb-4"),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span(time, className="font-medium text-gray-700"),
                            html.Span(f" ({data['count']} - {data['percentage']}%)", 
                                    className="text-sm text-gray-500 ml-2")
                        ], className="flex justify-between items-center mb-2")
                    ] for time, data in end_time_data.items())
                ], className="bg-white p-6 rounded-lg shadow-md")
            ]),
            
        ], className="p-8")
    ])



# Function to create the Accounts page layout
def create_accounts_layout():
    if merged_accounts_df.empty:
        return html.Div([
            html.Div([
                html.H2("Account Management", className="text-3xl font-bold text-primary mb-6"),
                html.Div("No account data available. Please check if account.csv and subaccount.csv exist.", 
                        className="text-red-600 text-center p-8"),
            ], className="p-8")
        ])
    
    # Calculate statistics outside the layout
    account_counts = merged_accounts_df['Account'].value_counts()
    multi_sub_accounts = len(account_counts[account_counts > 1])
    avg_sub_accounts = round(len(merged_accounts_df) / len(merged_accounts_df['Account'].unique()), 2) if len(merged_accounts_df['Account'].unique()) > 0 else 0
    
    return html.Div([
        html.Div([
            html.H2("Account Management", className="text-3xl font-bold text-primary mb-6"),
            
            # Account Statistics Cards
            html.Div([
                html.Div([
                    html.H3("Total Parent Accounts", className="text-lg font-semibold text-gray-700 mb-2"),
                    html.P(f"{len(merged_accounts_df['Account'].unique())}", 
                          className="text-3xl font-bold text-primary")
                ], className="bg-white p-6 rounded-lg shadow-md text-center"),
                
                html.Div([
                    html.H3("Total Sub-accounts", className="text-lg font-semibold text-gray-700 mb-2"),
                    html.P(f"{len(merged_accounts_df)}", 
                          className="text-3xl font-bold text-primary")
                ], className="bg-white p-6 rounded-lg shadow-md text-center"),
                
                html.Div([
                    html.H3("Accounts with Multiple Sub-accounts", className="text-lg font-semibold text-gray-700 mb-2"),
                    html.P(f"{multi_sub_accounts}", 
                          className="text-3xl font-bold text-primary")
                ], className="bg-white p-6 rounded-lg shadow-md text-center"),
                
                html.Div([
                    html.H3("Average Sub-accounts per Account", className="text-lg font-semibold text-gray-700 mb-2"),
                    html.P(f"{avg_sub_accounts}", 
                          className="text-3xl font-bold text-primary")
                ], className="bg-white p-6 rounded-lg shadow-md text-center"),
            ], className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"),
            
            # Account Relationship Visualization
            html.Div([
                html.H3("Account Relationships", className="text-xl font-semibold text-primary mb-4"),
                cyto.Cytoscape(
                    id='account-cytoscape',
                    layout={'name': 'cose'},
                    style={'width': '100%', 'height': '600px', 'border': '1px solid #e5e7eb', 'borderRadius': '8px'},
                    elements=generate_account_elements(),
                    stylesheet=[
                        # Node styles
                        {
                            'selector': 'node',
                            'style': {
                                'background-color': '#3b82f6',
                                'label': 'data(label)',
                                'font-size': '14px',
                                'text-valign': 'center',
                                'text-halign': 'center',
                                'color': '#1f2937',
                                'width': 'mapData(weight, 1, 10, 50, 100)',
                                'height': 'mapData(weight, 1, 10, 50, 100)'
                            }
                        },
                        # Edge styles
                        {
                            'selector': 'edge',
                            'style': {
                                'width': 2,
                                'line-color': '#9ca3af',
                                'target-arrow-color': '#9ca3af',
                                'target-arrow-shape': 'triangle',
                                'curve-style': 'bezier'
                            }
                        },
                        # Parent account node style
                        {
                            'selector': '.parent',
                            'style': {
                                'background-color': '#1e40af',
                                'font-weight': 'bold'
                            }
                        },
                        # Sub-account node style
                        {
                            'selector': '.child',
                            'style': {
                                'background-color': '#60a5fa'
                            }
                        }
                    ]
                )
            ], className="bg-white p-6 rounded-lg shadow-md mb-8"),
            
            # Account Data Table
            html.Div([
                html.H3("Account Data", className="text-xl font-semibold text-primary mb-4"),
                dash_table.DataTable(
                    id='accounts-table',
                    columns=[
                        {"name": "Account", "id": "Account"},
                        {"name": "Parent Account Name", "id": "Parent Account Name"},
                        {"name": "Sub Account", "id": "Sub Account"},
                        {"name": "Sub-account Name", "id": "Sub-account Name"}
                    ],
                    data=merged_accounts_df.to_dict('records'),
                    page_size=15,
                    style_table={"overflowX": "auto", "minWidth": "100%"},
                    style_cell={
                        'padding': '12px', 
                        'textAlign': 'left', 
                        'border': '1px solid #e5e7eb', 
                        'fontSize': '14px'
                    },
                    style_header={
                        'backgroundColor': '#f8fafc',
                        'fontWeight': 'bold',
                        'border': '1px solid #e5e7eb',
                        'color': '#374151'
                    },
                    style_data={
                        'backgroundColor': 'white',
                        'border': '1px solid #e5e7eb'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f9fafb'
                        }
                    ],
                    sort_action="native",
                    filter_action="native",
                    export_format="xlsx",
                    export_headers="display"
                )
            ], className="bg-white p-6 rounded-lg shadow-md")
            
        ], className="p-8")
    ])


def generate_account_elements():
    """Generate cytoscape elements for account relationships."""
    elements = []
    
    if merged_accounts_df.empty:
        return elements
    
    # Add parent account nodes
    parent_accounts = merged_accounts_df[['Account', 'Parent Account Name']].drop_duplicates()
    for _, row in parent_accounts.iterrows():
        elements.append({
            'data': {'id': f"parent_{row['Account']}", 'label': f"{row['Parent Account Name']}\n({row['Account']})"},
            'classes': 'parent'
        })
    
    # Add sub-account nodes and edges
    for _, row in merged_accounts_df.iterrows():
        sub_account_id = f"child_{row['Sub Account']}"
        elements.append({
            'data': {'id': sub_account_id, 'label': f"{row['Sub-account Name']}\n({row['Sub Account']})"},
            'classes': 'child'
        })
        
        # Add edge from parent to sub-account
        elements.append({
            'data': {'source': f"parent_{row['Account']}", 'target': sub_account_id}
        })
    
    return elements


# Function to create the Adapters page layout
def create_adapters_layout():
    return html.Div([
        html.Div([
            html.H2("Adapters Configuration", className="text-3xl font-bold text-primary mb-6"),
            
            # Network Adapters Overview
            html.Div([
                html.H3("Network Adapters", className="text-xl font-semibold text-primary mb-4"),
                html.Div([
                    html.Div([
                        html.Div([
                            html.H4(network, className="text-lg font-semibold text-gray-800 mb-3"),
                            html.Ul([
                                html.Li(adapter, className="text-sm text-gray-600 py-1 px-3 bg-gray-50 rounded-md mb-1 border border-gray-200") 
                                for adapter in adapters
                            ], className="space-y-1")
                        ], className="bg-white p-4 rounded-lg shadow-sm border border-gray-200")
                    ] for network, adapters in adapter_data.items())
                ], className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4")
            ], className="mb-8"),
            
            # Adapter Statistics
            html.Div([
                html.H3("Adapter Statistics", className="text-xl font-semibold text-primary mb-4"),
                html.Div([
                    html.Div([
                        html.H4("Total Networks", className="text-lg font-semibold text-gray-700 mb-2"),
                        html.P(f"{len(adapter_data)}", className="text-2xl font-bold text-primary")
                    ], className="bg-white p-6 rounded-lg shadow-md text-center"),
                    
                    html.Div([
                        html.H4("Total Adapters", className="text-lg font-semibold text-gray-700 mb-2"),
                        html.P(f"{sum(len(adapters) for adapters in adapter_data.values())}", className="text-2xl font-bold text-primary")
                    ], className="bg-white p-6 rounded-lg shadow-md text-center"),
                    
                    html.Div([
                        html.H4("Average Adapters per Network", className="text-lg font-semibold text-gray-700 mb-2"),
                        html.P(f"{round(sum(len(adapters) for adapters in adapter_data.values()) / len(adapter_data), 1) if len(adapter_data) > 0 else 0}", className="text-2xl font-bold text-primary")
                    ], className="bg-white p-6 rounded-lg shadow-md text-center"),
                ], className="grid grid-cols-1 md:grid-cols-3 gap-6")
            ]),
            
        ], className="p-8")
    ])

# Side navigation bar component
def create_side_nav():
    return html.Div([
        html.Div([
            # Logo
            html.Div([
                html.Span("J", className="icon"),
                html.Span("Jefferies", className="label")
            ], className="side-nav-logo"),
            
            # Navigation items
            html.A([
                html.Span("🏠", className="icon"),
                html.Span("Dashboard", className="label"),
                html.Div("Dashboard", className="nav-tooltip")
            ], href="/", className="side-nav-item", id="nav-dashboard"),
            
            html.A([
                html.Span("📊", className="icon"),
                html.Span("Statistics", className="label"),
                html.Div("Statistics", className="nav-tooltip")
            ], href="/stats", className="side-nav-item", id="nav-stats"),
            
            html.A([
                html.Span("👥", className="icon"),
                html.Span("Accounts", className="label"),
                html.Div("Accounts", className="nav-tooltip")
            ], href="/accounts", className="side-nav-item", id="nav-accounts"),
            
            html.A([
                html.Span("🔌", className="icon"),
                html.Span("Adapters", className="label"),
                html.Div("Adapters", className="nav-tooltip")
            ], href="/adapters", className="side-nav-item", id="nav-adapters"),
            
        ], className="side-nav"),
        
        # Main content area with margin for side nav
        html.Div([
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content', className="min-h-screen bg-gray-100")
        ], className="main-app-container")
    ])

# Main app layout with side navigation
app.layout = html.Div([
    create_side_nav()
])

# Callback to update page content based on URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/stats':
        return create_stats_layout()
    elif pathname == '/accounts':
        return create_accounts_layout()
    elif pathname == '/adapters':
        return create_adapters_layout()
    else:  # Default to dashboard
        return create_dashboard_layout()

# Callback to update active nav item
@app.callback(
    [Output('nav-dashboard', 'className'),
     Output('nav-stats', 'className'),
     Output('nav-accounts', 'className'),
     Output('nav-adapters', 'className')],
    [Input('url', 'pathname')]
)
def update_nav_active(pathname):
    base_class = "side-nav-item"
    active_class = "side-nav-item active"
    
    if pathname == '/stats':
        return base_class, active_class, base_class, base_class
    elif pathname == '/accounts':
        return base_class, base_class, active_class, base_class
    elif pathname == '/adapters':
        return base_class, base_class, base_class, active_class
    else:  # Dashboard
        return active_class, base_class, base_class, base_class

# Callback to update OMS dropdown based on selected network
@app.callback(
    Output("value-dropdown", "options"),
    [Input("network-tabs", "value")]
)
def update_dropdown_options(selected_network):
    if selected_network == "ALL":
        filtered_df = df
    else:
        filtered_df = df[df["Network"] == selected_network]
    
    oms_options = [{"label": oms, "value": oms} for oms in sorted(filtered_df["OMS"].dropna().unique())]
    return oms_options

# Callback to update the table based on all filters
@app.callback(
    Output("data-table", "data"),
    [Input("network-tabs", "value"),
     Input("value-dropdown", "value"),
     Input("client-search", "value"),
     Input("account-search", "value"),
     Input("service-type-checklist", "value")]
)
def update_table(selected_network, selected_oms, client_search, account_search, selected_services):
    filtered_df = df.copy()
    
    # Filter by network
    if selected_network != "ALL":
        filtered_df = filtered_df[filtered_df["Network"] == selected_network]
    
    # Filter by OMS
    if selected_oms:
        filtered_df = filtered_df[filtered_df["OMS"] == selected_oms]
    
    # Filter by client name (partial match)
    if client_search:
        filtered_df = filtered_df[filtered_df["Client Name"].str.contains(client_search, case=False, na=False)]
    
    # Filter by account number (partial match)
    if account_search:
        filtered_df = filtered_df[filtered_df["Account"].astype(str).str.contains(str(account_search), case=False, na=False)]
    
    # Filter by service types
    if selected_services:
        for service in selected_services:
            service_column = service_type_mapping.get(service, service)
            if service_column in filtered_df.columns:
                # Keep rows where the service column is not empty
                filtered_df = filtered_df[filtered_df[service_column].notna() & (filtered_df[service_column].astype(str) != '')]
    
    return filtered_df.to_dict("records")

# Callback to update summary output
@app.callback(
    Output("summary-output", "children"),
    [Input("data-table", "data")]
)
def update_summary(table_data):
    if not table_data:
        return "No data to display."
    
    filtered_df = pd.DataFrame(table_data)
    total_count = len(filtered_df)
    
    summary_elements = [
        html.P(f"Total Clients: {total_count}", className="font-semibold text-primary mb-2")
    ]
    
    # Add network distribution
    if 'Network' in filtered_df.columns:
        network_counts = filtered_df['Network'].value_counts()
        for network, count in network_counts.items():
            percentage = round((count / total_count * 100), 1) if total_count > 0 else 0
            summary_elements.append(
                html.P(f"{network}: {count} ({percentage}%)", className="text-sm text-gray-600 mb-1")
            )
    
    return html.Div(summary_elements)

# Callback to clear search inputs
@app.callback(
    [Output("client-search", "value"),
     Output("account-search", "value")],
    [Input("clear-search-btn", "n_clicks")]
)
def clear_search(n_clicks):
    if n_clicks > 0:
        return "", ""
    return dash.no_update, dash.no_update

# Callback to clear service type checkboxes
@app.callback(
    Output("service-type-checklist", "value"),
    [Input("clear-service-btn", "n_clicks")]
)
def clear_service_types(n_clicks):
    if n_clicks > 0:
        return []
    return dash.no_update

# Callback to show/hide modal and update its content
@app.callback(
    [Output("row-data-modal", "style"),
     Output("modal-content-container", "children")],
    [Input("data-table", "active_cell"),
    Input("modal-close-button", "n_clicks"),
    Input("modal-close-x-button", "n_clicks")],
    [State("data-table", "data"),
    State("row-data-modal", "style")]
)
def toggle_modal(active_cell, close_clicks, close_x_clicks, table_data, current_style):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_style, ""
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id in ["modal-close-button", "modal-close-x-button"]:
        return {'display': 'none'}, ""
    
    elif trigger_id == "data-table" and active_cell:
        # Get the row data for the clicked cell
        row_index = active_cell['row']
        row_data = table_data[row_index]
        
        # Check if the clicked cell is in the "Actions" column
        if active_cell.get('column_id') == 'Actions':
            # Create modal content
            modal_content = create_modal_content(row_data)
            return {'display': 'flex'}, modal_content
    
    return current_style, ""

def create_modal_content(row_data):
    """Create the content for the modal dialog."""
    # Create two-column layout: details and graph
    return html.Div([
        html.Div([
            # Left column - Client Details
            html.Div([
                html.H5("Client Details", className="text-lg font-semibold mb-3 text-primary"),
                html.Div([
                    html.Div([
                        html.Strong("Client Name: "),
                        html.Span(row_data.get('Client Name', 'N/A'))
                    ], className="modal-list-item"),
                    html.Div([
                        html.Strong("Account: "),
                        html.Span(row_data.get('Account', 'N/A'))
                    ], className="modal-list-item"),
                    html.Div([
                        html.Strong("OMS: "),
                        html.Span(row_data.get('OMS', 'N/A'))
                    ], className="modal-list-item"),
                    html.Div([
                        html.Strong("Network: "),
                        html.Span(row_data.get('Network', 'N/A'))
                    ], className="modal-list-item"),
                    html.Div([
                        html.Strong("Identifier: "),
                        html.Span(row_data.get('Identifier', 'N/A'))
                    ], className="modal-list-item"),
                ]),
                
                # Service Types
                html.H5("Service Types", className="text-lg font-semibold mt-4 mb-3 text-primary"),
                html.Div([
                    html.Div([
                        html.Strong("High Touch: "),
                        html.Span(row_data.get('High Touch', 'N/A'))
                    ], className="modal-list-item"),
                    html.Div([
                        html.Strong("Low Touch: "),
                        html.Span(row_data.get('Low Touch', 'N/A'))
                    ], className="modal-list-item"),
                    html.Div([
                        html.Strong("PT: "),
                        html.Span(row_data.get('PT', 'N/A'))
                    ], className="modal-list-item"),
                    html.Div([
                        html.Strong("ETF: "),
                        html.Span(row_data.get('ETF', 'N/A'))
                    ], className="modal-list-item"),
                    html.Div([
                        html.Strong("IS: "),
                        html.Span(row_data.get('IS', 'N/A'))
                    ], className="modal-list-item"),
                    html.Div([
                        html.Strong("Japan: "),
                        html.Span(row_data.get('Japan', 'N/A'))
                    ], className="modal-list-item"),
                    html.Div([
                        html.Strong("CB: "),
                        html.Span(row_data.get('CB', 'N/A'))
                    ], className="modal-list-item"),
                    html.Div([
                        html.Strong("Options: "),
                        html.Span(row_data.get('Options', 'N/A'))
                    ], className="modal-list-item"),
                    html.Div([
                        html.Strong("Direct Tokyo: "),
                        html.Span(row_data.get('Direct Tokyo', 'N/A'))
                    ], className="modal-list-item"),
                ]),
                
                # Trading Hours
                html.H5("Trading Hours", className="text-lg font-semibold mt-4 mb-3 text-primary"),
                html.Div([
                    html.Div([
                        html.Strong("Start Time: "),
                        html.Span(row_data.get('Start Time', 'N/A'))
                    ], className="modal-list-item"),
                    html.Div([
                        html.Strong("End Time: "),
                        html.Span(row_data.get('End Time', 'N/A'))
                    ], className="modal-list-item"),
                ]),
            ], className="modal-details-column"),
            
            # Right column - Graph/Visualization
            html.Div([
                html.H5("Client Activity", className="text-lg font-semibold mb-3 text-primary"),
                # Placeholder for graph - you can replace this with actual visualization
                html.Div([
                    html.P("Activity visualization would appear here.", 
                          className="text-gray-500 text-center"),
                    # You can add dcc.Graph component here for actual charts
                ], className="h-full flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg p-4")
            ], className="modal-graph-column"),
        ], className="modal-body-container"),
        
        # Edit button
        html.Div([
            html.Button("Edit", id="edit-button", n_clicks=0,
                      className="px-4 py-2 bg-primary text-white rounded-md hover:bg-blue-700 transition-colors")
        ], className="mt-6 text-center")
    ])

# Callback to update the adapter dropdown based on selected network
@app.callback(
    Output("adapter-dropdown-container", "children"),
    [Input("network-tabs", "value")]
)
def update_adapter_dropdown(selected_network):
    if selected_network == "ALL":
        return html.Div("Please select a specific network to see available adapters.",
                       className="text-gray-500 italic text-sm p-3 bg-gray-50 rounded-lg border border-gray-200 h-full")
    
    # Get adapters for the selected network
    adapters_list = adapter_data.get(selected_network, [])
    
    if not adapters_list:
        return html.Div(f"No adapters found for {selected_network}.",
                       className="text-gray-500 italic text-sm p-3 bg-gray-50 rounded-lg border border-gray-200 h-full")
    
    # Create dropdown with adapters
    return html.Div([
        dcc.Dropdown(
            id="adapter-dropdown",
            options=[{"label": adapter, "value": adapter} for adapter in adapters_list],
            placeholder=f"Select {selected_network} adapter...",
            className="w-full text-sm"
        )
    ], className="h-full")

if __name__ == "__main__":
    app.run(debug=True)
