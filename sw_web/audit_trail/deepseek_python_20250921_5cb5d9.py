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
                          className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition duration-200 mr-2"
                ),
                html.Button("Timeline", 
                          id='timeline-button',
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
        
        # Order Chain Information
        html.Div([
            html.Div([
                html.H2("Order Chain Relationships", className="text-xl font-semibold text-gray-800 mb-4"),
                html.Div(id='order-chain-info', className="space-y-4")
            ], className="bg-white p-6 rounded-xl shadow-sm")
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
            html.Div([
                html.H2("Execution Timeline", className="text-2xl font-bold text-gray-800 mb-6"),
                dcc.Graph(id='timeline-graph', className="rounded-lg bg-white p-4 shadow-sm")
            ], className="p-6")
        ])
    ]),
    
    # Store for sharing data between pages
    dcc.Store(id='audit-data-store'),
    dcc.Store(id='orders-store'),
    dcc.Store(id='replacement-chains-store'),
    dcc.Store(id='order-id-map-store')
], className="min-h-screen pt-16")  # Add padding-top to account for sticky header

def parse_fix_message(line):
    """Parse a FIX message line and return a dictionary of tag-value pairs."""
    fix_data = {}
    if 'Sending : ' in line or 'Receiving : ' in line:
        fix_part = line.split(':', 2)[-1].strip()
        for field in fix_part.split('|'):
            if '=' in field:
                tag, value = field.split('=', 1)
                try:
                    fix_data[int(tag)] = value
                except ValueError:
                    fix_data[tag] = value
    return fix_data

def process_fix_log(log_content):
    """Process FIX log content and return structured data."""
    orders = defaultdict(list)
    replacement_chains = {}
    order_id_map = {}  # Map ClOrdID to OrderID (Tag 37)
    lines = log_content.split('\n')
    
    for line in lines:
        if not line.strip():
            continue
            
        try:
            # Extract timestamp
            timestamp_str = line.split(' ')[0] + ' ' + line.split(' ')[1].split('_')[0]
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
            
            direction = 'OUT' if 'Sending : ' in line else 'IN'
            connector = line.split(']')[1].strip().strip('[]') if ']' in line else 'Unknown'
            
            fix_data = parse_fix_message(line)
            msg_type = fix_data.get(35, '')
            
            if msg_type in ['D', 'G', 'F', '8']:
                cl_ord_id = fix_data.get(11, '')
                orig_cl_ord_id = fix_data.get(41, '')
                order_id = fix_data.get(37, '')  # Tag 37 - OrderID
                avg_px = fix_data.get(6, '')  # Tag 6 - AvgPx
                
                event = {
                    'timestamp': timestamp,
                    'direction': direction,
                    'connector': connector,
                    'msg_type': msg_type,
                    'cl_ord_id': cl_ord_id,
                    'orig_cl_ord_id': orig_cl_ord_id,
                    'order_id': order_id,  # Tag 37
                    'order_qty': fix_data.get(38, ''),
                    'cum_qty': fix_data.get(14, ''),
                    'price': fix_data.get(6, ''),
                    'avg_px': avg_px,  # Tag 6 - AvgPx
                    'exec_type': fix_data.get(150, '0'),
                    'ord_status': fix_data.get(39, '0'),  # Tag 39 - OrdStatus
                    'symbol': fix_data.get(48, ''),
                    'raw_line': line.strip()
                }
                
                # Track OrderID mapping
                if order_id and cl_ord_id:
                    order_id_map[cl_ord_id] = order_id
                
                # Track replacement relationships
                if msg_type in ['G', 'F'] and orig_cl_ord_id and cl_ord_id:
                    replacement_chains[cl_ord_id] = orig_cl_ord_id
                
                if cl_ord_id:
                    orders[cl_ord_id].append(event)
                    
        except Exception as e:
            continue
            
    return orders, replacement_chains, order_id_map

