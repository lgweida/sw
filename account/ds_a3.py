import dash
from dash import html, dcc, dash_table, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random

# Generate sample data
def generate_sample_data():
    companies = [
        "BLACKROCK INC", "JP MORGAN CHASE", "GOLDMAN SACHS", "MORGAN STANLEY", 
        "BANK OF AMERICA", "WELLS FARGO", "CITIGROUP", "STATE STREET CORP",
        "FIDELITY INVESTMENTS", "VANGUARD GROUP", "CHARLES SCHWAB", "PRUDENTIAL FINANCIAL",
        "CAPITAL GROUP", "WELLINGTON MANAGEMENT", "NORTHERN TRUST", "T. ROWE PRICE",
        "INVESCO", "FRANKLIN TEMPLETON", "LEGG MASON", "ALLIANCEBERNSTEIN"
    ]

    # Generate account data
    account_data = []
    for i in range(20):
        account_id = 20000000 + i + 1
        company = companies[i]
        account_data.append([account_id, company])

    # Generate subaccount data
    subaccount_data = []
    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa", 
                   "James", "Jennifer", "William", "Maria", "Richard", "Susan", "Thomas", 
                   "Karen", "Charles", "Nancy", "Christopher", "Betty", "Daniel", "Helen"]

    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", 
                  "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", 
                  "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

    subaccount_id_start = 30000000

    for account in account_data:
        account_id = account[0]
        num_subaccounts = random.randint(1, 3)
        
        for j in range(num_subaccounts):
            subaccount_id = subaccount_id_start + len(subaccount_data) + 1
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            subaccount_name = f"{first_name} {last_name}"
            
            subaccount_data.append([subaccount_id, account_id, subaccount_name])

    return account_data, subaccount_data

# Create sample data
account_data, subaccount_data = generate_sample_data()

# Create DataFrames
accounts_df = pd.DataFrame(account_data, columns=['account_id', 'account_name'])
subaccounts_df = pd.DataFrame(subaccount_data, columns=['subaccount_id', 'account_id', 'subaccount_name'])
merged_df = pd.merge(subaccounts_df, accounts_df, on='account_id', how='left')

# Initialize Dash app with Tailwind CSS
app = dash.Dash(__name__)

