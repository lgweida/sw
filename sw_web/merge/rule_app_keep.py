import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
import configparser
from typing import Dict, List, Optional, Tuple
import colorsys
import random
from collections import defaultdict

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Routing Network Visualizer"

# Global variables
routing_rules = []
column_names = []
all_accounts = set()
accounts_df = None

def load_data():
    """Load routing data from files"""
    global routing_rules, column_names, all_accounts, accounts_df
    
    # Parse INI file
    config = configparser.ConfigParser()
    config.read('enrichments/enrichment_Flex17_MultiDesk_Routing.ini')
    
    separator = config.get('separator', 'value', fallback=';')
    
    # Get column names from INI
    column_map = {}
    if config.has_section('lookup'):
        for key, value in config.items('lookup'):
            column_map[int(key)] = value
    
    # Create column names list
    column_names = [column_map.get(i, f'Column_{i}') for i in range(13)]
    
    # Read CSV file
    routing_rules = []
    with open('enrichments/enrichment_Flex17_MultiDesk_Routing.csv', 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
                
            parts = line.split(separator)
            if len(parts) < 13:
                parts += [''] * (13 - len(parts))
            
            parts = [p.strip() for p in parts]
            
            account = parts[0] if len(parts) > 0 else ''
            desk = parts[12] if len(parts) > 12 else ''
            
            if account and account != '*':
                all_accounts.add(account)
            
            routing_rules.append({
                'id': line_num,
                'line': line,
                'account': account,
                'desk': desk,
                'etf': parts[9] if len(parts) > 9 else '',
                'has_prog': (len(parts) > 3 and parts[3] == 'PROG') or 
                           (len(parts) > 4 and parts[4] == 'PROG'),
                'has_pt': len(parts) > 5 and parts[5] == 'PT',
                'is_wildcard': account in ('', '*'),
                'all_columns': parts
            })
    
    # Create accounts dataframe for the table
    accounts_list = []
    for account in sorted(all_accounts):
        account_rules = [r for r in routing_rules if r['account'] == account]
        wildcard_rules = [r for r in routing_rules if r['is_wildcard']]
        total_rules = len(account_rules) + len(wildcard_rules)
        
        # Get unique desks for this account
        desks = set([r['desk'] for r in account_rules if r['desk']])
        wildcard_desks = set([r['desk'] for r in wildcard_rules if r['desk']])
        all_desks = list(desks.union(wildcard_desks))
        
        accounts_list.append({
            'account': account,
            'rule_count': len(account_rules),
            'total_rules': total_rules,
            'desks': ', '.join(all_desks) if all_desks else 'None',
            'has_prog': 'Yes' if any(r['has_prog'] for r in account_rules) else 'No',
            'has_pt': 'Yes' if any(r['has_pt'] for r in account_rules) else 'No',
            'has_etf': 'Yes' if any(r['etf'] for r in account_rules) else 'No'
        })
    
    accounts_df = pd.DataFrame(accounts_list)
    
    return routing_rules, column_names

# Load initial data
routing_rules, column_names = load_data()

# Modal dialog for account rules
account_modal = html.Div([
    html.Div([
        html.Div([
            html.H3("Account Routing Rules", id="modal-title", style={'marginTop': 0}),
            html.Button("×", id="close-modal", style={
                'position': 'absolute',
                'top': '10px',
                'right': '10px',
                'background': 'none',
                'border': 'none',
                'fontSize': '24px',
                'cursor': 'pointer',
                'color': '#666'
            }),
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),
        
        html.Div(id="modal-account-info", style={'marginBottom': '20px'}),
        
        dash_table.DataTable(
            id="modal-rules-table",
            columns=[
                {'name': 'ID', 'id': 'id'},
                {'name': 'Account', 'id': 'account'},
                {'name': 'Desk', 'id': 'desk'},
                {'name': 'ETF', 'id': 'etf'},
                {'name': 'PROG', 'id': 'has_prog'},
                {'name': 'PT', 'id': 'has_pt'},
                {'name': 'Wildcard', 'id': 'is_wildcard'},
                {'name': 'Full Rule', 'id': 'line'}
            ],
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '8px',
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth': '80px',
                'maxWidth': '200px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis'
            },
            style_header={
                'backgroundColor': 'rgba(52, 152, 219, 0.8)',
                'fontWeight': 'bold',
                'color': 'white'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgba(245, 245, 245, 0.7)'
                },
                {
                    'if': {'filter_query': '{is_wildcard} = "Yes"'},
                    'backgroundColor': 'rgba(255, 235, 59, 0.3)'
                }
            ],
            page_size=10,
            filter_action="native",
            sort_action="native",
            row_selectable="single",
            selected_rows=[]
        ),
        
        html.Div([
            html.H4("Rule Details", style={'marginTop': '20px'}),
            html.Div(id="modal-rule-details", style={
                'backgroundColor': '#f8f9fa',
                'padding': '15px',
                'borderRadius': '5px',
                'fontFamily': 'monospace',
                'maxHeight': '300px',
                'overflowY': 'auto'
            })
        ], id="modal-rule-details-container", style={'display': 'none'})
    ], style={
        'backgroundColor': 'white',
        'padding': '30px',
        'borderRadius': '10px',
        'boxShadow': '0 5px 15px rgba(0,0,0,0.3)',
        'maxWidth': '90vw',
        'maxHeight': '90vh',
        'overflowY': 'auto',
        'position': 'relative'
    })
], id="account-modal", style={
    'display': 'none',
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'width': '100%',
    'height': '100%',
    'backgroundColor': 'rgba(0,0,0,0.5)',
    'zIndex': 1000,
    'justifyContent': 'center',
    'alignItems': 'center'
})

