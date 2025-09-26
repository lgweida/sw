import dash
from dash import dcc, html, Input, Output, callback, dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Initialize Dash app
app = dash.Dash(__name__)

# Sample data (replace with your CSV files)
accounts_data = {
    'account_id': ['20000001', '20000002', '20000003', '20000004', '20000005', 
                   '20000006', '20000007', '20000008', '20000009', '20000010',
                   '20000011', '20000012', '20000013', '20000014', '20000015',
                   '20000016', '20000017', '20000018', '20000019', '20000020'],
    'account_name': ['BLACKROCK INC', 'JP MORGAN CHASE', 'GOLDMAN SACHS', 
                     'MORGAN STANLEY', 'BANK OF AMERICA', 'WELLS FARGO',
                     'CITIGROUP', 'STATE STREET CORP', 'FIDELITY INVESTMENTS',
                     'VANGUARD GROUP', 'CHARLES SCHWAB', 'PRUDENTIAL FINANCIAL',
                     'CAPITAL GROUP', 'WELLINGTON MANAGEMENT', 'NORTHERN TRUST',
                     'T. ROWE PRICE', 'INVESCO', 'FRANKLIN TEMPLETON',
                     'LEGG MASON', 'ALLIANCEBERNSTEIN']
}

subaccounts_data = {
    'subaccount_id': ['30000001', '30000002', '30000003', '30000004', '30000005',
                      '30000006', '30000007', '30000008', '30000009', '30000010',
                      '30000011', '30000012', '30000013', '30000014', '30000015',
                      '30000016', '30000017', '30000018', '30000019', '30000020',
                      '30000021', '30000022', '30000023', '30000024', '30000025',
                      '30000026', '30000027', '30000028', '30000029', '30000030',
                      '30000031', '30000032', '30000033', '30000034', '30000035',
                      '30000036', '30000037', '30000038', '30000039', '30000040'],
    'parent_account_id': ['20000001', '20000001', '20000002', '20000002', '20000003',
                          '20000003', '20000003', '20000004', '20000004', '20000005',
                          '20000005', '20000006', '20000006', '20000007', '20000008',
                          '20000009', '20000010', '20000010', '20000010', '20000011',
                          '20000011', '20000012', '20000012', '20000012', '20000013',
                          '20000013', '20000013', '20000014', '20000014', '20000015',
                          '20000016', '20000017', '20000017', '20000018', '20000018',
                          '20000019', '20000019', '20000020', '20000020', '20000020'],
    'subaccount_name': ['John Garcia', 'Sarah Miller', 'Daniel Johnson', 'Robert Jackson',
                        'Michael Anderson', 'David Davis', 'Nancy Garcia', 'Christopher Davis',
                        'Christopher Moore', 'Nancy Jackson', 'Nancy Jackson', 'Nancy Gonzalez',
                        'Jennifer Martin', 'Maria Taylor', 'Betty Jones', 'Betty Lopez',
                        'Susan Thomas', 'James Lopez', 'John Garcia', 'John Jones',
                        'Thomas Hernandez', 'Emily Williams', 'Maria Johnson', 'Emily Hernandez',
                        'Helen Rodriguez', 'Jane Taylor', 'Susan Jones', 'Lisa Gonzalez',
                        'Karen Wilson', 'Karen Hernandez', 'Susan Smith', 'Daniel Lopez',
                        'Helen Jackson', 'Betty Jones', 'Jennifer Martinez', 'Robert Rodriguez',
                        'Robert Lopez', 'James Jones', 'Karen Anderson', 'Nancy Wilson']
}

# Create DataFrames
accounts_df = pd.DataFrame(accounts_data)
subaccounts_df = pd.DataFrame(subaccounts_data)

# Merge dataframes to create a complete view
merged_df = subaccounts_df.merge(accounts_df, left_on='parent_account_id', right_on='account_id')

