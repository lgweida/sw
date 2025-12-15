import dash
from dash import html, dash_table, dcc, Input, Output, State
import pandas as pd
from typing import List, Dict, Any
import plotly.graph_objects as go
import io

# Sample customer data
customer_data = [
    {'id': 1, 'name': 'Customer A', 'sendercompid': 'BPGICRD', 'region': 'North America'},
    {'id': 2, 'name': 'Customer B', 'sendercompid': 'ARICMCRD', 'region': 'Europe'},
    {'id': 3, 'name': 'Customer C', 'sendercompid': 'GEODECRD', 'region': 'Asia'},
    {'id': 4, 'name': 'Customer D', 'sendercompid': 'ACAMLCRD', 'region': 'North America'},
    {'id': 5, 'name': 'Customer E', 'sendercompid': 'TVMGCRD', 'region': 'Europe'},
    {'id': 6, 'name': 'Customer F', 'sendercompid': 'BPGICRD', 'region': 'Asia'},
]

def get_consolidated_routing_rules_by_priority(sender_comp_id: str) -> pd.DataFrame:
    """
    Create consolidated routing rules visualization data from embedded CSV content.
    Consolidates rules with the same routing criteria and maintains high-to-low priority.
    """
    csv_content = """SENDERCOMPID;CURRENCY;TARGETSUBID;ETF;COUNTRYCODE;DESTINATION
BPGICRD;USD;PROG;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
BPGICRD;CAD;PROG;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
BPGICRD;*;PROG;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
BPGICRD;*;*;*;SI;MizuhoTKGOR42BuySide
BPGICRD;USD;*;*;*;FlexTradeBuySide42
BPGICRD;CAD;*;*;*;FlexTradeBuySide42
BPGICRD;AUD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;CNH;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;CNY;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;HKD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;IDR;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;INR;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;JPY;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;KRW;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;MYR;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;NZD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;PHP;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;SGD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;THB;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;TWD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
ARICMCRD;*;*;*;SI;MizuhoTKGOR42BuySide
ARICMCRD;USD;*;*;*;FlexTradeBuySide42
ARICMCRD;CAD;*;*;*;FlexTradeBuySide42
ARICMCRD;AUD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;CNH;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;CNY;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;HKD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;IDR;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;INR;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;JPY;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;KRW;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;MYR;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;NZD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;PHP;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;SGD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;THB;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;TWD;*;*;*;MizuhoTKGOR42BuySide
GEODECRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
ACAMLCRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
TVMGCRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42"""
    
    # Read CSV content
    df = pd.read_csv(io.StringIO(csv_content), delimiter=';')
    
    # Filter by sender_comp_id
    filtered_df = df[df['SENDERCOMPID'] == sender_comp_id].copy()
    
    if filtered_df.empty:
        return pd.DataFrame()

    # Add a column to store the priority based on original row index
    filtered_df['_priority'] = filtered_df.index
    
    # Define grouping columns (all criteria except CURRENCY)
    grouping_columns = ['TARGETSUBID', 'ETF', 'COUNTRYCODE', 'DESTINATION']
    
    # Group and consolidate currencies, taking the minimum priority index
    consolidated_df = filtered_df.groupby(grouping_columns).agg(
        CURRENCIES=('CURRENCY', lambda x: ', '.join(sorted(x.unique()))),
        _min_priority=('_priority', 'min')
    ).reset_index()
    
    # Add SENDERCOMPID back
    consolidated_df.insert(0, 'SENDERCOMPID', sender_comp_id)

    # Sort by the minimum priority index to maintain original high-to-low order
    consolidated_df = consolidated_df.sort_values(by='_min_priority', ascending=True)
    
    # Identify and drop columns that only contain '*'
    columns_to_check_for_wildcard = ['TARGETSUBID', 'ETF', 'COUNTRYCODE']
    columns_to_drop = []
    
    for col in columns_to_check_for_wildcard:
        if col in consolidated_df.columns and (consolidated_df[col].unique() == ['*']).all():
            columns_to_drop.append(col)

    if columns_to_drop:
        consolidated_df = consolidated_df.drop(columns=columns_to_drop)

    # Clean up and reorder columns
    all_final_columns = ['SENDERCOMPID', 'CURRENCIES', 'TARGETSUBID', 'ETF', 'COUNTRYCODE', 'DESTINATION']
    column_order = [col for col in all_final_columns if col in consolidated_df.columns]
    
    return consolidated_df[column_order]

