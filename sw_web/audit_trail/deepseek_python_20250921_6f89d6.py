import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import re
from datetime import datetime
from collections import defaultdict
import plotly.graph_objects as go
from plotly.subplots import make_subplots

app = dash.Dash(__name__)
app.title = "FIX Order Audit Trail Analyzer"

# External CSS for Tailwind (using CDN)
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
    # Sticky Header
    html.Div([
        html.Div([
            # Left side: Logo/Title
            html.Div([
                html.H1("FIX Order Audit Trail Analyzer", 
                       className="text-xl font-bold text-white"),
            ], className="flex-shrink-0"),
            
            # Right side: Navigation Buttons
            html.Div([
                html.Button("Order Audit Trail", 
                          id='audit-button',
                          n_clicks=0,
                          className="bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition duration-200 mr-2"
                ),
                html.Button("Timeline", 
                          id='timeline-button',
                          n_clicks=0,
                          className="bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg transition duration-200"
                ),
            ], className="flex space-x-2"),
        ], className="flex justify-between items-center w-full max-w-7xl mx-auto px-4")
    ], className="bg-gradient-to-r from-blue-600 to-purple-700 p-4 shadow-lg sticky top-0 z-50"),
    
    # Main Content Area
    html.Div(id='main-content', children=[
        # Input Section
        html.Div([
            html.Div([
                html.H2("Input FIX Log Content", className="text-xl font-semibold text-gray-800 mb-4"),
                dcc.Textarea(
                    id='fix-log-input',
                    placeholder='Paste your FIX log content here...',
                    className="w-full h-48 p-3 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                ),
                html.Button("Analyze Log", 
                          id='analyze-button', 
                          className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition duration-200 shadow-md"
                )
            ], className="bg-white p-6 rounded-xl shadow-sm")
        ], className="p-6"),
        
        # Summary Cards
        html.Div([
            html.Div([
                # Total Messages
                html.Div([
                    html.H3("Total Messages", className="text-sm font-medium text-gray-600 uppercase tracking-wider"),
                    html.H2(id='total-messages', className="text-2xl font-bold text-blue-600")
                ], className="bg-white p-4 rounded-lg shadow-sm border-l-4 border-blue-500"),
                
                # Order Chain ID
                html.Div([
                    html.H3("Order Chain ID", className="text-sm font-medium text-gray-600 uppercase tracking-wider"),
                    html.H2(id='order-chain-id', className="text-2xl font-bold text-green-600 font-mono")
                ], className="bg-white p-4 rounded-lg shadow-sm border-l-4 border-green-500"),
                
                # Symbol
                html.Div([
                    html.H3("Symbol", className="text-sm font-medium text-gray-600 uppercase tracking-wider"),
                    html.H2(id='symbol', className="text-2xl font-bold text-purple-600")
                ], className="bg-white p-4 rounded-lg shadow-sm border-l-4 border-purple-500"),
                
                # Total Quantity
                html.Div([
                    html.H3("Total Quantity", className="text-sm font-medium text-gray-600 uppercase tracking-wider"),
                    html.H2(id='total-quantity', className="text-2xl font-bold text-orange-600")
                ], className="bg-white p-4 rounded-lg shadow-sm border-l-4 border-orange-500"),
                
                # Filled Quantity
                html.Div([
                    html.H3("Filled Quantity", className="text-sm font-medium text-gray-600 uppercase tracking-wider"),
                    html.H2(id='filled-quantity', className="text-2xl font-bold text-red-600")
                ], className="bg-white p-4 rounded-lg shadow-sm border-l-4 border-red-500"),
                
                # Average Price (avg_px)
                html.Div([
                    html.H3("Average Price", className="text-sm font-medium text-gray-600 uppercase tracking-wider"),
                    html.H2(id='avg-px', className="text-2xl font-bold text-indigo-600")
                ], className="bg-white p-4 rounded-lg shadow-sm border-l-4 border-indigo-500"),
                
                # Final Order Status
                html.Div([
                    html.H3("Final Status", className="text-sm font-medium text-gray-600 uppercase tracking-wider"),
                    html.H2(id='final-status', className="text-2xl font-bold text-pink-600")
                ], className="bg-white p-4 rounded-lg shadow-sm border-l-4 border-pink-500"),
            ], className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-7 gap-4")
        ], className="px-6 pb-6"),
        
        # Audit Trail Table
        html.Div([
            html.Div([
                html.H2("Order Audit Trail", className="text-xl font-semibold text-gray-800 mb-4"),
                html.Div(id='audit-table-container', className="overflow-x-auto")
            ], className="bg-white p-6 rounded-xl shadow-sm")
        ], className="px-6 pb-6")
    ]),
    
    # Timeline Page (initially hidden)
    html.Div(id='timeline-content', className='hidden', children=[
        html.Div([
            # Execution Timeline Graph
            html.Div([
                html.H2("Execution Timeline", className="text-2xl font-bold text-gray-800 mb-6"),
                dcc.Graph(id='timeline-graph', className="rounded-lg bg-white p-4 shadow-sm")
            ], className="p-6 mb-6"),
            
            # Order Chain Relationships (moved to timeline page)
            html.Div([
                html.H2("Order Chain Relationships", className="text-2xl font-bold text-gray-800 mb-6"),
                html.Div(id='order-chain-info', className="bg-white p-6 rounded-xl shadow-sm")
            ], className="px-6")
        ])
    ]),
    
    # Store for sharing data between pages
    dcc.Store(id='audit-data-store'),
    dcc.Store(id='orders-store'),
    dcc.Store(id='replacement-chains-store'),
    dcc.Store(id='order-id-map-store')
], className="min-h-screen pt-16")  # Add padding-top to account for sticky header

