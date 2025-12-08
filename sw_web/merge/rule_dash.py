import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
import configparser
from typing import Dict, List, Optional, Tuple
import io

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Routing Flow Visualizer"

# Global variables to store data
routing_rules = []
column_names = []
FILE_PATH='enrichments'

def load_data():
    """Load routing data from files"""
    global routing_rules, column_names
    
    # Parse INI file
    config = configparser.ConfigParser()
    config.read(f'{FILE_PATH}/enrichment_Flex17_MultiDesk_Routing.ini')
    
    separator = config.get('separator', 'value', fallback=';')
    
    # Get column names from INI
    column_map = {}
    if config.has_section('lookup'):
        for key, value in config.items('lookup'):
            column_map[int(key)] = value
    
    # Create column names list
    column_names = [column_map.get(i, f'Column_{i}') for i in range(13)]
    
    # Read CSV file
    routing_rules = []
    with open(f'{FILE_PATH}/enrichment_Flex17_MultiDesk_Routing.csv', 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
                
            parts = line.split(separator)
            if len(parts) < 13:
                parts += [''] * (13 - len(parts))
            
            parts = [p.strip() for p in parts]
            
            routing_rules.append({
                'id': line_num,
                'line': line,
                'account': parts[0] if len(parts) > 0 else '',
                'desk': parts[12] if len(parts) > 12 else '',
                'etf': parts[9] if len(parts) > 9 else '',
                'has_prog': (len(parts) > 3 and parts[3] == 'PROG') or 
                           (len(parts) > 4 and parts[4] == 'PROG'),
                'has_pt': len(parts) > 5 and parts[5] == 'PT',
                'is_wildcard': parts[0] in ('', '*'),
                'all_columns': parts
            })
    
    return routing_rules, column_names

# Load initial data
routing_rules, column_names = load_data()

def find_matching_rules(account: str) -> List[Dict]:
    """Find all rules that match the given account"""
    matching_rules = []
    
    for rule in routing_rules:
        # Check if rule matches account
        if rule['account'] == account or rule['is_wildcard']:
            matching_rules.append(rule)
    
    return matching_rules

def determine_routing_flow(account: str, etf: Optional[str] = None) -> List[Dict]:
    """Determine the routing flow for an account"""
    matching_rules = find_matching_rules(account)
    
    # Categorize rules by type
    exact_account_rules = [r for r in matching_rules if r['account'] == account]
    wildcard_rules = [r for r in matching_rules if r['is_wildcard']]
    
    # Determine which rule would be selected based on priority
    selected_rules = []
    flow_steps = []
    
    # Priority 1: Exact account rules
    if exact_account_rules:
        for rule in exact_account_rules:
            flow_steps.append({
                'type': 'account',
                'label': f"Account: {account}",
                'value': account,
                'rule_id': rule['id']
            })
            
            # Check for conditions
            if rule['has_prog']:
                flow_steps.append({
                    'type': 'condition',
                    'label': "Condition: PROG",
                    'value': 'PROG',
                    'rule_id': rule['id']
                })
            elif rule['has_pt']:
                flow_steps.append({
                    'type': 'condition',
                    'label': "Condition: PT",
                    'value': 'PT',
                    'rule_id': rule['id']
                })
            elif rule['etf']:
                flow_steps.append({
                    'type': 'condition',
                    'label': f"ETF: {rule['etf']}",
                    'value': rule['etf'],
                    'rule_id': rule['id']
                })
            
            flow_steps.append({
                'type': 'desk',
                'label': f"Desk: {rule['desk']}",
                'value': rule['desk'],
                'rule_id': rule['id']
            })
            
            selected_rules.append(rule)
    
    # Priority 2: Wildcard rules with specific conditions
    else:
        # Check ETF-specific wildcards first
        if etf and etf in ['MIZOATPC', 'MIZOETPC', 'MIZOETPP']:
            etf_rules = [r for r in wildcard_rules if r['etf'] == etf]
            if etf_rules:
                rule = etf_rules[0]
                flow_steps.extend([
                    {
                        'type': 'account',
                        'label': f"Account: {account}",
                        'value': account,
                        'rule_id': rule['id']
                    },
                    {
                        'type': 'condition',
                        'label': f"ETF: {etf}",
                        'value': etf,
                        'rule_id': rule['id']
                    },
                    {
                        'type': 'desk',
                        'label': f"Desk: {rule['desk']}",
                        'value': rule['desk'],
                        'rule_id': rule['id']
                    }
                ])
                selected_rules.append(rule)
        
        # Check PROG/PT wildcards
        if not flow_steps:
            prog_pt_rules = [r for r in wildcard_rules if r['has_prog'] or r['has_pt']]
            if prog_pt_rules:
                rule = prog_pt_rules[0]
                flow_steps.extend([
                    {
                        'type': 'account',
                        'label': f"Account: {account}",
                        'value': account,
                        'rule_id': rule['id']
                    }
                ])
                
                if rule['has_prog']:
                    flow_steps.append({
                        'type': 'condition',
                        'label': "Condition: PROG",
                        'value': 'PROG',
                        'rule_id': rule['id']
                    })
                elif rule['has_pt']:
                    flow_steps.append({
                        'type': 'condition',
                        'label': "Condition: PT",
                        'value': 'PT',
                        'rule_id': rule['id']
                    })
                
                flow_steps.append({
                    'type': 'desk',
                    'label': f"Desk: {rule['desk']}",
                    'value': rule['desk'],
                    'rule_id': rule['id']
                })
                selected_rules.append(rule)
        
        # Default wildcard
        if not flow_steps and wildcard_rules:
            # Get the last wildcard rule
            rule = wildcard_rules[-1]
            flow_steps.extend([
                {
                    'type': 'account',
                    'label': f"Account: {account}",
                    'value': account,
                    'rule_id': rule['id']
                },
                {
                    'type': 'desk',
                    'label': f"Desk: {rule['desk']} (Default)",
                    'value': rule['desk'],
                    'rule_id': rule['id']
                }
            ])
            selected_rules.append(rule)
    
    return flow_steps, selected_rules, exact_account_rules, wildcard_rules

def create_flowchart_figure(flow_steps: List[Dict]) -> go.Figure:
    """Create a flowchart visualization"""
    if not flow_steps:
        # Return empty figure
        fig = go.Figure()
        fig.update_layout(
            title="No routing found",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )
        return fig
    
    # Create nodes
    nodes = []
    node_colors = []
    node_labels = []
    
    for step in flow_steps:
        nodes.append(step['label'])
        
        # Set colors based on type
        if step['type'] == 'account':
            node_colors.append('#1f77b4')  # Blue
        elif step['type'] == 'condition':
            node_colors.append('#ff7f0e')  # Orange
        elif step['type'] == 'desk':
            node_colors.append('#2ca02c')  # Green
    
    # Create edges
    edges = []
    edge_labels = []
    
    for i in range(len(flow_steps) - 1):
        edges.append((i, i + 1))
        edge_labels.append('→')
    
    # Create figure
    fig = go.Figure()
    
    # Add nodes as scatter points
    x_positions = list(range(len(nodes)))
    y_positions = [0] * len(nodes)  # All on same line
    
    # Add node trace
    fig.add_trace(go.Scatter(
        x=x_positions,
        y=y_positions,
        mode='markers+text',
        marker=dict(
            size=50,
            color=node_colors,
            line=dict(width=2, color='DarkSlateGrey')
        ),
        text=nodes,
        textposition="top center",
        textfont=dict(size=12, color='black'),
        hoverinfo='text',
        hovertext=[f"Type: {step['type']}<br>Value: {step['value']}" for step in flow_steps],
        name="Nodes"
    ))
    
    # Add edges as lines
    for edge, label in zip(edges, edge_labels):
        x0, x1 = x_positions[edge[0]], x_positions[edge[1]]
        y0, y1 = y_positions[edge[0]], y_positions[edge[1]]
        
        # Add arrow
        fig.add_annotation(
            x=x1,
            y=y1,
            ax=x0,
            ay=y0,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            text="",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#666666"
        )
        
        # Add edge label in middle
        fig.add_annotation(
            x=(x0 + x1) / 2,
            y=0.1,
            text=label,
            showarrow=False,
            font=dict(size=14, color="#666666")
        )
    
    # Update layout
    fig.update_layout(
        title="Routing Flow",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-0.5, len(nodes) - 0.5]
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-0.5, 0.5]
        ),
        plot_bgcolor='white',
        showlegend=False,
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

