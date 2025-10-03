import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd

# Mock data for the table
mock_account_data = pd.DataFrame({
    'account_number': ['20012833', '20012438', '20012426', '20012567', '20012689'],
    'account_name': ['Account A', 'Account B', 'Account C', 'Account D', 'Account E'],
    'status': ['Active', 'Inactive', 'Active', 'Pending', 'Active']
})

# Mock function to get routing rules
def get_routing_rules(account_number):
    """Mock function to simulate getting routing rules for an account"""
    routing_rules = {
        '20012833': [
            {'rule': 'Rule 0, 1', 'condition': '#TARGETSUBID-PROG', 'result': 'PT17'},
            {'rule': 'Rule 1, 2', 'condition': 'All other cases', 'result': 'IS17'},
            {'rule': 'Rule 2, 3', 'condition': 'ETF-yes', 'result': 'IS17'}
        ],
        '20012438': [
            {'rule': 'Rule 0, 1', 'condition': '#TARGETSUBID-PROG', 'result': 'PT17'},
            {'rule': 'Rule 1, 2', 'condition': 'All other cases', 'result': 'IS17'}
        ],
        '20012426': [
            {'rule': 'Rule 0, 1', 'condition': '#TARGETSUBID-PROG', 'result': 'PT17'},
            {'rule': 'Rule 1, 2', 'condition': 'All other cases', 'result': 'IS17'}
        ]
    }
    return routing_rules.get(account_number, [])

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
    html.H1("Account Management System", className="text-3xl font-bold text-center mb-8 text-gray-800"),
    
    # Accounts Table
    html.Div([
        dash_table.DataTable(
            id='accounts-table',
            columns=[
                {"name": "Account Number", "id": "account_number"},
                {"name": "Account Name", "id": "account_name"},
                {"name": "Status", "id": "status"}
            ],
            data=mock_account_data.to_dict('records'),
            row_selectable='single',
            selected_rows=[],
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_table={'marginBottom': '2rem'}
        )
    ], className="mb-8"),
    
    # Modal for displaying routing rules
    html.Div([
        # Modal backdrop
        html.Div(
            id="modal-backdrop",
            className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 hidden"
        ),
        # Modal content
        html.Div(
            id="modal-content",
            className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 hidden",
            children=[
                html.Div([
                    # Modal header
                    html.Div([
                        html.H3("Routing Rules", className="text-xl font-semibold text-gray-900"),
                        html.Button(
                            "×",
                            id="modal-close-btn",
                            className="text-gray-400 bg-transparent hover:bg-gray-200 rounded-lg text-sm p-1.5 ml-auto inline-flex items-center"
                        )
                    ], className="flex items-start justify-between p-4 border-b rounded-t"),
                    
                    # Modal body
                    html.Div([
                        html.Div(id="modal-account-info", className="mb-4"),
                        html.Div(id="modal-rules-content")
                    ], className="p-6 space-y-4"),
                    
                    # Modal footer
                    html.Div([
                        html.Button(
                            "Close",
                            id="modal-close-btn-2",
                            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                        )
                    ], className="flex items-center p-6 border-t border-gray-200 rounded-b")
                ], className="relative bg-white rounded-lg shadow-lg w-full max-w-md")
            ]
        )
    ], id="modal")
])

# Callback to show/hide modal and update content
@app.callback(
    [Output('modal-backdrop', 'className'),
     Output('modal-content', 'className'),
     Output('modal-account-info', 'children'),
     Output('modal-rules-content', 'children')],
    [Input('accounts-table', 'selected_rows'),
     Input('modal-close-btn', 'n_clicks'),
     Input('modal-close-btn-2', 'n_clicks')],
    [State('accounts-table', 'data')],
    prevent_initial_call=True
)
def handle_modal(selected_rows, close_btn1, close_btn2, table_data):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return [dash.no_update] * 4
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Handle modal close
    if trigger_id in ['modal-close-btn', 'modal-close-btn-2']:
        return ["fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 hidden", 
                "fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 hidden", 
                "", ""]
    
    # Handle row selection - show modal
    elif trigger_id == 'accounts-table' and selected_rows:
        selected_row = selected_rows[0]
        account_data = table_data[selected_row]
        account_number = account_data['account_number']
        
        # Get routing rules
        rules = get_routing_rules(account_number)
        
        # Create account info with Tailwind classes
        account_info = html.Div([
            html.H4(f"Account: {account_number}", className="text-lg font-bold text-gray-800 mb-2"),
            html.P(f"Name: {account_data['account_name']}", className="text-gray-600 mb-1"),
            html.P(f"Status: {account_data['status']}", className="text-gray-600")
        ])
        
        # Create rules display with Tailwind classes
        if rules:
            rules_elements = []
            for rule in rules:
                rule_element = html.Div([
                    html.Span(f"{rule['rule']}: ", className="font-bold text-blue-600"),
                    html.Span(rule['condition'], className="text-gray-700"),
                    html.Span(" → ", className="mx-2"),
                    html.Span(rule['result'], className="font-bold text-green-600")
                ], className="p-3 bg-blue-50 rounded border-l-4 border-blue-500 mb-2")
                rules_elements.append(rule_element)
            
            rules_content = html.Div(rules_elements, className="space-y-2")
        else:
            rules_content = html.Div("No routing rules found for this account.", 
                                   className="text-gray-500 italic")
        
        # Show modal
        return ["fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50", 
                "fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50", 
                account_info, rules_content]
    
    return [dash.no_update] * 4

# Callback to clear table selection when modal closes
@app.callback(
    Output('accounts-table', 'selected_rows'),
    [Input('modal-close-btn', 'n_clicks'),
     Input('modal-close-btn-2', 'n_clicks')],
    prevent_initial_call=True
)
def clear_selection(close1, close2):
    return []

if __name__ == '__main__':
    app.run(debug=True)
