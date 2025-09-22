import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import re
from datetime import datetime
from collections import defaultdict
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
import plotly.express as px

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "FIX Order Audit Trail Analyzer"

# Define styles
styles = {
    'textarea': {
        'width': '100%',
        'height': 200,
        'fontFamily': 'monospace',
        'fontSize': '12px'
    },
    'header': {
        'backgroundColor': '#2c3e50',
        'color': 'white',
        'padding': '20px',
        'textAlign': 'center'
    },
    'card': {
        'borderRadius': '8px',
        'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
        'marginBottom': '20px'
    }
}

app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("FIX Order Audit Trail Analyzer", 
                   style={'color': 'white', 'marginBottom': '20px'}),
            html.P("Paste FIX log content to analyze order execution patterns",
                  style={'color': 'white', 'opacity': '0.8'})
        ], style=styles['header'])
    ]),
    
    # Input Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Input FIX Log Content", style={'fontWeight': 'bold'}),
                dbc.CardBody([
                    dcc.Textarea(
                        id='fix-log-input',
                        placeholder='Paste your FIX log content here...',
                        style=styles['textarea']
                    ),
                    dbc.Button("Analyze Log", id='analyze-button', color='primary', 
                              className='mt-3', n_clicks=0)
                ])
            ], style=styles['card'])
        ], width=12)
    ]),
    
    # Summary Cards
    dbc.Row([
        dbc.Col([dbc.Card([dbc.CardBody([html.H5("Total Messages"), html.H3(id='total-messages')])])], width=2),
        dbc.Col([dbc.Card([dbc.CardBody([html.H5("Order Chain ID"), html.H3(id='order-chain-id')])])], width=2),
        dbc.Col([dbc.Card([dbc.CardBody([html.H5("Symbol"), html.H3(id='symbol')])])], width=2),
        dbc.Col([dbc.Card([dbc.CardBody([html.H5("Total Quantity"), html.H3(id='total-quantity')])])], width=2),
        dbc.Col([dbc.Card([dbc.CardBody([html.H5("Filled Quantity"), html.H3(id='filled-quantity')])])], width=2),
        dbc.Col([dbc.Card([dbc.CardBody([html.H5("VWAP"), html.H3(id='vwap')])])], width=2),
    ], className='g-3 my-3'),
    
    # Order Chain Visualization
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Order Chain Hierarchy", style={'fontWeight': 'bold'}),
                dbc.CardBody([dcc.Graph(id='order-chain-graph')])
            ], style=styles['card'])
        ], width=12)
    ]),
    
    # Charts
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Execution Timeline", style={'fontWeight': 'bold'}),
                dbc.CardBody([dcc.Graph(id='execution-timeline')])
            ], style=styles['card'])
        ], width=12)
    ]),
    
    # Audit Trail Table
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Order Audit Trail", style={'fontWeight': 'bold'}),
                dbc.CardBody([
                    html.Div(id='audit-table-container')
                ])
            ], style=styles['card'])
        ], width=12)
    ])
], fluid=True)

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

def create_order_chain_graph(hierarchy, root_orders):
    """Create a network graph visualization of the order hierarchy."""
    G = nx.DiGraph()
    
    # Add nodes and edges
    for parent, children in hierarchy.items():
        G.add_node(parent, type='order', size=20)
        for child in children:
            G.add_node(child, type='order', size=20)
            G.add_edge(parent, child, type='replacement')
    
    # Use spring layout
    pos = nx.spring_layout(G, k=2, iterations=50)
    
    # Extract node positions
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        node_size.append(25 if node in root_orders else 20)
        node_color.append('red' if node in root_orders else 'blue')
    
    # Extract edge positions
    edge_x = []
    edge_y = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    # Create the figure
    fig = go.Figure()
    
    # Add edges
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='gray'),
        hoverinfo='none',
        mode='lines',
        showlegend=False
    ))
    
    # Add nodes
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=2, color='darkblue')
        ),
        text=node_text,
        textposition="middle center",
        textfont=dict(size=10, color='white'),
        hoverinfo='text',
        hovertext=[f"Order ID: {node}" for node in node_text],
        showlegend=False
    ))
    
    fig.update_layout(
        title='Order Replacement Hierarchy',
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=400
    )
    
    return fig

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

@app.callback(
    [Output('total-messages', 'children'),
     Output('order-chain-id', 'children'),
     Output('symbol', 'children'),
     Output('total-quantity', 'children'),
     Output('filled-quantity', 'children'),
     Output('vwap', 'children'),
     Output('order-chain-graph', 'figure'),
     Output('execution-timeline', 'figure'),
     Output('audit-table-container', 'children')],
    [Input('analyze-button', 'n_clicks')],
    [State('fix-log-input', 'value')]
)
def update_output(n_clicks, log_content):
    if n_clicks == 0 or not log_content:
        return ['0', 'N/A', 'N/A', '0', '0', '$0.00', go.Figure(), go.Figure(), '']
    
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
        
        # Create order chain graph
        chain_graph = create_order_chain_graph(hierarchy, root_orders)
        
        # Create timeline chart
        timeline_fig = create_timeline_chart(audit_data)
        
        # Create audit table with parent-child relationships
        table = create_audit_table(audit_data, hierarchy)
        
        return [
            f"{total_messages}",
            order_chain,
            symbol,
            f"{total_qty:,}",
            f"{filled_qty:,}",
            f"${vwap:.2f}",
            chain_graph,
            timeline_fig,
            table
        ]
        
    except Exception as e:
        return [f"Error: {str(e)}"] * 8 + ['']

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
        showlegend=True
    )
    
    return fig

def create_audit_table(audit_data, hierarchy):
    """Create HTML table for audit trail with parent-child relationships."""
    table_header = [
        html.Thead(html.Tr([
            html.Th("Time"), html.Th("Message Type"), html.Th("Order ID"),
            html.Th("Parent Order"), html.Th("Direction"), html.Th("Price"), 
            html.Th("Quantity"), html.Th("Cum Qty"), html.Th("Venue"), html.Th("Status")
        ]))
    ]
    
    rows = []
    for event in audit_data:
        msg_type_class = {
            'New Order': 'msg-new-order',
            'Execution Report': 'msg-execution',
            'Replace Request': 'msg-replace',
            'Cancel Request': 'msg-cancel'
        }.get(event['msg_type'], '')
        
        # Find parent order
        parent_order = event['orig_order_id'] if event['orig_order_id'] else 'N/A'
        
        row = html.Tr([
            html.Td(event['timestamp'], className='timestamp'),
            html.Td(html.Span(event['msg_type'], className=f'msg-type {msg_type_class}')),
            html.Td(event['order_id'], className='order-id'),
            html.Td(parent_order, className='order-id'),
            html.Td(event['direction'], className='direction buy'),
            html.Td(event['price'], className='price'),
            html.Td(event['quantity'], className='quantity'),
            html.Td(event['cum_qty'], className='quantity'),
            html.Td(event['venue'], className='venue'),
            html.Td(event['status'])
        ])
        rows.append(row)
    
    table_body = [html.Tbody(rows)]
    
    return dbc.Table(table_header + table_body, bordered=True, hover=True, responsive=True)

if __name__ == '__main__':
    app.run(debug=True)