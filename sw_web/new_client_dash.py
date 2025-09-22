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
app = dash.Dash(__name__, suppress_callback_exceptions=True)

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

predefined_networks = ['ALL', 'BLOOMBERG', 'FIDDESSA', 'ITG', 'TRADEWARE', 'TRADEWEB', 'NYFIX']

networks = predefined_networks

def create_dashboard_layout():
    return html.Div([
        html.Div([
            html.Div([
                html.Div([
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
            
            html.Div([
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
                ], className="mb-4 p-4 bg-green-50 rounded-lg border border-green-200"),
                # Summary Section
                #html.Div([
                    #html.H3("🔍 Current View", className="text-xl font-semibold mb-3 text-primary"),
                    html.Div(id="summary-output", className="text-sm text-gray-700 mb-4 "),
                #], className="mb-6 p-4 bg-purple-50 rounded-lg border border-purple-200"),
                
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
    ])

# Function to create the Stats page layout
def create_stats_layout():
    if len(df) == 0:
        return html.Div([
            html.Div([
                html.H2("📈 Advanced Statistics", className="text-3xl font-bold text-primary mb-6"),
                html.Div("No data available. Please check if client.json exists.", className="text-red-600 text-center p-8"),
            ], className="p-8")
        ])
    
    # Calculate comprehensive statistics for the stats page
    total_clients = len(df)
    total_networks = len(df['Network'].dropna().unique())
    total_oms = len(df['OMS'].dropna().unique())
    
    # Group by Network
    network_counts = df.groupby('Network').size().to_dict()
    print(network_counts)
    
    # Group by OMS
    oms_counts = df.groupby('OMS').size().to_dict()
    print(oms_counts)
    
    #####################
    # Calculate service type statistics
    service_columns = ['High Touch', 'Low Touch', 'PT', 'ETF', 'IS', 'Japan', 'CB', 'Options', 'Direct Tokyo']
    active_services = {}
    for col in service_columns:
        if col in df.columns:
            active_count = len(df[df[col].notna() & (df[col] != '')])
            if active_count > 0:
                active_services[col] = active_count
    
    unique_identifiers = len(df['Identifier'].dropna().unique())
    
    return html.Div([
        html.Div([
            html.H2("📈 Advanced Statistics", className="text-3xl font-bold text-primary mb-6"),
            html.P("Comprehensive statistical analysis of all client connectivity data", 
                   className="text-gray-600 mb-8"),
            
            # Statistics Grid - moved from dashboard
            html.Div([
                html.H4("📊 Statistics Overview", className="text-2xl font-semibold mb-6 text-primary"),
                
                # Top row stats cards
                html.Div([
                    # Total Clients Card
                    html.Div([
                        html.Div("👥", className="text-3xl mb-3"),
                        html.Div(f"{total_clients}", className="text-3xl font-bold text-primary"),
                        html.Div("Total Clients", className="text-sm text-gray-600"),
                        html.Div("All registered clients", className="text-xs text-gray-500")
                    ], className="bg-white p-6 rounded-lg shadow-md border border-gray-200 text-center"),
                    
                    # Networks Card
                    html.Div([
                        html.Div("🌐", className="text-3xl mb-3"),
                        html.Div(f"{total_networks}", className="text-3xl font-bold text-green-600"),
                        html.Div("Active Networks", className="text-sm text-gray-600"),
                        html.Div("Unique network connections", className="text-xs text-gray-500")
                    ], className="bg-white p-6 rounded-lg shadow-md border border-gray-200 text-center"),
                    
                    # OMS Systems Card
                    html.Div([
                        html.Div("🖥️⚙️", className="text-3xl mb-3"),
                        html.Div(f"{total_oms}", className="text-3xl font-bold text-orange-600"),
                        html.Div("OMS Systems", className="text-sm text-gray-600"),
                        html.Div("Order management systems", className="text-xs text-gray-500")
                    ], className="bg-white p-6 rounded-lg shadow-md border border-gray-200 text-center"),
                    
                    # Unique Identifiers Card
                    html.Div([
                        # html.Div("🏷️", className="text-3xl mb-3"),
                        html.Div("🪪", className="text-3xl mb-3"),
                        html.Div(f"{unique_identifiers}", className="text-3xl font-bold text-purple-600"),
                        html.Div("Unique Identifiers", className="text-sm text-gray-600"),
                        html.Div("Distinct client IDs", className="text-xs text-gray-500")
                    ], className="bg-white p-6 rounded-lg shadow-md border border-gray-200 text-center"),
                ], className="grid grid-cols-4 gap-6 mb-8"),
                
                # Detailed breakdowns
                html.Div([
                    # Clients by Network
                    html.Div([
                        html.H5("📡 Clients by Network", className="text-xl font-semibold mb-4 text-primary"),
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Span(network, className="font-medium text-gray-700 text-lg"),
                                    html.Span(f"{count} clients", className="text-sm text-gray-600")
                                ], className="flex justify-between items-center"),
                                html.Div([
                                    html.Div(
                                        className=f"w-full bg-primary h-3 rounded",
                                        style={"width": f"{(count/max(network_counts.values()))*100}%"}
                                    )
                                ], className="w-full bg-gray-200 rounded h-3 mt-2")
                            ], className="p-4 bg-gray-50 rounded-lg mb-3")
                            for network, count in sorted(network_counts.items(), key=lambda x: x[1], reverse=True)
                        ]) if network_counts else html.Div("No network data", className="text-gray-500 italic")
                    ], className="bg-white p-6 rounded-lg shadow-md border border-gray-200"),
                    
                    # Clients by OMS
                    html.Div([
                        html.H5("🖥️⚙️  Clients by OMS", className="text-xl font-semibold mb-4 text-primary"),
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Span(str(oms), className="font-medium text-gray-700 text-lg"),
                                    html.Span(f"{count} clients", className="text-sm text-gray-600")
                                ], className="flex justify-between items-center"),
                                html.Div([
                                    html.Div(
                                        className=f"w-full bg-orange-600 h-3 rounded",
                                        style={"width": f"{(count/max(oms_counts.values()))*100}%"}
                                    )
                                ], className="w-full bg-gray-200 rounded h-3 mt-2")
                            ], className="p-4 bg-gray-50 rounded-lg mb-3")
                            for oms, count in sorted(oms_counts.items(), key=lambda x: x[1], reverse=True)
                        ]) if oms_counts else html.Div("No OMS data", className="text-gray-500 italic")
                    ], className="bg-white p-6 rounded-lg shadow-md border border-gray-200"),
                ], className="grid grid-cols-2 gap-6 mb-6"),
                
                # Service Types Usage
                html.Div([
                    html.H5("👨‍💼 ¥$🛠️ ⚙️🤖🦾 Clients by Service Types", className="text-xl font-semibold mb-4 text-primary"),
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Span(f"{service.replace('_', ' ')}", className="font-medium text-gray-700 text-lg"),
                                html.Span(f"{count} clients", className="text-sm text-gray-600")
                            ], className="flex justify-between items-center mb-2"),
                            html.Div([
                                html.Div(
                                    className=f"w-full bg-green-600 h-4 rounded",
                                    style={"width": f"{(count/total_clients)*100}%"}
                                )
                            ], className="w-full bg-gray-200 rounded h-4")
                        ], className="p-4 bg-green-50 border border-green-200 rounded-lg mb-4")
                        for service, count in sorted(active_services.items(), key=lambda x: x[1], reverse=True)
                    ]) if active_services else html.Div("No active services found", className="text-gray-500 italic")
                ], className="bg-white p-6 rounded-lg shadow-md border border-gray-200"),
                
            ])
            
        ], className="p-8 max-w-7xl mx-auto")
    ])

