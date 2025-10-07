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
        <style>
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideUp {
                from { 
                    opacity: 0;
                    transform: translateY(20px) scale(0.95);
                }
                to { 
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
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
            className='fixed inset-0 bg-gradient-to-br from-gray-900/80 to-slate-900/80 backdrop-blur-sm z-40 hidden',
            style={'animation': 'fadeIn 0.3s ease-out'},
            children=[
                html.Div(
                    className='fixed inset-0 overflow-y-auto',
                    children=[
                        html.Div(
                            className='flex min-h-full items-center justify-center p-4',
                            children=[
                                html.Div(
                                    className='relative bg-white rounded-2xl shadow-2xl max-w-4xl w-full transform transition-all',
                                    style={'animation': 'slideUp 0.3s ease-out'},
                                    children=[
                                        # Close button (top right)
                                        html.Button(
                                            '✕',
                                            id='close-modal-x',
                                            n_clicks=0,
                                            className='absolute top-4 right-4 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full w-8 h-8 flex items-center justify-center transition-all duration-200 font-bold text-xl'
                                        ),
                                        # Modal header with gradient
                                        html.Div(
                                            className='bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-6 rounded-t-2xl',
                                            children=[
                                                html.Div(className='flex items-center gap-3', children=[
                                                    html.Div(className='bg-white/20 backdrop-blur-sm rounded-lg p-2', children=[
                                                        html.Span('🗺️', className='text-2xl')
                                                    ]),
                                                    html.H3(id='modal-title', className='text-2xl font-bold text-white drop-shadow-sm')
                                                ])
                                            ]
                                        ),
                                        # Modal body with enhanced styling
                                        html.Div(
                                            className='px-8 py-6 bg-gradient-to-br from-gray-50 to-blue-50/30',
                                            children=[
                                                html.Div(
                                                    className='bg-white border-2 border-blue-100 rounded-xl shadow-inner',
                                                    children=[
                                                        html.Pre(
                                                            id='modal-body',
                                                            className='p-6 font-mono text-sm overflow-x-auto whitespace-pre-wrap text-gray-800 leading-relaxed'
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        # Modal footer with better button
                                        html.Div(
                                            className='px-8 py-5 bg-gray-50 rounded-b-2xl flex justify-end gap-3',
                                            children=[
                                                html.Button(
                                                    'Close',
                                                    id='close-modal',
                                                    n_clicks=0,
                                                    className='bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold py-2.5 px-6 rounded-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200'
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
     Input('close-modal', 'n_clicks'),
     Input('close-modal-x', 'n_clicks')],
    [State('selected-account', 'data')]
)
def toggle_modal(selected_rows, close_clicks, close_x_clicks, stored_account):
    ctx = callback_context
    
    if not ctx.triggered:
        return 'fixed inset-0 bg-gradient-to-br from-gray-900/80 to-slate-900/80 backdrop-blur-sm z-40 hidden', "", "", None
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Close modal
    if trigger_id in ['close-modal', 'close-modal-x']:
        return 'fixed inset-0 bg-gradient-to-br from-gray-900/80 to-slate-900/80 backdrop-blur-sm z-40 hidden', "", "", None
    
    # Open modal with route info
    if trigger_id == 'account-table' and selected_rows:
        account = accounts_data[selected_rows[0]]['account']
        routes = get_routes(account)
        title = f"Routes for {account}"
        return 'fixed inset-0 bg-gradient-to-br from-gray-900/80 to-slate-900/80 backdrop-blur-sm z-40', title, routes, account
    
    return 'fixed inset-0 bg-gradient-to-br from-gray-900/80 to-slate-900/80 backdrop-blur-sm z-40 hidden', "", "", stored_account

if __name__ == '__main__':
    app.run(debug=True)
