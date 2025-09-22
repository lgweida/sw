import dash
from dash import dcc, html, Input, Output, State, callback_context
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
        <style>
            .nav-button {
                transition: all 0.3s ease;
                border: 2px solid transparent;
            }
            .nav-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
            .nav-button.active {
                border-color: white;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }
            .order-chain-item {
                transition: all 0.2s ease;
                border-left: 4px solid transparent;
            }
            .order-chain-item:hover {
                border-left-color: #3b82f6;
                background-color: #f8fafc;
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
                html.Button("📊 Order Audit Trail", 
                          id='audit-button',
                          n_clicks=0,
                          className="nav-button active bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md mr-3"
                ),
                html.Button("📈 Timeline", 
                          id='timeline-button',
                          n_clicks=0,
                          className="nav-button bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md"
                ),
            ], className="flex space-x-3 items-center"),
        ], className="flex justify-between items-center w-full max-w-7xl mx-auto px-4")
    ], className="bg-gradient-to-r from-gray-800 to-gray-900 p-4 shadow-xl sticky top-0 z-50 border-b border-gray-700"),
    
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
                          className="mt-4 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold py-3 px-8 rounded-lg transition duration-200 shadow-md transform hover:scale-105"
                )
            ], className="bg-white p-6 rounded-xl shadow-sm border border-gray-200")
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
            ], className="bg-white p-6 rounded-xl shadow-sm border border-gray-200")
        ], className="px-6 pb-6")
    ]),
    
    # Timeline Page (initially hidden)
    html.Div(id='timeline-content', className='hidden', children=[
        html.Div([
            # Execution Timeline Graph
            html.Div([
                html.H2("Execution Timeline", className="text-2xl font-bold text-gray-800 mb-6"),
                dcc.Graph(id='timeline-graph', className="rounded-lg bg-white p-4 shadow-sm border border-gray-200")
            ], className="p-6 mb-6"),
            
            # Order Chain Relationships (moved to timeline page)
            html.Div([
                html.H2("Order Chain Relationships", className="text-2xl font-bold text-gray-800 mb-6"),
                html.Div(id='order-chain-info', className="space-y-4")
            ], className="px-6")
        ])
    ]),
    
    # Store for sharing data between pages
    dcc.Store(id='audit-data-store'),
    dcc.Store(id='orders-store'),
    dcc.Store(id='replacement-chains-store'),
    dcc.Store(id='order-id-map-store')
], className="min-h-screen pt-20")

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
    order_timestamps = {}  # Track timestamps for each order
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
                    'direction': direction,  # IN or OUT
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
                
                # Track timestamps
                if cl_ord_id not in order_timestamps:
                    order_timestamps[cl_ord_id] = {'first_seen': timestamp, 'last_seen': timestamp}
                else:
                    order_timestamps[cl_ord_id]['last_seen'] = timestamp
                
                # Track replacement relationships
                if msg_type in ['G', 'F'] and orig_cl_ord_id and cl_ord_id:
                    replacement_chains[cl_ord_id] = orig_cl_ord_id
                
                if cl_ord_id:
                    orders[cl_ord_id].append(event)
                    
        except Exception as e:
            continue
            
    return orders, replacement_chains, order_id_map, order_timestamps

