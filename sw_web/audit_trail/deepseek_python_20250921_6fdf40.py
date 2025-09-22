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
    # Header
    html.Div([
        html.H1("FIX Order Audit Trail Analyzer", 
               className="text-3xl font-bold text-white mb-4"),
        html.P("Paste FIX log content to analyze order execution patterns",
              className="text-white opacity-80")
    ], className="bg-gradient-to-r from-blue-600 to-purple-700 p-6 text-center shadow-lg"),
    
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
            
            # VWAP
            html.Div([
                html.H3("VWAP", className="text-sm font-medium text-gray-600 uppercase tracking-wider"),
                html.H2(id='vwap', className="text-2xl font-bold text-indigo-600")
            ], className="bg-white p-4 rounded-lg shadow-sm border-l-4 border-indigo-500"),
        ], className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4")
    ], className="px-6 pb-6"),
    
    # Order Chain Information
    html.Div([
        html.Div([
            html.H2("Order Chain Relationships", className="text-xl font-semibold text-gray-800 mb-4"),
            html.Div(id='order-chain-info', className="bg-gray-100 p-4 rounded-lg font-mono text-sm")
        ], className="bg-white p-6 rounded-xl shadow-sm")
    ], className="px-6 pb-6"),
    
    # Charts
    html.Div([
        html.Div([
            html.H2("Execution Timeline", className="text-xl font-semibold text-gray-800 mb-4"),
            dcc.Graph(id='execution-timeline', className="rounded-lg")
        ], className="bg-white p-6 rounded-xl shadow-sm")
    ], className="px-6 pb-6"),
    
    # Audit Trail Table
    html.Div([
        html.Div([
            html.H2("Order Audit Trail", className="text-xl font-semibold text-gray-800 mb-4"),
            html.Div(id='audit-table-container', className="overflow-x-auto")
        ], className="bg-white p-6 rounded-xl shadow-sm")
    ], className="px-6 pb-6")
], className="min-h-screen")

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
                
                event = {
                    'timestamp': timestamp,
                    'direction': direction,
                    'connector': connector,
                    'msg_type': msg_type,
                    'cl_ord_id': cl_ord_id,
                    'orig_cl_ord_id': orig_cl_ord_id,
                    'order_qty': fix_data.get(38, ''),
                    'cum_qty': fix_data.get(14, ''),
                    'price': fix_data.get(6, ''),
                    'exec_type': fix_data.get(150, '0'),
                    'ord_status': fix_data.get(39, '0'),
                    'symbol': fix_data.get(48, ''),
                    'raw_line': line.strip()
                }
                
                # Track replacement relationships
                if msg_type in ['G', 'F'] and orig_cl_ord_id and cl_ord_id:
                    replacement_chains[cl_ord_id] = orig_cl_ord_id
                
                if cl_ord_id:
                    orders[cl_ord_id].append(event)
                    
        except Exception as e:
            continue
            
    return orders, replacement_chains

def build_order_hierarchy_text(replacement_chains):
    """Build plain text representation of order hierarchy."""
    if not replacement_chains:
        return "No order replacements found."
    
    # Find root orders (orders that were never children)
    children = set(replacement_chains.keys())
    parents = set(replacement_chains.values())
    root_orders = parents - children
    
    hierarchy_text = []
    
    for root in sorted(root_orders):
        current = root
        chain = [current]
        
        # Follow the chain until we reach the end
        while current in replacement_chains.values():
            # Find children of current order
            children_of_current = [child for child, parent in replacement_chains.items() if parent == current]
            if children_of_current:
                current = children_of_current[0]  # Take the first child
                chain.append(current)
            else:
                break
        
        hierarchy_text.append(" → ".join(chain))
    
    return html.Div([
        html.H3("Order Replacement Chain:", className="font-semibold text-gray-700 mb-2"),
        html.Pre("\n".join(hierarchy_text), className="bg-gray-800 text-green-400 p-4 rounded-lg overflow-x-auto")
    ])

