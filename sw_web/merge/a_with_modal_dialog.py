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
            
            /* ADAPTER TABS FIX - Fit content width */
            .adapter-tabs-container {
                display: flex !important;
                flex-wrap: nowrap !important;
                overflow-x: auto !important;
                overflow-y: hidden !important;
                white-space: nowrap !important;
                gap: 6px !important;
                padding: 2px 0 !important;
                margin: 4px 0 !important;
                scrollbar-width: thin !important;
                scrollbar-color: #cbd5e1 #f1f5f9 !important;
                width: 100% !important;
            }
            
            .adapter-tabs-container::-webkit-scrollbar {
                height: 4px !important;
            }
            
            .adapter-tabs-container::-webkit-scrollbar-track {
                background: #f1f5f9 !important;
                border-radius: 2px !important;
            }
            
            .adapter-tabs-container::-webkit-scrollbar-thumb {
                background: #cbd5e1 !important;
                border-radius: 2px !important;
            }
            
            .adapter-tabs-container::-webkit-scrollbar-thumb:hover {
                background: #94a3b8 !important;
            }
            
            .adapter-subtab {
                background-color: #f9fafb !important;
                border: 1px solid #d1d5db !important;
                padding: 4px 8px !important;
                border-radius: 6px !important;
                color: #374151 !important;
                cursor: pointer !important;
                font-size: 0.75rem !important;
                font-weight: 500 !important;
                text-align: center !important;
                transition: all 0.2s ease !important;
                white-space: nowrap !important;
                flex-shrink: 0 !important;
                min-width: auto !important;
                width: auto !important;
                max-width: 120px !important;
            }
            
            .adapter-subtab--selected {
                background-color: #2563eb !important;
                color: white !important;
                border-color: #1d4ed8 !important;
                box-shadow: 0 1px 3px rgba(37, 99, 235, 0.2) !important;
            }
            
            .adapter-subtab:hover:not(.adapter-subtab--selected) {
                background-color: #f3f4f6 !important;
                border-color: #2563eb !important;
                transform: translateY(-1px) !important;
            }
            
            /* Make ALL tab more compact */
            .adapter-subtab:first-child {
                padding: 6px 10px !important;
                min-width: 50px !important;
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
                
                .adapter-tabs-container {
                    gap: 4px !important;
                    padding: 6px 0 !important;
                }
                
                .adapter-subtab {
                    font-size: 0.7rem !important;
                    padding: 4px 8px !important;
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
                    
                    
                    # html.Div([
                    #     html.H3("OMS Filter", className="text-lg font-semibold mb-4 text-primary"),
                        
                    #     html.Div([
                    #         html.Label("Select OMS:", className="block text-sm font-medium text-gray-700 mb-1"),
                    #         dcc.Dropdown(
                    #             id="value-dropdown",
                    #             clearable=False,
                    #             className="w-full text-sm"
                    #         ),
                    #     ], className="mb-4"),
                    # ], className="p-4 bg-orange-50 rounded-lg border border-orange-200"),

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

                    # New container for Adapters
                    html.Div([
                        html.H3("Adapters", className="text-xl font-semibold mb-2 text-primary"),
                        html.Div(id="adapter-subtabs-container", children=[
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
                            columns=[{"name": col, "id": col} for col in df.columns] if len(df) > 0 else [],
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
                                    'textAlign': 'left'
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
    
    # Safe calculation for other stats
    total_networks = len(df['Network'].dropna().unique()) if 'Network' in df.columns else 0
    total_oms = len(df['OMS'].dropna().unique()) if 'OMS' in df.columns else 0
    unique_identifiers = len(df['Identifier'].dropna().unique()) if 'Identifier' in df.columns else 0
    
    return html.Div([
        html.Div([
            html.H2("Advanced Statistics", className="text-3xl font-bold text-primary mb-6"),
            html.P("Comprehensive statistical analysis of all client connectivity data", 
                   className="text-gray-600 mb-8"),
            
            html.Div([
                html.H4("Statistics Overview", className="text-2xl font-semibold mb-6 text-primary"),
                
                # Top row stats cards
                html.Div([
                    html.Div([
                        html.Div("👥", className="text-3xl mb-3"),
                        html.Div(f"{total_clients}", className="text-3xl font-bold text-primary"),
                        html.Div("Total Clients", className="text-sm text-gray-600"),
                        html.Div("All registered clients", className="text-xs text-gray-500")
                    ], className="bg-white p-6 rounded-lg shadow-md border border-gray-200 text-center"),
                    
                    html.Div([
                        html.Div("🌐", className="text-3xl mb-3"),
                        html.Div(f"{total_networks}", className="text-3xl font-bold text-green-600"),
                        html.Div("Active Networks", className="text-sm text-gray-600"),
                        html.Div("Unique network connections", className="text-xs text-gray-500")
                    ], className="bg-white p-6 rounded-lg shadow-md border border-gray-200 text-center"),
                    
                    html.Div([
                        html.Div("🖥️", className="text-3xl mb-3"),
                        html.Div(f"{total_oms}", className="text-3xl font-bold text-orange-600"),
                        html.Div("OMS Systems", className="text-sm text-gray-600"),
                        html.Div("Order management systems", className="text-xs text-gray-500")
                    ], className="bg-white p-6 rounded-lg shadow-md border border-gray-200 text-center"),
                    
                    html.Div([
                        html.Div("🏷️", className="text-3xl mb-3"),
                        html.Div(f"{unique_identifiers}", className="text-3xl font-bold text-purple-600"),
                        html.Div("Unique Identifiers", className="text-sm text-gray-600"),
                        html.Div("Distinct client IDs", className="text-xs text-gray-500")
                    ], className="bg-white p-6 rounded-lg shadow-md border border-gray-200 text-center"),
                ], className="grid grid-cols-4 gap-6 mb-8"),
                
                # Detailed breakdowns with percentages
                html.Div([
                    html.Div([
                        html.H5("Clients by Network", className="text-xl font-semibold mb-4 text-primary"),
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Span(str(network), className="font-medium text-gray-700 text-lg"),
                                    html.Div([
                                        html.Span(f"{data['count']} clients", className="text-sm text-gray-600 mr-2"),
                                        html.Span(f"({data['percentage']}%)", className="text-sm font-semibold text-primary")
                                    ], className="flex items-center")
                                ], className="flex justify-between items-center"),
                                html.Div([
                                    html.Div(
                                        className="w-full bg-primary h-3 rounded",
                                        style={"width": f"{min(data['percentage'], 100)}%"}
                                    )
                                ], className="w-full bg-gray-200 rounded h-3 mt-2")
                            ], className="p-4 bg-gray-50 rounded-lg mb-3")
                            for network, data in sorted(network_data.items(), key=lambda x: x[1]['count'], reverse=True)
                        ]) if network_data else html.Div("No network data", className="text-gray-500 italic")
                    ], className="bg-white p-6 rounded-lg shadow-md border border-gray-200"),
                    
                    html.Div([
                        html.H5("Service Types Usage", className="text-xl font-semibold mb-4 text-primary"),
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Span(f"{service.replace('_', ' ')}", className="font-medium text-gray-700 text-lg"),
                                    html.Div([
                                        html.Span(f"{data['count']} clients", className="text-sm text-gray-600 mr-2"),
                                        html.Span(f"({data['percentage']}%)", className="text-sm font-semibold text-green-600")
                                    ], className="flex items-center")
                                ], className="flex justify-between items-center mb-2"),
                                html.Div([
                                    html.Div(
                                        className="w-full bg-green-600 h-4 rounded",
                                        style={"width": f"{min(data['percentage'], 100)}%"}
                                    )
                                ], className="w-full bg-gray-200 rounded h-4")
                            ], className="p-4 bg-green-50 border border-green-200 rounded-lg mb-4")
                            for service, data in sorted(active_services.items(), key=lambda x: x[1]['count'], reverse=True)
                        ]) if active_services else html.Div("No active services found", className="text-gray-500 italic")
                    ], className="bg-white p-6 rounded-lg shadow-md border border-gray-200"),
                ], className="grid grid-cols-2 gap-6 mb-6"),
                
                html.Div([
                    html.Div([
                        html.H5("Clients by OMS", className="text-xl font-semibold mb-4 text-primary"),
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Span(str(oms), className="font-medium text-gray-700 text-lg"),
                                    html.Div([
                                        html.Span(f"{data['count']} clients", className="text-sm text-gray-600 mr-2"),
                                        html.Span(f"({data['percentage']}%)", className="text-sm font-semibold text-orange-600")
                                    ], className="flex items-center")
                                ], className="flex justify-between items-center"),
                                html.Div([
                                    html.Div(
                                        className="w-full bg-orange-600 h-3 rounded",
                                        style={"width": f"{min(data['percentage'], 100)}%"}
                                    )
                                ], className="w-full bg-gray-200 rounded h-3 mt-2")
                            ], className="p-4 bg-gray-50 rounded-lg mb-3")
                            for oms, data in sorted(oms_data.items(), key=lambda x: x[1]['count'], reverse=True)
                        ]) if oms_data else html.Div("No OMS data", className="text-gray-500 italic")
                    ], className="bg-white p-6 rounded-lg shadow-md border border-gray-200"),
                ]),
                
            ])
            
        ], className="p-8 max-w-7xl mx-auto")
    ])

