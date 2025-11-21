import dash
from dash import dcc, html, Input, Output, callback, State, clientside_callback
import plotly.express as px
import pandas as pd
import numpy as np
import time
import json
import os
import re
from urllib.parse import urlparse

# Sample data
np.random.seed(42)
df = pd.DataFrame({
    'Category': ['A', 'B', 'C', 'D', 'E'] * 20,
    'Value': np.random.randn(100),
    'Date': pd.date_range('2023-01-01', periods=100, freq='D')
})

def safe_date_format(date_obj, format_str='%Y-%m-%d'):
    """Safely format a date object, handling both datetime and string inputs"""
    if hasattr(date_obj, 'strftime'):
        return date_obj.strftime(format_str)
    else:
        try:
            return pd.to_datetime(date_obj).strftime(format_str)
        except:
            return str(date_obj)

def load_domains():
    """Load companies and their owned domains from domains.json file"""
    try:
        if os.path.exists('domains.json'):
            with open('domains.json', 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return {domain: [] for domain in data}
                elif isinstance(data, dict):
                    if all(isinstance(v, list) for v in data.values()):
                        return data
                    else:
                        return {}
                return data
        return {}
    except:
        return {}

def save_domains(companies_data):
    """Save companies and their domains to domains.json file"""
    try:
        with open('domains.json', 'w') as f:
            json.dump(companies_data, f, indent=2)
        return True
    except:
        return False

def clean_domain(url):
    """Clean and extract domain from URL"""
    if not url:
        return None
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc if parsed.netloc else parsed.hostname
        
        if domain and domain.startswith('www.'):
            domain = domain[4:]
        
        return domain.lower()
    except:
        return None

# Load initial domains data
domains_data = load_domains()

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Define the layout
app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.H1("Dashboard Analytics", className="text-3xl font-bold text-gray-800 mb-2"),
            html.P("Interactive data visualization with company & domain management", className="text-gray-600")
        ], className="flex-1"),
        
        html.Div([
            html.Button(
                "Admin Login", 
                id="admin-login-button", 
                n_clicks=0,
                className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200 mr-3"
            ),
            html.Button(
                "Manage Companies & Domains", 
                id="add-website-button", 
                n_clicks=0,
                disabled=True,
                className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200 mr-3 disabled:bg-gray-300 disabled:cursor-not-allowed"
            ),
            html.Button(
                "Update Data", 
                id="update-button", 
                n_clicks=0,
                disabled=True,
                className="bg-blue-500 hover:bg-blue-700 disabled:bg-gray-300 text-white font-bold py-2 px-4 rounded transition-colors duration-200 disabled:cursor-not-allowed"
            ),
            html.Div(id="update-status", className="ml-4 text-sm")
        ], className="flex items-center")
    ], className="bg-white p-6 shadow-sm mb-6 flex justify-between items-center"),
    
    # Loading overlay
    html.Div(
        id="loading-overlay",
        className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 hidden",
        children=[
            html.Div(
                className="bg-white p-6 rounded-lg shadow-lg text-center",
                children=[
                    html.Div(className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"),
                    html.Div("Updating data...", className="text-lg font-semibold mb-2"),
                    html.Div("Please wait while we fetch the latest data", className="text-gray-600")
                ]
            )
        ]
    ),
    
    # Company Dialog Modal
    html.Div(
        id="website-dialog-overlay",
        className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 hidden",
        children=[
            html.Div(
                className="bg-white p-6 rounded-lg shadow-lg w-full max-w-6xl mx-4 max-h-[90vh] overflow-hidden flex flex-col",
                children=[
                    html.Div([
                        html.H3("Manage Companies & Domains", id="dialog-title", className="text-xl font-bold text-gray-800"),
                        html.Button(
                            "×", 
                            id="close-dialog-button",
                            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-2xl font-bold w-8 h-8 flex items-center justify-center"
                        )
                    ], className="relative mb-4 flex justify-between items-center"),
                    
                    dcc.Tabs(id="company-type-tabs", value='single-company', className="mb-4", children=[
                        dcc.Tab(label='Single Company', value='single-company', className="px-4 py-2 font-semibold"),
                        dcc.Tab(label='Parent Company (Holding)', value='parent-company', className="px-4 py-2 font-semibold"),
                    ]),
                    
                    html.Div(id='company-tabs-content', className="flex-1 overflow-hidden flex flex-col"),
                    
                    html.Div(id="dialog-status-message", className="mt-4"),
                    
                    html.Div([
                        html.Button(
                            "Close",
                            id="cancel-dialog-button", 
                            className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-6 rounded transition-colors duration-200"
                        )
                    ], className="flex justify-end mt-4 pt-4 border-t border-gray-200")
                ]
            )
        ]
    ),
    
    # Admin Login Dialog Modal
    html.Div(
        id="admin-login-overlay",
        className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 hidden",
        children=[
            html.Div(
                className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md mx-4",
                children=[
                    html.H3("Admin Login", className="text-xl font-bold text-gray-800 mb-4"),
                    html.Div([
                        html.Label("Password:", className="block text-sm font-medium text-gray-700 mb-2"),
                        dcc.Input(
                            id="admin-password-input",
                            type="password",
                            placeholder="Enter admin password",
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent mb-3",
                            style={"fontSize": "14px"}
                        ),
                        html.Div(id="admin-login-message", className="mb-4 text-sm")
                    ]),
                    html.Div([
                        html.Button(
                            "Cancel",
                            id="cancel-admin-login-button",
                            className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-6 rounded transition-colors duration-200 mr-3"
                        ),
                        html.Button(
                            "Login",
                            id="submit-admin-login-button",
                            className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-6 rounded transition-colors duration-200"
                        )
                    ], className="flex justify-end")
                ]
            )
        ]
    ),
    
    # Confirmation Dialog Modal
    html.Div(
        id="confirmation-dialog-overlay",
        className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 hidden",
        children=[
            html.Div(
                className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md mx-4",
                children=[
                    html.H3("Confirm Changes", className="text-xl font-bold text-gray-800 mb-4"),
                    html.P(id="confirmation-message", className="text-gray-600 mb-6"),
                    html.Div([
                        html.Button(
                            "Cancel",
                            id="cancel-confirmation-button",
                            className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-6 rounded transition-colors duration-200 mr-3"
                        ),
                        html.Button(
                            "Confirm",
                            id="confirm-confirmation-button",
                            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded transition-colors duration-200"
                        )
                    ], className="flex justify-end")
                ]
            )
        ]
    ),
    
    # Tabs
    dcc.Tabs(id="tabs", value='tab-4', className="mb-6", children=[
        dcc.Tab(label='Companies & Domains', value='tab-4', className="px-4 py-2 font-semibold"),
        dcc.Tab(label='Overview', value='tab-1', className="px-4 py-2 font-semibold"),
        dcc.Tab(label='Charts', value='tab-2', className="px-4 py-2 font-semibold"),
        dcc.Tab(label='Data Table', value='tab-3', className="px-4 py-2 font-semibold"),
    ]),
    
    html.Div(id='tabs-content', className="bg-white p-6 rounded-lg shadow-sm"),
    
    # Store components
    dcc.Store(id='data-store', data=df.to_dict('records')),
    dcc.Store(id='loading-state', data=False),
    dcc.Store(id='companies-store', data=domains_data),
    dcc.Store(id='dialog-state', data=False),
    dcc.Store(id='selected-company', data=None),
    dcc.Store(id='current-company-type', data='single-company'),
    dcc.Store(id='pending-changes', data=None),
    dcc.Store(id='confirmation-state', data=False),
    dcc.Store(id='admin-authenticated', data=False),
    dcc.Store(id='admin-login-dialog-state', data=False)
], className="min-h-screen bg-gray-50 p-6", id="main-container")