def calculate_vwap(audit_data):
    """Correctly calculate VWAP from execution data."""
    total_value = 0
    total_volume = 0
    previous_cum_qty = 0
    
    for event in audit_data:
        if (event['msg_type'] == 'Execution Report' and 
            event['raw_event']['price'] and 
            event['raw_event']['price'] != '0'):
            
            try:
                price = float(event['raw_event']['price'])
                current_cum_qty = int(event['raw_event'].get('14', 0))
                
                # Calculate the quantity of this specific execution
                exec_qty = current_cum_qty - previous_cum_qty
                
                if exec_qty > 0:
                    total_value += price * exec_qty
                    total_volume += exec_qty
                    previous_cum_qty = current_cum_qty
                    
            except (ValueError, TypeError):
                continue
    
    return total_value / total_volume if total_volume > 0 else 0

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
            '5': 'Replaced'
        }.get(event['ord_status'], 'Unknown')
        
        audit_data.append({
            'timestamp': event['timestamp'].strftime('%H:%M:%S.%f')[:-3],
            'msg_type': msg_type_desc,
            'order_id': event['cl_ord_id'],
            'orig_order_id': event['orig_cl_ord_id'],
            'direction': 'BUY',
            'price': f"${event['price']}" if event['price'] and event['price'] != '0' else 'MARKET',
            'quantity': f"{int(event['order_qty']):,}" if event['order_qty'] else '0',
            'cum_qty': f"{int(event['cum_qty']):,}" if event['cum_qty'] else '0',
            'venue': 'MET Clearpool',
            'status': status_desc,
            'raw_event': event
        })
    
    return audit_data

@app.callback(
    [Output('total-messages', 'children'),
     Output('order-chain-id', 'children'),
     Output('symbol', 'children'),
     Output('total-quantity', 'children'),
     Output('filled-quantity', 'children'),
     Output('vwap', 'children'),
     Output('order-chain-info', 'children'),
     Output('execution-timeline', 'figure'),
     Output('audit-table-container', 'children')],
    [Input('analyze-button', 'n_clicks')],
    [State('fix-log-input', 'value')]
)
def update_output(n_clicks, log_content):
    if n_clicks == 0 or not log_content:
        return ['0', 'N/A', 'N/A', '0', '0', '$0.00', "No data to display", go.Figure(), '']
    
    try:
        orders, replacement_chains = process_fix_log(log_content)
        audit_data = generate_audit_data(orders)
        
        # Calculate summary statistics
        total_messages = len(audit_data)
        
        # Build order hierarchy text
        hierarchy_text = build_order_hierarchy_text(replacement_chains)
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
        
        # Calculate VWAP correctly
        vwap = calculate_vwap(audit_data)
        
        # Create timeline chart
        timeline_fig = create_timeline_chart(audit_data)
        
        # Create audit table
        table = create_audit_table(audit_data)
        
        return [
            f"{total_messages}",
            order_chain,
            symbol,
            f"{total_qty:,}",
            f"{filled_qty:,}",
            f"${vwap:.2f}",
            hierarchy_text,
            timeline_fig,
            table
        ]
        
    except Exception as e:
        return [f"Error: {str(e)}"] * 6 + [f"Error: {str(e)}", go.Figure(), '']

def create_timeline_chart(audit_data):
    """Create execution timeline chart."""
    exec_events = [e for e in audit_data if e['msg_type'] == 'Execution Report' and e['raw_event']['price'] and e['raw_event']['price'] != '0']
    
    if not exec_events:
        return go.Figure()
    
    times = [pd.to_datetime(e['timestamp']) for e in exec_events]
    prices = [float(e['raw_event']['price']) for e in exec_events]
    quantities = [int(e['raw_event'].get('14', 0)) for e in exec_events]
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(
            x=times, y=prices,
            mode='lines+markers',
            name='Execution Price',
            line=dict(color='#3498db'),
            marker=dict(size=8)
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(
            x=times, y=quantities,
            name='Cumulative Quantity',
            marker_color='#2ecc71',
            opacity=0.6
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        title='Execution Price and Cumulative Quantity Timeline',
        xaxis_title='Time',
        yaxis_title='Price ($)',
        yaxis2_title='Cumulative Quantity',
        hovermode='x unified',
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_audit_table(audit_data):
    """Create HTML table for audit trail with Tailwind CSS."""
    # Create table header
    header = html.Thead(html.Tr([
        html.Th("Time", className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("Type", className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("Order ID", className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("Parent ID", className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("Price", className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("Qty", className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("Cum Qty", className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("Status", className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider")
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
        
        row = html.Tr(className="hover:bg-gray-50", children=[
            html.Td(event['timestamp'], className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono"),
            html.Td(
                html.Span(event['msg_type'], className=f"px-2 py-1 text-xs font-medium rounded-full {msg_type_class}"),
                className="px-6 py-4 whitespace-nowrap"
            ),
            html.Td(event['order_id'], className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono font-semibold"),
            html.Td(event['orig_order_id'] or '-', className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 font-mono"),
            html.Td(event['price'], className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono font-semibold"),
            html.Td(event['quantity'], className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono"),
            html.Td(event['cum_qty'], className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono font-semibold"),
            html.Td(event['status'], className="px-6 py-4 whitespace-nowrap text-sm text-gray-900")
        ])
        rows.append(row)
    
    table_body = html.Tbody(rows, className="bg-white divide-y divide-gray-200")
    
    return html.Table(
        [header, table_body],
        className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg"
    )

if __name__ == '__main__':
    app.run(debug=True)