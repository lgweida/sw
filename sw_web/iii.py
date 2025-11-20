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
            # Try to convert string to datetime and then format
            return pd.to_datetime(date_obj).strftime(format_str)
        except:
            return str(date_obj)

def load_domains():
    """Load companies and their owned domains from domains.json file"""
    try:
        if os.path.exists('domains.json'):
            with open('domains.json', 'r') as f:
                data = json.load(f)
                # Handle different formats
                if isinstance(data, list):
                    # Convert old format to new format - treat as single companies
                    return {domain: [] for domain in data}
                elif isinstance(data, dict):
                    # Check if it's the old alias format or new company format
                    if all(isinstance(v, list) for v in data.values()):
                        # This is already the correct format
                        return data
                    else:
                        # Convert any other format
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
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc if parsed.netloc else parsed.hostname
        
        # Remove www. prefix
        if domain and domain.startswith('www.'):
            domain = domain[4:]
        
        return domain.lower()  # Normalize to lowercase
    except:
        return None

# Load initial domains data
domains_data = load_domains()

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout with Tailwind CSS
app.layout = html.Div([
    # Header with update button and add website button
    html.Div([
        html.Div([
            html.H1("Dashboard Analytics", className="text-3xl font-bold text-gray-800 mb-2"),
            html.P("Interactive data visualization with company & domain management", className="text-gray-600")
        ], className="flex-1"),
        
        # Buttons and status
        html.Div([
            html.Button(
                "Manage Companies & Domains", 
                id="add-website-button", 
                n_clicks=0,
                className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200 mr-3"
            ),
            html.Button(
                "Update Data", 
                id="update-button", 
                n_clicks=0,
                className="bg-blue-500 hover:bg-blue-700 disabled:bg-blue-300 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
            ),
            html.Div(id="update-status", className="ml-4 text-sm")
        ], className="flex items-center")
    ], className="bg-white p-6 shadow-sm mb-6 flex justify-between items-center"),
    
    # Loading overlay (initially hidden)
    html.Div(
        id="loading-overlay",
        className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 hidden",
        children=[
            html.Div(
                className="bg-white p-6 rounded-lg shadow-lg text-center",
                children=[
                    html.Div(
                        className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"
                    ),
                    html.Div("Updating data...", className="text-lg font-semibold mb-2"),
                    html.Div("Please wait while we fetch the latest data", className="text-gray-600")
                ]
            )
        ]
    ),
    
    # Company Dialog Modal (initially hidden)
    html.Div(
        id="website-dialog-overlay",
        className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 hidden",
        children=[
            html.Div(
                className="bg-white p-6 rounded-lg shadow-lg w-full max-w-5xl mx-4 max-h-[90vh] overflow-hidden flex flex-col",
                children=[
                    # Header
                    html.Div([
                        html.H3("Manage Companies & Domains", id="dialog-title", className="text-xl font-bold text-gray-800"),
                        html.Button(
                            "×", 
                            id="close-dialog-button",
                            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-2xl font-bold w-8 h-8 flex items-center justify-center"
                        )
                    ], className="relative mb-4 flex justify-between items-center"),
                    
                    # Three-column layout
                    html.Div([
                        # Left column - Companies list
                        html.Div([
                            html.H4("Companies", className="text-lg font-semibold text-gray-700 mb-3"),
                            html.Div(
                                id="companies-list-container",
                                className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto border border-gray-200",
                                children=[
                                    html.Div("Loading companies...", className="text-gray-500 text-center p-4")
                                ]
                            ),
                            html.Div(id="companies-count", className="text-sm text-gray-600 mt-2")
                        ], className="flex-1 pr-4"),
                        
                        # Middle column - Add/Edit form
                        html.Div([
                            html.H4("Add/Edit Company", className="text-lg font-semibold text-gray-700 mb-3"),
                            html.Div([
                                html.Label("Company Name:", className="block text-sm font-medium text-gray-700 mb-2"),
                                dcc.Input(
                                    id="company-name-input",
                                    type="text",
                                    placeholder="Enter company name or domain (e.g., MSFT or adobe.com)",
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                                    style={"fontSize": "14px"}
                                ),
                                html.Div(id="company-validation-message", className="mt-2 text-sm"),
                                
                                # Hidden input for edit mode
                                dcc.Input(id="edit-company-index", type="hidden", value=-1),
                                
                                # Form buttons
                                html.Div([
                                    html.Button(
                                        "Clear",
                                        id="clear-form-button", 
                                        className="bg-gray-300 hover:bg-gray-400 text-gray-700 font-bold py-2 px-4 rounded mr-2 transition-colors duration-200"
                                    ),
                                    html.Button(
                                        "Add Company",
                                        id="submit-company-button", 
                                        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
                                    )
                                ], className="flex justify-end mt-6")
                            ], className="bg-white p-4 rounded-lg border border-gray-200")
                        ], className="flex-1 px-4 border-l border-r border-gray-200"),
                        
                        # Right column - Domains management
                        html.Div([
                            html.H4("Manage Owned Domains", className="text-lg font-semibold text-gray-700 mb-3"),
                            html.Div([
                                html.Label("Selected Company:", className="block text-sm font-medium text-gray-700 mb-2"),
                                html.Div(
                                    id="selected-company-display",
                                    className="text-sm text-gray-600 mb-4 p-2 bg-gray-50 rounded"
                                ),
                                html.Label("Add Domain:", className="block text-sm font-medium text-gray-700 mb-2"),
                                dcc.Input(
                                    id="domain-input",
                                    type="text",
                                    placeholder="Enter owned domain (e.g., microsoft.com)",
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-2",
                                    style={"fontSize": "14px"}
                                ),
                                html.Button(
                                    "Add Domain",
                                    id="add-domain-button",
                                    className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200 w-full mb-4"
                                ),
                                html.Label("Current Domains:", className="block text-sm font-medium text-gray-700 mb-2"),
                                html.Div(
                                    id="domains-list-container",
                                    className="bg-gray-50 rounded-lg p-3 max-h-48 overflow-y-auto border border-gray-200",
                                    children=[
                                        html.Div("Select a company to manage domains", className="text-gray-500 text-center p-4")
                                    ]
                                )
                            ], className="bg-white p-4 rounded-lg border border-gray-200")
                        ], className="flex-1 pl-4")
                    ], className="flex flex-1 space-x-4"),
                    
                    # Status message at the bottom
                    html.Div(
                        id="dialog-status-message",
                        className="mt-4"
                    ),
                    
                    # Footer with close button
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
    
    # Tabs - Companies & Domains moved to first position
    dcc.Tabs(id="tabs", value='tab-4', className="mb-6", children=[
        dcc.Tab(label='Companies & Domains', value='tab-4', className="px-4 py-2 font-semibold"),
        dcc.Tab(label='Overview', value='tab-1', className="px-4 py-2 font-semibold"),
        dcc.Tab(label='Charts', value='tab-2', className="px-4 py-2 font-semibold"),
        dcc.Tab(label='Data Table', value='tab-3', className="px-4 py-2 font-semibold"),
    ]),
    
    # Tab content
    html.Div(id='tabs-content', className="bg-white p-6 rounded-lg shadow-sm"),
    
    # Store components
    dcc.Store(id='data-store', data=df.to_dict('records')),
    dcc.Store(id='loading-state', data=False),
    dcc.Store(id='companies-store', data=domains_data),
    dcc.Store(id='dialog-state', data=False),
    dcc.Store(id='selected-company', data=None)
], className="min-h-screen bg-gray-50 p-6", id="main-container")

# Callback to update companies list in the modal
@app.callback(
    [Output('companies-list-container', 'children'),
     Output('companies-count', 'children')],
    Input('companies-store', 'data'),
    prevent_initial_call=False
)
def update_companies_list(companies_data):
    if not companies_data:
        companies_list = html.Div([
            html.P("No companies added yet. Add your first company using the form on the right.", 
                   className="text-gray-500 text-center p-4")
        ])
        count_text = "Total: 0 companies"
        return companies_list, count_text
    
    # Create company items
    company_items = []
    for i, (company_name, domains) in enumerate(companies_data.items()):
        domain_count = len(domains)
        domain_badge = html.Span(
            f"{domain_count} domain{'s' if domain_count != 1 else ''}",
            className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded ml-2"
        ) if domain_count > 0 else ""
        
        company_item = html.Div([
            html.Div([
                html.Span(f"{i+1}.", className="font-semibold text-gray-600 mr-2"),
                html.Span(company_name, className="text-gray-800 flex-1"),
                domain_badge
            ], className="flex items-center"),
            html.Div([
                # Edit button with icon
                html.Button(
                    "✎",  # Edit icon
                    id={'type': 'edit-company-button', 'index': i},
                    n_clicks=0,
                    title="Edit company",
                    className="text-gray-600 hover:text-blue-600 hover:bg-gray-100 text-sm mr-1 px-2 py-1 border border-gray-300 rounded transition-colors duration-200"
                ),
                # Domains button
                html.Button(
                    "🔗",  # Link icon for domains
                    id={'type': 'manage-domains-button', 'index': i},
                    n_clicks=0,
                    title="Manage domains",
                    className="text-gray-600 hover:text-green-600 hover:bg-gray-100 text-sm mr-1 px-2 py-1 border border-gray-300 rounded transition-colors duration-200"
                ),
                # Delete button with icon
                html.Button(
                    "🗑",  # Trash icon
                    id={'type': 'delete-company-button', 'index': i},
                    n_clicks=0,
                    title="Delete company",
                    className="text-gray-600 hover:text-red-600 hover:bg-gray-100 text-sm px-2 py-1 border border-gray-300 rounded transition-colors duration-200"
                )
            ], className="flex space-x-1")
        ], className="flex items-center justify-between p-3 border-b border-gray-200 hover:bg-white rounded transition-colors duration-200")
        
        company_items.append(company_item)
    
    companies_list = html.Div(company_items)
    count_text = f"Total: {len(companies_data)} companies"
    
    return companies_list, count_text

# Callback to handle company selection for domains management
@app.callback(
    [Output('selected-company', 'data'),
     Output('selected-company-display', 'children'),
     Output('domains-list-container', 'children')],
    [Input({'type': 'manage-domains-button', 'index': dash.ALL}, 'n_clicks'),
     Input('companies-store', 'data')],
    [State('companies-store', 'data')],
    prevent_initial_call=True
)
def handle_company_selection(manage_clicks, companies_data, current_companies):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id.startswith('{"index":') and 'manage-domains-button' in button_id:
        try:
            button_data = json.loads(button_id)
            company_index = button_data['index']
            company_keys = list(current_companies.keys())
            if 0 <= company_index < len(company_keys):
                selected_company = company_keys[company_index]
                domains = current_companies.get(selected_company, [])
                
                # Display selected company
                company_display = html.Div([
                    html.Strong(selected_company),
                    html.Span(f" ({len(domains)} domains)", className="text-gray-500 ml-2")
                ])
                
                # Create domains list
                if domains:
                    domains_list = html.Div([
                        html.Div([
                            html.Span(domain, className="flex-1 text-sm"),
                            html.Button(
                                "🗑",
                                id={'type': 'delete-domain-button', 'company': selected_company, 'domain': domain},
                                n_clicks=0,
                                title="Delete domain",
                                className="text-red-500 hover:text-red-700 text-xs px-1"
                            )
                        ], className="flex items-center justify-between p-2 border-b border-gray-200 hover:bg-white")
                        for domain in domains
                    ])
                else:
                    domains_list = html.Div([
                        html.P("No domains yet. Add domains using the form above.", 
                               className="text-gray-500 text-center p-2 text-sm")
                    ])
                
                return selected_company, company_display, domains_list
        except:
            pass
    
    return dash.no_update, dash.no_update, dash.no_update

# Callback to add domains
@app.callback(
    [Output('companies-store', 'data', allow_duplicate=True),
     Output('domain-input', 'value'),
     Output('dialog-status-message', 'children', allow_duplicate=True)],
    Input('add-domain-button', 'n_clicks'),
    [State('domain-input', 'value'),
     State('selected-company', 'data'),
     State('companies-store', 'data')],
    prevent_initial_call=True
)
def add_domain(add_clicks, domain_value, selected_company, companies_data):
    if not add_clicks or not domain_value or not selected_company:
        return dash.no_update, dash.no_update, dash.no_update
    
    cleaned_domain = clean_domain(domain_value)
    if not cleaned_domain:
        error_status = html.Div([
            html.Span("⚠", className="mr-2"),
            html.Span("Invalid domain URL format", className="text-red-600")
        ])
        return dash.no_update, dash.no_update, error_status
    
    # Check if domain already exists for any company
    for company, domains in companies_data.items():
        if cleaned_domain in domains:
            error_status = html.Div([
                html.Span("⚠", className="mr-2"),
                html.Span(f"Domain {cleaned_domain} already exists for {company}", className="text-yellow-600")
            ])
            return dash.no_update, dash.no_update, error_status
    
    # Add domain to selected company
    updated_companies = companies_data.copy()
    if selected_company in updated_companies:
        if cleaned_domain not in updated_companies[selected_company]:
            updated_companies[selected_company].append(cleaned_domain)
            
            # Save to file
            if save_domains(updated_companies):
                success_status = html.Div([
                    html.Span("✅", className="mr-2"),
                    html.Span(f"Added domain {cleaned_domain} to {selected_company}", className="text-green-600")
                ])
                return updated_companies, "", success_status
            else:
                error_status = html.Div([
                    html.Span("❌", className="mr-2"),
                    html.Span("Failed to save domain", className="text-red-600")
                ])
                return dash.no_update, dash.no_update, error_status
    
    return dash.no_update, dash.no_update, dash.no_update

# Callback to delete domains
@app.callback(
    [Output('companies-store', 'data', allow_duplicate=True),
     Output('dialog-status-message', 'children', allow_duplicate=True)],
    Input({'type': 'delete-domain-button', 'company': dash.ALL, 'domain': dash.ALL}, 'n_clicks'),
    [State('companies-store', 'data')],
    prevent_initial_call=True
)
def delete_domain(delete_clicks, companies_data):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id.startswith('{"domain":') and 'delete-domain-button' in button_id:
        try:
            button_data = json.loads(button_id)
            company_name = button_data['company']
            domain_name = button_data['domain']
            
            if company_name in companies_data and domain_name in companies_data[company_name]:
                updated_companies = companies_data.copy()
                updated_companies[company_name].remove(domain_name)
                
                # Save to file
                if save_domains(updated_companies):
                    success_status = html.Div([
                        html.Span("✅", className="mr-2"),
                        html.Span(f"Deleted domain {domain_name} from {company_name}", className="text-green-600")
                    ])
                    return updated_companies, success_status
                else:
                    error_status = html.Div([
                        html.Span("❌", className="mr-2"),
                        html.Span("Failed to delete domain", className="text-red-600")
                    ])
                    return dash.no_update, error_status
        except:
            pass
    
    return dash.no_update, dash.no_update

# Combined callback for dialog operations (opening/closing, editing, deleting, submitting)
@app.callback(
    [Output('dialog-state', 'data'),
     Output('dialog-title', 'children'),
     Output('company-name-input', 'value'),
     Output('edit-company-index', 'value'),
     Output('submit-company-button', 'children'),
     Output('companies-store', 'data'),
     Output('dialog-status-message', 'children'),
     Output('selected-company', 'data', allow_duplicate=True),
     Output('selected-company-display', 'children', allow_duplicate=True),
     Output('domains-list-container', 'children', allow_duplicate=True)],
    [Input('add-website-button', 'n_clicks'),
     Input('close-dialog-button', 'n_clicks'),
     Input('cancel-dialog-button', 'n_clicks'),
     Input({'type': 'edit-company-button', 'index': dash.ALL}, 'n_clicks'),
     Input({'type': 'delete-company-button', 'index': dash.ALL}, 'n_clicks'),
     Input('submit-company-button', 'n_clicks'),
     Input('clear-form-button', 'n_clicks')],
    [State('dialog-state', 'data'),
     State('edit-company-index', 'value'),
     State('companies-store', 'data'),
     State('company-name-input', 'value')],
    prevent_initial_call=True
)
def handle_dialog_operations(add_clicks, close_clicks, cancel_clicks, edit_clicks, delete_clicks, submit_clicks, clear_clicks,
                           dialog_open, edit_index, current_companies, company_value):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Handle dialog opening
    if button_id == 'add-website-button':
        return True, "Manage Companies & Domains", "", -1, "Add Company", dash.no_update, "", None, "No company selected", html.Div("Select a company to manage domains", className="text-gray-500 text-center p-4")
    
    # Handle dialog closing
    elif button_id in ['close-dialog-button', 'cancel-dialog-button']:
        return False, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, "", None, "No company selected", html.Div("Select a company to manage domains", className="text-gray-500 text-center p-4")
    
    # Handle edit button
    elif button_id.startswith('{"index":') and 'edit-company-button' in button_id:
        try:
            button_data = json.loads(button_id)
            company_index = button_data['index']
            company_keys = list(current_companies.keys())
            if 0 <= company_index < len(company_keys):
                company_name = company_keys[company_index]
                return dash.no_update, dash.no_update, company_name, company_index, "Update Company", dash.no_update, "", dash.no_update, dash.no_update, dash.no_update
        except:
            pass
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Handle delete button
    elif button_id.startswith('{"index":') and 'delete-company-button' in button_id:
        try:
            button_data = json.loads(button_id)
            company_index = button_data['index']
            company_keys = list(current_companies.keys())
            if 0 <= company_index < len(company_keys):
                deleted_company = company_keys[company_index]
                updated_companies = current_companies.copy()
                del updated_companies[deleted_company]
                
                # Save to file
                if save_domains(updated_companies):
                    success_status = html.Div([
                        html.Span("✅", className="mr-2"),
                        html.Span(f"Deleted {deleted_company} successfully!", className="text-green-600")
                    ])
                    return dash.no_update, dash.no_update, "", -1, "Add Company", updated_companies, success_status, None, "No company selected", html.Div("Select a company to manage domains", className="text-gray-500 text-center p-4")
                else:
                    error_status = html.Div([
                        html.Span("❌", className="mr-2"),
                        html.Span("Failed to delete company", className="text-red-600")
                    ])
                    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, error_status, dash.no_update, dash.no_update, dash.no_update
        except:
            pass
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Handle clear form button
    elif button_id == 'clear-form-button':
        return dash.no_update, dash.no_update, "", -1, "Add Company", dash.no_update, "", dash.no_update, dash.no_update, dash.no_update
    
    # Handle form submission
    elif button_id == 'submit-company-button':
        if not company_value:
            error_status = html.Div([
                html.Span("⚠", className="mr-2"),
                html.Span("Please enter a company name", className="text-red-600")
            ])
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, error_status, dash.no_update, dash.no_update, dash.no_update
        
        cleaned_company = company_value.strip()
        
        if not cleaned_company:
            error_status = html.Div([
                html.Span("⚠", className="mr-2"),
                html.Span("Invalid company name", className="text-red-600")
            ])
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, error_status, dash.no_update, dash.no_update, dash.no_update
        
        # Check for duplicates
        if edit_index == -1:  # Add mode
            if cleaned_company in current_companies:
                duplicate_status = html.Div([
                    html.Span("⚠", className="mr-2"),
                    html.Span("Company already exists", className="text-yellow-600")
                ])
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, duplicate_status, dash.no_update, dash.no_update, dash.no_update
        else:  # Edit mode
            company_keys = list(current_companies.keys())
            if 0 <= edit_index < len(company_keys):
                old_company = company_keys[edit_index]
                if cleaned_company in current_companies and cleaned_company != old_company:
                    duplicate_status = html.Div([
                        html.Span("⚠", className="mr-2"),
                        html.Span("Company already exists", className="text-yellow-600")
                    ])
                    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, duplicate_status, dash.no_update, dash.no_update, dash.no_update
        
        # Add new company or update existing
        if edit_index == -1:  # Add mode
            updated_companies = current_companies.copy()
            updated_companies[cleaned_company] = []
            success_message = f"Added {cleaned_company} successfully!"
        else:  # Edit mode
            company_keys = list(current_companies.keys())
            if 0 <= edit_index < len(company_keys):
                old_company = company_keys[edit_index]
                updated_companies = current_companies.copy()
                domains = updated_companies.pop(old_company)
                updated_companies[cleaned_company] = domains
                success_message = f"Updated {old_company} to {cleaned_company} successfully!"
            else:
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        # Save to file
        if save_domains(updated_companies):
            success_status = html.Div([
                html.Span("✅", className="mr-2"),
                html.Span(success_message, className="text-green-600")
            ])
            return dash.no_update, dash.no_update, "", -1, "Add Company", updated_companies, success_status, None, "No company selected", html.Div("Select a company to manage domains", className="text-gray-500 text-center p-4")
        else:
            error_status = html.Div([
                html.Span("❌", className="mr-2"),
                html.Span("Failed to save company", className="text-red-600")
            ])
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, error_status, dash.no_update, dash.no_update, dash.no_update
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Callback to validate company input
@app.callback(
    Output('company-validation-message', 'children'),
    Input('company-name-input', 'value'),
    prevent_initial_call=True
)
def validate_company_input(company_value):
    if not company_value:
        return ""
    
    cleaned = company_value.strip()
    if cleaned:
        return html.Div([
            html.Span("✓ ", className="text-green-600"),
            html.Span(f"Company: {cleaned}", className="text-green-600 text-sm")
        ])
    else:
        return html.Div([
            html.Span("⚠ ", className="text-red-600"),
            html.Span("Please enter a valid company name", className="text-red-600 text-sm")
        ])

# Clientside callback to handle dialog visibility
clientside_callback(
    """
    function(dialog_open) {
        const dialogOverlay = document.getElementById('website-dialog-overlay');
        const companyInput = document.getElementById('company-name-input');
        
        if (dialog_open) {
            if (dialogOverlay) {
                dialogOverlay.classList.remove('hidden');
            }
            // Focus on input after a short delay to ensure it's rendered
            setTimeout(() => {
                if (companyInput) {
                    companyInput.focus();
                }
            }, 100);
            return 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50';
        } else {
            if (dialogOverlay) {
                dialogOverlay.classList.add('hidden');
            }
            // Clear input when closing
            if (companyInput) {
                companyInput.value = '';
            }
            return 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 hidden';
        }
    }
    """,
    Output('website-dialog-overlay', 'className'),
    Input('dialog-state', 'data'),
    prevent_initial_call=True
)

# Clientside callback to handle loading overlay and button state
clientside_callback(
    """
    function(loading) {
        const loadingOverlay = document.getElementById('loading-overlay');
        const updateButton = document.getElementById('update-button');
        const mainContainer = document.getElementById('main-container');
        
        if (loading) {
            // Show loading cursor
            if (document.body) {
                document.body.style.cursor = 'wait';
            }
            if (mainContainer) {
                mainContainer.style.cursor = 'wait';
            }
            
            // Show loading overlay
            if (loadingOverlay) {
                loadingOverlay.classList.remove('hidden');
            }
            
            // Disable button
            if (updateButton) {
                updateButton.disabled = true;
                updateButton.textContent = 'Updating...';
            }
            
            return 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50';
        } else {
            // Remove loading cursor
            if (document.body) {
                document.body.style.cursor = 'default';
            }
            if (mainContainer) {
                mainContainer.style.cursor = 'default';
            }
            
            // Hide loading overlay
            if (loadingOverlay) {
                loadingOverlay.classList.add('hidden');
            }
            
            // Enable button
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

# Callback to start loading state when button is clicked
@app.callback(
    [Output('loading-state', 'data'),
     Output('update-status', 'children')],
    Input('update-button', 'n_clicks'),
    State('loading-state', 'data'),
    prevent_initial_call=True
)
def start_loading(n_clicks, loading):
    if n_clicks > 0 and not loading:
        # Show inline loading status
        loading_status = html.Div([
            html.Span(
                className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500 inline-block mr-2"
            ),
            html.Span("Updating...", className="text-blue-600")
        ])
        return True, loading_status
    return dash.no_update, dash.no_update

# Callback to handle the actual data update when loading state becomes True
@app.callback(
    [Output('data-store', 'data'),
     Output('loading-state', 'data', allow_duplicate=True),
     Output('update-status', 'children', allow_duplicate=True)],
    Input('loading-state', 'data'),
    prevent_initial_call=True
)
def update_data(loading):
    if loading:
        # Simulate API call with a delay
        time.sleep(2)  # Simulate network latency
        
        # Simulate success or failure randomly
        if np.random.random() > 0.2:  # 80% success rate
            # Generate new data
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
            # Show error status
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
    
    # Convert Date column from string to datetime if needed
    if 'Date' in df.columns and df['Date'].dtype == 'object':
        try:
            df['Date'] = pd.to_datetime(df['Date'])
        except:
            pass
    
    # Companies & Domains tab (now first)
    if tab == 'tab-4':
        # Calculate total domains count
        total_domains = sum(len(domains) for domains in companies_data.values())
        
        # Companies management tab
        return html.Div([
            html.H2("Companies & Owned Domains", className="text-2xl font-bold text-gray-800 mb-6"),
            
            # Stats
            html.Div([
                html.Div([
                    html.Div([
                        html.H3("Total Companies", className="text-lg font-semibold text-gray-700"),
                        html.P(f"{len(companies_data)}", className="text-3xl font-bold text-blue-600")
                    ], className="p-4")
                ], className="bg-white rounded-lg shadow-sm border-l-4 border-blue-500"),
                
                html.Div([
                    html.Div([
                        html.H3("Total Domains", className="text-lg font-semibold text-gray-700"),
                        html.P(f"{total_domains}", className="text-3xl font-bold text-green-600")
                    ], className="p-4")
                ], className="bg-white rounded-lg shadow-sm border-l-4 border-green-500"),
                
                html.Div([
                    html.Div([
                        html.H3("File Status", className="text-lg font-semibold text-gray-700"),
                        html.P("Active" if os.path.exists('domains.json') else "Not Found", 
                               className="text-3xl font-bold text-purple-600" if os.path.exists('domains.json') else "text-3xl font-bold text-red-600")
                    ], className="p-4")
                ], className="bg-white rounded-lg shadow-sm border-l-4 border-purple-500"),
            ], className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6"),
            
            # Companies list with domains
            html.Div([
                html.H3("Current Companies & Domains", className="text-xl font-semibold text-gray-800 mb-4"),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span(f"{i+1}.", className="font-semibold text-gray-600 mr-2"),
                            html.Span(company_name, className="text-gray-800 font-medium"),
                            html.Span(
                                f"({len(domains)} domains)",
                                className="text-sm text-gray-500 ml-2"
                            )
                        ], className="mb-2"),
                        html.Div([
                            html.Span("Domains: ", className="text-sm text-gray-600 font-medium"),
                            html.Span(
                                ", ".join(domains) if domains else "No domains (single company)",
                                className="text-sm text-gray-700"
                            )
                        ], className="ml-4")
                    ], className="p-3 border-b border-gray-200 hover:bg-gray-50")
                    for i, (company_name, domains) in enumerate(companies_data.items())
                ], className="bg-white rounded-lg shadow-sm max-h-96 overflow-y-auto") if companies_data else html.Div([
                    html.P("No companies added yet.", className="text-gray-500 text-center p-8")
                ], className="bg-white rounded-lg shadow-sm"),
                
                # Instructions
                html.Div([
                    html.H4("Instructions", className="font-semibold text-gray-800 mb-2"),
                    html.Ul([
                        html.Li("Click 'Manage Companies & Domains' to add, edit, or delete companies and domains", className="text-gray-600"),
                        html.Li("Parent companies can have multiple owned domains (e.g., MSFT → microsoft.com, github.com)", className="text-gray-600"),
                        html.Li("Single companies can be added with no domains (e.g., adobe.com, sailpoints.com)", className="text-gray-600"),
                        html.Li("Domains are automatically cleaned (removes http/https, www)", className="text-gray-600"),
                        html.Li("Duplicate domains across different companies are not allowed", className="text-gray-600"),
                        html.Li("The domains.json file is saved in the current directory", className="text-gray-600")
                    ], className="list-disc pl-6 space-y-1")
                ], className="bg-gray-50 p-4 rounded-lg mt-4")
            ])
        ])
    
    elif tab == 'tab-1':
        # Safely get date range
        if 'Date' in df.columns and len(df) > 0:
            try:
                date_min = df['Date'].min()
                date_max = df['Date'].max()
                date_range = f"{safe_date_format(date_min)} to {safe_date_format(date_max)}"
            except:
                date_range = "Date range not available"
        else:
            date_range = "Date range not available"
        
        # Calculate total domains count
        total_domains = sum(len(domains) for domains in companies_data.values())
        
        return html.Div([
            html.H2("Overview Dashboard", className="text-2xl font-bold text-gray-800 mb-6"),
            
            # Stats cards
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
                        html.H3("Total Companies", className="text-lg font-semibold text-gray-700"),
                        html.P(f"{len(companies_data)}", className="text-3xl font-bold text-orange-600")
                    ], className="p-4")
                ], className="bg-white rounded-lg shadow-sm border-l-4 border-orange-500"),
                
                html.Div([
                    html.Div([
                        html.H3("Total Domains", className="text-lg font-semibold text-gray-700"),
                        html.P(f"{total_domains}", className="text-3xl font-bold text-indigo-600")
                    ], className="p-4")
                ], className="bg-white rounded-lg shadow-sm border-l-4 border-indigo-500"),
            ], className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6"),
            
            # Quick summary
            html.Div([
                html.H3("Data Summary", className="text-xl font-semibold text-gray-800 mb-4"),
                html.P(f"Dataset contains {len(df)} records across {df['Category'].nunique()} categories."),
                html.P(f"Date range: {date_range}"),
                html.P(f"Currently managing {len(companies_data)} companies with {total_domains} domains."),
            ], className="bg-gray-50 p-4 rounded-lg")
        ])
    
    elif tab == 'tab-2':
        return html.Div([
            html.H2("Data Visualization", className="text-2xl font-bold text-gray-800 mb-6"),
            
            # Charts row
            html.Div([
                # Bar chart
                html.Div([
                    dcc.Graph(
                        id='bar-chart',
                        figure=px.bar(df, x='Category', y='Value', title='Values by Category')
                        .update_layout(title_x=0.5, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    )
                ], className="bg-white p-4 rounded-lg shadow-sm"),
                
                # Scatter plot
                html.Div([
                    dcc.Graph(
                        id='scatter-plot',
                        figure=px.scatter(df, x='Date', y='Value', color='Category', 
                                         title='Value Trends Over Time')
                        .update_layout(title_x=0.5, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    )
                ], className="bg-white p-4 rounded-lg shadow-sm"),
            ], className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6"),
            
            # Additional chart
            html.Div([
                dcc.Graph(
                    id='histogram',
                    figure=px.histogram(df, x='Value', color='Category', 
                                       title='Value Distribution by Category', barmode='overlay')
                    .update_layout(title_x=0.5, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                )
            ], className="bg-white p-4 rounded-lg shadow-sm")
        ])
    
    elif tab == 'tab-3':
        return html.Div([
            html.H2("Data Table", className="text-2xl font-bold text-gray-800 mb-6"),
            
            # Data table with controls
            html.Div([
                html.Label("Show entries:", className="font-semibold text-gray-700 mr-2"),
                dcc.Dropdown(
                    id='rows-dropdown',
                    options=[{'label': str(i), 'value': i} for i in [10, 25, 50, 100]],
                    value=10,
                    className="w-20 inline-block"
                )
            ], className="mb-4"),
            
            # Data table
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
            
            # Summary
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
            /* Ensure overlays appear above everything */
            .z-50 {
                z-index: 50;
            }
            
            /* Smooth transitions for buttons */
            .transition-colors {
                transition-property: background-color, border-color, color, fill, stroke;
                transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
                transition-duration: 200ms;
            }
            
            /* Loading spinner animation */
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
            
            /* Input focus styles */
            input:focus {
                outline: none;
                border-color: #3B82F6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            /* Dialog positioning */
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