# Confirmation modal for Add to Visualization
confirmation_modal = html.Div([
    html.Div([
        html.Div([
            html.H3("Add Account to Visualization", id="confirm-modal-title", style={'marginTop': 0}),
            html.Button("×", id="close-confirm-modal", style={
                'position': 'absolute',
                'top': '10px',
                'right': '10px',
                'background': 'none',
                'border': 'none',
                'fontSize': '24px',
                'cursor': 'pointer',
                'color': '#666'
            }),
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),
        
        html.Div(id="confirm-modal-content", style={'marginBottom': '20px', 'padding': '20px'}),
        
        html.Div([
            html.Button("OK", id="confirm-ok-button", style={
                'padding': '10px 30px',
                'backgroundColor': '#2ecc71',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'marginRight': '10px'
            }),
            html.Button("Cancel", id="confirm-cancel-button", style={
                'padding': '10px 30px',
                'backgroundColor': '#e74c3c',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer'
            }),
        ], style={'textAlign': 'center', 'marginTop': '20px'})
    ], style={
        'backgroundColor': 'white',
        'padding': '30px',
        'borderRadius': '10px',
        'boxShadow': '0 5px 15px rgba(0,0,0,0.3)',
        'maxWidth': '500px',
        'maxHeight': '80vh',
        'overflowY': 'auto',
        'position': 'relative'
    })
], id="confirmation-modal", style={
    'display': 'none',
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'width': '100%',
    'height': '100%',
    'backgroundColor': 'rgba(0,0,0,0.5)',
    'zIndex': 1001,
    'justifyContent': 'center',
    'alignItems': 'center'
})

# App layout
app.layout = html.Div([
    html.Div([
        html.H1("Routing Network Visualizer", style={'textAlign': 'center', 'color': '#2c3e50'}),
        
        # Controls
        html.Div([
            html.Div([
                html.Label("Select Accounts (comma-separated):", style={'fontWeight': 'bold'}),
                dcc.Input(
                    id='accounts-input',
                    type='text',
                    placeholder='e.g., 20010003,20010035,20010280',
                    style={'width': '400px', 'marginRight': '10px'}
                ),
                html.Span("Leave empty to show all accounts", style={'fontSize': '12px', 'color': '#666'}),
            ], style={'marginBottom': '10px'}),
            
            html.Div([
                html.Label("Max Accounts to Display:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                dcc.Slider(
                    id='max-accounts-slider',
                    min=5,
                    max=50,
                    step=5,
                    value=20,
                    marks={i: str(i) for i in range(5, 51, 10)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
            ], style={'marginBottom': '20px', 'width': '400px'}),
            
            html.Div([
                html.Button('Show Network Graph', id='btn-network', n_clicks=0,
                           style={'marginRight': '10px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Button('Show Sankey Diagram', id='btn-sankey', n_clicks=0,
                           style={'marginRight': '10px', 'backgroundColor': '#2ecc71', 'color': 'white'}),
                html.Button('Show Parallel Coordinates', id='btn-parallel', n_clicks=0,
                           style={'backgroundColor': '#e74c3c', 'color': 'white'}),
            ], style={'marginBottom': '30px'}),
            
            dcc.Loading(
                id="loading-1",
                type="default",
                children=[
                    dcc.Store(id='selected-accounts-store', data=[]),
                    html.Div(id='graph-container'),
                    html.Div(id='stats-container', style={'marginTop': '20px'})
                ]
            )
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'
        }),
        
        # Accounts table
        html.Div([
            html.Div([
                html.H3("Accounts Table", style={'display': 'inline-block', 'marginRight': '20px'}),
                html.Button("Refresh", id="refresh-accounts", style={
                    'padding': '5px 15px',
                    'backgroundColor': '#3498db',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '5px',
                    'cursor': 'pointer'
                })
            ], style={'marginBottom': '15px'}),
            
            dash_table.DataTable(
                id="accounts-table",
                columns=[
                    {'name': 'Account', 'id': 'account', 'selectable': True},
                    {'name': 'Direct Rules', 'id': 'rule_count'},
                    {'name': 'Total Rules', 'id': 'total_rules'},
                    {'name': 'Desks', 'id': 'desks'},
                    {'name': 'Has PROG', 'id': 'has_prog'},
                    {'name': 'Has PT', 'id': 'has_pt'},
                    {'name': 'Has ETF', 'id': 'has_etf'}
                ],
                data=accounts_df.to_dict('records') if accounts_df is not None else [],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'minWidth': '100px',
                    'maxWidth': '200px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis'
                },
                style_header={
                    'backgroundColor': 'rgba(52, 152, 219, 0.8)',
                    'fontWeight': 'bold',
                    'color': 'white'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgba(245, 245, 245, 0.7)'
                    },
                    {
                        'if': {'state': 'selected'},
                        'backgroundColor': 'rgba(52, 152, 219, 0.3)',
                        'border': '2px solid #3498db'
                    }
                ],
                page_size=15,
                filter_action="native",
                sort_action="native",
                row_selectable="single",
                selected_rows=[],
                page_action="native",
                page_current=0,
                style_as_list_view=True,
                css=[{
                    'selector': '.dash-spreadsheet tr',
                    'rule': 'cursor: pointer'
                }]
            ),
            
            html.Div([
                html.Button("View Selected Account Rules", id="view-account-rules", style={
                    'padding': '10px 20px',
                    'backgroundColor': '#2ecc71',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '5px',
                    'cursor': 'pointer',
                    'marginTop': '15px',
                    'display': 'inline-block'
                }),
                html.Button("Add to Visualization", id="add-to-visualization", style={
                    'padding': '10px 20px',
                    'backgroundColor': '#3498db',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '5px',
                    'cursor': 'pointer',
                    'marginTop': '15px',
                    'marginLeft': '10px',
                    'display': 'inline-block'
                })
            ])
        ], style={
            'marginTop': '30px',
            'padding': '20px',
            'backgroundColor': 'white',
            'borderRadius': '10px',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'
        }),
        
        # Data table
        html.Div([
            html.H3("Routing Rules Data", style={'color': '#2c3e50'}),
            dash_table.DataTable(
                id='data-table',
                columns=[
                    {'name': 'Rule ID', 'id': 'id'},
                    {'name': 'Account', 'id': 'account'},
                    {'name': 'Desk', 'id': 'desk'},
                    {'name': 'ETF', 'id': 'etf'},
                    {'name': 'Has PROG', 'id': 'has_prog'},
                    {'name': 'Has PT', 'id': 'has_pt'},
                ],
                data=[],
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'minWidth': '100px',
                    'backgroundColor': 'rgba(255, 255, 255, 0.7)'
                },
                style_header={
                    'backgroundColor': 'rgba(52, 152, 219, 0.3)',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgba(245, 245, 245, 0.5)'
                    }
                ]
            )
        ], style={
            'marginTop': '30px',
            'padding': '20px',
            'backgroundColor': 'white',
            'borderRadius': '10px',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'
        }),
        
    ], style={
        'padding': '30px',
        'maxWidth': '1400px',
        'margin': '0 auto',
        'backgroundColor': '#f8f9fa',
        'minHeight': '100vh'
    }),
    
    # Modal dialogs
    account_modal,
    confirmation_modal
])