# Create account layout function
def create_account_layout():
    """Creates the layout for the parent-child account relationship page."""
    if merged_accounts_df.empty:
        return html.Div([
            html.H2("Account Information", className="text-3xl font-bold text-primary mb-6 p-8"),
            html.Div("No account data available. Please check if account.csv and subaccount.csv exist.", 
                     className="text-red-600 text-center p-8")
        ])

    return html.Div([
        html.Div([
            html.H2("Account & Sub-account Relationships", className="text-3xl font-bold text-primary mb-6"),
            html.P("Search and view parent-child account structures", 
                   className="text-gray-600 mb-8"),
            
            # Search and Filter Section
            html.Div([
                html.H4("Search Filters", className="text-xl font-semibold mb-4 text-primary"),
                html.Div([
                    # Search Inputs
                    dcc.Input(id="parent-account-name-search", type="text", placeholder="Parent Name...", className="px-3 py-2 border border-gray-300 rounded-md"),
                    dcc.Input(id="sub-account-holder-search", type="text", placeholder="Sub-account Name...", className="px-3 py-2 border border-gray-300 rounded-md"),
                    dcc.Input(id="parent-account-id-search", type="number", placeholder="Account...", className="px-3 py-2 border border-gray-300 rounded-md"),
                    dcc.Input(id="sub-account-id-search", type="number", placeholder="Sub Account...", className="px-3 py-2 border border-gray-300 rounded-md"),
                    html.Button("Clear Filters", id="clear-account-filters-btn", n_clicks=0, className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"),
                ], className="grid grid-cols-5 gap-4 items-center"),
            ], className="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-8"),

            # Account Data Table
            html.Div([
                dash_table.DataTable(
                    id="account-table",
                    columns=[{"name": i, "id": i} for i in ['Parent Account Name', 'Account', 'Sub-account Name', 'Sub Account']],
                    data=merged_accounts_df.to_dict("records"),
                    page_size=20,
                    style_table={"overflowX": "auto"},
                    style_cell={'padding': '10px', 'textAlign': 'left', 'border': '1px solid #e5e7eb'},
                    style_header={'backgroundColor': '#f8fafc', 'fontWeight': 'bold'},
                    style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f9fafb'}],
                    sort_action="native",
                )
            ], className="bg-white p-6 rounded-lg shadow-md border border-gray-200"),

        ], className="p-8 max-w-7xl mx-auto")
    ])

# App layout with side navigation and dynamic content
app.layout = html.Div([
    # Side Navigation Bar
    html.Div([
        # Navigation Items
        html.A([
            html.Span("🏠", className="icon"),
            html.Span("Home", className="label"),
            html.Div("Home", className="nav-tooltip")
        ], id="nav-home-link", className="side-nav-item active", href="#"),
        
        html.A([
            html.Span("📊", className="icon"),
            html.Span("Statistics", className="label"),
            html.Div("Statistics", className="nav-tooltip")
        ], id="nav-stats-link", className="side-nav-item", href="#"),
        
        html.A([
            html.Span("👥", className="icon"),
            html.Span("Account", className="label"),
            html.Div("Account", className="nav-tooltip"),
        ], id="nav-account-link", className="side-nav-item", href="#"),
        
    ], className="side-nav"),
    
    # Main Application Container
    html.Div([
        # Header with Title (simplified since we have side nav now)
        html.Div([
            html.Div([
                html.H1("Client Connectivity Dashboard",
                        className="text-2xl font-bold text-primary"),
                html.P("Filter and view client connectivity data by network",
                       className="text-secondary text-sm")
            ], className="flex-1"),
        ], className="bg-white/90 px-6 py-4 border-b border-gray-200"),
       
        # Dynamic content based on navigation
        html.Div(id="page-content"),
        
    ], className="main-app-container"),
    
    # Store to track current page
    dcc.Store(id="current-page", data="home")
], className="min-h-screen bg-gray-100")
# Callback to update adapter sub-tabs based on selected network
@app.callback(
    Output("adapter-subtabs-container", "children"),
    Input("network-tabs", "value"),
    prevent_initial_call=False
)
def update_adapter_subtabs(selected_network):
    if not selected_network or selected_network == 'ALL':
        return html.Div([
            html.Label("Select Adapters:", className="block text-sm font-medium text-gray-700 mb-2"),
            html.Div("Please select a specific network to see available adapters.", 
                   className="text-gray-500 italic text-sm")
        ], className="p-3 bg-gray-50 rounded-lg border border-gray-200")
    
    # Get adapters for the selected network
    adapters = adapter_data.get(selected_network, [])

    if not adapters:
        return html.Div([
            html.Label("Select Adapters:", className="block text-sm font-medium text-gray-700 mb-2"),
            html.Div(f"No adapters found for {selected_network}.", 
                   className="text-gray-500 italic text-sm")
        ], className="p-3 bg-gray-50 rounded-lg border border-gray-200")

    # Create options for the dropdown
    options = [{"label": "ALL", "value": "ALL"}]
    options.extend([{"label": adapter, "value": adapter} for adapter in adapters])

    return dcc.Dropdown(
        id="adapter-dropdown",
        options=options,
        value="ALL",
        clearable=False,
        className="w-full text-sm"
    )

# [Rest of the callbacks remain exactly the same]

# --- New Callbacks for Account Page ---

# Callback to filter the account table
@app.callback(
    Output("account-table", "data"),
    Input("parent-account-name-search", "value"),
    Input("sub-account-holder-search", "value"),
    Input("parent-account-id-search", "value"),
    Input("sub-account-id-search", "value"),
    Input("current-page", "data")
)
def update_account_table(parent_name, sub_holder, parent_id, sub_id, page):
    if page != "account" or merged_accounts_df.empty:
        return dash.no_update

    filtered_df = merged_accounts_df.copy()

    if parent_name:
        filtered_df = filtered_df[filtered_df['Parent Account Name'].str.contains(parent_name, case=False, na=False)]
    if sub_holder:
        filtered_df = filtered_df[filtered_df['Sub-account Name'].str.contains(sub_holder, case=False, na=False)]
    if parent_id:
        filtered_df = filtered_df[filtered_df['Account'] == parent_id]
    if sub_id:
        filtered_df = filtered_df[filtered_df['Sub Account'] == sub_id]

    return filtered_df.to_dict("records")

# Callback to clear account search filters
@app.callback(
    Output("parent-account-name-search", "value"),
    Output("sub-account-holder-search", "value"),
    Output("parent-account-id-search", "value"),
    Output("sub-account-id-search", "value"),
    Input("clear-account-filters-btn", "n_clicks"),
    Input("current-page", "data"),
    prevent_initial_call=True
)
def clear_account_filters(n_clicks, page):
    if n_clicks > 0 and page == "account":
        return "", "", None, None
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update


# Callback to clear search inputs when network tab changes
@app.callback(
    Output("client-search", "value", allow_duplicate=True),
    Output("account-search", "value", allow_duplicate=True),
    Input("network-tabs", "value"),
    prevent_initial_call=True
)
def clear_searches_on_network_change(selected_network):
    """Clears the client and account search fields when a new network is selected."""
    return "", ""



# Callback for side navigation
@app.callback(
    Output("page-content", "children"),
    Output("current-page", "data"),
    Output("nav-home-link", "className"),
    Output("nav-stats-link", "className"),
    Output("nav-account-link", "className"),
    Input("nav-home-link", "n_clicks"),
    Input("nav-stats-link", "n_clicks"),
    Input("nav-account-link", "n_clicks"),
    prevent_initial_call=False
)
def update_page_content(home_clicks, stats_clicks, account_clicks):
    ctx = dash.callback_context
    
    # Default to home
    current_page = "home"
    
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == "nav-stats-link":
            current_page = "stats"
        elif button_id == "nav-account-link":
            current_page = "account"
        else:
            current_page = "home"
    
    # Update navigation styles
    home_class = "side-nav-item"
    stats_class = "side-nav-item"
    account_class = "side-nav-item"
    
    if current_page == "home":
        home_class += " active"
    elif current_page == "stats":
        stats_class += " active"
    elif current_page == "account":
        account_class += " active"
    
    # Return appropriate content
    if current_page == "stats":
        return create_stats_layout(), current_page, home_class, stats_class, account_class
    elif current_page == "account":
        return create_account_layout(), current_page, home_class, stats_class, account_class
    else:
        return create_dashboard_layout(), current_page, home_class, stats_class, account_class

# [Rest of tohe callbacks remain exactly the same - only showing the key adapter callback above]
# Callback 1: Clear search inputs (only when on home page)
@app.callback(
    Output("client-search", "value"),
    Output("account-search", "value"),
    Output("service-type-checklist", "value"),
    Input("clear-search-btn", "n_clicks"),
    Input("clear-service-btn", "n_clicks"),
    Input("current-page", "data"),
    prevent_initial_call=True
)
def clear_search(clear_search_clicks, clear_service_clicks, current_page):
    if current_page != "home":
        return dash.no_update, dash.no_update, dash.no_update
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == "clear-search-btn":
        return "", "", dash.no_update
    elif button_id == "clear-service-btn":
        return dash.no_update, dash.no_update, []
    
    return dash.no_update, dash.no_update, dash.no_update

# Callback 2: Populate OMS dropdown based on current filtered data (only when on home page)
@app.callback(
    Output("value-dropdown", "options"),
    Output("value-dropdown", "value"),
    Input("network-tabs", "value"),
    Input("client-search", "value"),
    Input("account-search", "value"),
    Input("service-type-checklist", "value"),
    Input("current-page", "data"),
    prevent_initial_call=True
)
def update_oms_dropdown(selected_network, client_search, account_search, service_types_selected, current_page):
    if current_page != "home":
        return dash.no_update, dash.no_update
    
    if len(df) == 0:
        return [], ""
        
    # Start with all data
    filtered_df = df.copy()
    
    # Apply search filters first (global search regardless of network/OMS)
    if client_search and client_search.strip():
        filtered_df = filtered_df[filtered_df['Client Name'].str.contains(client_search.strip(), case=False, na=False)]
    
    if account_search is not None and str(account_search).strip():
        search_term = str(account_search).strip()
        filtered_df = filtered_df[filtered_df['Account'].astype(str).str.contains(search_term, case=False, na=False)]
    
    # Apply service type filter (OR logic - show clients that have ANY of the selected services)
    if service_types_selected:
        service_filters = []
        for service_type in service_types_selected:
            column_name = service_type_mapping.get(service_type, service_type)
            if column_name in filtered_df.columns:
                # Create a filter for this service type
                service_filter = (filtered_df[column_name].notna()) & (filtered_df[column_name] != '')
                service_filters.append(service_filter)
        
        # Combine filters with OR logic
        if service_filters:
            combined_filter = service_filters[0]
            for filter_obj in service_filters[1:]:
                combined_filter = combined_filter | filter_obj
            filtered_df = filtered_df[combined_filter]
    
    # Then apply network filter for the dropdown values
    if selected_network and selected_network != 'ALL':
        network_filtered_df = filtered_df[filtered_df['Network'] == selected_network]
    else:
        network_filtered_df = filtered_df
    
    # Get unique OMS values
    unique_oms = network_filtered_df['OMS'].dropna().unique()
    
    # Add "ALL" option first, then individual OMS systems
    options = [{"label": "ALL", "value": "ALL"}]
    options.extend([{"label": str(val), "value": str(val)} for val in unique_oms if str(val).strip()])
    
    return options, "ALL"

# Callback 3: Filter table and update summary based on all selections and searches (only when on home page)
@app.callback(
    Output("data-table", "data"),
    Output("summary-output", "children"),
    Input("value-dropdown", "value"),
    Input("network-tabs", "value"),
    Input("client-search", "value"),
    Input("account-search", "value"),
    Input("service-type-checklist", "value"),
    Input("current-page", "data"),
    prevent_initial_call=True
)
def update_table_and_summary(selected_oms, selected_network, client_search, account_search, service_types_selected, current_page):
    if current_page != "home":
        return dash.no_update, dash.no_update
    
    if len(df) == 0:
        return [], html.Div("No data available. Please check if client.json exists.", className="text-red-600")
    
    # Start with all data
    filtered_df = df.copy()
    filter_descriptions = []
    
    # Apply global search filters first (regardless of network/OMS)
    if client_search and client_search.strip():
        filtered_df = filtered_df[filtered_df['Client Name'].str.contains(client_search.strip(), case=False, na=False)]
        filter_descriptions.append(f"Client Name contains '{client_search.strip()}'")
    
    if account_search is not None and str(account_search).strip():
        search_term = str(account_search).strip()
        filtered_df = filtered_df[filtered_df['Account'].astype(str).str.contains(search_term, case=False, na=False)]
        filter_descriptions.append(f"Account contains '{search_term}'")
    
    # Apply service type filter (OR logic - show clients that have ANY of the selected services)
    if service_types_selected:
        service_filters = []
        for service_type in service_types_selected:
            column_name = service_type_mapping.get(service_type, service_type)
            if column_name in filtered_df.columns:
                # Create a filter for this service type
                service_filter = (filtered_df[column_name].notna()) & (filtered_df[column_name] != '')
                service_filters.append(service_filter)
        
        # Combine filters with OR logic
        if service_filters:
            combined_filter = service_filters[0]
            for filter_obj in service_filters[1:]:
                combined_filter = combined_filter | filter_obj
            filtered_df = filtered_df[combined_filter]
            service_labels = ", ".join(service_types_selected)
            filter_descriptions.append(f"Service Types: {service_labels}")
    
    # Apply network filter from tabs
    if selected_network and selected_network != 'ALL':
        filtered_df = filtered_df[filtered_df['Network'] == selected_network]
        filter_descriptions.append(f"Network = {selected_network}")
    elif selected_network == 'ALL':
        filter_descriptions.append("Network = ALL (showing all networks)")
    
    # Apply OMS filter
    if selected_oms and selected_oms != "ALL":
        filtered_df = filtered_df[filtered_df['OMS'] == selected_oms]
        filter_descriptions.append(f"OMS = {selected_oms}")
    elif selected_oms == "ALL":
        filter_descriptions.append("OMS = ALL (showing all OMS systems)")
    
    # Calculate statistics for both total and filtered data
    total_clients = len(df)
    filtered_clients = len(filtered_df)
    
    # Create summary layout focusing on current view and filters only
    summary = html.Div(
        [
            html.Div([
                html.Span("Showing "),
                html.Span(f"{filtered_clients}", className="font-bold text-primary text-lg"),
                html.Span(f" of {total_clients} total clients")
            ], className="mb-3 font-medium"),
            html.Div([
                html.P("Active Filters:", className="font-medium text-gray-700 mb-1"),
                html.Ul([html.Li(f, className="ml-4 list-disc") for f in filter_descriptions] if filter_descriptions else html.Li("None"), className="text-xs text-gray-600")
            ])
        ])
    
    return filtered_df.to_dict("records"), summary

# Callback to open and populate the modal
@app.callback(
    Output("row-data-modal", "style"),
    Output("row-data-modal", "className"),
    Output("modal-content-container", "children"),
    Input("data-table", "active_cell"),
    Input("modal-close-button", "n_clicks"),
    Input("modal-close-x-button", "n_clicks"),
    State("data-table", "data"),
    State("data-table", "page_current"),
    State("data-table", "page_size"),
    prevent_initial_call=True
)
def display_row_data_in_modal(active_cell, close_clicks_main, close_clicks_x, table_data, page_current, page_size):
    ctx = dash.callback_context
    if not ctx.triggered: return dash.no_update, dash.no_update, dash.no_update
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Close modal if close button is clicked
    if triggered_id in ["modal-close-button", "modal-close-x-button"]:
        return {'display': 'none'}, "modal-overlay", []

    # Open modal if a cell is clicked
    if triggered_id == "data-table" and active_cell:
        # Calculate the absolute index based on the current page
        # This fixes the issue of selecting the wrong row on pages > 1
        page_current = page_current or 0 # page_current can be None on first load
        page_size = page_size or 15 # Default page size if not set
        absolute_row_index = (page_current * page_size) + active_cell['row']
        selected_row = table_data[absolute_row_index]

        # --- 1. Prepare the text details for the left column ---
        details_list = html.Ul(
            [html.Li([
                html.Span(f"{key}:", className="font-semibold text-gray-600 mr-4"),
                html.Span(value, className="text-gray-800")
            ], className="modal-list-item") for key, value in selected_row.items()],
            className="list-none p-0"
        )

        # --- 2. Prepare the graph elements for the right column ---
        service_cols = ['High Touch', 'Low Touch', 'PT', 'ETF', 'IS', 'Japan', 'CB', 'Options', 'Direct Tokyo']
        client_name = selected_row.get('Client Name', 'Client')
        
        # Define nodes
        nodes = [{'data': {'id': 'client', 'label': client_name}}]
        edges = []

        for service in service_cols:
            # Check if the service is active ("Yes" or any non-empty string)
            if selected_row.get(service) and str(selected_row.get(service)).strip():
                service_id = service.lower().replace(' ', '-')
                nodes.append({'data': {'id': service_id, 'label': service}})
                edges.append({'data': {'source': 'client', 'target': service_id}})
        
        graph_elements = nodes + edges

        # Define stylesheet for the graph
        stylesheet = [
            {'selector': 'node', 'style': {
                'label': 'data(label)', 
                'background-color': '#64748b', 
                'color': 'white', 
                'text-halign': 'center', 
                'text-valign': 'center', 
                'width': '90px', 
                'height': '40px', 
                'shape': 'round-rectangle',
                'text-wrap': 'wrap',
                'text-max-width': '80px'
            }},
            {'selector': '#client', 'style': {
                'background-color': '#2563eb', 
                'width': '120px', 
                'height': '50px',
                'text-wrap': 'wrap',
                'text-max-width': '110px'
            }},
            {'selector': 'edge', 'style': {'width': 2, 'line-color': '#cbd5e1', 'target-arrow-color': '#cbd5e1', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier'}}
        ]

        # --- 3. Combine details and graph into a two-column layout ---
        modal_body = html.Div(
            [
                # Left Column: Details
                html.Div(details_list, className="modal-details-column"),
                
                # Right Column: Graph
                html.Div(
                    cyto.Cytoscape(
                        id='service-graph',
                        elements=graph_elements,
                        stylesheet=stylesheet,
                        layout={'name': 'breadthfirst', 'directed': True, 'spacingFactor': 1.5},
                        style={'width': '100%', 'height': '100%'}
                    ),
                    className="modal-graph-column"
                )
            ],
            className="modal-body-container"
        )

        # Use style to show the modal
        return {'display': 'flex'}, "modal-overlay modal-open", modal_body

    # Default case: do not change anything
    return dash.no_update, dash.no_update, dash.no_update


if __name__ == "__main__":
    app.run(debug=True)
