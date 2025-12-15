import dash
from dash import html, dash_table, dcc, Input, Output, State
import pandas as pd
from typing import List, Dict, Any
import plotly.graph_objects as go
import io # Added for in-memory file handling

# --- IMPORT CONSOLIDATION FUNCTION ---
# Assuming consolidate_rule_drop.py is in the same directory
from consolidate_rule_drop import get_consolidated_routing_rules_by_priority

# Sample customer data (no change)
customer_data = [
    {'id': 1, 'name': 'Customer A', 'sendercompid': 'BPGICRD', 'region': 'North America'},
    {'id': 2, 'name': 'Customer B', 'sendercompid': 'ARICMCRD', 'region': 'Europe'},
    {'id': 3, 'name': 'Customer C', 'sendercompid': 'GEODECRD', 'region': 'Asia'},
    {'id': 4, 'name': 'Customer D', 'sendercompid': 'ACAMLCRD', 'region': 'North America'},
    {'id': 5, 'name': 'Customer E', 'sendercompid': 'TVMGCRD', 'region': 'Europe'},
    {'id': 6, 'name': 'Customer F', 'sendercompid': 'BPGICRD', 'region': 'Asia'},
]

# Embedded CSV content (no change)
CSV_CONTENT = """SENDERCOMPID;CURRENCY;TARGETSUBID;ETF;COUNTRYCODE;DESTINATION
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

# --- NEW FUNCTION FOR CONSOLIDATION ---
# This function wraps the get_consolidated_routing_rules_by_priority
def get_consolidated_rules_for_dash(sender_comp_id: str) -> pd.DataFrame:
    # Use io.StringIO to treat the CSV string content as a file
    csv_file_like = io.StringIO(CSV_CONTENT)
    # The get_consolidated_routing_rules_by_priority is designed to read a file,
    # but here we pass the in-memory object (StringIO) as the file path.
    # We must ensure the underlying function can handle a file-like object 
    # instead of a path, or just pass a temporary path if needed.
    # As an immediate fix, we'll write the content to a temporary file 
    # if the consolidation function cannot handle StringIO, but for simplicity 
    # and to avoid file I/O, let's modify the way the consolidation function is called 
    # or create a local copy that first loads the data into a DataFrame.

    # TEMPORARY: Directly load into DataFrame and pass it (a cleaner solution would 
    # be to modify get_consolidated_routing_rules_by_priority to accept a DataFrame)
    
    lines = CSV_CONTENT.strip().split('\n')
    headers = lines[0].split(';')
    data = [line.split(';') for line in lines[1:]]
    df_raw = pd.DataFrame(data, columns=headers)
    
    # We will need a file path to use the existing function as written:
    TEMP_FILE_PATH = "temp_routing.csv"
    with open(TEMP_FILE_PATH, "w") as f:
        f.write(CSV_CONTENT)
        
    consolidated_df = get_consolidated_routing_rules_by_priority(TEMP_FILE_PATH, sender_comp_id)
    return consolidated_df.fillna('*') # Fill NaN from dropped columns with '*' for display

# --- MODIFIED/REMOVED FUNCTIONS ---

# This function is now **REMOVED** as its logic is replaced by the consolidation function.
# def create_routing_rules_from_csv(): ... 
# def get_routing_rules_for_customer(sendercompid: str) -> List[Dict[str, Any]]: ...

# We will need a new helper function to transform the consolidated DataFrame 
# into the list-of-dicts format required by create_flow_arrow_chart
def transform_consolidated_df_to_chart_rules(df: pd.DataFrame, sendercompid: str) -> List[Dict[str, Any]]:
    if df.empty:
        return []
    
    destination_colors = {
        'O_FLEXTRADE_GLOBAL_PT_FIX42': '#3b82f6',  # Blue
        'MizuhoTKGOR42BuySide': '#10b981',         # Green
        'FlexTradeBuySide42': '#f59e0b'            # Orange
    }
    
    chart_rules = []
    # Columns not in the final consolidated df will be missing (e.g., if TARGETSUBID/ETF/COUNTRYCODE 
    # only contained '*' and were dropped). Check for their existence.
    cols = df.columns
    
    for _, rule in df.iterrows():
        order_type_parts = []
        
        # CURRENCIES is always present and consolidated
        if rule['CURRENCIES'] != '*':
            order_type_parts.append(rule['CURRENCIES'])
            
        if 'TARGETSUBID' in cols and rule['TARGETSUBID'] != '*':
            order_type_parts.append(f"SubID:{rule['TARGETSUBID']}")
        
        if 'COUNTRYCODE' in cols and rule['COUNTRYCODE'] != '*':
            country_name = "Singapore" if rule['COUNTRYCODE'] == 'SI' else rule['COUNTRYCODE']
            order_type_parts.append(f"Country:{country_name}")
            
        if 'ETF' in cols and rule['ETF'] != '*':
            order_type_parts.append(f"ETF:{rule['ETF']}")
        
        order_type = f"{' + '.join(order_type_parts)} - {sendercompid}" if order_type_parts else f"All Orders - {sendercompid}"
        color = destination_colors.get(rule['DESTINATION'], '#6b7280')
        
        chart_rules.append({
            'orderType': order_type,
            'destination': rule['DESTINATION'],
            'color': color,
            'sendercompid': sendercompid # Rule is already filtered
        })
    return chart_rules

def get_destinations_for_consolidated_rules(df: pd.DataFrame) -> List[str]:
    if df.empty:
        return []
    return list(df['DESTINATION'].unique())

# Desk descriptions (no change)
desk_descriptions = {
    'O_FLEXTRADE_GLOBAL_PT_FIX42': 'Primary global order routing destination for standard executions',
    'MizuhoTKGOR42BuySide': 'Mizuho Bank routing for specific currencies and country codes',
    'FlexTradeBuySide42': 'FlexTrade system for USD and CAD currency orders'
}

def trim_sendercompid_from_order_type(order_type: str) -> str:
    if " - " in order_type:
        return order_type.rsplit(" - ", 1)[0].rstrip()
    return order_type.rstrip()

# create_flow_arrow_chart (no change)
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
    title_text = f"Consolidated Order Routing Flow for {sendercompid}" if sendercompid else "Order Routing Flow - Directional Arrow Diagram"
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


# Convert customer data to DataFrame (no change)
df_customers = pd.DataFrame(customer_data)

# Initialize Dash app (no change)
app = dash.Dash(__name__)

# App layout (MODIFIED to include a DataTable for consolidated rules)
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
                
                # ✅ ADDED: Consolidated Routing Rules Table
                html.Div([
                    html.H2('Consolidated Rules (Priority Order)', className='text-xl font-semibold text-gray-900 mb-4'),
                    dash_table.DataTable(
                        id='consolidated-rules-table',
                        columns=[], # Will be populated in callback
                        data=[],    # Will be populated in callback
                        style_header={'backgroundColor': '#f8fafc', 'fontWeight': 'bold'},
                        style_data={'whiteSpace': 'normal', 'height': 'auto'},
                        style_cell={'textAlign': 'left', 'padding': '10px'},
                        # Add a tooltip for CURRENCIES to show the full list if it wraps
                        tooltip_data=[
                            {
                                'CURRENCIES': {'value': r['CURRENCIES'], 'type': 'markdown'}
                                for r in df.to_dict('records')
                            } for df in [pd.DataFrame()] # Initialize with empty DataFrame
                        ],
                        export_format='csv',
                        className='mb-8'
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
    # Add a dcc.Store to cache the consolidated data for use by multiple callbacks
    dcc.Store(id='consolidated-rules-store'), 
    html.Div(id='modal-state', style={'display': 'none'})
])

# Callbacks (toggle_modal and update_customer_info remain unchanged)

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


# --- NEW CALLBACK TO COMPUTE AND STORE CONSOLIDATED RULES ---
@app.callback(
    Output('consolidated-rules-store', 'data'),
    Input('selected-customer-store', 'data')
)
def compute_consolidated_rules(selected_customer):
    if not selected_customer:
        return pd.DataFrame().to_dict('records') # Return empty list of dicts
    
    sendercompid = selected_customer['sendercompid']
    consolidated_df = get_consolidated_rules_for_dash(sendercompid)
    
    # Store the DataFrame data in the dcc.Store as a list of dictionaries (JSON serializable)
    return consolidated_df.to_dict('records')

# --- MODIFIED CALLBACK TO UPDATE DASHBOARD (Chart and Descriptions) ---
@app.callback(
    [Output('flow-chart', 'figure'),
     Output('desk-descriptions', 'children')],
    [Input('consolidated-rules-store', 'data'),
     State('selected-customer-store', 'data')]
)
def update_dashboard(consolidated_rules_data, selected_customer):
    if not selected_customer or not consolidated_rules_data:
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Select a customer to view routing rules", height=500, plot_bgcolor='#f9fafb')
        return empty_fig, "No customer selected or no rules found"

    sendercompid = selected_customer['sendercompid']
    consolidated_df = pd.DataFrame(consolidated_rules_data)

    if consolidated_df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(title=f"No consolidated routing rules for {sendercompid}", height=500, plot_bgcolor='#f9fafb')
        return empty_fig, "No routing rules found"

    # 1. Chart Data
    rules = transform_consolidated_df_to_chart_rules(consolidated_df, sendercompid)
    fig = create_flow_arrow_chart(rules, sendercompid=sendercompid)

    # 2. Desk descriptions
    destinations = get_destinations_for_consolidated_rules(consolidated_df)
    desk_elements = []
    
    # Get a list of colors from the rules for consistent display in descriptions
    destination_color_map = {rule['destination']: rule['color'] for rule in rules}
    
    for dest in destinations:
        desc = desk_descriptions.get(dest, "No description available")
        color = destination_color_map.get(dest, '#6b7280') # Use mapped color or default
        desk_elements.append(
            html.Div([
                html.H3(dest, className='text-lg font-semibold text-gray-900 mb-1'),
                html.P(desc, className='text-gray-600 text-sm')
            ], className='p-4 bg-gray-50 rounded-xl border-l-4 hover:shadow-md',
               style={'borderLeftColor': color})
        )

    return fig, desk_elements

# --- NEW CALLBACK TO UPDATE CONSOLIDATED RULES TABLE ---
@app.callback(
    [Output('consolidated-rules-table', 'data'),
     Output('consolidated-rules-table', 'columns')],
    [Input('consolidated-rules-store', 'data')]
)
def update_consolidated_table(consolidated_rules_data):
    if not consolidated_rules_data:
        return [], []

    df = pd.DataFrame(consolidated_rules_data)
    
    # Create columns list from DataFrame headers
    columns = [{"name": i, "id": i} for i in df.columns]

    return df.to_dict('records'), columns


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)