import dash
from dash import html, dcc, dash_table, Input, Output, State, callback_context

# Sample function to get routes - now returns structured data
def get_routes_data(account):
    routes = {
        'ARTISANMZHO': [
            {
                'title': 'Country Code Rule',
                'icon': '🌍',
                'gradient': 'from-emerald-500 to-teal-500',
                'condition_type': 'COUNTRYCODE',
                'condition_badge_color': 'bg-emerald-100 text-emerald-800',
                'condition_values': ['SI'],
                'destination': 'MizuhoTKGOR42BuySide',
                'dest_gradient': 'from-purple-500 to-indigo-500'
            },
            {
                'title': 'Currency Rule (USD/CAD)',
                'icon': '💵',
                'gradient': 'from-amber-500 to-orange-500',
                'condition_type': 'CURRENCY',
                'condition_badge_color': 'bg-amber-100 text-amber-800',
                'condition_values': ['USD', 'CAD'],
                'destination': 'FlexTradeBuySide42',
                'dest_gradient': 'from-rose-500 to-pink-500'
            },
            {
                'title': 'Currency Rule (Asian Markets)',
                'icon': '💱',
                'gradient': 'from-cyan-500 to-blue-500',
                'condition_type': 'CURRENCY',
                'condition_badge_color': 'bg-cyan-100 text-cyan-800',
                'condition_values': ['AUD', 'CNH', 'CNY', 'HKD', 'IDR', 'INR', 'JPY', 'KRW', 'MYR', 'NZD', 'PHP', 'SGD', 'THB', 'TWD'],
                'destination': 'MizuhoTKGOR42BuySide',
                'dest_gradient': 'from-purple-500 to-indigo-500'
            }
        ],
        'OSTERS': [
            {
                'title': 'Target SubID Rule',
                'icon': '🎯',
                'gradient': 'from-violet-500 to-purple-500',
                'condition_type': 'TARGETSUBID',
                'condition_badge_color': 'bg-violet-100 text-violet-800',
                'condition_values': ['PT'],
                'destination': 'O_FLEXTRADE_GLOBAL_PT_FIX42',
                'dest_gradient': 'from-indigo-500 to-blue-500'
            }
        ]
    }
    return routes.get(account, [])

