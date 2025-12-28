# app.py
import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import os
from datetime import datetime
import urllib.parse
import numpy as np

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Account Mapping Dashboard"

# Add Tailwind CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <!-- Tailwind CSS -->
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            /* Custom scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            ::-webkit-scrollbar-track {
                background: #f1f1f1;
                border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
            
            /* Table styling */
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table {
                border-collapse: separate;
                border-spacing: 0;
            }
            
            /* Tab styling */
            .tab {
                transition: all 0.3s ease;
            }
            
            .tab:hover {
                transform: translateY(-2px);
            }
            
            /* Card shadows */
            .card-shadow {
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }
            
            .card-shadow-hover:hover {
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            }
            
            /* Animation */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .fade-in {
                animation: fadeIn 0.5s ease-out;
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

# List of networks
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

# Function to load all CSV files
def load_all_network_files():
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
                print(f"✅ Loaded {filename}: {len(df)} rows")
                
            except Exception as e:
                print(f"❌ Error loading {filename}: {str(e)}")
        else:
            print(f"⚠️  File {filename} not found")
    
    # Create combined dataframe for 'total' tab
    if all_data:
        total_df = pd.concat(all_data.values(), ignore_index=True)
        all_data['total'] = total_df
        print(f"📊 Total combined rows: {len(total_df)}")
    
    return all_data

# Load data at startup
print(f"🔄 Loading data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
network_data = load_all_network_files()

# Create network statistics
network_stats = {}
if network_data:
    for network_key in NETWORKS.keys():
        if network_key in network_data:
            network_stats[network_key] = len(network_data[network_key])

# Create tab labels with counts
def create_tab_label(network_key):
    """Create tab label with count badge"""
    network_name = NETWORKS[network_key]
    count = network_stats.get(network_key, 0)
    return f"{network_name} ({count})"

# App layout with Tailwind CSS
app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.Div([
                html.I(className="fas fa-network-wired text-3xl text-blue-500 mr-3"),
                html.Div([
                    html.H1("Account Mapping Dashboard", className="text-2xl font-bold text-gray-800"),
                    html.P("Manage and search account mappings across trading networks", 
                          className="text-gray-600")
                ])
            ], className="flex items-center"),
            
            # Stats Cards
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-database text-blue-500 text-lg"),
                        html.Div([
                            html.P("Total Records", className="text-xs text-gray-500"),
                            html.P(f"{network_stats.get('total', 0):,}", 
                                  className="text-xl font-bold text-gray-800")
                        ], className="ml-3")
                    ], className="flex items-center")
                ], className="bg-white p-4 rounded-lg card-shadow"),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-sitemap text-green-500 text-lg"),
                        html.Div([
                            html.P("Networks", className="text-xs text-gray-500"),
                            html.P("7", className="text-xl font-bold text-gray-800")
                        ], className="ml-3")
                    ], className="flex items-center")
                ], className="bg-white p-4 rounded-lg card-shadow"),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-clock text-purple-500 text-lg"),
                        html.Div([
                            html.P("Last Updated", className="text-xs text-gray-500"),
                            html.P(datetime.now().strftime("%H:%M"), 
                                  className="text-xl font-bold text-gray-800")
                        ], className="ml-3")
                    ], className="flex items-center")
                ], className="bg-white p-4 rounded-lg card-shadow"),
            ], className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4")
        ], className="container mx-auto px-4")
    ], className="bg-gradient-to-r from-blue-50 to-indigo-50 py-6 border-b border-gray-200"),
    
    # Main Content
    html.Div([
        html.Div([
            # Left Column - Search and Filters
            html.Div([
                # Search Card
                html.Div([
                    html.Div([
                        html.H3("🔍 Search Accounts", className="text-lg font-semibold text-gray-800 mb-4"),
                        
                        html.Div([
                            html.Div([
                                html.Label("Search Term", className="block text-sm font-medium text-gray-700 mb-1"),
                                dcc.Input(
                                    id='search-input',
                                    type='text',
                                    placeholder='Type ACRONAME or ACCOUNT_NUMBER...',
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200"
                                ),
                            ], className="mb-4"),
                            
                            html.Div([
                                html.Label("Network", className="block text-sm font-medium text-gray-700 mb-1"),
                                dcc.Dropdown(
                                    id='network-filter',
                                    options=[{'label': NETWORKS[net], 'value': net} for net in NETWORKS.keys()],
                                    value='total',
                                    clearable=False,
                                    className="border border-gray-300 rounded-lg"
                                ),
                            ], className="mb-6"),
                            
                            html.Div([
                                html.Button(
                                    'Clear Filters',
                                    id='clear-button',
                                    n_clicks=0,
                                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition duration-200 font-medium mr-2"
                                ),
                                html.Button(
                                    'Export Data',
                                    id='export-button',
                                    n_clicks=0,
                                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition duration-200 font-medium"
                                ),
                            ], className="flex")
                        ])
                    ], className="p-6")
                ], className="bg-white rounded-xl card-shadow mb-6 fade-in"),
                
                # Network Stats Card
                html.Div([
                    html.Div([
                        html.H3("📊 Network Statistics", className="text-lg font-semibold text-gray-800 mb-4"),
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.Span(NETWORKS[net], className="font-medium text-gray-700"),
                                        html.Span(f"{network_stats.get(net, 0)}", 
                                                 className="ml-auto bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full")
                                    ], className="flex items-center justify-between mb-2"),
                                    html.Div([
                                        html.Div([
                                            html.Div(
                                                className="h-2 bg-blue-500 rounded-full",
                                                style={'width': f'{min(100, (network_stats.get(net, 0) / max(1, network_stats.get("total", 1))) * 100)}%'}
                                            )
                                        ], className="w-full bg-gray-200 rounded-full h-2")
                                    ])
                                ], className="mb-3") for net in NETWORKS.keys() if net != 'total'
                            ], id='network-stats')
                        ])
                    ], className="p-6")
                ], className="bg-white rounded-xl card-shadow fade-in"),
            ], className="lg:w-1/4"),
            
            # Right Column - Data Table
            html.Div([
                # Tabs
                html.Div([
                    dcc.Tabs(
                        id='tabs',
                        value='total',
                        children=[
                            dcc.Tab(
                                label=create_tab_label(network),
                                value=network,
                                className="tab px-4 py-3 mr-2 rounded-t-lg border border-b-0 border-gray-300 bg-white text-gray-700",
                                selected_className="tab px-4 py-3 mr-2 rounded-t-lg border border-b-0 border-blue-500 bg-blue-50 text-blue-700 font-semibold"
                            ) for network in NETWORKS.keys()
                        ],
                        className="flex border-b border-gray-300"
                    )
                ], className="mb-6"),
                
                # Results Card
                html.Div([
                    html.Div([
                        html.Div([
                            html.H3(id='results-title', className="text-xl font-bold text-gray-800"),
                            html.P(id='results-subtitle', className="text-gray-600 mt-1"),
                        ], className="mb-4"),
                        
                        # Stats Bar
                        html.Div(id='stats-bar', className="mb-6"),
                        
                        # Data Table
                        html.Div([
                            dash_table.DataTable(
                                id='data-table',
                                columns=[
                                    {"name": i, "id": i} 
                                    for i in ['NETWORK', 'ACRONAME', 'ACCOUNT_NUMBER']
                                ],
                                page_size=10,
                                page_current=0,
                                page_action='native',
                                sort_action='native',
                                sort_mode='multi',
                                filter_action='native',
                                style_table={
                                    'overflowX': 'auto',
                                    'borderRadius': '8px',
                                    'border': '1px solid #e5e7eb'
                                },
                                style_header={
                                    'backgroundColor': '#3b82f6',
                                    'color': 'white',
                                    'fontWeight': 'bold',
                                    'fontFamily': 'system-ui, -apple-system, sans-serif',
                                    'padding': '12px',
                                    'border': 'none'
                                },
                                style_cell={
                                    'textAlign': 'left',
                                    'padding': '12px',
                                    'fontFamily': 'system-ui, -apple-system, sans-serif',
                                    'borderBottom': '1px solid #e5e7eb',
                                    'borderRight': 'none',
                                    'borderLeft': 'none'
                                },
                                style_data={
                                    'border': 'none'
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': '#f9fafb'
                                    },
                                    {
                                        'if': {'state': 'selected'},
                                        'backgroundColor': '#dbeafe',
                                        'border': '1px solid #3b82f6'
                                    }
                                ],
                                style_filter={
                                    'backgroundColor': '#f3f4f6',
                                    'padding': '8px'
                                }
                            )
                        ], className="fade-in"),
                        
                        # Download Button
                        html.Div(id='download-section', className="mt-6 flex justify-end")
                    ], className="p-6")
                ], className="bg-white rounded-xl card-shadow fade-in"),
            ], className="lg:w-3/4")
        ], className="flex flex-col lg:flex-row gap-6")
    ], className="container mx-auto px-4 py-6"),
    
    # Hidden elements
    dcc.Download(id="download-data"),
    dcc.Store(id='search-store', data=''),
    dcc.Store(id='network-store', data='total'),
    
    # Footer
    html.Footer([
        html.Div([
            html.P("Account Mapping Dashboard v1.0", className="text-gray-600"),
            html.P(id='last-updated', className="text-gray-500 text-sm"),
        ], className="flex justify-between items-center py-4 border-t border-gray-200")
    ], className="container mx-auto px-4 mt-8")
], className="min-h-screen flex flex-col")