def build_order_hierarchy_text(replacement_chains, order_id_map):
    """Build plain text representation of order hierarchy with Tag 37 tracking."""
    if not replacement_chains:
        return html.Div([
            html.H3("No order replacements found.", className="font-semibold text-gray-700")
        ])
    
    # Find root orders (orders that were never children)
    children = set(replacement_chains.keys())
    parents = set(replacement_chains.values())
    root_orders = parents - children
    
    hierarchy_sections = []
    
    # Client Order ID Chain (Tag 11)
    client_chains = []
    for root in sorted(root_orders):
        current = root
        chain = [current]
        
        while current in replacement_chains.values():
            children_of_current = [child for child, parent in replacement_chains.items() if parent == current]
            if children_of_current:
                current = children_of_current[0]
                chain.append(current)
            else:
                break
        
        client_chains.append(" → ".join(chain))
    
    # Order ID Chain (Tag 37) - Broker's perspective
    order_id_chains = []
    for root in sorted(root_orders):
        current = root
        chain = []
        
        while current:
            order_id = order_id_map.get(current)
            if order_id:
                chain.append(order_id)
            
            if current in replacement_chains.values():
                children_of_current = [child for child, parent in replacement_chains.items() if parent == current]
                if children_of_current:
                    current = children_of_current[0]
                else:
                    break
            else:
                break
        
        if chain:
            order_id_chains.append(" → ".join(chain))
    
    hierarchy_sections.append(
        html.Div([
            html.H3("Client Order ID Chain (Tag 11 - ClOrdID):", 
                   className="font-semibold text-gray-700 mb-2"),
            html.Pre("\n".join(client_chains), 
                   className="bg-gray-800 text-green-400 p-4 rounded-lg overflow-x-auto mb-4")
        ])
    )
    
    if order_id_chains:
        hierarchy_sections.append(
            html.Div([
                html.H3("Broker Order ID Chain (Tag 37 - OrderID):", 
                       className="font-semibold text-gray-700 mb-2"),
                html.Pre("\n".join(order_id_chains), 
                       className="bg-blue-900 text-yellow-400 p-4 rounded-lg overflow-x-auto")
            ])
        )
    
    return html.Div(hierarchy_sections)

def calculate_avg_px(audit_data):
    """Calculate average price from execution data using Tag 6 (AvgPx)."""
    avg_px_values = []
    
    for event in audit_data:
        if (event['msg_type'] == 'Execution Report' and 
            event['raw_event']['avg_px'] and 
            event['raw_event']['avg_px'] != '0'):
            
            try:
                avg_px = float(event['raw_event']['avg_px'])
                avg_px_values.append(avg_px)
            except (ValueError, TypeError):
                continue
    
    # Return the last AvgPx value (most recent execution)
    return avg_px_values[-1] if avg_px_values else 0

def get_final_order_status(orders):
    """Get the final status of the order from the last execution report."""
    final_status = "Unknown"
    
    for order_id, events in orders.items():
        # Sort events by timestamp to get the most recent one
        events.sort(key=lambda x: x['timestamp'])
        
        for event in reversed(events):
            if event['msg_type'] == '8':  # Execution Report
                ord_status = event.get('ord_status', '0')
                status_map = {
                    '0': 'New',
                    '1': 'Partially Filled',
                    '2': 'Filled',
                    '4': 'Canceled',
                    '5': 'Replaced',
                    '6': 'Pending Cancel',
                    '8': 'Rejected',
                    'A': 'Pending New',
                    'C': 'Expired',
                    'E': 'Pending Replace'
                }
                final_status = status_map.get(ord_status, f'Unknown ({ord_status})')
                break
    
    return final_status

