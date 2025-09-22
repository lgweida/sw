import dash
from dash import dcc, html, Input, Output, State, callback_context
import pandas as pd
import re
from datetime import datetime
from collections import defaultdict
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

app = dash.Dash(__name__)
app.title = "FIX Order Audit Trail Analyzer"

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
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        fontFamily: {
                            'mono': ['Monaco', 'Menlo', 'Ubuntu Mono', 'monospace'],
                        }
                    }
                }
            }
        </script>
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
              className="text-gray-300")
    ], className="bg-gray-800 text-white py-8 px-6 text-center"),
    
    html.Div([
        # Input Section
        html.Div([
            html.Div([
                html.H2("Input FIX Log Content", 
                       className="text-lg font-semibold text-gray-800")
            ], className="bg-gray-50 px-6 py-4 border-b border-gray-200"),
            html.Div([
                dcc.Textarea(
                    id='fix-log-input',
                    placeholder='Paste your FIX log content here...',
                    className='w-full h-48 p-4 border border-gray-300 rounded-md font-mono text-sm resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                ),
                html.Button("Analyze Log", 
                           id='analyze-button', 
                           n_clicks=0,
                           className='mt-4 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed')
            ], className="p-6")
        ], className="bg-white rounded-lg shadow-lg mb-6"),
        
        # Summary Cards Container
        html.Div(id='summary-cards', className="mb-6"),
        
        # Order Chain Hierarchy
        html.Div([
            html.Div([
                html.H2("Order Chain Hierarchy", 
                       className="text-lg font-semibold text-gray-800")
            ], className="bg-gray-50 px-6 py-4 border-b border-gray-200"),
            html.Div(id='order-hierarchy-text', className="p-6")
        ], className="bg-white rounded-lg shadow-lg mb-6"),
        
        # Charts
        html.Div([
            html.Div([
                html.H2("Execution Timeline", 
                       className="text-lg font-semibold text-gray-800")
            ], className="bg-gray-50 px-6 py-4 border-b border-gray-200"),
            html.Div([
                dcc.Graph(id='execution-timeline')
            ], className="p-6")
        ], className="bg-white rounded-lg shadow-lg mb-6"),
        
        # Audit Trail Table
        html.Div([
            html.Div([
                html.H2("Order Audit Trail", 
                       className="text-lg font-semibold text-gray-800")
            ], className="bg-gray-50 px-6 py-4 border-b border-gray-200"),
            html.Div(id='audit-table-container', className="overflow-x-auto")
        ], className="bg-white rounded-lg shadow-lg")
        
    ], className="max-w-7xl mx-auto p-6")
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
    replacement_chains = {}  # Track parent-child relationships
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

def build_order_hierarchy(replacement_chains):
    """Build the complete order hierarchy from replacement chains."""
    hierarchy = defaultdict(list)
    all_orders = set()
    
    # Find all orders that are children (have parents)
    children = set(replacement_chains.keys())
    # Find all orders that are parents (have children)
    parents = set(replacement_chains.values())
    
    # Find root orders (parents that are not children)
    root_orders = parents - children
    
    # Build hierarchy
    for child, parent in replacement_chains.items():
        hierarchy[parent].append(child)
        all_orders.update([parent, child])
    
    # Add orders that don't have replacements
    for order in all_orders:
        if order not in hierarchy and order not in children:
            hierarchy[order] = []  # Standalone order
    
    return hierarchy, root_orders

def create_hierarchy_text(hierarchy, root_orders):
    """Create HTML text representation of order hierarchy."""
    if not root_orders and not hierarchy:
        return html.Div("No order hierarchy detected", 
                       className="text-gray-500 text-center py-4")
    
    def render_node(order_id, level=0):
        children = hierarchy.get(order_id, [])
        indent_class = f"ml-{level * 5}" if level > 0 else ""
        
        node_html = [
            html.Div([
                html.Span(order_id, 
                         className=f"font-mono text-sm {'font-bold text-red-700' if level == 0 else 'text-blue-700'}"),
                html.Span(f"{'(Root Order)' if level == 0 else '(Replacement)'}", 
                         className="ml-2 text-xs text-gray-600")
            ], className=f"flex items-center p-2 rounded mb-2 {indent_class} {'bg-red-100 border-l-4 border-red-500' if level == 0 else 'bg-blue-100 border-l-4 border-blue-500'}")
        ]
        
        for child_id in children:
            node_html.extend(render_node(child_id, level + 1))
        
        return node_html
    
    all_nodes = []
    if root_orders:
        for root_id in root_orders:
            all_nodes.extend(render_node(root_id))
    else:
        # Show standalone orders
        for order_id in hierarchy:
            if not hierarchy[order_id]:  # No children
                all_nodes.extend(render_node(order_id))
    
    return html.Div(all_nodes, className="space-y-2")

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
                current_cum_qty = int(event['raw_event'].get('cum_qty', 0))
                
                # Calculate the quantity of this specific execution
                exec_qty = current_cum_qty - previous_cum_qty
                
                if exec_qty > 0:  # Valid execution
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

def create_summary_cards(total_messages, order_chain, symbol, total_qty, filled_qty, vwap):
    """Create summary cards with Tailwind styling."""
    cards = [
        {"title": "Total Messages", "value": f"{total_messages}"},
        {"title": "Order Chain ID", "value": order_chain, "mono": True},
        {"title": "Symbol", "value": symbol},
        {"title": "Total Quantity", "value": f"{total_qty:,}"},
        {"title": "Filled Quantity", "value": f"{filled_qty:,}"},
        {"title": "VWAP", "value": f"${vwap:.2f}"}
    ]
    
    card_elements = []
    for card in cards:
        card_elements.append(
            html.Div([
                html.H3(card["title"], className="text-sm font-medium text-gray-500"),
                html.P(card["value"], 
                      className=f"text-2xl font-bold text-gray-900 {'font-mono text-sm' if card.get('mono') else ''}")
            ], className="bg-white p-6 rounded-lg shadow")
        )
    
    return html.Div(card_elements, 
                   className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4")

def create_timeline_chart(audit_data):
    """Create execution timeline chart."""
    exec_events = [e for e in audit_data if e['msg_type'] == 'Execution Report' 
                  and e['raw_event']['price'] and e['raw_event']['price'] != '0']
    
    if not exec_events:
        return go.Figure()
    
    times = [pd.to_datetime(e['timestamp']) for e in exec_events]
    prices = [float(e['raw_event']['price']) for e in exec_events]
    quantities = [int(e['raw_event'].get('cum_qty', 0)) for e in exec_events]
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(
            x=times, y=prices,
            mode='lines+markers',
            name='Execution Price',
            line=dict(color='#3b82f6'),
            marker=dict(size=8)
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(
            x=times, y=quantities,
            name='Cumulative Quantity',
            marker_color='#10b981',
            opacity=0.6
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        title='Execution Price and Cumulative Quantity Timeline',
        xaxis_title='Time',
        yaxis_title='Price ($)',
        hovermode='x unified',
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    fig.update_yaxes(title_text="Cumulative Quantity", secondary_y=True)
    
    return fig

def get_message_type_class(msg_type):
    """Get Tailwind classes for message type badges."""
    classes = {
        'New Order': 'bg-green-100 text-green-800',
        'Execution Report': 'bg-blue-100 text-blue-800',
        'Replace Request': 'bg-yellow-100 text-yellow-800',
        'Cancel Request': 'bg-red-100 text-red-800'
    }
    return classes.get(msg_type, 'bg-gray-100 text-gray-800')

def create_audit_table(audit_data):
    """Create HTML table for audit trail with Tailwind styling."""
    if not audit_data:
        return html.Div("No audit data available", className="text-center py-4 text-gray-500")
    
    header = html.Thead([
        html.Tr([
            html.Th("Time", className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
            html.Th("Message Type", className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
            html.Th("Order ID", className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
            html.Th("Parent Order", className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
            html.Th("Direction", className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
            html.Th("Price", className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
            html.Th("Quantity", className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
            html.Th("Cum Qty", className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
            html.Th("Venue", className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
            html.Th("Status", className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider")
        ])
    ], className="bg-gray-50")
    
    rows = []
    for event in audit_data:
        msg_type_class = get_message_type_class(event['msg_type'])
        
        row = html.Tr([
            html.Td(event['timestamp'], className="px-4 py-3 text-sm text-gray-900 font-mono"),
            html.Td([
                html.Span(event['msg_type'], 
                         className=f"inline-flex px-2 py-1 text-xs font-semibold rounded-full {msg_type_class}")
            ], className="px-4 py-3"),
            html.Td(event['order_id'], className="px-4 py-3 text-sm text-gray-900 font-mono"),
            html.Td(event['orig_order_id'] or 'N/A', className="px-4 py-3 text-sm text-gray-900 font-mono"),
            html.Td([
                html.Span(event['direction'], 
                         className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800")
            ], className="px-4 py-3"),
            html.Td(event['price'], className="px-4 py-3 text-sm text-gray-900"),
            html.Td(event['quantity'], className="px-4 py-3 text-sm text-gray-900"),
            html.Td(event['cum_qty'], className="px-4 py-3 text-sm text-gray-900"),
            html.Td(event['venue'], className="px-4 py-3 text-sm text-gray-900"),
            html.Td(event['status'], className="px-4 py-3 text-sm text-gray-900")
        ], className="hover:bg-gray-50")
        
        rows.append(row)
    
    tbody = html.Tbody(rows, className="bg-white divide-y divide-gray-200")
    
    return html.Table([header, tbody], className="w-full")

@app.callback(
    [Output('summary-cards', 'children'),
     Output('order-hierarchy-text', 'children'),
     Output('execution-timeline', 'figure'),
     Output('audit-table-container', 'children')],
    [Input('analyze-button', 'n_clicks')],
    [State('fix-log-input', 'value')]
)
def update_output(n_clicks, log_content):
    if n_clicks == 0 or not log_content:
        return [html.Div(), html.Div(), go.Figure(), html.Div()]
    
    try:
        orders, replacement_chains = process_fix_log(log_content)
        audit_data = generate_audit_data(orders)
        
        # Calculate summary statistics
        total_messages = len(audit_data)
        
        # Build order hierarchy
        hierarchy, root_orders = build_order_hierarchy(replacement_chains)
        order_chain = next(iter(root_orders)) if root_orders else list(orders.keys())[0] if orders else 'N/A'
        
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
        
        # Create components
        summary_cards = create_summary_cards(total_messages, order_chain, symbol, total_qty, filled_qty, vwap)
        hierarchy_text = create_hierarchy_text(hierarchy, root_orders)
        timeline_fig = create_timeline_chart(audit_data)
        audit_table = create_audit_table(audit_data)
        
        return [summary_cards, hierarchy_text, timeline_fig, audit_table]
        
    except Exception as e:
        error_msg = html.Div(f"Error: {str(e)}", className="text-red-600 text-center py-4")
        return [error_msg, error_msg, go.Figure(), error_msg]

if __name__ == '__main__':
    app.run(debug=True)