def create_routing_rules_from_csv():
    """
    Create routing rules visualization data from embedded CSV content.
    Maintains natural order and maps country code 'SI' → 'Singapore'.
    """
    csv_content = """SENDERCOMPID;CURRENCY;TARGETSUBID;ETF;COUNTRYCODE;DESTINATION
BPGICRD;USD;PROG;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
BPGICRD;CAD;PROG;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
BPGICRD;*;PROG;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
BPGICRD;*;*;*;SI;MizuhoTKGOR42BuySide
BPGICRD;USD;*;*;*;FlexTradeBuySide42
BPGICRD;CAD;*;*;*;FlexTradeBuySide42
BPGICRD;AUD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;CNH;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;CNY;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;HKD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;IDR;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;INR;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;JPY;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;KRW;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;MYR;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;NZD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;PHP;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;SGD;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;THB;*;*;*;MizuhoTKGOR42BuySide
BPGICRD;TWD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
ARICMCRD;*;*;*;SI;MizuhoTKGOR42BuySide
ARICMCRD;USD;*;*;*;FlexTradeBuySide42
ARICMCRD;CAD;*;*;*;FlexTradeBuySide42
ARICMCRD;AUD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;CNH;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;CNY;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;HKD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;IDR;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;INR;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;JPY;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;KRW;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;MYR;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;NZD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;PHP;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;SGD;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;THB;*;*;*;MizuhoTKGOR42BuySide
ARICMCRD;TWD;*;*;*;MizuhoTKGOR42BuySide
GEODECRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
ACAMLCRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42
TVMGCRD;*;*;*;*;O_FLEXTRADE_GLOBAL_PT_FIX42"""
    
    lines = csv_content.strip().split('\n')
    headers = lines[0].split(';')
    data = [line.split(';') for line in lines[1:]]
    df = pd.DataFrame(data, columns=headers)
    
    destination_colors = {
        'O_FLEXTRADE_GLOBAL_PT_FIX42': '#3b82f6',  # Blue
        'MizuhoTKGOR42BuySide': '#10b981',         # Green
        'FlexTradeBuySide42': '#f59e0b'            # Orange
    }
    
    routing_rules = []
    for _, rule in df.iterrows():
        order_type_parts = []
        if rule['CURRENCY'] != '*':
            order_type_parts.append(rule['CURRENCY'])
        if rule['TARGETSUBID'] != '*':
            order_type_parts.append(f"SubID:{rule['TARGETSUBID']}")
        if rule['COUNTRYCODE'] != '*':
            country_name = "Singapore" if rule['COUNTRYCODE'] == 'SI' else rule['COUNTRYCODE']
            order_type_parts.append(f"Country:{country_name}")
        if rule['ETF'] != '*':
            order_type_parts.append(f"ETF:{rule['ETF']}")
        
        order_type = f"{' + '.join(order_type_parts)} - {rule['SENDERCOMPID']}" if order_type_parts else f"All Orders - {rule['SENDERCOMPID']}"
        color = destination_colors.get(rule['DESTINATION'], '#6b7280')
        
        routing_rules.append({
            'orderType': order_type,
            'destination': rule['DESTINATION'],
            'color': color,
            'sendercompid': rule['SENDERCOMPID']
        })
    
    return routing_rules[::-1]

def get_routing_rules_for_customer(sendercompid: str) -> List[Dict[str, Any]]:
    all_rules = create_routing_rules_from_csv()
    return [rule for rule in all_rules if rule['sendercompid'] == sendercompid]

def get_destinations_for_customer(sendercompid: str) -> List[str]:
    customer_rules = get_routing_rules_for_customer(sendercompid)
    return list(set(rule['destination'] for rule in customer_rules))

# Desk descriptions
desk_descriptions = {
    'O_FLEXTRADE_GLOBAL_PT_FIX42': 'Primary global order routing destination for standard executions',
    'MizuhoTKGOR42BuySide': 'Mizuho Bank routing for specific currencies and country codes',
    'FlexTradeBuySide42': 'FlexTrade system for USD and CAD currency orders'
}

def trim_sendercompid_from_order_type(order_type: str) -> str:
    if " - " in order_type:
        return order_type.rsplit(" - ", 1)[0].rstrip()
    return order_type.rstrip()