# App layout with navigation and dynamic content
app.layout = html.Div([
    # Sticky Header with Navigation
    html.Div([
        html.Div([
            # Left side - Title
            html.Div([
                html.H1("Client Connectivity Dashboard",
                        className="text-2xl font-bold text-primary"),
                html.P("Filter and view client connectivity data by network",
                       className="text-secondary text-sm")
            ], className="flex-1"),
            
            # Right side - Navigation buttons
            html.Div([
                html.Button(
                    [html.Span("📋"), html.Span(" Client Data", className="ml-2")],
                    id="nav-dashboard-btn",
                    n_clicks=0,
                    className="nav-btn nav-btn-active px-6 py-3 mx-2 bg-white text-gray-700 rounded-lg font-medium flex items-center"
                ),
                html.Button(
                    [html.Span("📊"), html.Span(" Stats", className="ml-2")],
                    id="nav-stats-btn",
                    n_clicks=0,
                    className="nav-btn px-6 py-3 mx-2 bg-white text-gray-700 rounded-lg font-medium flex items-center"
                ),
            ], className="flex items-center"),
            
        ], className="container mx-auto px-4 py-4 flex items-center justify-between")
    ], className="sticky-header bg-white/90"),
   
    # Dynamic content based on navigation
    html.Div(id="page-content"),
    
    # Store to track current page
    dcc.Store(id="current-page", data="dashboard")
], className="min-h-screen bg-gray-100")

