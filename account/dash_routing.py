import dash
from dash import html, dash_table, dcc, Input, Output, State
import pandas as pd
import csv
from typing import List, Dict, Any

# Sample customer data - replace with your actual data
customer_data = [
    {'id': 1, 'name': 'Customer A', 'sendercompid': 'BPGICRD', 'region': 'North America'},
    {'id': 2, 'name': 'Customer B', 'sendercompid': 'ARICMCRD', 'region': 'Europe'},
    {'id': 3, 'name': 'Customer C', 'sendercompid': 'GEODECRD', 'region': 'Asia'},
    {'id': 4, 'name': 'Customer D', 'sendercompid': 'ACAMLCRD', 'region': 'North America'},
    {'id': 5, 'name': 'Customer E', 'sendercompid': 'TVMGCRD', 'region': 'Europe'},
    {'id': 6, 'name': 'Customer F', 'sendercompid': 'BPGICRD', 'region': 'Asia'},
]

# Initialize Dash app
app = dash.Dash(__name__)

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

# Routing rules functions
def get_routing_rules(sendercompid: str, csv_file_path: str = 'routing.csv') -> List[Dict[str, Any]]:
    """
    Get routing rules for a given sendercompid from the routing CSV file.
    """
    routing_rules = []
    
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            
            for row in reader:
                if row['SENDERCOMPID'] == sendercompid:
                    routing_rules.append({
                        'SENDERCOMPID': row['SENDERCOMPID'],
                        'CURRENCY': row['CURRENCY'],
                        'TARGETSUBID': row['TARGETSUBID'],
                        'ETF': row['ETF'],
                        'COUNTRYCODE': row['COUNTRYCODE'],
                        'DESTINATION': row['DESTINATION']
                    })
    
    except FileNotFoundError:
        print(f"Error: Routing file '{csv_file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error reading routing file: {e}")
        return []
    
    return routing_rules

def get_smart_routing_display(sendercompid: str) -> List[Dict[str, Any]]:
    """
    Smart routing display that handles single-rule and multi-rule scenarios with currency grouping.
    """
    all_rules = get_routing_rules(sendercompid)
    
    if not all_rules:
        return []
    
    # Check if there's only one rule (typically a catch-all)
    if len(all_rules) == 1:
        single_rule = all_rules[0]
        # Return as "all -> destination"
        return [{
            'conditions': ['all'],
            'DESTINATION': single_rule['DESTINATION'],
            'is_default': True,
            'priority': 1
        }]
    
    # For multiple rules, group specific rules and find default
    specific_rules = []
    default_rule = None
    
    # First, group specific rules by destination and conditions (maintaining currency grouping)
    grouped_specific_rules = {}
    
    for i, rule in enumerate(all_rules, 1):
        # Check if this is a catch-all rule (all wildcards)
        is_catch_all = (
            rule['CURRENCY'] == '*' and 
            rule['TARGETSUBID'] == '*' and 
            rule['ETF'] == '*' and 
            rule['COUNTRYCODE'] == '*'
        )
        
        if is_catch_all:
            default_rule = {
                'conditions': ['rest'],
                'DESTINATION': rule['DESTINATION'],
                'is_default': True,
                'priority': i
            }
        else:
            # Group specific rules by destination and non-currency conditions
            key = (rule['DESTINATION'], rule['TARGETSUBID'], rule['ETF'], rule['COUNTRYCODE'])
            
            if key not in grouped_specific_rules:
                grouped_specific_rules[key] = {
                    'DESTINATION': rule['DESTINATION'],
                    'TARGETSUBID': rule['TARGETSUBID'],
                    'ETF': rule['ETF'],
                    'COUNTRYCODE': rule['COUNTRYCODE'],
                    'CURRENCIES': [],
                    'MIN_PRIORITY': i,
                    'RULE_COUNT': 0
                }
            
            if rule['CURRENCY'] != '*':
                if rule['CURRENCY'] not in grouped_specific_rules[key]['CURRENCIES']:
                    grouped_specific_rules[key]['CURRENCIES'].append(rule['CURRENCY'])
            
            grouped_specific_rules[key]['RULE_COUNT'] += 1
    
    # Convert grouped rules to display format
    for key, grouped_rule in grouped_specific_rules.items():
        conditions = []
        
        # Add currencies as grouped condition
        if grouped_rule['CURRENCIES']:
            sorted_currencies = sorted(grouped_rule['CURRENCIES'])
            if len(sorted_currencies) > 2:
                display_text = f"[{', '.join(sorted_currencies[:2])} +{len(sorted_currencies)-2} more]"
            else:
                display_text = f"[{', '.join(sorted_currencies)}]"
            conditions.append(display_text)
        
        # Add other conditions
        if grouped_rule['TARGETSUBID'] != '*':
            conditions.append(f"SubID:{grouped_rule['TARGETSUBID']}")
        if grouped_rule['COUNTRYCODE'] != '*':
            conditions.append(f"Country:{grouped_rule['COUNTRYCODE']}")
        if grouped_rule['ETF'] != '*':
            conditions.append(f"ETF:{grouped_rule['ETF']}")
        
        specific_rules.append({
            'conditions': conditions,
            'DESTINATION': grouped_rule['DESTINATION'],
            'is_default': False,
            'priority': grouped_rule['MIN_PRIORITY'],
            'rule_count': grouped_rule['RULE_COUNT']
        })
    
    # Sort specific rules by priority
    specific_rules.sort(key=lambda x: x['priority'])
    
    # If no explicit catch-all found, use the last rule as default
    if not default_rule and all_rules:
        default_rule = {
            'conditions': ['rest'],
            'DESTINATION': all_rules[-1]['DESTINATION'],
            'is_default': True,
            'priority': len(all_rules)
        }
    
    # Combine specific rules and default rule
    display_rules = specific_rules
    if default_rule:
        display_rules.append(default_rule)
    
    return display_rules