def create_detailed_flowchart(flow_steps: List[Dict]) -> go.Figure:
    """Create a more detailed flowchart with decision points"""
    if not flow_steps:
        return go.Figure()
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes with attributes
    for i, step in enumerate(flow_steps):
        G.add_node(i, 
                  label=step['label'],
                  type=step['type'],
                  value=step['value'])
    
    # Add edges
    for i in range(len(flow_steps) - 1):
        G.add_edge(i, i + 1)
    
    # Use networkx to calculate positions
    pos = nx.spring_layout(G, seed=42)
    
    # Create edge trace
    edge_x = []
    edge_y = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    # Create node trace
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_data = G.nodes[node]
        node_text.append(node_data['label'])
        
        # Color based on type
        if node_data['type'] == 'account':
            node_colors.append('#4287f5')  # Blue
        elif node_data['type'] == 'condition':
            node_colors.append('#f5a742')  # Orange
        elif node_data['type'] == 'desk':
            node_colors.append('#42f554')  # Green
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        marker=dict(
            size=40,
            color=node_colors,
            line=dict(width=2, color='darkblue')
        ),
        hoverinfo='text',
        textfont=dict(size=12)
    )
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title='Detailed Routing Flow',
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20, l=5, r=5, t=40),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       height=400
                   ))
    
    return fig