# Callback to update company tabs content
@app.callback(
    Output('company-tabs-content', 'children'),
    Input('company-type-tabs', 'value'),
    prevent_initial_call=False
)
def render_company_tabs_content(company_type):
    if company_type == 'single-company':
        return html.Div([
            html.Div([
                html.Div([
                    html.H4("Single Companies", className="text-lg font-semibold text-gray-700 mb-3"),
                    html.Div(
                        id="single-companies-list-container",
                        className="bg-gray-50 rounded-lg p-4 max-h-80 overflow-y-auto border border-gray-200",
                        children=[html.Div("Loading single companies...", className="text-gray-500 text-center p-4")]
                    ),
                    html.Div(id="single-companies-count", className="text-sm text-gray-600 mt-2")
                ], className="flex-1 pr-4"),
                
                html.Div([
                    html.H4("Add/Edit Single Company", className="text-lg font-semibold text-gray-700 mb-3"),
                    html.Div([
                        html.Label("Company Domain:", className="block text-sm font-medium text-gray-700 mb-2"),
                        dcc.Input(
                            id="single-company-input",
                            type="text",
                            placeholder="Enter company domain (e.g., adobe.com)",
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                            style={"fontSize": "14px"}
                        ),
                        html.Div(id="single-company-validation-message", className="mt-2 text-sm"),
                        
                        dcc.Input(id="edit-single-company-index", type="hidden", value=-1),
                        
                        html.Div([
                            html.Button(
                                "Clear",
                                id="clear-single-form-button", 
                                className="bg-gray-300 hover:bg-gray-400 text-gray-700 font-bold py-2 px-4 rounded mr-2 transition-colors duration-200"
                            ),
                            html.Button(
                                "Add Single Company",
                                id="submit-single-company-button", 
                                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
                            )
                        ], className="flex justify-end mt-6")
                    ], className="bg-white p-4 rounded-lg border border-gray-200")
                ], className="flex-1 pl-4")
            ], className="flex flex-1 space-x-4")
        ])
    else:  # parent-company
        return html.Div([
            html.Div([
                html.Div([
                    html.H4("Parent Companies", className="text-lg font-semibold text-gray-700 mb-3"),
                    html.Div(
                        id="parent-companies-list-container",
                        className="bg-gray-50 rounded-lg p-4 max-h-80 overflow-y-auto border border-gray-200",
                        children=[html.Div("Loading parent companies...", className="text-gray-500 text-center p-4")]
                    ),
                    html.Div(id="parent-companies-count", className="text-sm text-gray-600 mt-2")
                ], className="flex-1 pr-4"),
                
                html.Div([
                    html.H4("Add/Edit Parent Company", className="text-lg font-semibold text-gray-700 mb-3"),
                    html.Div([
                        html.Label("Parent Company Name:", className="block text-sm font-medium text-gray-700 mb-2"),
                        dcc.Input(
                            id="parent-company-input",
                            type="text",
                            placeholder="Enter parent company name (e.g., MSFT)",
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                            style={"fontSize": "14px"}
                        ),
                        html.Div(id="parent-company-validation-message", className="mt-2 text-sm"),
                        
                        dcc.Input(id="edit-parent-company-index", type="hidden", value=-1),
                        
                        html.Div([
                            html.Button(
                                "Clear",
                                id="clear-parent-form-button", 
                                className="bg-gray-300 hover:bg-gray-400 text-gray-700 font-bold py-2 px-4 rounded mr-2 transition-colors duration-200"
                            ),
                            html.Button(
                                "Add Parent Company",
                                id="submit-parent-company-button", 
                                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
                            )
                        ], className="flex justify-end mt-6")
                    ], className="bg-white p-4 rounded-lg border border-gray-200")
                ], className="flex-1 px-4 border-l border-r border-gray-200"),
                
                html.Div([
                    html.H4("Manage Subsidiary Domains", className="text-lg font-semibold text-gray-700 mb-3"),
                    html.Div([
                        html.Label("Selected Parent Company:", className="block text-sm font-medium text-gray-700 mb-2"),
                        html.Div(id="selected-parent-company-display", className="text-sm text-gray-600 mb-4 p-2 bg-gray-50 rounded"),
                        html.Label("Add Subsidiary Domain:", className="block text-sm font-medium text-gray-700 mb-2"),
                        dcc.Input(
                            id="subsidiary-domain-input",
                            type="text",
                            placeholder="Enter subsidiary domain (e.g., microsoft.com)",
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-2",
                            style={"fontSize": "14px"}
                        ),
                        html.Button(
                            "Add Subsidiary Domain",
                            id="add-subsidiary-domain-button",
                            className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200 w-full mb-4"
                        ),
                        html.Label("Current Subsidiary Domains:", className="block text-sm font-medium text-gray-700 mb-2"),
                        html.Div(
                            id="subsidiary-domains-list-container",
                            className="bg-gray-50 rounded-lg p-3 max-h-48 overflow-y-auto border border-gray-200",
                            children=[html.Div("Select a parent company to manage subsidiary domains", className="text-gray-500 text-center p-4")]
                        )
                    ], className="bg-white p-4 rounded-lg border border-gray-200")
                ], className="flex-1 pl-4")
            ], className="flex flex-1 space-x-4")
        ])

# Callback to handle admin login dialog opening
@app.callback(
    [Output('admin-login-dialog-state', 'data'),
     Output('admin-login-message', 'children', allow_duplicate=True)],
    [Input('admin-login-button', 'n_clicks'),
     Input('cancel-admin-login-button', 'n_clicks')],
    [State('admin-authenticated', 'data')],
    prevent_initial_call=True
)
def handle_admin_login_dialog(login_clicks, cancel_clicks, is_authenticated):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # If already authenticated, don't open dialog
    if button_id == 'admin-login-button' and is_authenticated:
        return False, ""
    
    if button_id == 'admin-login-button':
        return True, ""
    elif button_id == 'cancel-admin-login-button':
        return False, ""
    
    return dash.no_update, dash.no_update

# Clientside callback for admin login dialog visibility
clientside_callback(
    """
    function(dialog_open) {
        const dialogOverlay = document.getElementById('admin-login-overlay');
        
        if (dialog_open) {
            if (dialogOverlay) {
                dialogOverlay.classList.remove('hidden');
            }
            return 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50';
        } else {
            if (dialogOverlay) {
                dialogOverlay.classList.add('hidden');
            }
            return 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 hidden';
        }
    }
    """,
    Output('admin-login-overlay', 'className'),
    Input('admin-login-dialog-state', 'data'),
    prevent_initial_call=True
)