def create_routing_csv():
    """
    Create the routing CSV file from the provided data
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
    
    with open('routing.csv', 'w', encoding='utf-8') as f:
        f.write(csv_content)

# Create the routing CSV file
create_routing_csv()

# Convert customer data to DataFrame
df_customers = pd.DataFrame(customer_data)

# App layout
app.layout = html.Div([
    # Main content
    html.Div([
        html.Div([
            html.H1("Customer Routing Rules", className="text-3xl font-bold text-gray-800 mb-2"),
            html.P("Click on any customer to view their routing rules", className="text-gray-600")
        ], className="text-center mb-8"),
        
        html.Div([
            html.H2("Customers", className="text-xl font-semibold text-gray-700 mb-4"),
            html.Div([
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
                        'textAlign': 'left', 
                        'padding': '12px',
                        'fontFamily': 'Inter, sans-serif',
                        'minWidth': '80px', 'width': '150px', 'maxWidth': '250px'
                    },
                    style_header={
                        'backgroundColor': '#f8fafc',
                        'fontWeight': '600',
                        'borderBottom': '2px solid #e2e8f0',
                        'textAlign': 'left'
                    },
                    style_data={
                        'border': '1px solid #e2e8f0'
                    },
                    style_data_conditional=[
                        {
                            'if': {'state': 'selected'},
                            'backgroundColor': '#dbeafe',
                            'border': '2px solid #3b82f6'
                        },
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f8fafc'
                        }
                    ]
                )
            ], className="bg-white rounded-lg shadow-sm border border-gray-200 p-4")
        ], className="mb-8")
    ], className="container mx-auto px-4 py-8 max-w-6xl"),
    
    # Modal Dialog
    html.Div([
        html.Div([
            # Modal header
            html.Div([
                html.Div([
                    html.H3("Routing Rules", className="text-xl font-semibold text-gray-800"),
                    html.Button(
                        html.I(className="fas fa-times text-lg"),
                        id="close-modal",
                        className="text-gray-400 hover:text-gray-600 transition-colors duration-200 p-1 rounded-full hover:bg-gray-100"
                    )
                ], className="flex justify-between items-center")
            ], className="px-6 py-4 border-b border-gray-200 bg-gray-50 rounded-t-lg"),
            
            # Modal body
            html.Div([
                html.Div(id="modal-customer-info", className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200"),
                html.Div(id="modal-routing-rules", className="space-y-2")
            ], className="px-6 py-4")
        ], className="bg-white rounded-lg shadow-xl w-full max-w-4xl mx-auto transform transition-all")
    ], id="routing-modal", className="fixed inset-0 z-50 flex items-center justify-center p-4 modal-backdrop hidden"),
    
    # Store component
    dcc.Store(id='selected-customer-store'),
    
    # Hidden div to track modal state
    html.Div(id='modal-state', style={'display': 'none'})
])

@app.callback(
    [Output('routing-modal', 'className'),
     Output('selected-customer-store', 'data'),
     Output('customer-table', 'selected_rows')],
    [Input('customer-table', 'selected_rows'),
     Input('close-modal', 'n_clicks'),
     Input('modal-state', 'children')],
    [State('customer-table', 'data'),
     State('routing-modal', 'className'),
     State('selected-customer-store', 'data')]
)
def toggle_modal(selected_rows, close_clicks, modal_state, customer_data, current_class, stored_customer):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "fixed inset-0 z-50 flex items-center justify-center p-4 modal-backdrop hidden", None, []
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'close-modal':
        return "fixed inset-0 z-50 flex items-center justify-center p-4 modal-backdrop hidden", None, []
    
    if trigger_id == 'customer-table' and selected_rows:
        selected_row_index = selected_rows[0]
        selected_customer = customer_data[selected_row_index]
        
        customer_store_data = {
            'id': selected_customer['id'],
            'name': selected_customer['name'],
            'sendercompid': selected_customer['sendercompid'],
            'region': selected_customer['region']
        }
        
        # Always open modal when a row is clicked, even if it's the same row
        return "fixed inset-0 z-50 flex items-center justify-center p-4 modal-backdrop", customer_store_data, selected_rows
    
    return "fixed inset-0 z-50 flex items-center justify-center p-4 modal-backdrop hidden", None, []

@app.callback(
    Output('modal-customer-info', 'children'),
    [Input('selected-customer-store', 'data')]
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
    Output('modal-routing-rules', 'children'),
    [Input('selected-customer-store', 'data')]
)
def update_modal_routing_rules(selected_customer):
    if not selected_customer:
        return html.Div(
            "No customer selected",
            className="text-center text-gray-500 py-8"
        )
    
    sendercompid = selected_customer['sendercompid']
    display_rules = get_smart_routing_display(sendercompid)
    
    if not display_rules:
        return html.Div(
            "No routing rules found for this customer",
            className="text-center text-gray-500 py-8"
        )
    
    rules_rows = []
    
    for rule in display_rules:
        condition_badges = []
        
        if rule['is_default']:
            # Default rule - "all" or "rest"
            if rule['conditions'][0] == 'all':
                condition_badges.append(
                    html.Span("all", className="all-badge px-3 py-1 rounded text-sm font-bold")
                )
            else:  # 'rest'
                condition_badges.append(
                    html.Span("rest", className="default-badge px-3 py-1 rounded text-sm font-bold")
                )
            
            row_class = "default-row"
        else:
            # Specific rule with currency grouping
            condition_badges.append(
                html.Span(f"#{rule['priority']}", className="priority-badge px-2 py-1 rounded text-xs font-bold")
            )
            
            # Add rule count badge if multiple rules were grouped
            if rule.get('rule_count', 1) > 1:
                condition_badges.append(
                    html.Span(f"{rule['rule_count']} rules", className="priority-badge px-2 py-1 rounded text-xs")
                )
            
            # Add all conditions (currencies are already grouped)
            for condition in rule['conditions']:
                if condition.startswith('[') and condition.endswith(']'):
                    # Currency group
                    condition_badges.append(
                        html.Span(condition, className="currency-group-badge px-2 py-1 rounded text-xs font-medium")
                    )
                elif condition.startswith('SubID:'):
                    condition_badges.append(
                        html.Span(condition, className="target-badge px-2 py-1 rounded text-xs")
                    )
                elif condition.startswith('Country:'):
                    condition_badges.append(
                        html.Span(condition, className="country-badge px-2 py-1 rounded text-xs")
                    )
                elif condition.startswith('ETF:'):
                    condition_badges.append(
                        html.Span(condition, className="target-badge px-2 py-1 rounded text-xs")
                    )
            
            row_class = "rule-row"
        
        row = html.Div([
            html.Div([
                # Left side - Conditions
                html.Div([
                    html.Div(condition_badges, className="flex items-center gap-1 flex-wrap")
                ], className="flex-1"),
                
                # Arrow
                html.Div([
                    html.Span("→", className="text-gray-400 mx-2")
                ], className="flex items-center"),
                
                # Right side - Destination
                html.Div([
                    html.Span(
                        rule['DESTINATION'],
                        className="destination-badge px-3 py-1 rounded text-sm font-semibold"
                    )
                ], className="flex items-center")
            ], className="flex items-center justify-between py-2 px-3")
        ], className=f"{row_class} bg-white rounded border border-gray-100 hover:shadow-sm")
        
        rules_rows.append(row)
    
    return html.Div(rules_rows)

if __name__ == '__main__':
    app.run(debug=True, port=8050)