def create_flow_arrow_chart(rules, sendercompid=None):
    if not rules:
        fig = go.Figure()
        fig.update_layout(
            title="No routing rules to display",
            height=500,
            plot_bgcolor='#f9fafb',
            paper_bgcolor='#f9fafb'
        )
        return fig

    sources = []
    targets = []
    for i, rule in enumerate(rules):
        sources.append({'x': 0.05, 'y': i, 'label': trim_sendercompid_from_order_type(rule['orderType']), 'color': rule['color']})
        targets.append({'x': 0.95, 'y': i, 'label': rule['destination'], 'color': rule['color']})

    fig = go.Figure()

    # Source nodes
    fig.add_trace(go.Scatter(
        x=[s['x'] for s in sources],
        y=[s['y'] for s in sources],
        mode='markers+text',
        marker=dict(size=16, color=[s['color'] for s in sources], line=dict(width=2, color='white')),
        text=[s['label'] for s in sources],
        textposition="middle right",
        textfont=dict(size=11, color='black', weight='bold'),
        name='Order Types',
        hovertemplate='<b>%{text}</b><extra></extra>'
    ))

    # Target nodes
    fig.add_trace(go.Scatter(
        x=[t['x'] for t in targets],
        y=[t['y'] for t in targets],
        mode='markers+text',
        marker=dict(size=16, color=[t['color'] for t in targets], line=dict(width=2, color='white')),
        text=[t['label'] for t in targets],
        textposition="middle left",
        textfont=dict(size=11, color='black', weight='bold'),
        name='Destinations',
        hovertemplate='<b>%{text}</b><extra></extra>'
    ))

    # Shorter arrows
    for i, (source, target) in enumerate(zip(sources, targets)):
        arrow_start_x = source['x'] + 0.25
        arrow_end_x = target['x'] - 0.3
        fig.add_annotation(
            x=arrow_end_x,
            y=target['y'],
            ax=arrow_start_x,
            ay=source['y'],
            xref="x", yref="y",
            axref="x", ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=3,
            arrowcolor=source['color'],
            opacity=0.85
        )

    # Build title
    title_text = f"Order Routing Flow for {sendercompid}" if sendercompid else "Order Routing Flow - Directional Arrow Diagram"
    fig.update_layout(
        title={
            'text': title_text,
            'font': {'size': 20, 'color': '#1f2937', 'weight': 'bold'},
            'x': 0.5,
            'xanchor': 'center'
        },
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 1]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, len(rules) - 0.5]),
        plot_bgcolor='#f9fafb',
        paper_bgcolor='#f9fafb',
        margin=dict(l=100, r=100, t=80, b=50),
        height=max(500, len(rules) * 50),
        width=900
    )

    return fig

# Convert customer data to DataFrame
df_customers = pd.DataFrame(customer_data)

# Initialize Dash app
app = dash.Dash(__name__)