# Callback for navigation between pages
@app.callback(
    Output("page-content", "children"),
    Output("current-page", "data"),
    Output("nav-dashboard-btn", "className"),
    Output("nav-stats-btn", "className"),
    Input("nav-dashboard-btn", "n_clicks"),
    Input("nav-stats-btn", "n_clicks"),
    prevent_initial_call=False
)
def update_page_content(dashboard_clicks, stats_clicks):
    ctx = dash.callback_context
    
    # Default to dashboard
    current_page = "dashboard"
    
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == "nav-stats-btn":
            current_page = "stats"
        else:
            current_page = "dashboard"
    
    # Update button styles
    dashboard_btn_class = "nav-btn px-6 py-3 mx-2 bg-white text-gray-700 rounded-lg font-medium flex items-center"
    stats_btn_class = "nav-btn px-6 py-3 mx-2 bg-white text-gray-700 rounded-lg font-medium flex items-center"
    
    if current_page == "dashboard":
        dashboard_btn_class += " nav-btn-active"
    else:
        stats_btn_class += " nav-btn-active"
    
    # Return appropriate content
    if current_page == "stats":
        return create_stats_layout(), current_page, dashboard_btn_class, stats_btn_class
    else:
        return create_dashboard_layout(), current_page, dashboard_btn_class, stats_btn_class

# Callback 1: Clear search inputs (only when on dashboard)
@app.callback(
    Output("client-search", "value"),
    Output("account-search", "value"),
    Input("clear-search-btn", "n_clicks"),
    Input("current-page", "data"),
    prevent_initial_call=True
)
def clear_search(n_clicks, current_page):
    if current_page != "dashboard":
        return dash.no_update, dash.no_update
    if n_clicks > 0:
        return "", ""
    return dash.no_update, dash.no_update

# Callback 2: Populate OMS dropdown based on current filtered data (only when on dashboard)
@app.callback(
    Output("value-dropdown", "options"),
    Output("value-dropdown", "value"),
    Input("network-tabs", "value"),
    Input("client-search", "value"),
    Input("account-search", "value"),
    Input("current-page", "data"),
    prevent_initial_call=True
)
def update_oms_dropdown(selected_network, client_search, account_search, current_page):
    if current_page != "dashboard":
        return dash.no_update, dash.no_update
    
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

# Callback 3: Filter table and update summary based on all selections and searches (only when on dashboard)
@app.callback(
    Output("data-table", "data"),
    Output("summary-output", "children"),
    Input("value-dropdown", "value"),
    Input("network-tabs", "value"),
    Input("client-search", "value"),
    Input("account-search", "value"),
    Input("current-page", "data"),
    prevent_initial_call=True
)
def update_table_and_summary(selected_oms, selected_network, client_search, account_search, current_page):
    if current_page != "dashboard":
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
    
    # Calculate statistics for both total and filtered data
    total_clients = len(df)
    filtered_clients = len(filtered_df)
    
    # Create summary layout focusing on current view and filters only
    summary = html.Div([
        # Filter status
        html.Div([
            html.H4("🔍 Current View", className="text-lg font-semibold mb-2 text-primary"),
            html.Div([
                html.Span("Showing "),
                html.Span(f"{filtered_clients}", className="font-bold text-primary text-xl"),
                html.Span(f" of {total_clients} total clients")
            ], className="mb-2 font-medium"),
            html.Div([
                html.Span("Active Filters: ", className="font-medium text-gray-700"),
                html.Span(" | ".join(filter_descriptions) if filter_descriptions else "None", className="text-gray-600 text-sm")
            ], className="text-xs mb-4")
        ], className="p-4 bg-blue-50 rounded-lg border border-blue-200"),
    ])
    
    return filtered_df.to_dict("records"), summary

if __name__ == "__main__":
    app.run(debug=True)