def build_order_hierarchy_text(replacement_chains, order_id_map, order_timestamps, orders):
    """Build enhanced order hierarchy display with timeline information."""
    if not replacement_chains:
        return html.Div([
            html.H3("No order replacements found.", className="font-semibold text-gray-700 mb-4")
        ])
    
    # Find root orders (orders that were never children)
    children = set(replacement_chains.keys())
    parents = set(replacement_chains.values())
    root_orders = parents - children
    
    hierarchy_sections = []
    
    for root in sorted(root_orders):
        current = root
        client_chain = [current]
        broker_chain = []
        timeline_data = []
        
        # Build the complete chain
        while current:
            # Add to broker chain if available
            broker_id = order_id_map.get(current)
            if broker_id:
                broker_chain.append(broker_id)
            
            # Get timeline info for this order
            if current in order_timestamps:
                timeline_info = order_timestamps[current]
                order_events = orders.get(current, [])
                status = "Unknown"
                if order_events:
                    last_event = sorted(order_events, key=lambda x: x['timestamp'])[-1]
                    status = last_event.get('ord_status', '0')
                
                timeline_data.append({
                    'order_id': current,
                    'broker_id': broker_id,
                    'start_time': timeline_info['first_seen'],
                    'end_time': timeline_info['last_seen'],
                    'duration': (timeline_info['last_seen'] - timeline_info['first_seen']).total_seconds(),
                    'status': status
                })
            
            # Move to next in chain
            if current in replacement_chains.values():
                children_of_current = [child for child, parent in replacement_chains.items() if parent == current]
                if children_of_current:
                    current = children_of_current[0]
                    client_chain.append(current)
                else:
                    break
            else:
                break
        
        # Create timeline visualization
        timeline_fig = create_order_timeline_figure(timeline_data)
        
        # Create chain display
        chain_display = html.Div([
            html.H3("Order Chain Timeline", className="font-semibold text-gray-700 mb-4 border-b pb-2"),
            
            # Client Chain
            html.Div([
                html.H4("Client Order ID Chain (Tag 11)", className="font-medium text-gray-600 mb-2"),
                html.Div([
                    html.Div([
                        html.Span(f"Step {i+1}: ", className="font-semibold text-blue-600"),
                        html.Span(order_id, className="font-mono bg-blue-100 text-blue-800 px-2 py-1 rounded")
                    ], className="order-chain-item p-3 mb-2 rounded-lg bg-white shadow-sm")
                    for i, order_id in enumerate(client_chain)
                ], className="space-y-2")
            ], className="mb-6"),
            
            # Broker Chain
            html.Div([
                html.H4("Broker Order ID Chain (Tag 37)", className="font-medium text-gray-600 mb-2"),
                html.Div([
                    html.Div([
                        html.Span(f"Step {i+1}: ", className="font-semibold text-purple-600"),
                        html.Span(broker_id, className="font-mono bg-purple-100 text-purple-800 px-2 py-1 rounded")
                    ], className="order-chain-item p-3 mb-2 rounded-lg bg-white shadow-sm")
                    for i, broker_id in enumerate(broker_chain)
                ], className="space-y-2")
            ], className="mb-6"),
            
            # Timeline Graph
            html.Div([
                html.H4("Chain Timeline Visualization", className="font-medium text-gray-600 mb-4"),
                dcc.Graph(figure=timeline_fig, className="rounded-lg bg-white p-4 shadow-sm")
            ]),
            
            # Statistics
            html.Div([
                html.H4("Chain Statistics", className="font-medium text-gray-600 mb-3"),
                html.Div([
                    html.Div([
                        html.Span("Total Orders: ", className="font-semibold"),
                        html.Span(str(len(client_chain)), className="text-blue-600 font-bold")
                    ], className="text-sm mb-1"),
                    html.Div([
                        html.Span("Total Duration: ", className="font-semibold"),
                        html.Span(f"{sum(item['duration'] for item in timeline_data):.1f}s", className="text-green-600 font-bold")
                    ], className="text-sm mb-1"),
                    html.Div([
                        html.Span("First Order: ", className="font-semibold"),
                        html.Span(timeline_data[0]['start_time'].strftime('%H:%M:%S.%f')[:-3], className="text-gray-600")
                    ], className="text-sm mb-1"),
                    html.Div([
                        html.Span("Last Order: ", className="font-semibold"),
                        html.Span(timeline_data[-1]['end_time'].strftime('%H:%M:%S.%f')[:-3], className="text-gray-600")
                    ], className="text-sm")
                ], className="bg-gray-50 p-3 rounded-lg")
            ], className="mt-4")
        ], className="bg-gray-100 p-6 rounded-xl")
        
        hierarchy_sections.append(chain_display)
    
    return html.Div(hierarchy_sections, className="space-y-6")

