import dash
from dash import html, dcc, dash_table, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Load data from CSV files
def load_data():
    accounts_df = pd.read_csv('account.csv', header=None, names=['account_id', 'account_name'])
    subaccounts_df = pd.read_csv('subaccount.csv', header=None, names=['subaccount_id', 'account_id', 'subaccount_name'])
    merged_df = pd.merge(subaccounts_df, accounts_df, on='account_id', how='left')
    return accounts_df, subaccounts_df, merged_df

accounts_df, subaccounts_df, merged_df = load_data()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Account - Subaccount Relationship Dashboard", 
            style={'textAlign': 'center', 'marginBottom': 30, 'color': '#2c3e50'}),
    
    # Summary Cards
    html.Div([
        html.Div([
            html.H3(f"{len(accounts_df)}", style={'margin': '0', 'fontSize': '2.5em', 'color': '#3498db'}),
            html.P("Total Parent Accounts", style={'margin': '0', 'color': '#7f8c8d'})
        ], className='card', style={'width': '23%', 'display': 'inline-block', 'textAlign': 'center', 
                                   'padding': '20px', 'backgroundColor': '#ecf0f1', 'margin': '1%', 
                                   'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}),
        
        html.Div([
            html.H3(f"{len(subaccounts_df)}", style={'margin': '0', 'fontSize': '2.5em', 'color': '#27ae60'}),
            html.P("Total Subaccounts", style={'margin': '0', 'color': '#7f8c8d'})
        ], className='card', style={'width': '23%', 'display': 'inline-block', 'textAlign': 'center', 
                                   'padding': '20px', 'backgroundColor': '#ecf0f1', 'margin': '1%', 
                                   'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}),
        
        html.Div([
            html.H3(f"{merged_df['account_id'].nunique()}", style={'margin': '0', 'fontSize': '2.5em', 'color': '#e74c3c'}),
            html.P("Accounts with Subaccounts", style={'margin': '0', 'color': '#7f8c8d'})
        ], className='card', style={'width': '23%', 'display': 'inline-block', 'textAlign': 'center', 
                                   'padding': '20px', 'backgroundColor': '#ecf0f1', 'margin': '1%', 
                                   'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}),
        
        html.Div([
            html.H3(f"{len(accounts_df) - merged_df['account_id'].nunique()}", style={'margin': '0', 'fontSize': '2.5em', 'color': '#f39c12'}),
            html.P("Accounts without Subaccounts", style={'margin': '0', 'color': '#7f8c8d'})
        ], className='card', style={'width': '23%', 'display': 'inline-block', 'textAlign': 'center', 
                                   'padding': '20px', 'backgroundColor': '#ecf0f1', 'margin': '1%', 
                                   'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}),
    ]),
    
    # Controls
    html.Div([
        html.Label("Select Account to Filter:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
        dcc.Dropdown(
            id='account-filter',
            options=[{'label': 'All Accounts', 'value': 'all'}] + 
                    [{'label': f"{row['account_id']} - {row['account_name']}", 'value': row['account_id']} 
                     for _, row in accounts_df.iterrows()],
            value='all',
            style={'width': '300px', 'display': 'inline-block'}
        )
    ], style={'margin': '20px 0'}),
    
    # Visualizations
    html.Div([
        html.Div([
            html.H3("Hierarchy Tree Map"),
            dcc.Graph(id='hierarchy-tree')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            html.H3("Subaccounts Distribution"),
            dcc.Graph(id='subaccounts-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '4%'})
    ]),
    
    # Data Tables
    html.H2("Detailed Data View", style={'marginTop': '40px'}),
    
    html.Div([
        html.Div([
            html.H3("Parent Accounts"),
            dash_table.DataTable(
                id='accounts-table',
                columns=[{"name": "Account ID", "id": "account_id"},
                        {"name": "Account Name", "id": "account_name"},
                        {"name": "Subaccount Count", "id": "subaccount_count"}],
                data=[],
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': '#3498db', 'color': 'white', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'}
                ],
                page_size=10
            )
        ], style={'width': '100%', 'marginBottom': '30px'}),
        
        html.Div([
            html.H3("Subaccounts"),
            dash_table.DataTable(
                id='subaccounts-table',
                columns=[{"name": "Subaccount ID", "id": "subaccount_id"},
                        {"name": "Account ID", "id": "account_id"},
                        {"name": "Account Name", "id": "account_name"},
                        {"name": "Subaccount Name", "id": "subaccount_name"}],
                data=[],
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': '#27ae60', 'color': 'white', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'}
                ],
                page_size=15
            )
        ], style={'width': '100%'})
    ])
])

@app.callback(
    [Output('hierarchy-tree', 'figure'),
     Output('subaccounts-chart', 'figure'),
     Output('accounts-table', 'data'),
     Output('subaccounts-table', 'data')],
    [Input('account-filter', 'value')]
)
def update_dashboard(selected_account):
    # Filter data based on selection
    if selected_account == 'all':
        filtered_merged = merged_df
        filtered_accounts = accounts_df
    else:
        filtered_merged = merged_df[merged_df['account_id'] == selected_account]
        filtered_accounts = accounts_df[accounts_df['account_id'] == selected_account]
    
    # Prepare data for hierarchy tree
    labels = []
    parents = []
    customdata = []
    
    # Add parent accounts
    for _, account in filtered_accounts.iterrows():
        labels.append(f"{account['account_name']}")
        parents.append("")
        customdata.append([f"Account ID: {account['account_id']}"])
    
    # Add subaccounts
    for _, subaccount in filtered_merged.iterrows():
        labels.append(f"{subaccount['subaccount_name']}")
        parents.append(f"{subaccount['account_name']}")
        customdata.append([f"Subaccount ID: {subaccount['subaccount_id']}"])
    
    # Create tree map
    tree_fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        customdata=customdata,
        hovertemplate='<b>%{label}</b><br>%{customdata[0]}<extra></extra>',
        marker=dict(
            colors=["#3498db" if parent == "" else "#27ae60" for parent in parents],
            depthfade=True
        ),
        textinfo="label+value"
    ))
    
    tree_fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),
        height=400
    )
    
    # Create subaccounts distribution chart
    subaccount_counts = merged_df.groupby('account_name').size().reset_index(name='count')
    if selected_account != 'all':
        account_name = accounts_df[accounts_df['account_id'] == selected_account]['account_name'].iloc[0]
        subaccount_counts = subaccount_counts[subaccount_counts['account_name'] == account_name]
    
    chart_fig = px.bar(
        subaccount_counts, 
        x='account_name', 
        y='count',
        title=f"Number of Subaccounts per Account",
        labels={'account_name': 'Account Name', 'count': 'Number of Subaccounts'},
        color='count',
        color_continuous_scale='Viridis'
    )
    
    chart_fig.update_layout(height=400, showlegend=False)
    
    # Prepare table data
    accounts_with_counts = accounts_df.copy()
    subaccount_count_map = merged_df.groupby('account_id').size()
    accounts_with_counts['subaccount_count'] = accounts_with_counts['account_id'].map(
        lambda x: subaccount_count_map.get(x, 0)
    )
    
    if selected_account != 'all':
        accounts_with_counts = accounts_with_counts[accounts_with_counts['account_id'] == selected_account]
    
    return (
        tree_fig,
        chart_fig,
        accounts_with_counts.to_dict('records'),
        filtered_merged.to_dict('records')
    )

if __name__ == '__main__':
    app.run(debug=True)