# Define the layout with Tailwind CSS
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Account Hierarchy Dashboard", 
                className="text-4xl font-bold text-gray-800 mb-2"),
        html.P("Explore parent-child relationships between accounts and subaccounts", 
               className="text-gray-600 text-lg")
    ], className="bg-white p-6 shadow-sm border-b"),
    
    # Main content
    html.Div([
        # Search and filters section
        html.Div([
            html.Div([
                html.Label("Search Accounts or Subaccounts:", 
                          className="block text-sm font-medium text-gray-700 mb-2"),
                dcc.Input(
                    id='search-input',
                    type='text',
                    placeholder='Search by account name, subaccount name, or ID...',
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                )
            ], className="mb-4"),
            
            html.Div([
                html.Label("Filter by Account:", 
                          className="block text-sm font-medium text-gray-700 mb-2"),
                dcc.Dropdown(
                    id='account-filter',
                    options=[{'label': 'All Accounts', 'value': 'all'}] + 
                           [{'label': f"{row['account_id']} - {row['account_name']}", 
                             'value': row['account_id']} for _, row in accounts_df.iterrows()],
                    value='all',
                    className="text-sm"
                )
            ], className="mb-6")
        ], className="bg-white p-6 rounded-lg shadow-sm border"),
        
        # Statistics cards
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Total Accounts", className="text-lg font-medium text-gray-600"),
                    html.P(f"{len(accounts_df)}", className="text-3xl font-bold text-blue-600")
                ], className="bg-white p-6 rounded-lg shadow-sm border")
            ], className="w-1/3"),
            
            html.Div([
                html.Div([
                    html.H3("Total Subaccounts", className="text-lg font-medium text-gray-600"),
                    html.P(f"{len(subaccounts_df)}", className="text-3xl font-bold text-green-600")
                ], className="bg-white p-6 rounded-lg shadow-sm border")
            ], className="w-1/3"),
            
            html.Div([
                html.Div([
                    html.H3("Avg Subaccounts", className="text-lg font-medium text-gray-600"),
                    html.P(f"{len(subaccounts_df)/len(accounts_df):.1f}", 
                          className="text-3xl font-bold text-purple-600")
                ], className="bg-white p-6 rounded-lg shadow-sm border")
            ], className="w-1/3")
        ], className="flex space-x-6 mb-6"),
        
        # Charts section
        html.Div([
            # Hierarchy visualization
            html.Div([
                html.H3("Account Distribution", 
                       className="text-xl font-semibold text-gray-800 mb-4"),
                dcc.Graph(id='hierarchy-chart')
            ], className="bg-white p-6 rounded-lg shadow-sm border w-1/2"),
            
            html.Div([
                html.H3("Subaccounts by Account", 
                       className="text-xl font-semibold text-gray-800 mb-4"),
                dcc.Graph(id='subaccount-distribution')
            ], className="bg-white p-6 rounded-lg shadow-sm border w-1/2")
        ], className="flex space-x-6 mb-6"),
        
        # Data table section
        html.Div([
            html.H3("Detailed View", 
                   className="text-xl font-semibold text-gray-800 mb-4"),
            html.Div(id='data-table')
        ], className="bg-white p-6 rounded-lg shadow-sm border")
    ], className="p-6 space-y-6")
], className="min-h-screen bg-gray-50")

# Callbacks
@app.callback(
    [Output('hierarchy-chart', 'figure'),
     Output('subaccount-distribution', 'figure'),
     Output('data-table', 'children')],
    [Input('search-input', 'value'),
     Input('account-filter', 'value')]
)
def update_dashboard(search_value, account_filter):
    # Filter data based on inputs
    filtered_df = merged_df.copy()
    
    # Apply account filter
    if account_filter != 'all':
        filtered_df = filtered_df[filtered_df['parent_account_id'] == account_filter]
    
    # Apply search filter
    if search_value:
        search_mask = (
            filtered_df['account_name'].str.contains(search_value, case=False, na=False) |
            filtered_df['subaccount_name'].str.contains(search_value, case=False, na=False) |
            filtered_df['account_id'].str.contains(search_value, case=False, na=False) |
            filtered_df['subaccount_id'].str.contains(search_value, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]
    
    # Create hierarchy chart (sunburst)
    hierarchy_data = []
    for _, row in filtered_df.iterrows():
        hierarchy_data.extend([
            {'ids': row['account_id'], 'labels': row['account_name'], 'parents': ''},
            {'ids': row['subaccount_id'], 'labels': row['subaccount_name'], 
             'parents': row['account_id']}
        ])
    
    hierarchy_fig = go.Figure(go.Sunburst(
        ids=[d['ids'] for d in hierarchy_data],
        labels=[d['labels'] for d in hierarchy_data],
        parents=[d['parents'] for d in hierarchy_data],
        branchvalues="total",
    ))
    hierarchy_fig.update_layout(
        title="Account Hierarchy (Sunburst)",
        font_size=12,
        height=400,
        margin=dict(t=50, l=0, r=0, b=0)
    )
    
    # Create subaccount distribution chart
    subaccount_counts = filtered_df.groupby(['account_id', 'account_name']).size().reset_index(name='count')
    
    dist_fig = px.bar(
        subaccount_counts,
        x='account_name',
        y='count',
        title='Number of Subaccounts per Account',
        labels={'count': 'Number of Subaccounts', 'account_name': 'Account Name'}
    )
    dist_fig.update_layout(
        height=400,
        margin=dict(t=50, l=0, r=0, b=50),
        xaxis_tickangle=-45
    )
    dist_fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)', marker_line_width=1.5)
    
    # Create data table
    table_data = filtered_df[['account_id', 'account_name', 'subaccount_id', 'subaccount_name']].to_dict('records')
    
    data_table = dash_table.DataTable(
        data=table_data,
        columns=[
            {'name': 'Account ID', 'id': 'account_id'},
            {'name': 'Account Name', 'id': 'account_name'},
            {'name': 'Subaccount ID', 'id': 'subaccount_id'},
            {'name': 'Subaccount Name', 'id': 'subaccount_name'}
        ],
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'fontFamily': 'Arial, sans-serif'
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        page_size=10,
        sort_action="native",
        filter_action="native"
    )
    
    return hierarchy_fig, dist_fig, data_table

# Add Tailwind CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <script src="https://cdn.tailwindcss.com"></script>
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
    app.run(debug=True)