def generate_audit_data(orders):
    """Generate audit trail data from parsed orders."""
    audit_data = []
    all_events = []
    
    for order_id, events in orders.items():
        all_events.extend(events)
    
    # Sort by timestamp
    all_events.sort(key=lambda x: x['timestamp'])
    
    for event in all_events:
        msg_type_desc = {
            'D': 'New Order',
            'G': 'Replace Request',
            'F': 'Cancel Request',
            '8': 'Execution Report'
        }.get(event['msg_type'], 'Unknown')
        
        status_desc = {
            '0': 'New',
            '1': 'Partial Fill',
            '2': 'Filled',
            '4': 'Canceled',
            '5': 'Replaced',
            '6': 'Pending Cancel',
            '8': 'Rejected',
            'A': 'Pending New',
            'C': 'Expired',
            'E': 'Pending Replace'
        }.get(event['ord_status'], f'Unknown ({event["ord_status"]})')
        
        audit_data.append({
            'timestamp': event['timestamp'].strftime('%H:%M:%S.%f')[:-3],
            'msg_type': msg_type_desc,
            'order_id': event['cl_ord_id'],
            'broker_order_id': event['order_id'],  # Tag 37
            'orig_order_id': event['orig_cl_ord_id'],
            'direction': 'BUY',
            'price': f"${event['price']}" if event['price'] and event['price'] != '0' else 'MARKET',
            'avg_px': f"${event['avg_px']}" if event['avg_px'] and event['avg_px'] != '0' else '-',
            'quantity': f"{int(event['order_qty']):,}" if event['order_qty'] else '0',
            'cum_qty': f"{int(event['cum_qty']):,}" if event['cum_qty'] else '0',
            'venue': 'MET Clearpool',
            'status': status_desc,
            'ord_status_code': event['ord_status'],
            'raw_event': event
        })
    
    return audit_data