# Callback to handle admin login submission
@app.callback(
    [Output('admin-authenticated', 'data'),
     Output('admin-password-input', 'value'),
     Output('admin-login-message', 'children'),
     Output('admin-login-button', 'children'),
     Output('admin-login-button', 'className')],
    Input('submit-admin-login-button', 'n_clicks'),
    [State('admin-password-input', 'value'),
     State('admin-authenticated', 'data')],
    prevent_initial_call=True
)
def handle_admin_login(n_clicks, password, is_authenticated):
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    if password == "test123":
        success_msg = html.Div([
            html.Span("✅ ", className="mr-2"),
            html.Span("Login successful!", className="text-green-600 font-semibold")
        ])
        return True, "", success_msg, "Admin (Logged In)", "bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200 mr-3"
    else:
        error_msg = html.Div([
            html.Span("❌ ", className="mr-2"),
            html.Span("Invalid password!", className="text-red-600 font-semibold")
        ])
        return False, "", error_msg, dash.no_update, dash.no_update

# Callback to enable/disable buttons based on admin authentication
@app.callback(
    [Output('add-website-button', 'disabled'),
     Output('update-button', 'disabled')],
    Input('admin-authenticated', 'data'),
    prevent_initial_call=False
)
def toggle_admin_buttons(is_authenticated):
    if is_authenticated:
        return False, False
    else:
        return True, True