# App layout
app.layout = html.Div([
    html.Div([
        html.H1("Routing Flow Visualizer", style={'textAlign': 'center'}),
        
        html.Div([
            html.Div([
                html.Label("Account Number:"),
                dcc.Input(
                    id='account-input',
                    type='text',
                    value='20010003',
                    style={'width': '200px', 'marginRight': '20px'}
                ),
            ], style={'display': 'inline-block', 'marginRight': '20px'}),
            
            html.Div([
                html.Label("ETF (Optional):"),
                dcc.Dropdown(
                    id='etf-input',
                    options=[
                        {'label': 'None', 'value': ''},
                        {'label': 'MIZOATPC', 'value': 'MIZOATPC'},
                        {'label': 'MIZOETPC', 'value': 'MIZOETPC'},
                        {'label': 'MIZOETPP', 'value': 'MIZOETPP'},
                    ],
                    value='',
                    style={'width': '200px', 'display': 'inline-block'}
                ),
            ], style={'display': 'inline-block', 'marginRight': '20px'}),
            
            html.Button('Show Routing Flow', id='submit-button', n_clicks=0),
        ], style={'textAlign': 'center', 'marginBottom': '30px'}),
        
        # Flowchart visualization
        html.Div([
            dcc.Graph(id='flowchart-graph'),
        ], style={'marginBottom': '30px'}),
        
        # Detailed view
        html.Div([
            html.H3("Routing Details"),
            html.Div(id='routing-details'),
        ], style={'marginBottom': '30px'}),
        
        # Matching rules table
        html.Div([
            html.H3("All Matching Rules"),
            dash_table.DataTable(
                id='rules-table',
                columns=[
                    {'name': 'Rule ID', 'id': 'id'},
                    {'name': 'Account', 'id': 'account'},
                    {'name': 'Desk', 'id': 'desk'},
                    {'name': 'ETF', 'id': 'etf'},
                    {'name': 'Has PROG', 'id': 'has_prog'},
                    {'name': 'Has PT', 'id': 'has_pt'},
                    {'name': 'Is Wildcard', 'id': 'is_wildcard'},
                ],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'minWidth': '100px',
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                page_size=10,
            ),
        ], style={'marginBottom': '30px'}),
        
        # Rule details
        html.Div([
            html.H3("Selected Rule Details"),
            html.Div(id='rule-details'),
        ]),
    ], style={'padding': '20px', 'maxWidth': '1200px', 'margin': '0 auto'})
])