# Callback to handle account table selection and modal
@app.callback(
    [Output('account-modal', 'style'),
     Output('modal-title', 'children'),
     Output('modal-account-info', 'children'),
     Output('modal-rules-table', 'data'),
     Output('modal-rule-details', 'children'),
     Output('modal-rule-details-container', 'style')],
    [Input('view-account-rules', 'n_clicks'),
     Input('close-modal', 'n_clicks'),
     Input('accounts-table', 'selected_rows'),
     Input('modal-rules-table', 'selected_rows')],
    [State('accounts-table', 'data'),
     State('modal-rules-table', 'data'),
     State('account-modal', 'style')]
)
def handle_account_modal(view_clicks, close_clicks, account_selected_rows, rule_selected_rows, 
                        accounts_table_data, modal_rules_data, modal_style):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return modal_style, "Account Routing Rules", "", [], "Select a rule to see details", {'display': 'none'}
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Handle modal close
    if trigger_id == 'close-modal':
        modal_style['display'] = 'none'
        return modal_style, "Account Routing Rules", "", [], "Select a rule to see details", {'display': 'none'}
    
    # Handle view account rules button
    elif trigger_id == 'view-account-rules' and account_selected_rows:
        # Show modal with account rules
        selected_row = account_selected_rows[0]
        account = accounts_table_data[selected_row]['account']
        
        # Get all rules for this account
        account_rules = [r for r in routing_rules if r['account'] == account]
        wildcard_rules = [r for r in routing_rules if r['is_wildcard']]
        all_rules = account_rules + wildcard_rules
        
        # Prepare table data
        table_data_rules = []
        for rule in all_rules:
            table_data_rules.append({
                'id': rule['id'],
                'account': rule['account'],
                'desk': rule['desk'],
                'etf': rule['etf'],
                'has_prog': '✓' if rule['has_prog'] else '',
                'has_pt': '✓' if rule['has_pt'] else '',
                'is_wildcard': 'Yes' if rule['is_wildcard'] else 'No',
                'line': rule['line']
            })
        
        # Create account info
        desks_set = set([r['desk'] for r in all_rules if r['desk']])
        desks_list = ', '.join(desks_set) if desks_set else ''
        
        account_info = html.Div([
            html.H4(f"Account: {account}"),
            html.P(f"Direct rules: {len(account_rules)}"),
            html.P(f"Wildcard rules applicable: {len(wildcard_rules)}"),
            html.P(f"Total applicable rules: {len(all_rules)}"),
            html.P(f"Possible desks: {desks_list if desks_list else 'None'}")
        ])
        
        modal_style['display'] = 'flex'
        return modal_style, f"Routing Rules for Account {account}", account_info, table_data_rules, "Select a rule to see details", {'display': 'none'}
    
    # Handle rule selection in modal table
    elif trigger_id == 'modal-rules-table' and rule_selected_rows and modal_rules_data:
        selected_row = rule_selected_rows[0]
        rule = modal_rules_data[selected_row]
        
        # Find the full rule object
        rule_obj = next((r for r in routing_rules if r['id'] == rule['id']), None)
        
        if not rule_obj:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, "Rule details not found", {'display': 'none'}
        
        # Create detailed view
        details = html.Div([
            html.H5(f"Rule ID: {rule_obj['id']}"),
            html.P(f"Full line: {rule_obj['line']}"),
            html.Hr(),
            html.H5("Column Breakdown:"),
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Column"),
                    html.Th("Name"),
                    html.Th("Value")
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(i),
                        html.Td(column_names[i] if i < len(column_names) else f'Column_{i}'),
                        html.Td(rule_obj['all_columns'][i] if i < len(rule_obj['all_columns']) else '')
                    ]) for i in range(13)
                ])
            ], style={'width': '100%', 'borderCollapse': 'collapse', 'fontSize': '12px'}),
            
            html.Hr(),
            html.Div([
                html.Strong("Special Flags:"),
                html.Ul([
                    html.Li(f"Has PROG: {'Yes' if rule_obj['has_prog'] else 'No'}"),
                    html.Li(f"Has PT: {'Yes' if rule_obj['has_pt'] else 'No'}"),
                    html.Li(f"ETF: {rule_obj['etf'] if rule_obj['etf'] else 'None'}"),
                    html.Li(f"Wildcard Rule: {'Yes' if rule_obj['is_wildcard'] else 'No'}"),
                    html.Li(f"Target Desk: {rule_obj['desk']}")
                ])
            ])
        ])
        
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, details, {'display': 'block'}
    
    return modal_style, "Account Routing Rules", "", [], "Select a rule to see details", {'display': 'none'}