# Callback to update single companies list
@app.callback(
    [Output('single-companies-list-container', 'children'),
     Output('single-companies-count', 'children')],
    Input('companies-store', 'data'),
    prevent_initial_call=False
)
def update_single_companies_list(companies_data):
    single_companies = {company: domains for company, domains in companies_data.items() if not domains}
    
    if not single_companies:
        companies_list = html.Div([
            html.P("No single companies added yet. Add your first single company using the form on the right.", 
                   className="text-gray-500 text-center p-4")
        ])
        count_text = "Total: 0 single companies"
        return companies_list, count_text
    
    company_items = []
    for i, (company_name, domains) in enumerate(single_companies.items()):
        company_item = html.Div([
            html.Div([
                html.Span(f"{i+1}.", className="font-semibold text-gray-600 mr-2"),
                html.Span(company_name, className="text-gray-800 flex-1"),
                html.Span("Single Company", className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded ml-2")
            ], className="flex items-center"),
            html.Div([
                html.Button(
                    "✎",
                    id={'type': 'edit-single-company-button', 'index': list(companies_data.keys()).index(company_name)},
                    n_clicks=0,
                    title="Edit company",
                    className="text-gray-600 hover:text-blue-600 hover:bg-gray-100 text-sm mr-1 px-2 py-1 border border-gray-300 rounded transition-colors duration-200"
                ),
                html.Button(
                    "🗑",
                    id={'type': 'delete-single-company-button', 'index': list(companies_data.keys()).index(company_name)},
                    n_clicks=0,
                    title="Delete company",
                    className="text-gray-600 hover:text-red-600 hover:bg-gray-100 text-sm px-2 py-1 border border-gray-300 rounded transition-colors duration-200"
                )
            ], className="flex space-x-1")
        ], className="flex items-center justify-between p-3 border-b border-gray-200 hover:bg-white rounded transition-colors duration-200")
        
        company_items.append(company_item)
    
    companies_list = html.Div(company_items)
    count_text = f"Total: {len(single_companies)} single companies"
    
    return companies_list, count_text

# Callback to update parent companies list
@app.callback(
    [Output('parent-companies-list-container', 'children'),
     Output('parent-companies-count', 'children')],
    Input('companies-store', 'data'),
    prevent_initial_call=False
)
def update_parent_companies_list(companies_data):
    parent_companies = {company: domains for company, domains in companies_data.items() if domains}
    
    if not parent_companies:
        companies_list = html.Div([
            html.P("No parent companies added yet. Add your first parent company using the form in the middle.", 
                   className="text-gray-500 text-center p-4")
        ])
        count_text = "Total: 0 parent companies"
        return companies_list, count_text
    
    company_items = []
    for i, (company_name, domains) in enumerate(parent_companies.items()):
        domain_count = len(domains)
        domain_badge = html.Span(
            f"{domain_count} subsidiary{'s' if domain_count != 1 else ''}",
            className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded ml-2"
        )
        
        company_item = html.Div([
            html.Div([
                html.Span(f"{i+1}.", className="font-semibold text-gray-600 mr-2"),
                html.Span(company_name, className="text-gray-800 flex-1"),
                domain_badge
            ], className="flex items-center"),
            html.Div([
                html.Button(
                    "✎",
                    id={'type': 'edit-parent-company-button', 'index': list(companies_data.keys()).index(company_name)},
                    n_clicks=0,
                    title="Edit company",
                    className="text-gray-600 hover:text-blue-600 hover:bg-gray-100 text-sm mr-1 px-2 py-1 border border-gray-300 rounded transition-colors duration-200"
                ),
                html.Button(
                    "🔗",
                    id={'type': 'manage-subsidiary-domains-button', 'index': list(companies_data.keys()).index(company_name)},
                    n_clicks=0,
                    title="Manage subsidiary domains",
                    className="text-gray-600 hover:text-green-600 hover:bg-gray-100 text-sm mr-1 px-2 py-1 border border-gray-300 rounded transition-colors duration-200"
                ),
                html.Button(
                    "🗑",
                    id={'type': 'delete-parent-company-button', 'index': list(companies_data.keys()).index(company_name)},
                    n_clicks=0,
                    title="Delete company",
                    className="text-gray-600 hover:text-red-600 hover:bg-gray-100 text-sm px-2 py-1 border border-gray-300 rounded transition-colors duration-200"
                )
            ], className="flex space-x-1")
        ], className="flex items-center justify-between p-3 border-b border-gray-200 hover:bg-white rounded transition-colors duration-200")
        
        company_items.append(company_item)
    
    companies_list = html.Div(company_items)
    count_text = f"Total: {len(parent_companies)} parent companies"
    
    return companies_list, count_text

# Callback to handle parent company selection for subsidiary domains management
@app.callback(
    [Output('selected-company', 'data'),
     Output('selected-parent-company-display', 'children'),
     Output('subsidiary-domains-list-container', 'children')],
    [Input({'type': 'manage-subsidiary-domains-button', 'index': dash.ALL}, 'n_clicks'),
     Input('companies-store', 'data')],
    [State('companies-store', 'data'),
     State('company-type-tabs', 'value')],
    prevent_initial_call=True
)
def handle_parent_company_selection(manage_clicks, companies_data, current_companies, current_tab):
    if current_tab != 'parent-company':
        return dash.no_update, dash.no_update, dash.no_update
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id.startswith('{"index":') and 'manage-subsidiary-domains-button' in button_id:
        try:
            button_data = json.loads(button_id)
            company_index = button_data['index']
            company_keys = list(current_companies.keys())
            if 0 <= company_index < len(company_keys):
                selected_company = company_keys[company_index]
                domains = current_companies.get(selected_company, [])
                
                company_display = html.Div([
                    html.Strong(selected_company),
                    html.Span(f" ({len(domains)} subsidiaries)", className="text-gray-500 ml-2")
                ])
                
                if domains:
                    domains_list = html.Div([
                        html.Div([
                            html.Span(domain, className="flex-1 text-sm"),
                            html.Button(
                                "🗑",
                                id={'type': 'delete-subsidiary-domain-button', 'company': selected_company, 'domain': domain},
                                n_clicks=0,
                                title="Delete subsidiary domain",
                                className="text-red-500 hover:text-red-700 text-xs px-1"
                            )
                        ], className="flex items-center justify-between p-2 border-b border-gray-200 hover:bg-white")
                        for domain in domains
                    ])
                else:
                    domains_list = html.Div([
                        html.P("No subsidiary domains yet. Add domains using the form above.", 
                               className="text-gray-500 text-center p-2 text-sm")
                    ])
                
                return selected_company, company_display, domains_list
        except:
            pass
    
    return dash.no_update, dash.no_update, dash.no_update

# Callback to add subsidiary domains - with confirmation
@app.callback(
    [Output('pending-changes', 'data', allow_duplicate=True),
     Output('confirmation-message', 'children', allow_duplicate=True),
     Output('confirmation-state', 'data', allow_duplicate=True),
     Output('subsidiary-domain-input', 'value'),
     Output('dialog-status-message', 'children', allow_duplicate=True)],
    Input('add-subsidiary-domain-button', 'n_clicks'),
    [State('subsidiary-domain-input', 'value'),
     State('selected-company', 'data'),
     State('companies-store', 'data')],
    prevent_initial_call=True
)
def add_subsidiary_domain(add_clicks, domain_value, selected_company, companies_data):
    if not add_clicks or not domain_value or not selected_company:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    cleaned_domain = clean_domain(domain_value)
    if not cleaned_domain:
        error_status = html.Div([
            html.Span("⚠ ", className="mr-2"),
            html.Span("Invalid domain URL format", className="text-red-600")
        ])
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, error_status
    
    for company, domains in companies_data.items():
        if cleaned_domain in domains:
            error_status = html.Div([
                html.Span("⚠ ", className="mr-2"),
                html.Span(f"Domain {cleaned_domain} already exists for {company}", className="text-yellow-600")
            ])
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, error_status
    
    updated_companies = companies_data.copy()
    if selected_company in updated_companies:
        if cleaned_domain not in updated_companies[selected_company]:
            updated_companies[selected_company].append(cleaned_domain)
            
            pending_changes = {
                'action': 'add_subsidiary',
                'data': updated_companies,
                'company': selected_company,
                'domain': cleaned_domain
            }
            confirmation_msg = html.Div([
                html.P(f"Add subsidiary domain '{cleaned_domain}' to company '{selected_company}'?", className="font-semibold mb-2"),
                html.P("This will update the domains.json file.", className="text-sm text-gray-600")
            ])
            return pending_changes, confirmation_msg, True, "", ""
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Callback to delete subsidiary domains - with confirmation
@app.callback(
    [Output('pending-changes', 'data', allow_duplicate=True),
     Output('confirmation-message', 'children', allow_duplicate=True),
     Output('confirmation-state', 'data', allow_duplicate=True),
     Output('dialog-status-message', 'children', allow_duplicate=True)],
    Input({'type': 'delete-subsidiary-domain-button', 'company': dash.ALL, 'domain': dash.ALL}, 'n_clicks'),
    [State('companies-store', 'data')],
    prevent_initial_call=True
)
def delete_subsidiary_domain(delete_clicks, companies_data):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id.startswith('{"domain":') and 'delete-subsidiary-domain-button' in button_id:
        try:
            button_data = json.loads(button_id)
            company_name = button_data['company']
            domain_name = button_data['domain']
            
            if company_name in companies_data and domain_name in companies_data[company_name]:
                updated_companies = companies_data.copy()
                updated_companies[company_name].remove(domain_name)
                
                pending_changes = {
                    'action': 'delete_subsidiary',
                    'data': updated_companies,
                    'company': company_name,
                    'domain': domain_name
                }
                confirmation_msg = html.Div([
                    html.P(f"Delete subsidiary domain '{domain_name}' from company '{company_name}'?", className="font-semibold mb-2"),
                    html.P("This will update the domains.json file.", className="text-sm text-gray-600")
                ])
                return pending_changes, confirmation_msg, True, ""
        except:
            pass
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Callback for single company operations - with confirmation
@app.callback(
    [Output('pending-changes', 'data', allow_duplicate=True),
     Output('confirmation-message', 'children', allow_duplicate=True),
     Output('confirmation-state', 'data', allow_duplicate=True),
     Output('dialog-status-message', 'children', allow_duplicate=True)],
    [Input('submit-single-company-button', 'n_clicks'),
     Input('clear-single-form-button', 'n_clicks'),
     Input({'type': 'edit-single-company-button', 'index': dash.ALL}, 'n_clicks'),
     Input({'type': 'delete-single-company-button', 'index': dash.ALL}, 'n_clicks')],
    [State('single-company-input', 'value'),
     State('edit-single-company-index', 'value'),
     State('companies-store', 'data'),
     State('company-type-tabs', 'value')],
    prevent_initial_call=True
)
def handle_single_company_operations(submit_clicks, clear_clicks, edit_clicks, delete_clicks, 
                                   single_company_value, edit_index, current_companies, current_tab):
    if current_tab != 'single-company':
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'submit-single-company-button':
        if not single_company_value:
            error_status = html.Div([
                html.Span("⚠ ", className="mr-2"),
                html.Span("Please enter a company domain", className="text-red-600")
            ])
            return dash.no_update, dash.no_update, dash.no_update, error_status
        
        cleaned_company = clean_domain(single_company_value) or single_company_value.strip()
        
        if not cleaned_company:
            error_status = html.Div([
                html.Span("⚠ ", className="mr-2"),
                html.Span("Invalid company domain", className="text-red-600")
            ])
            return dash.no_update, dash.no_update, dash.no_update, error_status
        
        if edit_index == -1:
            if cleaned_company in current_companies:
                duplicate_status = html.Div([
                    html.Span("⚠ ", className="mr-2"),
                    html.Span("Company already exists", className="text-yellow-600")
                ])
                return dash.no_update, dash.no_update, dash.no_update, duplicate_status
        else:
            company_keys = list(current_companies.keys())
            if 0 <= edit_index < len(company_keys):
                old_company = company_keys[edit_index]
                if cleaned_company in current_companies and cleaned_company != old_company:
                    duplicate_status = html.Div([
                        html.Span("⚠ ", className="mr-2"),
                        html.Span("Company already exists", className="text-yellow-600")
                    ])
                    return dash.no_update, dash.no_update, dash.no_update, duplicate_status
        
        if edit_index == -1:
            updated_companies = current_companies.copy()
            updated_companies[cleaned_company] = []
            action_text = f"Add single company '{cleaned_company}'?"
        else:
            company_keys = list(current_companies.keys())
            if 0 <= edit_index < len(company_keys):
                old_company = company_keys[edit_index]
                updated_companies = current_companies.copy()
                updated_companies.pop(old_company)
                updated_companies[cleaned_company] = []
                action_text = f"Update company '{old_company}' to '{cleaned_company}'?"
            else:
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        pending_changes = {
            'action': 'single_company_submit',
            'data': updated_companies,
            'edit_index': edit_index
        }
        confirmation_msg = html.Div([
            html.P(action_text, className="font-semibold mb-2"),
            html.P("This will update the domains.json file.", className="text-sm text-gray-600")
        ])
        return pending_changes, confirmation_msg, True, ""
    
    elif button_id == 'clear-single-form-button':
        return dash.no_update, dash.no_update, dash.no_update, ""
    
    elif button_id.startswith('{"index":') and 'edit-single-company-button' in button_id:
        return dash.no_update, dash.no_update, dash.no_update, ""
    
    elif button_id.startswith('{"index":') and 'delete-single-company-button' in button_id:
        try:
            button_data = json.loads(button_id)
            company_index = button_data['index']
            company_keys = list(current_companies.keys())
            if 0 <= company_index < len(company_keys):
                deleted_company = company_keys[company_index]
                updated_companies = current_companies.copy()
                del updated_companies[deleted_company]
                
                pending_changes = {
                    'action': 'delete_single_company',
                    'data': updated_companies,
                    'company': deleted_company
                }
                confirmation_msg = html.Div([
                    html.P(f"Delete single company '{deleted_company}'?", className="font-semibold mb-2"),
                    html.P("This will update the domains.json file.", className="text-sm text-gray-600")
                ])
                return pending_changes, confirmation_msg, True, ""
        except:
            pass
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Callback for parent company operations - with confirmation
@app.callback(
    [Output('pending-changes', 'data', allow_duplicate=True),
     Output('confirmation-message', 'children', allow_duplicate=True),
     Output('confirmation-state', 'data', allow_duplicate=True),
     Output('dialog-status-message', 'children', allow_duplicate=True)],
    [Input('submit-parent-company-button', 'n_clicks'),
     Input('clear-parent-form-button', 'n_clicks'),
     Input({'type': 'edit-parent-company-button', 'index': dash.ALL}, 'n_clicks'),
     Input({'type': 'delete-parent-company-button', 'index': dash.ALL}, 'n_clicks')],
    [State('parent-company-input', 'value'),
     State('edit-parent-company-index', 'value'),
     State('companies-store', 'data'),
     State('company-type-tabs', 'value')],
    prevent_initial_call=True
)
def handle_parent_company_operations(submit_clicks, clear_clicks, edit_clicks, delete_clicks, 
                                   parent_company_value, edit_index, current_companies, current_tab):
    if current_tab != 'parent-company':
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'submit-parent-company-button':
        if not parent_company_value:
            error_status = html.Div([
                html.Span("⚠ ", className="mr-2"),
                html.Span("Please enter a parent company name", className="text-red-600")
            ])
            return dash.no_update, dash.no_update, dash.no_update, error_status
        
        cleaned_company = parent_company_value.strip()
        
        if not cleaned_company:
            error_status = html.Div([
                html.Span("⚠ ", className="mr-2"),
                html.Span("Invalid parent company name", className="text-red-600")
            ])
            return dash.no_update, dash.no_update, dash.no_update, error_status
        
        if edit_index == -1:
            if cleaned_company in current_companies:
                duplicate_status = html.Div([
                    html.Span("⚠ ", className="mr-2"),
                    html.Span("Company already exists", className="text-yellow-600")
                ])
                return dash.no_update, dash.no_update, dash.no_update, duplicate_status
        else:
            company_keys = list(current_companies.keys())
            if 0 <= edit_index < len(company_keys):
                old_company = company_keys[edit_index]
                if cleaned_company in current_companies and cleaned_company != old_company:
                    duplicate_status = html.Div([
                        html.Span("⚠ ", className="mr-2"),
                        html.Span("Company already exists", className="text-yellow-600")
                    ])
                    return dash.no_update, dash.no_update, dash.no_update, duplicate_status
        
        if edit_index == -1:
            updated_companies = current_companies.copy()
            updated_companies[cleaned_company] = []
            action_text = f"Add parent company '{cleaned_company}'?"
        else:
            company_keys = list(current_companies.keys())
            if 0 <= edit_index < len(company_keys):
                old_company = company_keys[edit_index]
                updated_companies = current_companies.copy()
                domains = updated_companies.pop(old_company)
                updated_companies[cleaned_company] = domains
                action_text = f"Update company '{old_company}' to '{cleaned_company}'?"
            else:
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        pending_changes = {
            'action': 'parent_company_submit',
            'data': updated_companies,
            'edit_index': edit_index
        }
        confirmation_msg = html.Div([
            html.P(action_text, className="font-semibold mb-2"),
            html.P("This will update the domains.json file.", className="text-sm text-gray-600")
        ])
        return pending_changes, confirmation_msg, True, ""
    
    elif button_id == 'clear-parent-form-button':
        return dash.no_update, dash.no_update, dash.no_update, ""
    
    elif button_id.startswith('{"index":') and 'edit-parent-company-button' in button_id:
        return dash.no_update, dash.no_update, dash.no_update, ""
    
    elif button_id.startswith('{"index":') and 'delete-parent-company-button' in button_id:
        try:
            button_data = json.loads(button_id)
            company_index = button_data['index']
            company_keys = list(current_companies.keys())
            if 0 <= company_index < len(company_keys):
                deleted_company = company_keys[company_index]
                updated_companies = current_companies.copy()
                del updated_companies[deleted_company]
                
                pending_changes = {
                    'action': 'delete_parent_company',
                    'data': updated_companies,
                    'company': deleted_company
                }
                confirmation_msg = html.Div([
                    html.P(f"Delete parent company '{deleted_company}'?", className="font-semibold mb-2"),
                    html.P("This will update the domains.json file.", className="text-sm text-gray-600")
                ])
                return pending_changes, confirmation_msg, True, ""
        except:
            pass
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Callback to update single company form when editing
@app.callback(
    [Output('single-company-input', 'value', allow_duplicate=True),
     Output('edit-single-company-index', 'value', allow_duplicate=True),
     Output('submit-single-company-button', 'children', allow_duplicate=True)],
    Input({'type': 'edit-single-company-button', 'index': dash.ALL}, 'n_clicks'),
    [State('companies-store', 'data'),
     State('company-type-tabs', 'value')],
    prevent_initial_call=True
)
def update_single_company_form(edit_clicks, companies_data, current_tab):
    if current_tab != 'single-company':
        return dash.no_update, dash.no_update, dash.no_update
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id.startswith('{"index":') and 'edit-single-company-button' in button_id:
        try:
            button_data = json.loads(button_id)
            company_index = button_data['index']
            company_keys = list(companies_data.keys())
            if 0 <= company_index < len(company_keys):
                company_name = company_keys[company_index]
                return company_name, company_index, "Update Single Company"
        except:
            pass
    
    return dash.no_update, dash.no_update, dash.no_update

# Callback to update parent company form when editing
@app.callback(
    [Output('parent-company-input', 'value', allow_duplicate=True),
     Output('edit-parent-company-index', 'value', allow_duplicate=True),
     Output('submit-parent-company-button', 'children', allow_duplicate=True)],
    Input({'type': 'edit-parent-company-button', 'index': dash.ALL}, 'n_clicks'),
    [State('companies-store', 'data'),
     State('company-type-tabs', 'value')],
    prevent_initial_call=True
)
def update_parent_company_form(edit_clicks, companies_data, current_tab):
    if current_tab != 'parent-company':
        return dash.no_update, dash.no_update, dash.no_update
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id.startswith('{"index":') and 'edit-parent-company-button' in button_id:
        try:
            button_data = json.loads(button_id)
            company_index = button_data['index']
            company_keys = list(companies_data.keys())
            if 0 <= company_index < len(company_keys):
                company_name = company_keys[company_index]
                return company_name, company_index, "Update Parent Company"
        except:
            pass
    
    return dash.no_update, dash.no_update, dash.no_update

# Callback to clear single company form
@app.callback(
    [Output('single-company-input', 'value'),
     Output('edit-single-company-index', 'value'),
     Output('submit-single-company-button', 'children')],
    Input('clear-single-form-button', 'n_clicks'),
    State('company-type-tabs', 'value'),
    prevent_initial_call=True
)
def clear_single_company_form(clear_clicks, current_tab):
    if current_tab != 'single-company':
        return dash.no_update, dash.no_update, dash.no_update
    
    return "", -1, "Add Single Company"

# Callback to clear parent company form
@app.callback(
    [Output('parent-company-input', 'value'),
     Output('edit-parent-company-index', 'value'),
     Output('submit-parent-company-button', 'children')],
    Input('clear-parent-form-button', 'n_clicks'),
    State('company-type-tabs', 'value'),
    prevent_initial_call=True
)
def clear_parent_company_form(clear_clicks, current_tab):
    if current_tab != 'parent-company':
        return dash.no_update, dash.no_update, dash.no_update
    
    return "", -1, "Add Parent Company"

# Callback to validate single company input
@app.callback(
    Output('single-company-validation-message', 'children'),
    Input('single-company-input', 'value'),
    State('company-type-tabs', 'value'),
    prevent_initial_call=True
)
def validate_single_company_input(company_value, current_tab):
    if current_tab != 'single-company':
        return ""
    
    if not company_value:
        return ""
    
    cleaned = clean_domain(company_value) or company_value.strip()
    if cleaned:
        return html.Div([
            html.Span("✓ ", className="text-green-600"),
            html.Span(f"Company: {cleaned}", className="text-green-600 text-sm")
        ])
    else:
        return html.Div([
            html.Span("⚠ ", className="text-red-600"),
            html.Span("Please enter a valid company domain", className="text-red-600 text-sm")
        ])

# Callback to validate parent company input
@app.callback(
    Output('parent-company-validation-message', 'children'),
    Input('parent-company-input', 'value'),
    State('company-type-tabs', 'value'),
    prevent_initial_call=True
)
def validate_parent_company_input(company_value, current_tab):
    if current_tab != 'parent-company':
        return ""
    
    if not company_value:
        return ""
    
    cleaned = company_value.strip()
    if cleaned:
        return html.Div([
            html.Span("✓ ", className="text-green-600"),
            html.Span(f"Parent Company: {cleaned}", className="text-green-600 text-sm")
        ])
    else:
        return html.Div([
            html.Span("⚠ ", className="text-red-600"),
            html.Span("Please enter a valid parent company name", className="text-red-600 text-sm")
        ])

# Clientside callback for confirmation dialog visibility
clientside_callback(
    """
    function(confirmation_open) {
        const confirmationOverlay = document.getElementById('confirmation-dialog-overlay');
        
        if (confirmation_open) {
            if (confirmationOverlay) {
                confirmationOverlay.classList.remove('hidden');
            }
            return 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50';
        } else {
            if (confirmationOverlay) {
                confirmationOverlay.classList.add('hidden');
            }
            return 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 hidden';
        }
    }
    """,
    Output('confirmation-dialog-overlay', 'className'),
    Input('confirmation-state', 'data'),
    prevent_initial_call=True
)

# Callback to handle confirmation button (actually save the changes)
@app.callback(
    [Output('companies-store', 'data', allow_duplicate=True),
     Output('confirmation-state', 'data', allow_duplicate=True),
     Output('dialog-status-message', 'children', allow_duplicate=True),
     Output('pending-changes', 'data', allow_duplicate=True)],
    Input('confirm-confirmation-button', 'n_clicks'),
    [State('pending-changes', 'data')],
    prevent_initial_call=True
)
def confirm_changes(n_clicks, pending_changes):
    if not n_clicks or not pending_changes:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    updated_companies = pending_changes.get('data')
    action = pending_changes.get('action')
    
    if not updated_companies:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    if save_domains(updated_companies):
        if action == 'add_subsidiary':
            company = pending_changes.get('company', '')
            domain = pending_changes.get('domain', '')
            message = f"Added subsidiary domain {domain} to {company}"
        elif action == 'delete_subsidiary':
            company = pending_changes.get('company', '')
            domain = pending_changes.get('domain', '')
            message = f"Deleted subsidiary domain {domain} from {company}"
        elif action == 'single_company_submit':
            message = "Single company saved successfully"
        elif action == 'parent_company_submit':
            message = "Parent company saved successfully"
        elif action == 'delete_single_company':
            company = pending_changes.get('company', '')
            message = f"Deleted single company {company}"
        elif action == 'delete_parent_company':
            company = pending_changes.get('company', '')
            message = f"Deleted parent company {company}"
        else:
            message = "Changes saved successfully"
        
        success_status = html.Div([
            html.Span("✅", className="mr-2"),
            html.Span(message, className="text-green-600")
        ])
        return updated_companies, False, success_status, None
    else:
        error_status = html.Div([
            html.Span("❌", className="mr-2"),
            html.Span("Failed to save changes to domains.json", className="text-red-600")
        ])
        return dash.no_update, False, error_status, None

# Callback to handle cancel confirmation button
@app.callback(
    [Output('confirmation-state', 'data', allow_duplicate=True),
     Output('pending-changes', 'data', allow_duplicate=True),
     Output('dialog-status-message', 'children', allow_duplicate=True)],
    Input('cancel-confirmation-button', 'n_clicks'),
    prevent_initial_call=True
)
def cancel_confirmation(n_clicks):
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update
    
    cancel_status = html.Div([
        html.Span("ℹ️", className="mr-2"),
        html.Span("Changes cancelled", className="text-blue-600")
    ])
    return False, None, cancel_status

# Callback for dialog opening/closing
@app.callback(
    Output('dialog-state', 'data'),
    [Input('add-website-button', 'n_clicks'),
     Input('close-dialog-button', 'n_clicks'),
     Input('cancel-dialog-button', 'n_clicks')],
    prevent_initial_call=True
)
def handle_dialog_open_close(add_clicks, close_clicks, cancel_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'add-website-button':
        return True
    elif button_id in ['close-dialog-button', 'cancel-dialog-button']:
        return False
    
    return dash.no_update

# Clientside callback for dialog visibility
clientside_callback(
    """
    function(dialog_open) {
        const dialogOverlay = document.getElementById('website-dialog-overlay');
        
        if (dialog_open) {
            if (dialogOverlay) {
                dialogOverlay.classList.remove('hidden');
            }
            return 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50';
        } else {
            if (dialogOverlay) {
                dialogOverlay.classList.add('hidden');
            }
            return 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 hidden';
        }
    }
    """,
    Output('website-dialog-overlay', 'className'),
    Input('dialog-state', 'data'),
    prevent_initial_call=True
)

# Clientside callback for loading overlay
clientside_callback(
    """
    function(loading) {
        const loadingOverlay = document.getElementById('loading-overlay');
        const updateButton = document.getElementById('update-button');
        const mainContainer = document.getElementById('main-container');
        
        if (loading) {
            if (document.body) {
                document.body.style.cursor = 'wait';
            }
            if (mainContainer) {
                mainContainer.style.cursor = 'wait';
            }
            
            if (loadingOverlay) {
                loadingOverlay.classList.remove('hidden');
            }
            
            if (updateButton) {
                updateButton.disabled = true;
                updateButton.textContent = 'Updating...';
            }
            
            return 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50';
        } else {
            if (document.body) {
                document.body.style.cursor = 'default';
            }
            if (mainContainer) {
                mainContainer.style.cursor = 'default';
            }
            
            if (loadingOverlay) {
                loadingOverlay.classList.add('hidden');
            }
            
            if (updateButton) {
                updateButton.disabled = false;
                updateButton.textContent = 'Update Data';
            }
            
            return 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 hidden';
        }
    }
    """,
    Output('loading-overlay', 'className'),
    Input('loading-state', 'data'),
    prevent_initial_call=True
)

# Callback to start loading state
@app.callback(
    [Output('loading-state', 'data'),
     Output('update-status', 'children')],
    Input('update-button', 'n_clicks'),
    State('loading-state', 'data'),
    prevent_initial_call=True
)
def start_loading(n_clicks, loading):
    if n_clicks > 0 and not loading:
        loading_status = html.Div([
            html.Span(className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500 inline-block mr-2"),
            html.Span("Updating...", className="text-blue-600")
        ])
        return True, loading_status
    return dash.no_update, dash.no_update

# Callback to update data
@app.callback(
    [Output('data-store', 'data'),
     Output('loading-state', 'data', allow_duplicate=True),
     Output('update-status', 'children', allow_duplicate=True)],
    Input('loading-state', 'data'),
    prevent_initial_call=True
)
def update_data(loading):
    if loading:
        time.sleep(2)
        
        if np.random.random() > 0.2:
            new_df = pd.DataFrame({
                'Category': ['A', 'B', 'C', 'D', 'E'] * 20,
                'Value': np.random.randn(100),
                'Date': pd.date_range('2023-01-01', periods=100, freq='D')
            })
            
            success_status = html.Div([
                html.Span("✅", className="mr-2"),
                html.Span("Data updated successfully!", className="text-green-600")
            ])
            
            return new_df.to_dict('records'), False, success_status
        else:
            error_status = html.Div([
                html.Span("❌", className="mr-2"),
                html.Span("Failed to update data. Please try again.", className="text-red-600")
            ])
            
            return dash.no_update, False, error_status
    
    return dash.no_update, dash.no_update, dash.no_update

# Callback to update tab content
@callback(Output('tabs-content', 'children'),
          [Input('tabs', 'value'),
           Input('data-store', 'data'),
           Input('companies-store', 'data')])
def render_content(tab, data, companies_data):
    df = pd.DataFrame(data)
    
    if 'Date' in df.columns and df['Date'].dtype == 'object':
        try:
            df['Date'] = pd.to_datetime(df['Date'])
        except:
            pass
    
    if tab == 'tab-4':
        total_domains = sum(len(domains) for domains in companies_data.values())
        single_companies = {company: domains for company, domains in companies_data.items() if not domains}
        parent_companies = {company: domains for company, domains in companies_data.items() if domains}
        
        return html.Div([
            html.H2("Companies & Owned Domains", className="text-2xl font-bold text-gray-800 mb-6"),
            
            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Total Companies", className="text-lg font-semibold text-gray-700"),
                        html.P(f"{len(companies_data)}", className="text-3xl font-bold text-blue-600")
                    ], className="p-4")
                ], className="bg-white rounded-lg shadow-sm border-l-4 border-blue-500"),
                
                html.Div([
                    html.Div([
                        html.H3("Single Companies", className="text-lg font-semibold text-gray-700"),
                        html.P(f"{len(single_companies)}", className="text-3xl font-bold text-green-600")
                    ], className="p-4")
                ], className="bg-white rounded-lg shadow-sm border-l-4 border-green-500"),
                
                html.Div([
                    html.Div([
                        html.H3("Parent Companies", className="text-lg font-semibold text-gray-700"),
                        html.P(f"{len(parent_companies)}", className="text-3xl font-bold text-purple-600")
                    ], className="p-4")
                ], className="bg-white rounded-lg shadow-sm border-l-4 border-purple-500"),
                
                html.Div([
                    html.Div([
                        html.H3("Total Domains", className="text-lg font-semibold text-gray-700"),
                        html.P(f"{total_domains}", className="text-3xl font-bold text-orange-600")
                    ], className="p-4")
                ], className="bg-white rounded-lg shadow-sm border-l-4 border-orange-500"),
            ], className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6"),
            
            html.Div([
                html.Div([
                    html.H3("Parent Companies & Subsidiary Domains", className="text-xl font-semibold text-gray-800 mb-4"),
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Span(f"{i+1}.", className="font-semibold text-gray-600 mr-2"),
                                html.Span(company_name, className="text-gray-800 font-medium"),
                                html.Span(f"({len(domains)} subsidiaries)", className="text-sm text-gray-500 ml-2")
                            ], className="mb-2"),
                            html.Div([
                                html.Span("Subsidiary Domains: ", className="text-sm text-gray-600 font-medium"),
                                html.Span(", ".join(domains) if domains else "No subsidiary domains", className="text-sm text-gray-700")
                            ], className="ml-4")
                        ], className="p-3 border-b border-gray-200 hover:bg-gray-50")
                        for i, (company_name, domains) in enumerate(parent_companies.items())
                    ], className="bg-white rounded-lg shadow-sm max-h-96 overflow-y-auto") if parent_companies else html.Div([
                        html.P("No parent companies added yet.", className="text-gray-500 text-center p-8")
                    ], className="bg-white rounded-lg shadow-sm"),
                ], className="mb-6"),
                
                html.Div([
                    html.H3("Single Companies", className="text-xl font-semibold text-gray-800 mb-4"),
                    html.Div([
                        html.Div([
                            html.Span(f"{i+1}.", className="font-semibold text-gray-600 mr-2"),
                            html.Span(company_name, className="text-gray-800 font-medium"),
                            html.Span("Single Company", className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded ml-2")
                        ], className="p-3 border-b border-gray-200 hover:bg-gray-50")
                        for i, (company_name, domains) in enumerate(single_companies.items())
                    ], className="bg-white rounded-lg shadow-sm max-h-96 overflow-y-auto") if single_companies else html.Div([
                        html.P("No single companies added yet.", className="text-gray-500 text-center p-8")
                    ], className="bg-white rounded-lg shadow-sm"),
                ]),
                
                html.Div([
                    html.H4("Instructions", className="font-semibold text-gray-800 mb-2"),
                    html.Ul([
                        html.Li("Click 'Manage Companies & Domains' to add, edit, or delete companies", className="text-gray-600"),
                        html.Li("Use the 'Single Company' tab for companies with no subsidiaries (e.g., adobe.com)", className="text-gray-600"),
                        html.Li("Use the 'Parent Company' tab for holding companies with subsidiaries (e.g., MSFT → microsoft.com, github.com)", className="text-gray-600"),
                        html.Li("Domains are automatically cleaned (removes http/https, www)", className="text-gray-600"),
                        html.Li("Duplicate domains across different companies are not allowed", className="text-gray-600"),
                        html.Li("All changes require confirmation before saving to domains.json", className="text-gray-600"),
                        html.Li("The domains.json file is saved in the current directory", className="text-gray-600")
                    ], className="list-disc pl-6 space-y-1")
                ], className="bg-gray-50 p-4 rounded-lg mt-4")
            ])
        ])
    
    elif tab == 'tab-1':
        if 'Date' in df.columns and len(df) > 0:
            try:
                date_min = df['Date'].min()
                date_max = df['Date'].max()
                date_range = f"{safe_date_format(date_min)} to {safe_date_format(date_max)}"
            except:
                date_range = "Date range not available"
        else:
            date_range = "Date range not available"
        
        total_domains = sum(len(domains) for domains in companies_data.values())
        single_companies = {company: domains for company, domains in companies_data.items() if not domains}
        parent_companies = {company: domains for company, domains in companies_data.items() if domains}
        
        return html.Div([
            html.H2("Overview Dashboard", className="text-2xl font-bold text-gray-800 mb-6"),
            
            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Total Records", className="text-lg font-semibold text-gray-700"),
                        html.P(f"{len(df):,}", className="text-3xl font-bold text-blue-600")
                    ], className="p-4")
                ], className="bg-white rounded-lg shadow-sm border-l-4 border-blue-500"),
                
                html.Div([
                    html.Div([
                        html.H3("Average Value", className="text-lg font-semibold text-gray-700"),
                        html.P(f"{df['Value'].mean():.2f}", className="text-3xl font-bold text-green-600")
                    ], className="p-4")
                ], className="bg-white rounded-lg shadow-sm border-l-4 border-green-500"),
                
                html.Div([
                    html.Div([
                        html.H3("Categories", className="text-lg font-semibold text-gray-700"),
                        html.P(f"{df['Category'].nunique()}", className="text-3xl font-bold text-purple-600")
                    ], className="p-4")
                ], className="bg-white rounded-lg shadow-sm border-l-4 border-purple-500"),
                
                html.Div([
                    html.Div([
                        html.H3("Single Companies", className="text-lg font-semibold text-gray-700"),
                        html.P(f"{len(single_companies)}", className="text-3xl font-bold text-orange-600")
                    ], className="p-4")
                ], className="bg-white rounded-lg shadow-sm border-l-4 border-orange-500"),
                
                html.Div([
                    html.Div([
                        html.H3("Parent Companies", className="text-lg font-semibold text-gray-700"),
                        html.P(f"{len(parent_companies)}", className="text-3xl font-bold text-indigo-600")
                    ], className="p-4")
                ], className="bg-white rounded-lg shadow-sm border-l-4 border-indigo-500"),
            ], className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6"),
            
            html.Div([
                html.H3("Data Summary", className="text-xl font-semibold text-gray-800 mb-4"),
                html.P(f"Dataset contains {len(df)} records across {df['Category'].nunique()} categories."),
                html.P(f"Date range: {date_range}"),
                html.P(f"Currently managing {len(companies_data)} companies ({len(single_companies)} single, {len(parent_companies)} parent) with {total_domains} total domains."),
            ], className="bg-gray-50 p-4 rounded-lg")
        ])
    
    elif tab == 'tab-2':
        return html.Div([
            html.H2("Data Visualization", className="text-2xl font-bold text-gray-800 mb-6"),
            
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='bar-chart',
                        figure=px.bar(df, x='Category', y='Value', title='Values by Category')
                        .update_layout(title_x=0.5, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    )
                ], className="bg-white p-4 rounded-lg shadow-sm"),
                
                html.Div([
                    dcc.Graph(
                        id='scatter-plot',
                        figure=px.scatter(df, x='Date', y='Value', color='Category', title='Value Trends Over Time')
                        .update_layout(title_x=0.5, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    )
                ], className="bg-white p-4 rounded-lg shadow-sm"),
            ], className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6"),
            
            html.Div([
                dcc.Graph(
                    id='histogram',
                    figure=px.histogram(df, x='Value', color='Category', title='Value Distribution by Category', barmode='overlay')
                    .update_layout(title_x=0.5, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                )
            ], className="bg-white p-4 rounded-lg shadow-sm")
        ])
    
    elif tab == 'tab-3':
        return html.Div([
            html.H2("Data Table", className="text-2xl font-bold text-gray-800 mb-6"),
            
            html.Div([
                html.Label("Show entries:", className="font-semibold text-gray-700 mr-2"),
                dcc.Dropdown(
                    id='rows-dropdown',
                    options=[{'label': str(i), 'value': i} for i in [10, 25, 50, 100]],
                    value=10,
                    className="w-20 inline-block"
                )
            ], className="mb-4"),
            
            html.Div([
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Index", className="px-4 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-200"),
                            html.Th("Category", className="px-4 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-200"),
                            html.Th("Value", className="px-4 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-200"),
                            html.Th("Date", className="px-4 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-200")
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td(i, className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 border-b border-gray-200"),
                            html.Td(row['Category'], className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 border-b border-gray-200"),
                            html.Td(f"{row['Value']:.2f}", className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 border-b border-gray-200"),
                            html.Td(safe_date_format(row['Date']), className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 border-b border-gray-200")
                        ], className="hover:bg-gray-50") for i, row in df.head(10).iterrows()
                    ])
                ], className="min-w-full divide-y divide-gray-200")
            ], className="bg-white rounded-lg shadow ring-1 ring-black ring-opacity-5 overflow-hidden"),
            
            html.Div([
                html.P(f"Showing 1 to 10 of {len(df)} entries", className="text-sm text-gray-600 mt-4")
            ])
        ])

# Add Tailwind CSS and custom styles
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
                        colors: {
                            primary: '#3B82F6',
                            secondary: '#6B7280',
                        }
                    }
                }
            }
        </script>
        <style>
            .z-50 {
                z-index: 50;
            }
            
            .transition-colors {
                transition-property: background-color, border-color, color, fill, stroke;
                transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
                transition-duration: 200ms;
            }
            
            @keyframes spin {
                from {
                    transform: rotate(0deg);
                }
                to {
                    transform: rotate(360deg);
                }
            }
            
            .animate-spin {
                animation: spin 1s linear infinite;
            }
            
            input:focus {
                outline: none;
                border-color: #3B82F6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            .dialog-content {
                max-height: 90vh;
                overflow-y: auto;
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
    app.run(debug=True, host='0.0.0.0', port=9050)