import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
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

# Load the data
df = load_client_data()

# Initialize Dash app
app = dash.Dash(__name__)

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
                padding: 12px 20px !important;
                margin-right: 5px !important;
                margin-bottom: -1px !important;
                border-top-left-radius: 8px !important;
                border-top-right-radius: 8px !important;
                color: #374151 !important;
                cursor: pointer !important;
                font-size: 0.9rem !important;
                font-weight: 500 !important;
                min-width: 100px !important;
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

# Define predefined networks for tabs (ensuring ALL is first)
predefined_networks = ['ALL', 'BLOOMBERG', 'FIDDESSA', 'ITG', 'TRADEWARE', 'TRADEWEB', 'NYFIX']

# Get unique networks for tabs - use predefined list with ALL included
networks = predefined_networks

# App layout with sticky header and sidebar
app.layout = html.Div([
    # Sticky Header
    html.Div([
        html.Div([
            html.H1("Client Connectivity Dashboard",
                    className="text-2xl font-bold text-primary"),
            html.P("Filter and view client connectivity data by network",
                   className="text-secondary text-sm")
        ], className="container mx-auto px-4 py-4")
    ], className="sticky-header bg-white/90"),
   
    # Main container with sidebar and content
    html.Div([
        # Left Sidebar
        html.Div([
            html.Div([
                # Search Section
                html.Div([
                    html.H3("🔍 Global Search", className="text-lg font-semibold mb-4 text-primary flex items-center"),
                    
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
                            type="text",
                            placeholder="Enter partial account...",
                            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                        ),
                    ], className="mb-4"),
                    
                    html.Button(
                        "Clear Search",
                        id="clear-search-btn",
                        n_clicks=0,
                        className="w-full px-4 py-2 text-sm bg-gray-500 hover:bg-gray-600 text-white rounded-md transition-colors"
                    ),
                ], className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200"),
                

                
                # Additional Filters Section
                html.Div([
                    html.H3("⚙️ OMS Filter", className="text-lg font-semibold mb-4 text-primary"),
                    
                    html.Div([
                        html.Label("Select OMS:", className="block text-sm font-medium text-gray-700 mb-1"),
                        dcc.Dropdown(
                            id="value-dropdown",
                            clearable=False,
                            className="w-full text-sm"
                        ),
                    ], className="mb-4"),
                ], className="p-4 bg-orange-50 rounded-lg border border-orange-200"),
                
            ], className="p-4")
        ], className="sidebar bg-white shadow-lg w-80 min-w-80"),
        
        # Main Content Area
        html.Div([
            # Network Tabs Section
            html.Div([
                html.H3("🌐 Network Filter", className="text-xl font-semibold mb-4 text-primary"),
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
            ], className="mb-6 p-4 bg-green-50 rounded-lg border border-green-200"),
            # Summary Section
            html.Div([
                html.H3("📊 Summary & Filter Status", className="text-xl font-semibold mb-3 text-primary"),
                html.Div(id="summary-output", className="text-sm text-gray-700")
            ], className="mb-6 p-4 bg-purple-50 rounded-lg border border-purple-200"),
            
            # Data table
            html.Div([
                html.H3("📋 Client Data", className="text-xl font-semibold mb-4 text-primary"),
                html.Div(id="table-container", children=[
                    dash_table.DataTable(
                        id="data-table",
                        columns=[{"name": col, "id": col} for col in df.columns] if len(df) > 0 else [],
                        data=df.to_dict("records") if len(df) > 0 else [],
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
                ])
            ], className="bg-white p-6 rounded-lg shadow-md"),
        ], className="main-content flex-1 p-6"),
        
    ], className="flex min-h-screen"),
], className="min-h-screen bg-gray-100")

# Callback 1: Clear search inputs
@app.callback(
    Output("client-search", "value"),
    Output("account-search", "value"),
    Input("clear-search-btn", "n_clicks")
)
def clear_search(n_clicks):
    if n_clicks > 0:
        return "", ""
    return dash.no_update, dash.no_update

# Callback 2: Populate OMS dropdown based on current filtered data
@app.callback(
    Output("value-dropdown", "options"),
    Output("value-dropdown", "value"),
    Input("network-tabs", "value"),
    Input("client-search", "value"),
    Input("account-search", "value")
)
def update_oms_dropdown(selected_network, client_search, account_search):
    if len(df) == 0:
        return [], ""
        
    # Start with all data
    filtered_df = df.copy()
    
    # Apply search filters first (global search regardless of network/OMS)
    if client_search and client_search.strip():
        filtered_df = filtered_df[filtered_df['Client Name'].str.contains(client_search.strip(), case=False, na=False)]
    
    if account_search and account_search.strip():
        filtered_df = filtered_df[filtered_df['Account'].str.contains(account_search.strip(), case=False, na=False)]
    
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

# Callback 3: Filter table and update summary based on all selections and searches
@app.callback(
    Output("data-table", "data"),
    Output("summary-output", "children"),
    Input("value-dropdown", "value"),
    Input("network-tabs", "value"),
    Input("client-search", "value"),
    Input("account-search", "value")
)
def update_table_and_summary(selected_oms, selected_network, client_search, account_search):
    if len(df) == 0:
        return [], html.Div("No data available. Please check if client.json exists.", className="text-red-600")
    
    # Start with all data
    filtered_df = df.copy()
    filter_descriptions = []
    
    # Apply global search filters first (regardless of network/OMS)
    if client_search and client_search.strip():
        filtered_df = filtered_df[filtered_df['Client Name'].str.contains(client_search.strip(), case=False, na=False)]
        filter_descriptions.append(f"Client Name contains '{client_search.strip()}'")
    
    if account_search and account_search.strip():
        filtered_df = filtered_df[filtered_df['Account'].str.contains(account_search.strip(), case=False, na=False)]
        filter_descriptions.append(f"Account contains '{account_search.strip()}'")
    
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
    
    # Create summary text
    if filter_descriptions:
        filter_text = " and ".join(filter_descriptions)
        summary = html.Div([
            html.Div([
                html.Span("Showing "),
                html.Span(f"{len(filtered_df)}", className="font-bold text-primary text-lg"),
                html.Span(f" of {len(df)} total rows")
            ], className="mb-2 font-medium"),
            html.Div([
                html.Span("Filters: ", className="font-medium"),
                html.Span(filter_text, className="text-gray-600")
            ], className="text-xs")
        ])
    else:
        summary = html.Div([
            html.Span("Showing all "),
            html.Span(f"{len(filtered_df)}", className="font-bold text-primary text-lg"),
            html.Span(" rows")
        ], className="font-medium")
    
    return filtered_df.to_dict("records"), summary

if __name__ == "__main__":
    app.run(debug=True)