# Callback to handle confirmation modal for Add to Visualization
@app.callback(
    [Output('confirmation-modal', 'style'),
     Output('confirm-modal-content', 'children'),
     Output('accounts-input', 'value', allow_duplicate=True)],
    [Input('add-to-visualization', 'n_clicks'),
     Input('close-confirm-modal', 'n_clicks'),
     Input('confirm-cancel-button', 'n_clicks'),
     Input('confirm-ok-button', 'n_clicks')],
    [State('accounts-table', 'selected_rows'),
     State('accounts-table', 'data'),
     State('accounts-input', 'value'),
     State('confirmation-modal', 'style')],
    prevent_initial_call=True
)
def handle_confirmation_modal(add_clicks, close_clicks, cancel_clicks, ok_clicks, 
                             selected_rows, table_data, current_value, modal_style):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return modal_style, "", current_value
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Handle modal close/cancel
    if trigger_id in ['close-confirm-modal', 'confirm-cancel-button']:
        modal_style['display'] = 'none'
        return modal_style, "", current_value
    
    # Handle Add to Visualization button
    elif trigger_id == 'add-to-visualization':
        if not selected_rows:
            # Show error message if no account selected
            error_content = html.Div([
                html.H4("No Account Selected", style={'color': '#e74c3c'}),
                html.P("Please select an account from the table first.")
            ])
            modal_style['display'] = 'flex'
            return modal_style, error_content, current_value
        
        # Show confirmation modal
        selected_row = selected_rows[0]
        account = table_data[selected_row]['account']
        
        # Check if account is already in the input
        accounts_in_input = []
        if current_value:
            accounts_in_input = [acc.strip() for acc in current_value.split(',') if acc.strip()]
        
        if account in accounts_in_input:
            # Account already exists
            content = html.Div([
                html.H4("Account Already Added", style={'color': '#f39c12'}),
                html.P(f"Account {account} is already in the visualization list."),
                html.P("Current accounts in visualization:"),
                html.Ul([html.Li(acc) for acc in accounts_in_input])
            ])
        else:
            # Show confirmation to add account
            content = html.Div([
                html.H4("Add Account to Visualization", style={'color': '#2c3e50'}),
                html.P(f"Add account {account} to visualization?"),
                html.Div([
                    html.Strong("Account Details:"),
                    html.Ul([
                        html.Li(f"Account: {account}"),
                        html.Li(f"Direct Rules: {table_data[selected_row]['rule_count']}"),
                        html.Li(f"Possible Desks: {table_data[selected_row]['desks']}")
                    ])
                ]),
                html.P("Click OK to add, or Cancel to go back.")
            ])
        
        modal_style['display'] = 'flex'
        return modal_style, content, current_value
    
    # Handle OK button (actually add the account)
    elif trigger_id == 'confirm-ok-button' and selected_rows:
        selected_row = selected_rows[0]
        account = table_data[selected_row]['account']
        
        # Update the input value
        if current_value:
            accounts = [acc.strip() for acc in current_value.split(',') if acc.strip()]
            if account not in accounts:
                accounts.append(account)
            new_value = ', '.join(accounts)
        else:
            new_value = account
        
        # Close modal and show success message
        success_content = html.Div([
            html.H4("Success!", style={'color': '#2ecc71'}),
            html.P(f"Account {account} has been added to visualization."),
            html.P("Click OK to continue.")
        ])
        
        modal_style['display'] = 'none'
        return modal_style, success_content, new_value
    
    return modal_style, "", current_value

