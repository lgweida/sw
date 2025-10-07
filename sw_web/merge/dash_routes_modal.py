import dash
from dash import html, dcc, dash_table, Input, Output, State, callback_context

# Sample function to get routes
def get_routes(account):
    routes = {
        'ARTISANMZHO': """Routes for ARTISANMZHO:
  COUNTRYCODE=SI -> MizuhoTKGOR42BuySide
  CURRENCY=USD,CAD -> FlexTradeBuySide42
  CURRENCY=AUD,CNH,CNY,HKD,IDR,INR,JPY,KRW,MYR,NZD,PHP,SGD,THB,TWD -> MizuhoTKGOR42BuySide
for ARTISANMZHO""",
        'OSTERS': """Routes for OSTERS:
  TARGETSUBID=PT -> O_FLEXTRADE_GLOBAL_PT_FIX42
for OSTERS"""
    }
    return routes.get(account, f"No routes found for {account}")

# Sample data for the client account table
accounts_data = [
    {'id': 1, 'account': 'ARTISANMZHO', 'name': 'Artisan Mizuho', 'status': 'Active'},
    {'id': 2, 'account': 'OSTERS', 'name': 'Osters Account', 'status': 'Active'},
    {'id': 3, 'account': 'TESTACCT', 'name': 'Test Account', 'status': 'Inactive'},
]

# Initialize the Dash app
app = dash.Dash(__name__)

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

# App layout
app.layout = html.Div(className="min-h-screen bg-gray-50 p-8", children=[
    html.Div(className="max-w-6xl mx-auto", children=[
        html.H1("Client Account Routes", className="text-3xl font-bold text-gray-900 mb-6"),
        
        # Table container
        html.Div(className="bg-white rounded-lg shadow overflow-hidden", children=[
            dash_table.DataTable(
                id='account-table',
                columns=[
                    {'name': 'ID', 'id': 'id'},
                    {'name': 'Account', 'id': 'account'},
                    {'name': 'Name', 'id': 'name'},
                    {'name': 'Status', 'id': 'status'}
                ],
                data=accounts_data,
                style_table={
                    'overflowX': 'auto'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '16px',
                    'fontFamily': 'system-ui, -apple-system, sans-serif',
                    'fontSize': '14px',
                    'border': 'none'
                },
                style_header={
                    'backgroundColor': '#f9fafb',
                    'color': '#111827',
                    'fontWeight': '600',
                    'borderBottom': '2px solid #e5e7eb',
                    'textTransform': 'uppercase',
                    'fontSize': '12px',
                    'letterSpacing': '0.05em'
                },
                style_data={
                    'cursor': 'pointer',
                    'borderBottom': '1px solid #f3f4f6'
                },
                style_data_conditional=[
                    {
                        'if': {'state': 'selected'},
                        'backgroundColor': '#dbeafe',
                        'border': '1px solid #3b82f6'
                    },
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#fafafa'
                    }
                ],
                row_selectable='single',
                selected_rows=[]
            )
        ]),
        
        # Modal overlay
        html.Div(
            id='modal-overlay',
            className='fixed inset-0 bg-black bg-opacity-50 z-40 hidden',
            children=[
                html.Div(
                    className='fixed inset-0 overflow-y-auto',
                    children=[
                        html.Div(
                            className='flex min-h-full items-center justify-center p-4',
                            children=[
                                html.Div(
                                    className='relative bg-white rounded-lg shadow-xl max-w-3xl w-full',
                                    children=[
                                        # Modal header
                                        html.Div(
                                            className='border-b border-gray-200 px-6 py-4',
                                            children=[
                                                html.H3(id='modal-title', className='text-xl font-semibold text-gray-900')
                                            ]
                                        ),
                                        # Modal body
                                        html.Div(
                                            className='px-6 py-4',
                                            children=[
                                                html.Pre(
                                                    id='modal-body',
                                                    className='bg-gray-50 p-4 rounded-md font-mono text-sm overflow-x-auto whitespace-pre-wrap text-gray-800'
                                                )
                                            ]
                                        ),
                                        # Modal footer
                                        html.Div(
                                            className='border-t border-gray-200 px-6 py-4 flex justify-end',
                                            children=[
                                                html.Button(
                                                    'Close',
                                                    id='close-modal',
                                                    n_clicks=0,
                                                    className='bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200'
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        
        # Store selected account
        dcc.Store(id='selected-account')
    ])
])

# Callback to handle row click and toggle modal
@app.callback(
    [Output('modal-overlay', 'className'),
     Output('modal-title', 'children'),
     Output('modal-body', 'children'),
     Output('selected-account', 'data')],
    [Input('account-table', 'selected_rows'),
     Input('close-modal', 'n_clicks')],
    [State('selected-account', 'data')]
)
def toggle_modal(selected_rows, close_clicks, stored_account):
    ctx = callback_context
    
    if not ctx.triggered:
        return 'fixed inset-0 bg-black bg-opacity-50 z-40 hidden', "", "", None
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Close modal
    if trigger_id == 'close-modal':
        return 'fixed inset-0 bg-black bg-opacity-50 z-40 hidden', "", "", None
    
    # Open modal with route info
    if trigger_id == 'account-table' and selected_rows:
        account = accounts_data[selected_rows[0]]['account']
        routes = get_routes(account)
        title = f"Routes for {account}"
        return 'fixed inset-0 bg-black bg-opacity-50 z-40', title, routes, account
    
    return 'fixed inset-0 bg-black bg-opacity-50 z-40 hidden', "", "", stored_account

if __name__ == '__main__':
    app.run(debug=True)