def filter_dataframe(df, search_term=None, network=None):
    """Filter dataframe by search term and network"""
    if df is None or df.empty:
        return pd.DataFrame()
    
    filtered_df = df.copy()
    
    # Filter by network if specified
    if network and network != 'total' and 'NETWORK' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['NETWORK'].str.lower() == network.lower()]
    
    # Apply search filter if search term is provided
    if search_term and search_term.strip():
        search_term = search_term.strip().lower()
        
        # Search in both ACRONAME and ACCOUNT_NUMBER
        mask = (filtered_df['ACRONAME'].astype(str).str.lower().str.contains(search_term, na=False)) | \
               (filtered_df['ACCOUNT_NUMBER'].astype(str).str.lower().str.contains(search_term, na=False))
        filtered_df = filtered_df[mask]
    
    return filtered_df

@app.callback(
    [Output('data-table', 'data'),
     Output('data-table', 'columns'),
     Output('results-title', 'children'),
     Output('results-subtitle', 'children'),
     Output('stats-bar', 'children'),
     Output('network-stats', 'children'),
     Output('last-updated', 'children'),
     Output('tabs', 'children')],
    [Input('tabs', 'value'),
     Input('search-input', 'value'),
     Input('network-filter', 'value'),
     Input('clear-button', 'n_clicks')]
)
def update_display(tab_value, search_term, network_filter, clear_clicks):
    """Update the display based on user interactions"""
    ctx = dash.callback_context
    
    # Initialize default values
    data = []
    columns = [{"name": "ACRONAME", "id": "ACRONAME"}, {"name": "ACCOUNT_NUMBER", "id": "ACCOUNT_NUMBER"}]
    results_title = "No Data Available"
    results_subtitle = "Please upload data files"
    stats_bar = html.Div()
    last_updated = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Update network stats
    network_stats_updated = {}
    if network_data:
        for network_key in NETWORKS.keys():
            if network_key in network_data:
                network_stats_updated[network_key] = len(network_data[network_key])
    
    # Handle clear button
    if ctx.triggered and ctx.triggered[0]['prop_id'] == 'clear-button.n_clicks':
        search_term = ''
        network_filter = 'total'
    
    # Get data for current tab
    current_df = network_data.get(tab_value, pd.DataFrame())
    
    if not current_df.empty:
        # Apply filtering
        filtered_df = filter_dataframe(current_df, search_term, network_filter if tab_value == 'total' else None)
        
        # Prepare data for table
        if not filtered_df.empty:
            # Update columns based on tab
            if tab_value == 'total':
                columns = [
                    {"name": "NETWORK", "id": "NETWORK"},
                    {"name": "ACRONAME", "id": "ACRONAME"},
                    {"name": "ACCOUNT_NUMBER", "id": "ACCOUNT_NUMBER"}
                ]
            else:
                columns = [
                    {"name": "ACRONAME", "id": "ACRONAME"},
                    {"name": "ACCOUNT_NUMBER", "id": "ACCOUNT_NUMBER"}
                ]
            
            data = filtered_df.to_dict('records')
            
            # Update titles and stats
            results_title = f"{NETWORKS[tab_value]} Accounts"
            if search_term:
                results_subtitle = f"Found {len(filtered_df):,} records matching '{search_term}'"
            else:
                results_subtitle = f"Showing {len(filtered_df):,} of {len(current_df):,} total records"
            
            # Create stats bar
            stats_items = [
                html.Div([
                    html.I(className="fas fa-table mr-2 text-blue-500"),
                    html.Span(f"{len(filtered_df):,} Records", className="text-gray-700")
                ], className="flex items-center bg-blue-50 px-3 py-2 rounded-lg"),
                html.Div([
                    html.I(className="fas fa-search mr-2 text-green-500"),
                    html.Span(f"Filter: {search_term if search_term else 'None'}", className="text-gray-700")
                ], className="flex items-center bg-green-50 px-3 py-2 rounded-lg"),
                html.Div([
                    html.I(className="fas fa-percentage mr-2 text-purple-500"),
                    html.Span(f"Match: {len(filtered_df)/len(current_df)*100:.1f}%", className="text-gray-700")
                ], className="flex items-center bg-purple-50 px-3 py-2 rounded-lg")
            ]
            
            stats_bar = html.Div(stats_items, className="flex flex-wrap gap-3")
            
        else:
            # No matching data
            data = []
            results_title = f"No Results Found"
            results_subtitle = f"No records match your search criteria in {NETWORKS[tab_value]}"
            
            stats_bar = html.Div([
                html.Div([
                    html.I(className="fas fa-exclamation-triangle mr-2 text-yellow-500"),
                    html.Span("No matches found", className="text-gray-700")
                ], className="flex items-center bg-yellow-50 px-3 py-2 rounded-lg")
            ])
    
    # Create network stats for sidebar
    network_stats_children = []
    for net in NETWORKS.keys():
        if net != 'total':
            count = network_stats_updated.get(net, 0)
            total_count = network_stats_updated.get('total', 1)
            percentage = (count / total_count * 100) if total_count > 0 else 0
            
            network_stats_children.append(
                html.Div([
                    html.Div([
                        html.Span(NETWORKS[net], className="font-medium text-gray-700"),
                        html.Span(f"{count:,}", 
                                 className="ml-auto bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full")
                    ], className="flex items-center justify-between mb-2"),
                    html.Div([
                        html.Div([
                            html.Div(
                                className="h-2 bg-blue-500 rounded-full",
                                style={'width': f'{percentage}%'}
                            )
                        ], className="w-full bg-gray-200 rounded-full h-2")
                    ])
                ], className="mb-3")
            )
    
    # Update tab labels with current counts
    tab_children = [
        dcc.Tab(
            label=f"{NETWORKS[network]} ({network_stats_updated.get(network, 0)})",
            value=network,
            className="tab px-4 py-3 mr-2 rounded-t-lg border border-b-0 border-gray-300 bg-white text-gray-700",
            selected_className="tab px-4 py-3 mr-2 rounded-t-lg border border-b-0 border-blue-500 bg-blue-50 text-blue-700 font-semibold"
        ) for network in NETWORKS.keys()
    ]
    
    return data, columns, results_title, results_subtitle, stats_bar, network_stats_children, last_updated, tab_children