# Function to create route card component
def create_route_card(route):
    # Determine if we need compact display for many values
    is_compact = len(route['condition_values']) > 4
    
    return html.Div(className="bg-white rounded-xl shadow-lg border border-blue-100 overflow-hidden transform transition-all hover:shadow-xl hover:scale-[1.01]", children=[
        # Header
        html.Div(className=f"bg-gradient-to-r {route['gradient']} px-6 py-3", children=[
            html.H3(className="text-white font-semibold text-lg flex items-center gap-2", children=[
                html.Span(route['icon'], className="text-xl"),
                route['title']
            ])
        ]),
        # Body
        html.Div(className="p-6", children=[
            html.Div(className="flex items-center justify-between flex-wrap gap-4", children=[
                # Condition section
                html.Div(className="flex-1 min-w-[200px]", children=[
                    html.Div("Condition", className="text-sm text-gray-500 font-medium mb-1"),
                    html.Div(className="flex items-start gap-2" if is_compact else "flex items-center gap-2 flex-wrap", children=[
                        html.Span(
                            route['condition_type'],
                            className=f"inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold {route['condition_badge_color']} {'whitespace-nowrap' if is_compact else ''}"
                        ),
                        html.Span("=", className="text-gray-400 font-bold"),
                        html.Div(className="flex flex-wrap gap-1", children=[
                            html.Span(
                                val,
                                className=f"inline-flex items-center {'px-2.5 py-1 text-xs' if is_compact else 'px-3 py-1 text-sm'} rounded-full font-semibold bg-blue-100 text-blue-800"
                            ) for val in route['condition_values']
                        ])
                    ])
                ]),
                # Arrow
                html.Div(className="flex items-center", children=[
                    html.Svg(className="w-8 h-8 text-gray-300", fill="none", stroke="currentColor", viewBox="0 0 24 24", children=[
                        html.Path(strokeLinecap="round", strokeLinejoin="round", strokeWidth="2", d="M13 7l5 5m0 0l-5 5m5-5H6")
                    ])
                ]),
                # Destination section
                html.Div(className="flex-1 min-w-[200px]", children=[
                    html.Div("Destination", className="text-sm text-gray-500 font-medium mb-1"),
                    html.Div(
                        route['destination'],
                        className=f"inline-flex items-center px-4 py-2 rounded-lg text-sm font-semibold bg-gradient-to-r {route['dest_gradient']} text-white shadow-md"
                    )
                ])
            ])
        ])
    ])

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
                                    className='relative bg-white rounded-2xl shadow-2xl max-w-5xl w-full transform transition-all',
                                    style={'animation': 'slideUp 0.3s ease-out'},
                                    children=[
                                        # Close button (top right)
                                        html.Button(
                                            '✕',
                                            id='close-modal-x',
                                            n_clicks=0,
                                            className='absolute top-4 right-4 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full w-8 h-8 flex items-center justify-center transition-all duration-200 font-bold text-xl z-10'
                                        ),
                                        # Modal header with gradient
                                        html.Div(
                                            className='bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-6 rounded-t-2xl',
                                            children=[
                                                html.Div(className='flex items-center gap-3', children=[
                                                    html.Div(className='bg-white/20 backdrop-blur-sm rounded-lg p-2', children=[
                                                        html.Span('🗺️', className='text-2xl')
                                                    ]),
                                                    html.Div(children=[
                                                        html.H3(id='modal-title', className='text-2xl font-bold text-white drop-shadow-sm'),
                                                        html.P(id='modal-subtitle', className='text-blue-100 text-sm mt-1')
                                                    ])
                                                ])
                                            ]
                                        ),
                                        # Modal body with route cards
                                        html.Div(
                                            id='modal-body',
                                            className='px-8 py-6 bg-gradient-to-br from-slate-50 to-blue-50 max-h-[70vh] overflow-y-auto'
                                        ),
                                        # Modal footer
                                        html.Div(
                                            className='px-8 py-5 bg-gray-50 rounded-b-2xl flex justify-between items-center',
                                            children=[
                                                html.P(id='modal-footer-info', className='text-sm text-gray-500'),
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
     Output('modal-subtitle', 'children'),
     Output('modal-body', 'children'),
     Output('modal-footer-info', 'children'),
     Output('selected-account', 'data')],
    [Input('account-table', 'selected_rows'),
     Input('close-modal', 'n_clicks'),
     Input('close-modal-x', 'n_clicks')],
    [State('selected-account', 'data')]
)
def toggle_modal(selected_rows, close_clicks, close_x_clicks, stored_account):
    ctx = callback_context
    
    if not ctx.triggered:
        return 'fixed inset-0 bg-gradient-to-br from-gray-900/80 to-slate-900/80 backdrop-blur-sm z-40 hidden', "", "", [], "", None
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Close modal
    if trigger_id in ['close-modal', 'close-modal-x']:
        return 'fixed inset-0 bg-gradient-to-br from-gray-900/80 to-slate-900/80 backdrop-blur-sm z-40 hidden', "", "", [], "", None
    
    # Open modal with route info
    if trigger_id == 'account-table' and selected_rows:
        account = accounts_data[selected_rows[0]]['account']
        routes_data = get_routes_data(account)
        
        if not routes_data:
            body_content = html.Div(className="text-center py-12", children=[
                html.Div("📭", className="text-6xl mb-4"),
                html.P("No routes configured for this account", className="text-gray-500 text-lg")
            ])
            footer_info = "Total Routes: 0"
        else:
            body_content = html.Div(className="space-y-4", children=[
                create_route_card(route) for route in routes_data
            ])
            footer_info = f"Total Routes: {len(routes_data)}"
        
        title = "Trading Routes"
        subtitle = f"Configured routing rules for account {account}"
        
        return (
            'fixed inset-0 bg-gradient-to-br from-gray-900/80 to-slate-900/80 backdrop-blur-sm z-40',
            title,
            subtitle,
            body_content,
            footer_info,
            account
        )
    
    return 'fixed inset-0 bg-gradient-to-br from-gray-900/80 to-slate-900/80 backdrop-blur-sm z-40 hidden', "", "", [], "", stored_account

if __name__ == '__main__':
    app.run(debug=True)