def create_order_timeline_figure(timeline_data):
    """Create a Gantt-style timeline for order chains."""
    if not timeline_data:
        return go.Figure()
    
    # Prepare data for the timeline
    orders = []
    starts = []
    ends = []
    texts = []
    colors = []
    
    status_colors = {
        '0': '#3B82F6',  # New - Blue
        '1': '#10B981',  # Partial Fill - Green
        '2': '#059669',  # Filled - Dark Green
        '4': '#EF4444',  # Canceled - Red
        '5': '#F59E0B',  # Replaced - Amber
        '6': '#F97316',  # Pending Cancel - Orange
        '8': '#DC2626',  # Rejected - Dark Red
        'A': '#60A5FA',  # Pending New - Light Blue
        'C': '#9CA3AF',  # Expired - Gray
        'E': '#FBBF24'   # Pending Replace - Yellow
    }
    
    for i, item in enumerate(timeline_data):
        orders.append(f"Step {i+1}: {item['order_id']}")
        starts.append(item['start_time'])
        ends.append(item['end_time'])
        
        duration = item['duration']
        status = item['status']
        color = status_colors.get(status, '#6B7280')  # Default gray
        
        texts.append(
            f"Order: {item['order_id']}<br>"
            f"Broker: {item['broker_id'] or 'N/A'}<br>"
            f"Duration: {duration:.2f}s<br>"
            f"Status: {status}<br>"
            f"Start: {item['start_time'].strftime('%H:%M:%S.%f')[:-3]}<br>"
            f"End: {item['end_time'].strftime('%H:%M:%S.%f')[:-3]}"
        )
        colors.append(color)
    
    fig = go.Figure()
    
    for i in range(len(orders)):
        fig.add_trace(go.Bar(
            y=[orders[i]],
            x=[(ends[i] - starts[i]).total_seconds() * 1000],  # Convert to milliseconds
            base=starts[i],
            orientation='h',
            marker_color=colors[i],
            opacity=0.8,
            hoverinfo='text',
            hovertext=[texts[i]],
            name=orders[i]
        ))
    
    fig.update_layout(
        title='Order Chain Timeline',
        xaxis_title='Time',
        yaxis_title='Order Steps',
        showlegend=False,
        height=300 + len(orders) * 40,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    fig.update_xaxis(
        tickformat='%H:%M:%S.%L',
        type='date'
    )
    
    fig.update_yaxis(
        autorange='reversed'  # Show first order at top
    )
    
    return fig

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
            '3': 'Done for Day',
            '4': 'Canceled',
            '5': 'Replaced',
            '6': 'Pending Cancel',
            '7': 'Stopped',
            '8': 'Rejected',
            '9': 'Suspended',
            'A': 'Pending New',
            'B': 'Calculated',
            'C': 'Expired',
            'D': 'Accepted for Bidding',
            'E': 'Pending Replace',
            'F': 'Restated',
            'G': 'Pending Last Look',
            'H': 'Pending Cancel Replace'
        }.get(event['ord_status'], f'Unknown ({event["ord_status"]})')
        
        audit_data.append({
            'timestamp': event['timestamp'].strftime('%H:%M:%S.%f')[:-3],
            'direction': event['direction'],  # IN or OUT
            'connector': event['connector'],
            'msg_type': msg_type_desc,
            'order_id': event['cl_ord_id'],
            'broker_order_id': event['order_id'],  # Tag 37
            'orig_order_id': event['orig_cl_ord_id'],
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

def create_order_timeline_figure(timeline_data):
    """Create a Gantt-style timeline for order chains."""
    if not timeline_data:
        return go.Figure()
    
    # Prepare data for the timeline
    orders = []
    starts = []
    ends = []
    texts = []
    colors = []
    
    status_colors = {
        '0': '#3B82F6',  # New - Blue
        '1': '#10B981',  # Partial Fill - Green
        '2': '#059669',  # Filled - Dark Green
        '4': '#EF4444',  # Canceled - Red
        '5': '#F59E0B',  # Replaced - Amber
        '6': '#F97316',  # Pending Cancel - Orange
        '8': '#DC2626',  # Rejected - Dark Red
        'A': '#60A5FA',  # Pending New - Light Blue
        'C': '#9CA3AF',  # Expired - Gray
        'E': '#FBBF24'   # Pending Replace - Yellow
    }
    
    for i, item in enumerate(timeline_data):
        orders.append(f"Step {i+1}: {item['order_id']}")
        starts.append(item['start_time'])
        ends.append(item['end_time'])
        
        duration = item['duration']
        status = item['status']
        color = status_colors.get(status, '#6B7280')  # Default gray
        
        texts.append(
            f"Order: {item['order_id']}<br>"
            f"Broker: {item['broker_id'] or 'N/A'}<br>"
            f"Duration: {duration:.2f}s<br>"
            f"Status: {status}<br>"
            f"Start: {item['start_time'].strftime('%H:%M:%S.%f')[:-3]}<br>"
            f"End: {item['end_time'].strftime('%H:%M:%S.%f')[:-3]}"
        )
        colors.append(color)
    
    # Create the figure with proper layout
    fig = go.Figure()
    
    for i in range(len(orders)):
        fig.add_trace(go.Bar(
            y=[orders[i]],
            x=[(ends[i] - starts[i]).total_seconds() * 1000],  # Convert to milliseconds
            base=starts[i],
            orientation='h',
            marker_color=colors[i],
            opacity=0.8,
            hoverinfo='text',
            hovertext=[texts[i]],
            name=orders[i]
        ))
    
    # Update layout with proper axis configuration
    fig.update_layout(
        title='Order Chain Timeline',
        xaxis=dict(
            title='Time',
            tickformat='%H:%M:%S.%L',
            type='date'
        ),
        yaxis=dict(
            title='Order Steps',
            autorange='reversed'  # Show first order at top
        ),
        showlegend=False,
        height=300 + len(orders) * 40,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    return fig

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

def create_audit_table(audit_data):
    """Create HTML table for audit trail with Tailwind CSS including Direction column."""
    # Create table header
    header = html.Thead(html.Tr([
        html.Th("Time", className="px-4 py-2 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
        html.Th("Direction", className="px-4 py-2 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
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
        
        # Determine direction styling
        direction_class = "bg-blue-100 text-blue-800" if event['direction'] == 'OUT' else "bg-green-100 text-green-800"
        direction_text = "OUTGOING" if event['direction'] == 'OUT' else "INCOMING"
        
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
                html.Span(direction_text, className=f"px-2 py-1 text-xs font-medium rounded-full {direction_class}"),
                className="px-4 py-2 whitespace-nowrap"
            ),
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

# Callbacks for navigation
@app.callback(
    [Output('main-content', 'className'),
     Output('timeline-content', 'className'),
     Output('audit-button', 'className'),
     Output('timeline-button', 'className')],
    [Input('audit-button', 'n_clicks'),
     Input('timeline-button', 'n_clicks')],
    prevent_initial_call=False
)
def navigate_to_page(audit_clicks, timeline_clicks):
    ctx = callback_context
    
    # Default state - show audit page
    if not ctx.triggered:
        return ('block', 'hidden', 
                'nav-button active bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold py-3 px-6 rounded-lg shadow-md mr-3', 
                'nav-button bg-gradient-to-r from-purple-500 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg shadow-md')
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'audit-button':
        return ('block', 'hidden', 
                'nav-button active bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold py-3 px-6 rounded-lg shadow-md mr-3', 
                'nav-button bg-gradient-to-r from-purple-500 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg shadow-md')
    elif button_id == 'timeline-button':
        return ('hidden', 'block', 
                'nav-button bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold py-3 px-6 rounded-lg shadow-md mr-3', 
                'nav-button active bg-gradient-to-r from-purple-500 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg shadow-md')
    
    return ('block', 'hidden', 
            'nav-button active bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold py-3 px-6 rounded-lg shadow-md mr-3', 
            'nav-button bg-gradient-to-r from-purple-500 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg shadow-md')

# Main analysis callback
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
     Output('order-chain-info', 'children'),
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
        orders, replacement_chains, order_id_map, order_timestamps = process_fix_log(log_content)
        audit_data = generate_audit_data(orders)
        
        # Calculate summary statistics
        total_messages = len(audit_data)
        
        # Build order hierarchy text with Tag 37 tracking
        hierarchy_text = build_order_hierarchy_text(replacement_chains, order_id_map, order_timestamps, orders)
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
            'order_id_map': order_id_map,
            'order_timestamps': order_timestamps
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
            hierarchy_text,
            store_data,
            dict(orders),
            replacement_chains,
            order_id_map
        ]
        
    except Exception as e:
        return [f"Error: {str(e)}"] * 8 + [go.Figure(), f"Error: {str(e)}", None, None, None, None]

if __name__ == '__main__':
    app.run(debug=True)