# Callback to refresh accounts table
@app.callback(
    Output('accounts-table', 'data'),
    [Input('refresh-accounts', 'n_clicks')]
)
def refresh_accounts(refresh_clicks):
    # Recreate accounts dataframe
    accounts_list = []
    for account in sorted(all_accounts):
        account_rules = [r for r in routing_rules if r['account'] == account]
        wildcard_rules = [r for r in routing_rules if r['is_wildcard']]
        total_rules = len(account_rules) + len(wildcard_rules)
        
        desks = set([r['desk'] for r in account_rules if r['desk']])
        wildcard_desks = set([r['desk'] for r in wildcard_rules if r['desk']])
        all_desks = list(desks.union(wildcard_desks))
        
        accounts_list.append({
            'account': account,
            'rule_count': len(account_rules),
            'total_rules': total_rules,
            'desks': ', '.join(all_desks) if all_desks else 'None',
            'has_prog': 'Yes' if any(r['has_prog'] for r in account_rules) else 'No',
            'has_pt': 'Yes' if any(r['has_pt'] for r in account_rules) else 'No',
            'has_etf': 'Yes' if any(r['etf'] for r in account_rules) else 'No'
        })
    
    return accounts_list

# Callbacks for visualization (from previous code)
def generate_light_color(seed=None):
    """Generate a light pastel color"""
    if seed is not None:
        random.seed(hash(seed) % 1000)
    
    h = random.random()
    s = random.uniform(0.2, 0.4)
    l = random.uniform(0.7, 0.9)
    
    rgb = colorsys.hls_to_rgb(h, l, s)
    
    return f'rgba({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)}, 0.3)'

