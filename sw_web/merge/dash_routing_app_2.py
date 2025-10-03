import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc

# Routing table lookup dictionary
routing_table = {
    'ARTISANMZHO': [
        {'CURRENCY': '*', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': 'SI', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'USD', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'FlexTradeBuySide42'},
        {'CURRENCY': 'CAD', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'FlexTradeBuySide42'},
        {'CURRENCY': 'AUD', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'CNH', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'CNY', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'HKD', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'IDR', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'INR', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'JPY', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'KRW', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'MYR', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'NZD', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'PHP', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'SGD', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'THB', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'TWD', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
    ],
    'PRIMECAP': [
        {'CURRENCY': 'USD', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'FlexTradeBuySide42'},
        {'CURRENCY': 'CAD', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'FlexTradeBuySide42'},
    ],
    'OSTERS': [
        {'CURRENCY': '*', 'TARGETSUBID': 'PT', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'O_FLEXTRADE_GLOBAL_PT_FIX42'},
    ],
    'THORNTREE': [
        {'CURRENCY': '*', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': 'SI', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'USD', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'FlexTradeBuySide42'},
        {'CURRENCY': 'CAD', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'FlexTradeBuySide42'},
        {'CURRENCY': 'AUD', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'CNH', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'CNY', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'HKD', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'IDR', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'INR', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'JPY', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'KRW', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'MYR', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'NZD', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'PHP', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'SGD', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'THB', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
        {'CURRENCY': 'TWD', 'TARGETSUBID': '*', 'DELIVERTTOSUBID': '*', 'FIX.5847': '*', 'ETF': '*', 'COUNTRYCODE': '*', 'DESTINATION': 'MizuhoTKGOR42BuySide'},
    ]
}


def get_routes(key):
    """
    Returns currency-to-destination routes for a given ONBEHALFOFCOMPTID key.
    Combines currencies with the same destination together.
    """
    routes = routing_table.get(key)
    if not routes:
        return None
    
    # Group routes by destination and conditions
    route_groups = {}
    for route in routes:
        # Check for non-wildcard conditions
        conditions = []
        for field in ['TARGETSUBID', 'DELIVERTTOSUBID', 'FIX.5847', 'ETF', 'COUNTRYCODE']:
            if route.get(field) and route[field] != '*':
                conditions.append(f"{field}={route[field]}")
        
        # Create a key for grouping
        if conditions:
            group_key = (route['DESTINATION'], ', '.join(conditions))
        else:
            group_key = (route['DESTINATION'], None)
        
        # Add currency to the group
        if group_key not in route_groups:
            route_groups[group_key] = []
        route_groups[group_key].append(route['CURRENCY'])
    
    # Build the route strings
    route_strings = []
    for (destination, conditions), currencies in route_groups.items():
        if conditions:
            route_str = f"{conditions} -> {destination}"
        else:
            currency_list = ','.join(currencies)
            route_str = f"CURRENCY={currency_list} -> {destination}"
        
        route_strings.append(route_str)
    
    return route_strings


# Mock client data
client_data = [
    {'id': 1, 'client_id': 'ARTISANMZHO', 'client_name': 'Artisan Mizuho', 'status': 'Active', 'region': 'APAC'},
    {'id': 2, 'client_id': 'PRIMECAP', 'client_name': 'Primecap Management', 'status': 'Active', 'region': 'Americas'},
    {'id': 3, 'client_id': 'OSTERS', 'client_name': 'Osters Capital', 'status': 'Active', 'region': 'EMEA'},
    {'id': 4, 'client_id': 'THORNTREE', 'client_name': 'Thorntree Capital', 'status': 'Active', 'region': 'APAC'},
]

# Initialize Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = dbc.Container([
    # Tailwind CSS
    html.Link(
        rel='stylesheet',
        href='https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css'
    ),
    
    html.Div([
        html.H1('Client Routing Configuration', className='text-3xl font-bold text-gray-800 mb-6 mt-6'),
        
        html.Div([
            dash_table.DataTable(
                id='client-table',
                columns=[
                    {'name': 'ID', 'id': 'id'},
                    {'name': 'Client ID', 'id': 'client_id'},
                    {'name': 'Client Name', 'id': 'client_name'},
                    {'name': 'Status', 'id': 'status'},
                    {'name': 'Region', 'id': 'region'},
                ],
                data=client_data,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '12px',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '14px',
                },
                style_header={
                    'backgroundColor': '#3B82F6',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'fontSize': '14px',
                },
                style_data={
                    'backgroundColor': 'white',
                    'color': '#374151',
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#F9FAFB',
                    },
                    {
                        'if': {'state': 'active'},
                        'backgroundColor': '#DBEAFE',
                        'border': '1px solid #3B82F6',
                    }
                ],
                row_selectable='single',
                selected_rows=[],
            ),
        ], className='bg-white rounded-lg shadow-md p-4'),
    ], className='container mx-auto px-4'),
    
    # Modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(id='modal-title', className='text-xl font-bold')),
        dbc.ModalBody([
            html.Div(id='modal-content', className='space-y-2')
        ]),
        dbc.ModalFooter(
            dbc.Button('Close', id='close-modal', className='bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded')
        ),
    ], id='routing-modal', size='lg', is_open=False),
    
], fluid=True, className='bg-gray-50 min-h-screen')


# Callback to open modal when row is clicked
@app.callback(
    [Output('routing-modal', 'is_open'),
     Output('modal-title', 'children'),
     Output('modal-content', 'children'),
     Output('client-table', 'selected_rows')],
    [Input('client-table', 'selected_rows'),
     Input('close-modal', 'n_clicks')],
    [State('routing-modal', 'is_open'),
     State('client-table', 'data')],
    prevent_initial_call=True
)
def toggle_modal(selected_rows, n_clicks, is_open, table_data):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return False, '', [], []
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Close modal and clear selection
    if trigger_id == 'close-modal':
        return False, '', [], []
    
    # Open modal with routing info
    if trigger_id == 'client-table' and selected_rows:
        row_index = selected_rows[0]
        client = table_data[row_index]
        client_id = client['client_id']
        client_name = client['client_name']
        
        routes = get_routes(client_id)
        
        if routes:
            route_elements = [
                html.Div([
                    html.Span('→ ', className='text-blue-600 font-bold mr-2'),
                    html.Span(route, className='text-gray-700 font-mono text-sm')
                ], className='bg-gray-50 p-3 rounded border-l-4 border-blue-500')
                for route in routes
            ]
        else:
            route_elements = [
                html.Div('No routes found for this client.', className='text-gray-500 italic')
            ]
        
        return True, f'Routing Configuration: {client_name} ({client_id})', route_elements, selected_rows
    
    return is_open, '', [], []


if __name__ == '__main__':
    app.run(debug=True, port=8050)