# Add Tailwind CSS and Font Awesome (fixed URLs)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .modal-backdrop {
                background-color: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
            }
            .rule-row {
                transition: all 0.2s ease-in-out;
                border-left: 3px solid #3b82f6;
            }
            .rule-row:hover {
                background-color: #f8fafc;
                transform: translateX(2px);
            }
            .default-row {
                border-left: 3px solid #10b981;
                background-color: #f0fdf4;
            }
            .default-row:hover {
                background-color: #dcfce7;
            }
            .priority-badge {
                background-color: #fef3c7;
                color: #92400e;
                border: 1px solid #f59e0b;
            }
            .default-badge {
                background-color: #10b981;
                color: white;
                border: 1px solid #059669;
            }
            .currency-group-badge {
                background-color: #e0f2fe;
                color: #0369a1;
                border: 1px solid #0ea5e9;
            }
            .target-badge {
                background-color: #f3e8ff;
                color: #7c3aed;
                border: 1px solid #a855f7;
            }
            .country-badge {
                background-color: #ffedd5;
                color: #ea580c;
                border: 1px solid #fb923c;
            }
            .destination-badge {
                background-color: #dcfce7;
                color: #166534;
                border: 1px solid #22c55e;
            }
            .all-badge {
                background-color: #6b7280;
                color: white;
                border: 1px solid #4b5563;
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

# App layout
app.layout = html.Div([
    html.Div([
        html.H1("Customer Routing Rules", className="text-3xl font-bold text-gray-800 mb-2 text-center"),
        html.P("Click on any customer to view their routing rules", className="text-gray-600 text-center mb-8"),
        
        html.Div([
            html.H2("Customers", className="text-xl font-semibold text-gray-700 mb-4"),
            dash_table.DataTable(
                id='customer-table',
                columns=[
                    {"name": "ID", "id": "id"},
                    {"name": "Customer Name", "id": "name"},
                    {"name": "SenderCompID", "id": "sendercompid"},
                    {"name": "Region", "id": "region"}
                ],
                data=customer_data,
                row_selectable='single',
                selected_rows=[],
                style_cell={
                    'textAlign': 'left', 'padding': '12px',
                    'fontFamily': 'Inter, sans-serif',
                    'minWidth': '80px', 'width': '150px', 'maxWidth': '250px'
                },
                style_header={
                    'backgroundColor': '#f8fafc',
                    'fontWeight': '600',
                    'borderBottom': '2px solid #e2e8f0',
                    'textAlign': 'left'
                },
                style_data={'border': '1px solid #e2e8f0'},
                style_data_conditional=[
                    {'if': {'state': 'selected'}, 'backgroundColor': '#dbeafe', 'border': '2px solid #3b82f6'},
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8fafc'}
                ]
            )
        ], className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-8 max-w-4xl mx-auto")
    ], className="container mx-auto px-4 py-8"),
    
    # Modal
    html.Div([
        html.Div([
            html.Div([
                html.H3("Routing Rules Visualization", className="text-xl font-semibold text-gray-800"),
                html.Button(html.I(className="fas fa-times text-lg"),
                    id="close-modal",
                    className="text-gray-400 hover:text-gray-600 p-1 rounded-full hover:bg-gray-100")
            ], className="flex justify-between items-center px-6 py-4 border-b border-gray-200 bg-gray-50 rounded-t-lg"),
            
            html.Div([
                html.Div(id="modal-customer-info", className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200"),
                
                # Chart
                html.Div([
                    dcc.Graph(id='flow-chart', config={'displayModeBar': True, 'displaylogo': False})
                ], className='bg-white rounded-2xl shadow-sm p-6 mb-8 border border-gray-100'),
                
                # Consolidated Routing Rules Table
                html.Div([
                    html.H2('Consolidated Routing Rules (Grouped by Priority)', className='text-xl font-semibold text-gray-900 mb-4'),
                    html.Div([
                        html.Span('Rules are consolidated by grouping criteria and sorted by priority (high to low). ', 
                                 className='text-sm text-gray-600 mb-3 block'),
                        html.Span('Wildcard columns (all "*") are automatically hidden.', 
                                 className='text-sm text-gray-600 block')
                    ], className='mb-4 p-3 bg-gray-50 rounded-lg'),
                    dash_table.DataTable(
                        id='consolidated-rules-table',
                        style_cell={
                            'textAlign': 'left',
                            'padding': '12px',
                            'fontFamily': 'Inter, sans-serif',
                            'minWidth': '100px',
                            'maxWidth': '300px',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis'
                        },
                        style_header={
                            'backgroundColor': '#f8fafc',
                            'fontWeight': '600',
                            'borderBottom': '2px solid #e2e8f0'
                        },
                        style_data={'border': '1px solid #e2e8f0'},
                        style_data_conditional=[
                            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8fafc'},
                            {'if': {'column_id': 'CURRENCIES'}, 'fontWeight': '500', 'color': '#0369a1'},
                            {'if': {'column_id': 'DESTINATION'}, 'fontWeight': '500', 'color': '#166534'}
                        ],
                        page_size=10,
                        sort_action='native',
                        filter_action='native'
                    )
                ], className='bg-white rounded-2xl shadow-sm p-6 mb-8 border border-gray-100'),
                
                # Desk descriptions
                html.Div([
                    html.H2('Desk Descriptions', className='text-xl font-semibold text-gray-900 mb-4'),
                    html.Div(id="desk-descriptions", className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6')
                ], className='bg-white rounded-2xl shadow-sm p-6 border border-gray-100')
            ], className="px-6 py-4")
        ], className="bg-white rounded-lg shadow-xl w-full max-w-7xl mx-auto max-h-[90vh] overflow-y-auto")
    ], id="routing-modal", className="fixed inset-0 z-50 flex items-center justify-center p-4 modal-backdrop hidden"),
    
    dcc.Store(id='selected-customer-store'),
    html.Div(id='modal-state', style={'display': 'none'})
])

# Callbacks
@app.callback(
    [Output('routing-modal', 'className'),
     Output('selected-customer-store', 'data'),
     Output('customer-table', 'selected_rows')],
    [Input('customer-table', 'selected_rows'),
     Input('close-modal', 'n_clicks')],
    [State('customer-table', 'data')]
)
def toggle_modal(selected_rows, close_clicks, customer_data):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "fixed inset-0 z-50 flex items-center justify-center p-4 modal-backdrop hidden", None, []
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == 'close-modal':
        return "fixed inset-0 z-50 flex items-center justify-center p-4 modal-backdrop hidden", None, []
    
    if selected_rows:
        customer = customer_data[selected_rows[0]]
        customer_store_data = {
            'id': customer['id'],
            'name': customer['name'],
            'sendercompid': customer['sendercompid'],
            'region': customer['region']
        }
        return "fixed inset-0 z-50 flex items-center justify-center p-4 modal-backdrop", customer_store_data, selected_rows
    
    return "fixed inset-0 z-50 flex items-center justify-center p-4 modal-backdrop hidden", None, []

@app.callback(
    Output('modal-customer-info', 'children'),
    Input('selected-customer-store', 'data')
)
def update_customer_info(selected_customer):
    if not selected_customer:
        return ""
    return html.Div([
        html.H4(f"{selected_customer['name']}", className="text-lg font-semibold text-gray-800 mb-2"),
        html.Div([
            html.Span([
                html.Strong("SenderCompID: ", className="text-gray-700"),
                html.Span(selected_customer['sendercompid'], className="font-mono bg-blue-100 px-2 py-1 rounded")
            ], className="mr-4"),
            html.Span([
                html.Strong("Region: ", className="text-gray-700"),
                html.Span(selected_customer['region'], className="bg-green-100 px-2 py-1 rounded")
            ])
        ], className="text-sm")
    ])

@app.callback(
    [Output('flow-chart', 'figure'),
     Output('desk-descriptions', 'children'),
     Output('consolidated-rules-table', 'data'),
     Output('consolidated-rules-table', 'columns')],
    [Input('selected-customer-store', 'data')]
)
def update_dashboard(selected_customer):
    if not selected_customer:
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Select a customer to view routing rules", height=500, plot_bgcolor='#f9fafb')
        return empty_fig, "No customer selected", [], []

    sendercompid = selected_customer['sendercompid']
    rules = get_routing_rules_for_customer(sendercompid)
    destinations = get_destinations_for_customer(sendercompid)
    
    # Get consolidated rules
    consolidated_df = get_consolidated_routing_rules_by_priority(sendercompid)
    
    if not rules:
        empty_fig = go.Figure()
        empty_fig.update_layout(title=f"No routing rules for {sendercompid}", height=500, plot_bgcolor='#f9fafb')
        return empty_fig, "No routing rules found", [], []

    # Chart
    fig = create_flow_arrow_chart(rules, sendercompid=sendercompid)

    # Desk descriptions
    desk_elements = []
    for dest in destinations:
        desc = desk_descriptions.get(dest, "No description available")
        color = rules[0]['color'] if rules else '#6b7280'
        desk_elements.append(
            html.Div([
                html.H3(dest, className='text-lg font-semibold text-gray-900 mb-1'),
                html.P(desc, className='text-gray-600 text-sm')
            ], className='p-4 bg-gray-50 rounded-xl border-l-4 hover:shadow-md',
               style={'borderLeftColor': color})
        )

    # Consolidated table data
    if not consolidated_df.empty:
        # Format the consolidated DataFrame for display
        formatted_df = consolidated_df.copy()
        
        # Replace '*' with more readable text
        for col in formatted_df.columns:
            if col != 'SENDERCOMPID':
                formatted_df[col] = formatted_df[col].apply(
                    lambda x: 'All' if x == '*' else ('Singapore' if x == 'SI' else x)
                )
        
        table_data = formatted_df.to_dict('records')
        table_columns = [{"name": col, "id": col} for col in formatted_df.columns]
    else:
        table_data = []
        table_columns = []

    return fig, desk_elements, table_data, table_columns

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)