# ... (keep all the existing functions: parse_fix_message, process_fix_log, build_order_hierarchy_text, 
# calculate_avg_px, get_final_order_status, generate_audit_data, create_timeline_figure, create_audit_table)
# They remain exactly the same as in the previous code

# Callbacks for navigation - FIXED VERSION
@app.callback(
    [Output('main-content', 'className'),
     Output('timeline-content', 'className'),
     Output('audit-button', 'className'),
     Output('timeline-button', 'className')],
    [Input('audit-button', 'n_clicks'),
     Input('timeline-button', 'n_clicks')],
    prevent_initial_call=False  # Allow initial call to set default state
)
def navigate_to_page(audit_clicks, timeline_clicks):
    ctx = callback_context
    
    # Default state - show audit page
    if not ctx.triggered:
        return 'block', 'hidden', 'bg-blue-600', 'bg-gray-500'
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'audit-button':
        return 'block', 'hidden', 'bg-blue-600', 'bg-gray-500'
    elif button_id == 'timeline-button':
        return 'hidden', 'block', 'bg-gray-500', 'bg-blue-600'
    
    return 'block', 'hidden', 'bg-blue-600', 'bg-gray-500'

# Main analysis callback - UPDATED to remove order-chain-info from main output
@app.callback(
    [Output('total-messages', 'children'),
     Output('order-chain-id', 'children'),
     Output('symbol', 'children'),
     Output('total-quantity', 'children'),
     Output('filled-quantity', 'children'),
     Output('avg-px', 'children'),
     Output('final-status', 'children'),
     Output('audit-table-container', 'children'),
     Output('timeline-graph', 'figure'),
     Output('order-chain-info', 'children'),  # This now goes to timeline page
     Output('audit-data-store', 'data'),
     Output('orders-store', 'data'),
     Output('replacement-chains-store', 'data'),
     Output('order-id-map-store', 'data')],
    [Input('analyze-button', 'n_clicks')],
    [State('fix-log-input', 'value')]
)
def update_output(n_clicks, log_content):
    if n_clicks == 0 or not log_content:
        return ['0', 'N/A', 'N/A', '0', '0', '$0.00', 'Unknown', '', go.Figure(), "No data to display", None, None, None, None]
    
    try:
        orders, replacement_chains, order_id_map = process_fix_log(log_content)
        audit_data = generate_audit_data(orders)
        
        # Calculate summary statistics
        total_messages = len(audit_data)
        
        # Build order hierarchy text with Tag 37 tracking
        hierarchy_text = build_order_hierarchy_text(replacement_chains, order_id_map)
        order_chain = next(iter(replacement_chains.values())) if replacement_chains else list(orders.keys())[0] if orders else 'N/A'
        
        # Find symbol
        symbol = 'BRXYZ91'
        for events in orders.values():
            for event in events:
                if event.get('symbol'):
                    symbol = event['symbol']
                    break
        
        # Calculate total and filled quantities
        total_qty = 0
        filled_qty = 0
        
        for events in orders.values():
            for event in events:
                if event.get('order_qty'):
                    try:
                        total_qty = max(total_qty, int(event['order_qty']))
                    except:
                        pass
                if event.get('cum_qty'):
                    try:
                        filled_qty = max(filled_qty, int(event['cum_qty']))
                    except:
                        pass
        
        # Calculate average price using Tag 6 (AvgPx)
        avg_px = calculate_avg_px(audit_data)
        
        # Get final order status
        final_status = get_final_order_status(orders)
        
        # Create audit table
        table = create_audit_table(audit_data)
        
        # Create timeline figure
        timeline_fig = create_timeline_figure(audit_data)
        
        # Store data for other pages
        store_data = {
            'audit_data': audit_data,
            'orders': {k: v for k, v in orders.items()},
            'replacement_chains': replacement_chains,
            'order_id_map': order_id_map
        }
        
        return [
            f"{total_messages}",
            order_chain,
            symbol,
            f"{total_qty:,}",
            f"{filled_qty:,}",
            f"${avg_px:.2f}" if avg_px > 0 else "$0.00",
            final_status,
            table,
            timeline_fig,
            hierarchy_text,  # This goes to timeline page now
            store_data,
            dict(orders),
            replacement_chains,
            order_id_map
        ]
        
    except Exception as e:
        return [f"Error: {str(e)}"] * 8 + [go.Figure(), f"Error: {str(e)}", None, None, None, None]

# Keep all the existing functions exactly as they were...
# parse_fix_message, process_fix_log, build_order_hierarchy_text, calculate_avg_px, 
# get_final_order_status, generate_audit_data, create_timeline_figure, create_audit_table

if __name__ == '__main__':
    app.run(debug=True)