@app.callback(
    [Output('flowchart-graph', 'figure'),
     Output('routing-details', 'children'),
     Output('rules-table', 'data'),
     Output('rule-details', 'children')],
    [Input('submit-button', 'n_clicks')],
    [State('account-input', 'value'),
     State('etf-input', 'value')]
)
def update_routing(n_clicks, account, etf):
    if not account:
        return go.Figure(), "Please enter an account", [], ""
    
    # Get routing flow
    flow_steps, selected_rules, exact_rules, wildcard_rules = determine_routing_flow(account, etf if etf else None)
    
    # Create flowchart
    fig = create_flowchart_figure(flow_steps)
    
    # Create routing details
    if flow_steps:
        details = html.Div([
            html.H4(f"Routing for Account: {account}"),
            html.Ul([
                html.Li(f"Total matching rules: {len(exact_rules) + len(wildcard_rules)}"),
                html.Li(f"Exact account rules: {len(exact_rules)}"),
                html.Li(f"Wildcard rules considered: {len(wildcard_rules)}"),
                html.Li(f"Selected desk: {flow_steps[-1]['value'] if flow_steps else 'None'}"),
                html.Li(f"Path length: {len(flow_steps)} steps"),
            ]),
            html.H5("Flow Steps:"),
            html.Ol([html.Li(step['label']) for step in flow_steps]),
        ])
    else:
        details = html.Div([
            html.H4(f"No routing found for Account: {account}"),
            html.P("No matching rules found in the routing table.")
        ])
    
    # Prepare table data
    all_matching = exact_rules + wildcard_rules
    table_data = []
    for rule in all_matching[:100]:  # Limit to 100 rows
        table_data.append({
            'id': rule['id'],
            'account': rule['account'],
            'desk': rule['desk'],
            'etf': rule['etf'],
            'has_prog': '✓' if rule['has_prog'] else '',
            'has_pt': '✓' if rule['has_pt'] else '',
            'is_wildcard': '✓' if rule['is_wildcard'] else '',
        })
    
    # Create rule details
    if selected_rules:
        rule_details = html.Div([
            html.H5("Selected Rule Information:"),
            html.Pre(selected_rules[0]['line'], style={
                'backgroundColor': '#f5f5f5',
                'padding': '10px',
                'borderRadius': '5px',
                'overflowX': 'auto'
            }),
            html.H6("Column Breakdown:"),
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Column"),
                    html.Th("Name"),
                    html.Th("Value")
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(i),
                        html.Td(column_names[i] if i < len(column_names) else f'Column_{i}'),
                        html.Td(selected_rules[0]['all_columns'][i] if i < len(selected_rules[0]['all_columns']) else '')
                    ]) for i in range(13)
                ])
            ], style={'width': '100%', 'borderCollapse': 'collapse'})
        ])
    else:
        rule_details = html.Div([
            html.H5("No rule selected"),
            html.P("No matching rule was found for this account.")
        ])
    
    return fig, details, table_data, rule_details

# Add custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f8f9fa;
            }
            .container {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            h1, h2, h3, h4, h5 {
                color: #333;
            }
            table {
                border-collapse: collapse;
                width: 100%;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            pre {
                white-space: pre-wrap;
                word-wrap: break-word;
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

if __name__ == '__main__':
    print("Loading routing data...")
    load_data()
    print(f"Loaded {len(routing_rules)} routing rules")
    print("Starting Dash app on http://127.0.0.1:8050")
    app.run(debug=True, port=8050)