@app.callback(
    [Output('search-input', 'value'),
     Output('network-filter', 'value')],
    [Input('clear-button', 'n_clicks')],
    [State('search-input', 'value'),
     State('network-filter', 'value')]
)
def clear_filters(n_clicks, current_search, current_network):
    """Clear all filters"""
    if n_clicks:
        return '', 'total'
    return current_search, current_network

@app.callback(
    Output('tabs', 'value'),
    [Input('network-filter', 'value')]
)
def sync_tabs_with_filter(selected_network):
    """Sync tabs with network filter"""
    return selected_network

@app.callback(
    Output('download-data', 'data'),
    [Input('export-button', 'n_clicks')],
    [State('tabs', 'value'),
     State('search-input', 'value'),
     State('network-filter', 'value')]
)
def export_data(n_clicks, tab_value, search_term, network_filter):
    """Export filtered data as CSV"""
    if n_clicks:
        current_df = network_data.get(tab_value, pd.DataFrame())
        if not current_df.empty:
            filtered_df = filter_dataframe(current_df, search_term, network_filter if tab_value == 'total' else None)
            if not filtered_df.empty:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"account_mapping_{tab_value}_{timestamp}.csv"
                
                return dcc.send_data_frame(filtered_df.to_csv, filename, index=False)
    return None

