# app.py
import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import os
from datetime import datetime
from urllib.parse import quote

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Account Mapping Viewer"

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

# Load data at startup
print(f"Loading data at {datetime.now()}")
network_data = load_all_network_files()

# App layout
app.layout = html.Div([
    html.Div([
        html.H1("Account Mapping Viewer", style={'textAlign': 'center', 'marginBottom': '10px'}),
        html.P("View and search account mappings across different trading networks", 
               style={'textAlign': 'center', 'color': '#666', 'marginBottom': '30px'}),
    ]),
    
    # Last updated timestamp
    html.Div(id='last-updated', style={
        'textAlign': 'center',
        'color': '#888',
        'fontSize': '12px',
        'marginBottom': '10px'
    }),
    
    # Stats summary
    html.Div(id='stats-summary', style={
        'textAlign': 'center',
        'color': '#444',
        'fontSize': '14px',
        'marginBottom': '20px'
    }),
    
    # Search input
    html.Div([
        html.Div([
            html.Label("🔍 Search:", 
                      style={'fontWeight': 'bold', 'marginRight': '10px', 'fontSize': '16px'}),
            dcc.Input(
                id='search-input',
                type='text',
                placeholder='Search by ACRONAME or ACCOUNT_NUMBER...',
                style={
                    'width': '400px', 
                    'marginRight': '10px', 
                    'padding': '10px',
                    'borderRadius': '5px',
                    'border': '1px solid #ddd',
                    'fontSize': '14px'
                },
                debounce=True
            ),
            html.Button('Clear', id='clear-button', n_clicks=0,
                       style={
                           'padding': '10px 20px',
                           'backgroundColor': '#f8f9fa',
                           'border': '1px solid #ddd',
                           'borderRadius': '5px',
                           'cursor': 'pointer'
                       }),
        ], style={
            'display': 'flex', 
            'alignItems': 'center', 
            'justifyContent': 'center',
            'margin': '20px 0',
            'padding': '20px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '8px'
        })
    ]),
    
    # Tabs
    html.Div([
        dcc.Tabs(
            id='tabs', 
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
    html.Div(id='table-container', style={'marginTop': '20px'}),
    
    # Hidden div to trigger initial callback
    html.Div(id='initial-load', style={'display': 'none'})
])

def filter_dataframe_1(df, search_term=None):
    """Filter dataframe by search term"""
    if df is None or df.empty:
        return pd.DataFrame()
    
    filtered_df = df.copy()
    
    # Apply search filter if search term is provided
    if search_term and search_term.strip():
        search_term = search_term.strip().lower()
        
        # Try to match exact account number first
        if search_term.isdigit():
            # Search for exact account number match
            mask_num = filtered_df['ACCOUNT_NUMBER'].astype(str).str.contains(f'^{search_term}', na=False)
            # Also search in ACRONAME
            mask_acroname = filtered_df['ACRONAME'].astype(str).str.lower().str.contains(search_term, na=False)
            mask = mask_num | mask_acroname
        else:
            # Search in ACRONAME (case insensitive)
            mask = filtered_df['ACRONAME'].astype(str).str.lower().str.contains(search_term, na=False)
        
        filtered_df = filtered_df[mask]
    
    return filtered_df

def filter_dataframe(df, search_term=None):
    """Filter dataframe by search term"""
    if df is None or df.empty:
        return pd.DataFrame()
    
    # If no search term, return the original dataframe
    if not search_term or not search_term.strip():
        return df.copy()
    
    search_term = search_term.strip().lower()
    df_copy = df.copy()
    
    # Convert columns to string and lowercase for case-insensitive search
    df_copy['ACCOUNT_NUMBER_STR'] = df_copy['ACCOUNT_NUMBER'].astype(str).str.lower()
    df_copy['ACRONAME_STR'] = df_copy['ACRONAME'].astype(str).str.lower()
    
    # Check if search term exists in either column
    mask = (df_copy['ACCOUNT_NUMBER_STR'].str.contains(search_term, na=False)) | \
           (df_copy['ACRONAME_STR'].str.contains(search_term, na=False))
    
    # Remove temporary columns and return filtered dataframe
    result = df_copy[mask].drop(columns=['ACCOUNT_NUMBER_STR', 'ACRONAME_STR'])
    return result


@app.callback(
    [Output('table-container', 'children'),
     Output('search-input', 'value'),
     Output('last-updated', 'children'),
     Output('stats-summary', 'children'),
     Output('tabs', 'children')],
    [Input('tabs', 'value'),
     Input('search-input', 'value'),
     Input('clear-button', 'n_clicks'),
     Input('initial-load', 'children')]
)
def update_display(tab_value, search_term, clear_clicks, initial_load):
    """Update the display based on user interactions"""
    print(f"DEBUG: Tab value: {tab_value}")
    print(f"DEBUG: Search term: {search_term}")
    print(f"DEBUG: Clear clicks: {clear_clicks}")
    
    ctx = dash.callback_context
    if ctx.triggered:
        print(f"DEBUG: Triggered by: {ctx.triggered[0]['prop_id']}")

    ctx = dash.callback_context
    
    # Initialize variables
    table_content = html.Div()
    search_value = search_term or ''
    last_updated = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    stats_summary = ""
    tab_children = []
    
    # Handle clear button click
    if ctx.triggered and ctx.triggered[0]['prop_id'] == 'clear-button.n_clicks':
        search_value = ''
        search_term = ''
    
    # Check if data is loaded
    if not network_data:
        table_content = html.Div([
            html.H3("No data loaded", style={'color': 'red', 'textAlign': 'center'}),
            html.P("Please ensure the CSV files are in the same directory as this app", 
                   style={'textAlign': 'center'})
        ])
        stats_summary = "No data available"
    else:
        # Get data for current tab
        current_df = network_data.get(tab_value)
        
        if current_df is None or current_df.empty:
            table_content = html.Div([
                html.H3(f"No data available for {NETWORKS[tab_value]}", 
                       style={'textAlign': 'center', 'color': '#666'})
            ])
            stats_summary = f"{NETWORKS[tab_value]}: 0 records"
        else:
            # Apply filtering
            filtered_df = filter_dataframe(current_df, search_term)
            
            if filtered_df.empty:
                table_content = html.Div([
                    html.H3(f"No matching records found in {NETWORKS[tab_value]}", 
                           style={'textAlign': 'center', 'color': '#666'}),
                    html.P(f"Search term: '{search_term}'" if search_term else "", 
                           style={'textAlign': 'center'})
                ])
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
                
                table_content = dash_table.DataTable(
                    id='data-table',
                    columns=columns,
                    data=filtered_df.to_dict('records'),
                    page_size=15,
                    page_current=0,
                    page_action='native',
                    sort_action='native',
                    sort_mode='single',
                    filter_action='none',  # We're handling filtering separately
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
                stats_summary = (
                    f"{NETWORKS[tab_value]}: Showing {len(filtered_df)} of {len(current_df)} records | "
                    f"Search: {'"' + search_term + '"' if search_term else 'None'}"
                )
                
                # Add download button for filtered data
                if not filtered_df.empty:
                    csv_string = filtered_df.to_csv(index=False, encoding='utf-8')
                    # csv_data = "data:text/csv;charset=utf-8," + pd.io.common.urlencode({'': csv_string})[1:]
                    csv_data = "data:text/csv;charset=utf-8," + quote(csv_string)
                    
                    download_button = html.A(
                        '📥 Download Filtered Data',
                        href=csv_data,
                        download=f"account_mapping_{tab_value}_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
                        style={
                            'display': 'inline-block',
                            'margin': '10px 0',
                            'padding': '10px 20px',
                            'backgroundColor': '#28a745',
                            'color': 'white',
                            'textDecoration': 'none',
                            'borderRadius': '5px',
                            'fontWeight': 'bold'
                        }
                    )
                    
                    table_content = html.Div([
                        html.Div([
                            html.H4(f"{NETWORKS[tab_value]} - Account Mappings", 
                                   style={'marginBottom': '10px'}),
                            html.P(f"Showing {len(filtered_df)} records (out of {len(current_df)} total)",
                                  style={'color': '#666', 'marginBottom': '15px'})
                        ]),
                        download_button,
                        html.Hr(style={'margin': '20px 0'}),
                        table_content
                    ])
    
    # Update tab labels with counts
    tab_children = [
        dcc.Tab(
            label=f'{NETWORKS[network]} ({len(network_data.get(network, pd.DataFrame()))})' 
                  if network in network_data else NETWORKS[network],
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
        ) for network in NETWORKS.keys()
    ]
    
    return table_content, search_value, last_updated, stats_summary, tab_children

# Additional callback to update tab counts when search is performed
@app.callback(
    Output('tabs', 'value'),
    [Input('search-input', 'n_submit')],
    [State('tabs', 'value')]
)
def maintain_tab_on_search(n_submit, current_tab):
    """Keep current tab when search is performed"""
    return current_tab

if __name__ == '__main__':
    # Print startup information
    print("\n" + "="*60)
    print("Account Mapping Viewer - Starting Server")
    print("="*60)
    print(f"\nLoaded networks:")
    for network_key in NETWORKS.keys():
        if network_key in network_data:
            df = network_data[network_key]
            print(f"  • {NETWORKS[network_key]:12} - {len(df):3} records")
    
    total_records = len(network_data.get('total', pd.DataFrame()))
    print(f"\nTotal records across all networks: {total_records}")
    print("\nAccess the application at: http://localhost:8050")
    print("="*60 + "\n")
    
    app.run(debug=True, port=8050)