@app.callback(
    [Output('graph-container', 'children'),
     Output('stats-container', 'children'),
     Output('data-table', 'data')],
    [Input('btn-network', 'n_clicks'),
     Input('btn-sankey', 'n_clicks'),
     Input('btn-parallel', 'n_clicks')],
    [State('selected-accounts-store', 'data'),
     State('max-accounts-slider', 'value')]
)
def update_graphs(network_clicks, sankey_clicks, parallel_clicks, selected_accounts, max_accounts):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return [], [], []
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Simple placeholder for visualization functions
    fig = go.Figure()
    fig.update_layout(
        title="Visualization Placeholder - Use original functions",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=400
    )
    
    stats_html = html.Div([
        html.H4("Visualization Statistics"),
        html.P("This is a placeholder. Use the original visualization functions."),
    ])
    
    table_data = []
    return [
        dcc.Graph(figure=fig),
        stats_html,
        table_data
    ]

@app.callback(
    Output('selected-accounts-store', 'data'),
    [Input('accounts-input', 'value')]
)
def update_selected_accounts(input_value):
    if not input_value:
        return []
    
    accounts = [acc.strip() for acc in input_value.split(',') if acc.strip()]
    return [acc for acc in accounts if acc in all_accounts]

# Add custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            
            h1, h2, h3, h4 {
                color: #2c3e50;
                margin-bottom: 15px;
            }
            
            button {
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            
            table {
                border-collapse: collapse;
                width: 100%;
            }
            
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            
            th {
                background-color: #f2f2f2;
            }
            
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner td {
                border: 1px solid #e0e0e0;
            }
            
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner th {
                border: 1px solid #ddd;
            }
            
            tr:hover {
                background-color: rgba(52, 152, 219, 0.1) !important;
            }
            
            .modal-backdrop {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.5);
                z-index: 1000;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .modal-content {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                max-width: 90vw;
                max-height: 90vh;
                overflow-y: auto;
                position: relative;
            }
            
            .close-modal {
                position: absolute;
                top: 10px;
                right: 10px;
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: #666;
            }
            
            .close-modal:hover {
                color: #000;
            }
            
            .success-message {
                color: #2ecc71;
                font-weight: bold;
            }
            
            .warning-message {
                color: #f39c12;
                font-weight: bold;
            }
            
            .error-message {
                color: #e74c3c;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    print("Loading routing data...")
    load_data()
    print(f"Loaded {len(routing_rules)} routing rules")
    print(f"Found {len(all_accounts)} unique accounts")
    print("Starting Dash app on http://127.0.0.1:8050")
    app.run(debug=True, port=8050)