# Create sample CSV files if they don't exist
def create_sample_data():
    """Create sample CSV files if they don't exist"""
    sample_acronames = ['ABC', 'XYZ', 'TRADE', 'FUND', 'CAP', 'INV', 'EQTY', 'BOND', 'ALPHA', 'BETA', 
                       'GAMMA', 'DELTA', 'OMEGA', 'SIGMA', 'TRUST', 'ASSET', 'WEALTH', 'GROWTH']
    
    for network_key, network_name in NETWORKS.items():
        if network_key == 'total':
            continue
            
        filename = f"account_mapping_{network_key}.csv"
        if not os.path.exists(filename):
            # Generate 3-8 rows
            num_rows = np.random.randint(3, 9)
            acronames = []
            account_numbers = []
            
            for i in range(num_rows):
                # Generate unique ACRONAME (3-8 chars)
                base = np.random.choice(sample_acronames)
                suffix = str(np.random.randint(1, 99)) if np.random.random() > 0.3 else ''
                acroname = f"{base}{suffix}"[:8]
                acronames.append(acroname)
                
                # Generate unique ACCOUNT_NUMBER (7 digits starting with 200)
                account_number = f"200{np.random.randint(1000, 9999)}"
                account_numbers.append(account_number)
            
            # Create DataFrame
            df = pd.DataFrame({
                'ACRONAME': acronames,
                'ACCOUNT_NUMBER': account_numbers,
                'NETWORK': network_name
            })
            
            # Save to CSV
            df.to_csv(filename, index=False)
            print(f"📝 Created sample file: {filename}")

# Create sample data if needed
create_sample_data()

if __name__ == '__main__':
    # Print startup information
    print("\n" + "="*60)
    print("🏦 Account Mapping Dashboard - Starting Server")
    print("="*60)
    print(f"\n📂 Loaded networks:")
    
    for network_key in NETWORKS.keys():
        if network_key in network_data:
            df = network_data[network_key]
            icon = "✅" if len(df) > 0 else "⚠️"
            print(f"   {icon} {NETWORKS[network_key]:12} - {len(df):3} records")
    
    total_records = len(network_data.get('total', pd.DataFrame()))
    print(f"\n📊 Total records across all networks: {total_records:,}")
    print(f"\n🌐 Access the dashboard at: http://localhost:8050")
    print("="*60 + "\n")
    
    app.run(debug=True, port=8050, dev_tools_ui=True, dev_tools_hot_reload=True)