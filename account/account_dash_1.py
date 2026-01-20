# app.py
import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import os
from datetime import datetime
from urllib.parse import quote
import re

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

def filter_dataframe(df, search_term=None):
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
    print(f"DEBUG: Search terms list: {search_list}")
    
    if not search_list:
        return df.copy()
    
    # Create a copy of the dataframe
    df_copy = df.copy()
    
    # Ensure columns are strings for comparison
    df_copy['ACCOUNT_NUMBER'] = df_copy['ACCOUNT_NUMBER'].astype(str).str.lower()
    df_copy['ACRONAME'] = df_copy['ACRONAME'].astype(str).str.lower()
    
    # Initialize mask to True for all rows
    mask = pd.Series([True] * len(df_copy), index=df_copy.index)
    
    # Apply each search term with AND logic
    for term in search_list:
        # Check if term exists in either column
        term_mask = (df_copy['ACCOUNT_NUMBER'].str.contains(term, na=False, regex=False)) | \
                    (df_copy['ACRONAME'].str.contains(term, na=False, regex=False))
        mask = mask & term_mask
    
    # Apply the combined mask
    result = df[mask].copy()
    print(f"DEBUG: Found {len(result)} matching records out of {len(df)} total")
    
    return result

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
                    id='search-input',
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
                html.Button('Clear', id='clear-button', n_clicks=0,
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
            'borderRadius': '8px'
        })
    ], style={'margin': '20px 0'}),
    
    # Search terms display
    html.Div(id='search-terms-display', style={
        'textAlign': 'center',
        'marginBottom': '15px',
        'fontSize': '13px',
        'color': '#555'
    }),
    
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

@app.callback(
    [Output('table-container', 'children'),
     Output('search-input', 'value'),
     Output('last-updated', 'children'),
     Output('stats-summary', 'children'),
     Output('tabs', 'children'),
     Output('search-terms-display', 'children')],
    [Input('tabs', 'value'),
     Input('search-input', 'value'),
     Input('clear-button', 'n_clicks'),
     Input('initial-load', 'children')]
)
def update_display(tab_value, search_term, clear_clicks, initial_load):
    """Update the display based on user interactions"""
    ctx = dash.callback_context
    
    # Initialize variables
    table_content = html.Div()
    search_value = search_term or ''
    last_updated = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    stats_summary = ""
    tab_children = []
    search_terms_display = ""
    
    # Handle clear button click
    if ctx.triggered and ctx.triggered[0]['prop_id'] == 'clear-button.n_clicks':
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
                    html.P(f"Search terms: {search_term}" if search_term else "", 
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
                
                # Add download button for filtered data
                if not filtered_df.empty:
                    csv_string = filtered_df.to_csv(index=False, encoding='utf-8')
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
    
    return table_content, search_value, last_updated, stats_summary, tab_children, search_terms_display

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
    
    app.run(debug=True, port=8080)