def create_timeline_figure(audit_data):
    """Create a detailed timeline visualization."""
    exec_events = [e for e in audit_data if e['msg_type'] == 'Execution Report' and e['raw_event']['price'] and e['raw_event']['price'] != '0']
    
    if not exec_events:
        return go.Figure()
    
    times = [pd.to_datetime(e['timestamp']) for e in exec_events]
    prices = [float(e['raw_event']['price']) for e in exec_events]
    quantities = [int(e['raw_event'].get('14', 0)) for e in exec_events]
    order_ids = [e['order_id'] for e in exec_events]
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Price line
    fig.add_trace(
        go.Scatter(
            x=times, y=prices,
            mode='lines+markers+text',
            name='Execution Price',
            line=dict(color='#3498db', width=2),
            marker=dict(size=8, color='#3498db'),
            text=[f'${p:.2f}' for p in prices],
            textposition="top center",
            hoverinfo='text',
            hovertext=[f'Time: {t}<br>Price: ${p:.2f}<br>Order: {oid}' 
                      for t, p, oid in zip(times, prices, order_ids)]
        ),
        secondary_y=False
    )
    
    # Cumulative quantity bars
    fig.add_trace(
        go.Bar(
            x=times, y=quantities,
            name='Cumulative Quantity',
            marker_color='#2ecc71',
            opacity=0.6,
            hoverinfo='text',
            hovertext=[f'Time: {t}<br>CumQty: {q:,}<br>Order: {oid}'
                      for t, q, oid in zip(times, quantities, order_ids)]
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        title='Order Execution Timeline - Price and Cumulative Quantity',
        xaxis_title='Time',
        yaxis_title='Price ($)',
        yaxis2_title='Cumulative Quantity',
        hovermode='closest',
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=600,
        font=dict(size=12)
    )
    
    fig.update_yaxes(title_text="Price ($)", secondary_y=False)
    fig.update_yaxes(title_text="Cumulative Quantity", secondary_y=True)
    
    return fig

# Callbacks for navigation
@app.callback(
    [Output('main-content', 'className'),
     Output('timeline-content', 'className'),
     Output('audit-button', 'className'),
     Output('timeline-button', 'className')],
    [Input('audit-button', 'n_clicks'),
     Input('timeline-button', 'n_clicks')],
    prevent_initial_call=True
)
def navigate_to_page(audit_clicks, timeline_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return 'block', 'hidden', 'bg-blue-600', 'bg-gray-500'
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'audit-button':
        return 'block', 'hidden', 'bg-blue-600', 'bg-gray-500'
    elif button_id == 'timeline-button':
        return 'hidden', 'block', 'bg-gray-500', 'bg-blue-600'
    
    return 'block', 'hidden', 'bg-blue-600', 'bg-gray-500'

# Main analysis callback
@app.callback(
    [Output('total-messages', 'children'),
     Output('order-chain-id', 'children'),
     Output('symbol', 'children'),
     Output('total-quantity', 'children'),
     Output('filled-quantity', 'children'),
     Output('avg-px', 'children'),
     Output('final-status', 'children'),
     Output('order-chain-info', 'children'),
     Output('audit-table-container', 'children'),
     Output('timeline-graph', 'figure'),
     Output('audit-data-store', 'data'),
     Output('orders-store', 'data'),
     Output('replacement-chains-store', 'data'),
     Output('order-id-map-store', 'data')],
    [Input('analyze-button', 'n_clicks')],
    [State('fix-log-input', 'value')]
)
def update_output(n_clicks, log_content):
    if n_clicks == 0 or not log_content:
        return ['0', 'N/A', 'N/A', '0', '0', '$0.00', 'Unknown', "No data to display", '', go.Figure(), None, None, None, None]
    
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
            hierarchy_text,
            table,
            timeline_fig,
            store_data,
            dict(orders),
            replacement_chains,
            order_id_map
        ]
        
    except Exception as e:
        return [f"Error: {str(e)}"] * 9 + [go.Figure(), None, None, None, None]

def create_audit_table(audit_data):
    """Create HTML table for audit trail with Tailwind CSS including Broker Order ID and AvgPx."""
    # Create table header
    header = html.Thead(html.Tr([
        html.Th("Time", className="px-4 py-2 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("Type", className="px-4 py-2 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("Client Order ID", className="px-4 py-2 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("Broker Order ID", className="px-4 py-2 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("Parent ID", className="px-4 py-2 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("Price", className="px-4 py-2 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("AvgPx", className="px-4 py-2 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("Qty", className="px-4 py-2 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("Cum Qty", className="px-4 py-2 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("Status", className="px-4 py-2 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("Status Code", className="px-4 py-2 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider")
    ]))
    
    # Create table rows
    rows = []
    for event in audit_data:
        # Determine message type styling
        msg_type_class = {
            'New Order': 'bg-green-100 text-green-800',
            'Execution Report': 'bg-blue-100 text-blue-800',
            'Replace Request': 'bg-yellow-100 text-yellow-800',
            'Cancel Request': 'bg-red-100 text-red-800'
        }.get(event['msg_type'], 'bg-gray-100 text-gray-800')
        
        # Determine status styling
        status_class = ""
        if 'Filled' in event['status']:
            status_class = "bg-green-100 text-green-800"
        elif 'Cancel' in event['status']:
            status_class = "bg-red-100 text-red-800"
        elif 'Pending' in event['status']:
            status_class = "bg-yellow-100 text-yellow-800"
        elif 'Rejected' in event['status']:
            status_class = "bg-red-100 text-red-800"
        
        row = html.Tr(className="hover:bg-gray-50", children=[
            html.Td(event['timestamp'], className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 font-mono"),
            html.Td(
                html.Span(event['msg_type'], className=f"px-2 py-1 text-xs font-medium rounded-full {msg_type_class}"),
                className="px-4 py-2 whitespace-nowrap"
            ),
            html.Td(event['order_id'], className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 font-mono font-semibold"),
            html.Td(event['broker_order_id'] or '-', className="px-4 py-2 whitespace-nowrap text-sm text-blue-600 font-mono"),
            html.Td(event['orig_order_id'] or '-', className="px-4 py-2 whitespace-nowrap text-sm text-gray-600 font-mono"),
            html.Td(event['price'], className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 font-mono font-semibold"),
            html.Td(event['avg_px'], className="px-4 py-2 whitespace-nowrap text-sm text-purple-600 font-mono font-semibold"),
            html.Td(event['quantity'], className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 font-mono"),
            html.Td(event['cum_qty'], className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 font-mono font-semibold"),
            html.Td(
                html.Span(event['status'], className=f"px-2 py-1 text-xs font-medium rounded-full {status_class}"),
                className="px-4 py-2 whitespace-nowrap"
            ),
            html.Td(event['ord_status_code'], className="px-4 py-2 whitespace-nowrap text-sm text-gray-500 font-mono")
        ])
        rows.append(row)
    
    table_body = html.Tbody(rows, className="bg-white divide-y divide-gray-200")
    
    return html.Table(
        [header, table_body],
        className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg text-xs"
    )

if __name__ == '__main__':
    app.run(debug=True)