# Add Tailwind CSS CDN
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        colors: {
                            primary: '#3B82F6',
                            secondary: '#1E40AF',
                            accent: '#10B981',
                            dark: '#1F2937',
                            light: '#F9FAFB'
                        }
                    }
                }
            }
        </script>
        <style>
            .dash-table-container {
                border-radius: 0.5rem;
                overflow: hidden;
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            }
            .dash-spreadsheet-container {
                border-radius: 0.5rem;
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

app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.H1("Account Management Dashboard", 
                   className="text-3xl font-bold text-white"),
            html.P("Visualize parent-child relationships between accounts and subaccounts", 
                  className="text-blue-100 mt-2"),
        ], className="container mx-auto px-4")
    ], className="bg-gradient-to-r from-blue-600 to-blue-800 py-8 shadow-lg"),
    
    # Main Content
    html.Div([
        # Summary Cards
        html.Div([
            html.Div([
                html.Div([
                    html.I(className="fas fa-building text-white text-2xl"),
                    html.Div([
                        html.H3(f"{len(accounts_df)}", className="text-3xl font-bold text-white"),
                        html.P("Total Parent Accounts", className="text-blue-100 text-sm")
                    ], className="ml-4")
                ], className="flex items-center")
            ], className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 shadow-lg"),
            
            html.Div([
                html.Div([
                    html.I(className="fas fa-users text-white text-2xl"),
                    html.Div([
                        html.H3(f"{len(subaccounts_df)}", className="text-3xl font-bold text-white"),
                        html.P("Total Subaccounts", className="text-green-100 text-sm")
                    ], className="ml-4")
                ], className="flex items-center")
            ], className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 shadow-lg"),
            
            html.Div([
                html.Div([
                    html.I(className="fas fa-link text-white text-2xl"),
                    html.Div([
                        html.H3(f"{merged_df['account_id'].nunique()}", className="text-3xl font-bold text-white"),
                        html.P("Active Relationships", className="text-purple-100 text-sm")
                    ], className="ml-4")
                ], className="flex items-center")
            ], className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 shadow-lg"),
            
            html.Div([
                html.Div([
                    html.I(className="fas fa-chart-pie text-white text-2xl"),
                    html.Div([
                        html.H3(f"{len([x for x in accounts_df['account_id'] if x not in merged_df['account_id'].unique()])}", 
                               className="text-3xl font-bold text-white"),
                        html.P("Orphan Accounts", className="text-red-100 text-sm")
                    ], className="ml-4")
                ], className="flex items-center")
            ], className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl p-6 shadow-lg"),
        ], className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"),
        
        # Filter Section
        html.Div([
            html.Label("Filter by Account:", className="block text-sm font-medium text-gray-700 mb-2 font-bold"),
            dcc.Dropdown(
                id='account-filter',
                options=[{'label': '📊 All Accounts', 'value': 'all'}] + 
                        [{'label': f"🏢 {row['account_id']} - {row['account_name']}", 'value': row['account_id']} 
                         for _, row in accounts_df.iterrows()],
                value='all',
                className="w-full md:w-96"
            )
        ], className="bg-white rounded-lg shadow-sm p-6 mb-8 border border-gray-200"),
        
        # Charts Section
        html.Div([
            # Tree Map
            html.Div([
                html.Div([
                    html.H3("Hierarchy Visualization", className="text-lg font-semibold text-gray-900 mb-4"),
                    html.Div([
                        dcc.Graph(id='hierarchy-tree')
                    ], className="rounded-lg bg-white p-2")
                ], className="bg-white rounded-lg shadow-sm p-6 border border-gray-200")
            ], className="w-full lg:w-1/2 pr-0 lg:pr-4 mb-6 lg:mb-0"),
            
            # Distribution Chart
            html.Div([
                html.Div([
                    html.H3("Subaccounts Distribution", className="text-lg font-semibold text-gray-900 mb-4"),
                    html.Div([
                        dcc.Graph(id='subaccounts-chart')
                    ], className="rounded-lg bg-white p-2")
                ], className="bg-white rounded-lg shadow-sm p-6 border border-gray-200")
            ], className="w-full lg:w-1/2 pl-0 lg:pl-4")
        ], className="flex flex-col lg:flex-row mb-8"),
        
        # Data Tables Section
        html.Div([
            # Accounts Table
            html.Div([
                html.Div([
                    html.H3("Parent Accounts", 
                           className="text-lg font-semibold text-gray-900 mb-4 flex items-center"),
                    html.Div([
                        html.Span(f"Total: {len(accounts_df)}", 
                                 className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded")
                    ], className="ml-auto")
                ], className="flex items-center mb-4"),
                html.Div([
                    dash_table.DataTable(
                        id='accounts-table',
                        columns=[
                            {"name": "🏢 Account ID", "id": "account_id", "type": "numeric"},
                            {"name": "📛 Account Name", "id": "account_name"},
                            {"name": "👥 Subaccount Count", "id": "subaccount_count", "type": "numeric"}
                        ],
                        data=[],
                        style_cell={
                            'textAlign': 'left', 
                            'padding': '12px', 
                            'fontFamily': 'Inter, sans-serif',
                            'border': '1px solid #E5E7EB'
                        },
                        style_header={
                            'backgroundColor': '#3B82F6',
                            'color': 'white',
                            'fontWeight': 'bold',
                            'border': 'none',
                            'textAlign': 'left',
                            'padding': '12px'
                        },
                        style_data={
                            'border': '1px solid #E5E7EB',
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': '#F9FAFB'
                            },
                            {
                                'if': {'column_id': 'subaccount_count', 'filter_query': '{subaccount_count} > 2'},
                                'backgroundColor': '#10B981',
                                'color': 'white'
                            }
                        ],
                        page_size=10,
                        sort_action='native',
                        filter_action='native',
                    )
                ], className="rounded-lg shadow-sm overflow-hidden")
            ], className="bg-white rounded-lg shadow-sm p-6 mb-8 border border-gray-200"),
            
            # Subaccounts Table
            html.Div([
                html.Div([
                    html.H3("Subaccounts", 
                           className="text-lg font-semibold text-gray-900 mb-4 flex items-center"),
                    html.Div([
                        html.Span(f"Total: {len(subaccounts_df)}", 
                                 className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded")
                    ], className="ml-auto")
                ], className="flex items-center mb-4"),
                html.Div([
                    dash_table.DataTable(
                        id='subaccounts-table',
                        columns=[
                            {"name": "🔢 Subaccount ID", "id": "subaccount_id", "type": "numeric"},
                            {"name": "🏢 Account ID", "id": "account_id", "type": "numeric"},
                            {"name": "📛 Account Name", "id": "account_name"},
                            {"name": "👤 Subaccount Name", "id": "subaccount_name"}
                        ],
                        data=[],
                        style_cell={
                            'textAlign': 'left', 
                            'padding': '12px', 
                            'fontFamily': 'Inter, sans-serif',
                            'border': '1px solid #E5E7EB'
                        },
                        style_header={
                            'backgroundColor': '#10B981',
                            'color': 'white',
                            'fontWeight': 'bold',
                            'border': 'none',
                            'textAlign': 'left',
                            'padding': '12px'
                        },
                        style_data={
                            'border': '1px solid #E5E7EB',
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': '#F9FAFB'
                            }
                        ],
                        page_size=15,
                        sort_action='native',
                        filter_action='native',
                    )
                ], className="rounded-lg shadow-sm overflow-hidden")
            ], className="bg-white rounded-lg shadow-sm p-6 border border-gray-200")
        ])
    ], className="container mx-auto px-4 py-8")
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
    
    # Hierarchy Tree
    labels = []
    parents = []
    customdata = []
    
    for _, account in filtered_accounts.iterrows():
        labels.append(f"{account['account_name']}")
        parents.append("")
        customdata.append([f"Account ID: {account['account_id']}"])
    
    for _, subaccount in filtered_merged.iterrows():
        labels.append(f"{subaccount['subaccount_name']}")
        parents.append(f"{subaccount['account_name']}")
        customdata.append([f"Subaccount ID: {subaccount['subaccount_id']}"])
    
    tree_fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        customdata=customdata,
        hovertemplate='<b>%{label}</b><br>%{customdata[0]}<extra></extra>',
        marker=dict(
            colors=["#3B82F6" if parent == "" else "#10B981" for parent in parents],
            depthfade=True
        ),
        textinfo="label+value"
    ))
    
    tree_fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#374151")
    )
    
    # Subaccounts Distribution Chart
    subaccount_counts = merged_df.groupby('account_name').size().reset_index(name='count')
    if selected_account != 'all':
        account_name = accounts_df[accounts_df['account_id'] == selected_account]['account_name'].iloc[0]
        subaccount_counts = subaccount_counts[subaccount_counts['account_name'] == account_name]
    
    chart_fig = px.bar(
        subaccount_counts, 
        x='account_name', 
        y='count',
        title="",
        labels={'account_name': 'Account Name', 'count': 'Number of Subaccounts'},
        color='count',
        color_continuous_scale='Viridis'
    )
    
    chart_fig.update_layout(
        height=400,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#374151"),
        xaxis_tickangle=-45
    )
    
    # Table Data
    accounts_with_counts = accounts_df.copy()
    subaccount_count_map = merged_df.groupby('account_id').size()
    accounts_with_counts['subaccount_count'] = accounts_with_counts['account_id'].map(
        lambda x: subaccount_count_map.get(x, 0)
    )
    
    if selected_account != 'all':
        accounts_with_counts = accounts_with_counts[accounts_with_counts['account_id'] == selected_account]
        filtered_merged = filtered_merged
    
    return (
        tree_fig,
        chart_fig,
        accounts_with_counts.to_dict('records'),
        filtered_merged.to_dict('records')
    )

if __name__ == '__main__':
    app.run(debug=True)
