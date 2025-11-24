import dash
from dash import html, dcc, Input, Output, State, callback_context, dash_table, callback
import dash_bootstrap_components as dbc
import pandas as pd
import uuid
import json
import os

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Domain & Company Editor"

# File path for portfolio data
PORTFOLIO_FILE = "domains.json"

def load_portfolio_data():
    """Load portfolio data from JSON file"""
    if os.path.exists(PORTFOLIO_FILE):
        try:
            with open(PORTFOLIO_FILE, 'r') as f:
                data = json.load(f)
                
                # Convert the simple domain strings to domain objects
                domain_strings = data.get('domain', [])
                domains = []
                for i, domain_str in enumerate(domain_strings):
                    domains.append({
                        "id": str(i + 1),
                        "symbol": domain_str
                    })
                
                # Convert the simple company structure to company objects
                company_dict = data.get('company', {})
                companies = []
                company_id = 1
                for symbol, domain_list in company_dict.items():
                    company_domains = []
                    for domain_str in domain_list:
                        # Find the domain ID for this domain string
                        domain_obj = next((d for d in domains if d['symbol'] == domain_str), None)
                        if domain_obj:
                            company_domains.append(domain_obj['id'])
                    
                    companies.append({
                        "id": str(company_id),
                        "symbol": symbol,
                        "domains": company_domains
                    })
                    company_id += 1
                
                return domains, companies
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading data: {e}")
            pass
    
    # Return default data if file doesn't exist or is invalid
    default_domains = [
        {"id": "1", "symbol": "palantir.com"},
        {"id": "2", "symbol": "github.com"},
        {"id": "3", "symbol": "google.com"},
        {"id": "4", "symbol": "microsoft.com"},
    ]
    
    default_companies = [
        {
            "id": "1", 
            "symbol": "MSFT", 
            "domains": ["2", "4"]
        },
        {
            "id": "2", 
            "symbol": "GOOGLE", 
            "domains": ["3", "1"]
        }
    ]
    
    return default_domains, default_companies

def save_portfolio_data(domains, companies):
    """Save portfolio data to JSON file in the simple format"""
    # Convert domains back to simple strings
    domain_strings = [domain['symbol'] for domain in domains]
    
    # Convert companies back to the simple format
    company_dict = {}
    for company in companies:
        company_domains = []
        for domain_id in company['domains']:
            # Find the domain symbol for this domain_id
            domain_obj = next((d for d in domains if d['id'] == domain_id), None)
            if domain_obj:
                company_domains.append(domain_obj['symbol'])
        company_dict[company['symbol']] = company_domains
    
    data = {
        'domain': domain_strings,
        'company': company_dict
    }
    
    try:
        with open(PORTFOLIO_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving portfolio data: {e}")
        return False

# Load initial data
initial_domains, initial_companies = load_portfolio_data()

# Navigation bar with button and save status
navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand("Domain & Company Portfolio Manager", className="ms-2"),
        html.Div([
            dbc.Badge("Saved", id="save-status", color="success", className="me-3"),
            dbc.Button("Manage Portfolio", id="open-modal-btn", color="primary"),
        ], className="d-flex align-items-center")
    ]),
    color="dark",
    dark=True,
    className="mb-4"
)

# Main content layout
main_content = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Portfolio Overview", className="text-xl font-bold mb-4"),
            html.Div(id="portfolio-overview")
        ])
    ])
])

# Confirmation modal for delete operations
delete_confirmation_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Confirm Delete")),
    dbc.ModalBody([
        html.Div(id="delete-confirmation-message"),
    ]),
    dbc.ModalFooter([
        dbc.Button("Cancel", id="cancel-delete-btn", color="secondary", className="me-2"),
        dbc.Button("Confirm Delete", id="confirm-delete-btn", color="danger"),
    ]),
], id="delete-confirmation-modal", is_open=False)

# Confirmation modal for save operations
save_confirmation_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Confirm Save")),
    dbc.ModalBody([
        html.Div(id="save-confirmation-message"),
    ]),
    dbc.ModalFooter([
        dbc.Button("Cancel", id="cancel-save-btn", color="secondary", className="me-2"),
        dbc.Button("Confirm Save", id="confirm-save-btn", color="primary"),
    ]),
], id="save-confirmation-modal", is_open=False)

# Modal for managing domains and companies
portfolio_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Manage Portfolio")),
    dbc.ModalBody([
        dbc.Tabs([
            # Domains Tab
            dbc.Tab([
                html.Div([
                    html.H4("Domains Management", className="font-bold mb-3"),
                    dbc.Button("Add New Domain", id="add-domain-btn", color="success", className="mb-3"),
                    
                    # Domains table with scroll
                    html.Div(
                        id="domains-table-container",
                        style={"maxHeight": "400px", "overflowY": "auto", "border": "1px solid #dee2e6", "borderRadius": "0.375rem"}
                    ),
                    
                    # Add/Edit Domain Form (initially hidden)
                    dbc.Collapse([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Domain Details", className="m-0")),
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Domain *"),
                                        dbc.Input(id="domain-symbol", type="text", placeholder="e.g., example.com"),
                                        dbc.FormText("Unique domain name")
                                    ])
                                ], className="mb-3"),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button("Save Domain", id="save-domain-btn", color="primary", className="me-2"),
                                        dbc.Button("Cancel", id="cancel-domain-btn", color="secondary"),
                                    ])
                                ])
                            ])
                        ], className="mt-3")
                    ], id="domain-form-collapse")
                ])
            ], label="Domains", tab_id="tab-domains"),
            
            # Companies Tab
            dbc.Tab([
                html.Div([
                    html.H4("Companies Management", className="font-bold mb-3"),
                    dbc.Button("Add New Company", id="add-company-btn", color="success", className="mb-3"),
                    
                    # Companies table with scroll
                    html.Div(
                        id="companies-table-container",
                        style={"maxHeight": "400px", "overflowY": "auto", "border": "1px solid #dee2e6", "borderRadius": "0.375rem"}
                    ),
                    
                    # Add/Edit Company Form (initially hidden)
                    dbc.Collapse([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Company Details", className="m-0")),
                            dbc.CardBody([
                                dbc.Row([
                                    # Left Column - Company Symbol and Domain Composition
                                    dbc.Col([
                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Label("Symbol *"),
                                                dbc.Input(id="company-symbol", type="text", placeholder="e.g., MSFT"),
                                                dbc.FormText("Unique company symbol")
                                            ])
                                        ], className="mb-3"),
                                        
                                        html.Div(id="company-composition-header"),
                                        # Domain composition with scroll
                                        html.Div(
                                            id="company-composition-container",
                                            style={"maxHeight": "200px", "overflowY": "auto", "border": "1px solid #dee2e6", "borderRadius": "0.375rem", "padding": "10px"}
                                        ),
                                    ], width=6),
                                    
                                    # Right Column - Add Domain and Save/Cancel buttons
                                    dbc.Col([
                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Label("Add Domain to Company"),
                                                dbc.Select(
                                                    id="domain-selector",
                                                    options=[],
                                                    placeholder="Select a domain to add..."
                                                ),
                                            ])
                                        ], className="mb-3"),
                                        
                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Button("Add", id="add-domain-to-company", color="outline-primary", className="w-100"),
                                            ])
                                        ], className="mb-4"),
                                        
                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Button("Save Company", id="save-company-btn", color="primary", className="w-100 mb-2"),
                                                dbc.Button("Cancel", id="cancel-company-btn", color="secondary", className="w-100"),
                                            ])
                                        ])
                                    ], width=6)
                                ])
                            ])
                        ], className="mt-3")
                    ], id="company-form-collapse")
                ])
            ], label="Companies", tab_id="tab-companies"),
        ])
    ])
], size="xl", scrollable=True, is_open=False, id="portfolio-modal", centered=True)

# App layout
app.layout = html.Div([
    navbar,
    main_content,
    portfolio_modal,
    delete_confirmation_modal,
    save_confirmation_modal,
    
    # Store components for state management
    dcc.Store(id='domains-store', data=initial_domains),
    dcc.Store(id='companies-store', data=initial_companies),
    dcc.Store(id='editing-domain-id', data=None),
    dcc.Store(id='editing-company-id', data=None),
    dcc.Store(id='company-composition', data=[]),
    dcc.Store(id='pending-delete', data={'type': None, 'id': None}),
    dcc.Store(id='pending-save', data={'type': None, 'data': None}),
    
    # Hidden div for triggering callbacks
    html.Div(id="dummy-output", style={"display": "none"}),
])

# Callback to save portfolio data whenever stores change
@app.callback(
    Output("save-status", "children"),
    [Input("domains-store", "data"),
     Input("companies-store", "data")]
)
def save_portfolio(domains, companies):
    if save_portfolio_data(domains, companies):
        return "Saved"
    else:
        return "Save Failed"

# Callback to open portfolio modal
@app.callback(
    Output("portfolio-modal", "is_open"),
    Input("open-modal-btn", "n_clicks"),
    State("portfolio-modal", "is_open"),
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open

# Callback to show/hide domain form and reset form
@app.callback(
    [Output("domain-form-collapse", "is_open"),
     Output("domain-symbol", "value")],
    [Input("add-domain-btn", "n_clicks"), 
     Input("cancel-domain-btn", "n_clicks"),
     Input("confirm-save-btn", "n_clicks")],
    [State("domain-form-collapse", "is_open"),
     State("editing-domain-id", "data"),
     State("domains-store", "data")],
    prevent_initial_call=True
)
def toggle_domain_form(add_clicks, cancel_clicks, save_clicks, is_open, editing_id, domains):
    ctx = callback_context
    if not ctx.triggered:
        return is_open, ""
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == "add-domain-btn":
        return True, ""
    elif trigger_id in ["cancel-domain-btn", "confirm-save-btn"]:
        return False, ""
    
    return is_open, ""

# Callback to show/hide company form and reset form
@app.callback(
    [Output("company-form-collapse", "is_open"),
     Output("company-symbol", "value"),
     Output("company-composition", "data")],
    [Input("add-company-btn", "n_clicks"), 
     Input("cancel-company-btn", "n_clicks"),
     Input("confirm-save-btn", "n_clicks")],
    [State("company-form-collapse", "is_open"),
     State("editing-company-id", "data"),
     State("companies-store", "data")],
    prevent_initial_call=True
)
def toggle_company_form(add_clicks, cancel_clicks, save_clicks, is_open, editing_id, companies):
    ctx = callback_context
    if not ctx.triggered:
        return is_open, "", []
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == "add-company-btn":
        return True, "", []
    elif trigger_id in ["cancel-company-btn", "confirm-save-btn"]:
        return False, "", []
    
    return is_open, "", []

# Callback to update domains table with action buttons
@app.callback(
    Output("domains-table-container", "children"),
    Input("domains-store", "data")
)
def update_domains_table(domains):
    if not domains:
        return html.P("No domains available. Add some domains to get started.", className="p-3")
    
    # Create table with action buttons
    table_header = [
        html.Thead(html.Tr([
            html.Th("Domain"), 
            html.Th("Actions")
        ]))
    ]
    
    table_rows = []
    for domain in domains:
        row = html.Tr([
            html.Td(domain['symbol']),
            html.Td([
                dbc.Button("Edit", id={'type': 'edit-domain', 'index': domain['id']}, 
                          color="warning", size="sm", className="me-1"),
                dbc.Button("Delete", id={'type': 'delete-domain', 'index': domain['id']}, 
                          color="danger", size="sm"),
            ])
        ])
        table_rows.append(row)
    
    table_body = [html.Tbody(table_rows)]
    
    return dbc.Table(table_header + table_body, bordered=True, hover=True, responsive=True, className="mb-0")

# Callback to handle delete confirmation for domains
@app.callback(
    [Output("delete-confirmation-modal", "is_open"),
     Output("delete-confirmation-message", "children"),
     Output("pending-delete", "data")],
    [Input({'type': 'delete-domain', 'index': dash.dependencies.ALL}, 'n_clicks'),
     Input({'type': 'delete-company', 'index': dash.dependencies.ALL}, 'n_clicks')],
    [State("domains-store", "data"),
     State("companies-store", "data"),
     State("pending-delete", "data")],
    prevent_initial_call=True
)
def show_delete_confirmation(domain_delete_clicks, company_delete_clicks, domains, companies, pending_delete):
    ctx = callback_context
    if not ctx.triggered:
        return False, "", pending_delete
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    # Check if the trigger was from a button that was actually clicked (not None)
    if ctx.triggered[0]['value'] is None:
        return False, "", pending_delete
    
    # Handle domain delete button clicks
    if 'delete-domain' in trigger_id:
        button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
        domain_id = button_id['index']
        
        # Find the domain to delete
        domain_to_delete = next((s for s in domains if s['id'] == domain_id), None)
        if domain_to_delete:
            message = html.Div([
                html.H5("Delete Domain?", className="text-danger"),
                html.P(f"Are you sure you want to delete {domain_to_delete['symbol']}?"),
                html.P("This action cannot be undone.", className="text-muted")
            ])
            pending_delete = {'type': 'domain', 'id': domain_id}
            return True, message, pending_delete
    
    # Handle company delete button clicks
    elif 'delete-company' in trigger_id:
        button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
        company_id = button_id['index']
        
        # Find the company to delete
        company_to_delete = next((e for e in companies if e['id'] == company_id), None)
        if company_to_delete:
            message = html.Div([
                html.H5("Delete Company?", className="text-danger"),
                html.P(f"Are you sure you want to delete {company_to_delete['symbol']}?"),
                html.P("This action cannot be undone.", className="text-muted")
            ])
            pending_delete = {'type': 'company', 'id': company_id}
            return True, message, pending_delete
    
    return False, "", pending_delete

# Callback to handle save confirmation for domains and companies
@app.callback(
    [Output("save-confirmation-modal", "is_open"),
     Output("save-confirmation-message", "children"),
     Output("pending-save", "data")],
    [Input("save-domain-btn", "n_clicks"),
     Input("save-company-btn", "n_clicks")],
    [State("domain-symbol", "value"),
     State("editing-domain-id", "data"),
     State("company-symbol", "value"),
     State("company-composition", "data"),
     State("editing-company-id", "data"),
     State("domains-store", "data"),
     State("companies-store", "data")],
    prevent_initial_call=True
)
def show_save_confirmation(domain_save_clicks, company_save_clicks, domain_symbol, editing_domain_id, company_symbol, company_composition, editing_company_id, domains, companies):
    ctx = callback_context
    if not ctx.triggered:
        return False, "", {'type': None, 'data': None}
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Handle domain save button click
    if trigger_id == "save-domain-btn" and domain_save_clicks:
        if not domain_symbol:
            return False, "", {'type': None, 'data': None}
        
        # Check if symbol already exists (for new domains)
        if not editing_domain_id:
            existing_symbol = any(s['symbol'].upper() == domain_symbol.upper() for s in domains)
            if existing_symbol:
                return False, "", {'type': None, 'data': None}
        
        action = "update" if editing_domain_id else "add"
        domain_data = {
            'symbol': domain_symbol,
            'editing_id': editing_domain_id
        }
        
        message = html.Div([
            html.H5(f"Confirm {action.capitalize()} Domain", className="text-primary"),
            html.P(f"Domain: {domain_symbol}"),
            html.P("Are you sure you want to save these changes?", className="mt-3")
        ])
        
        pending_save = {'type': 'domain', 'data': domain_data}
        return True, message, pending_save
    
    # Handle company save button click
    elif trigger_id == "save-company-btn" and company_save_clicks:
        if not company_symbol:
            return False, "", {'type': None, 'data': None}
        
        # Check if company has at least one domain
        if not company_composition or len(company_composition) == 0:
            # Show error message instead of save confirmation
            error_message = html.Div([
                html.H5("Cannot Save Company", className="text-danger"),
                html.P("A company must contain at least one domain."),
                html.P("Please add domains to the company before saving.", className="text-muted")
            ])
            return True, error_message, {'type': 'error', 'data': None}
        
        # Check if symbol already exists (for new companies)
        if not editing_company_id:
            existing_symbol = any(e['symbol'].upper() == company_symbol.upper() for e in companies)
            if existing_symbol:
                return False, "", {'type': None, 'data': None}
        
        action = "update" if editing_company_id else "add"
        company_data = {
            'symbol': company_symbol,
            'domains': company_composition,
            'editing_id': editing_company_id
        }
        
        message = html.Div([
            html.H5(f"Confirm {action.capitalize()} Company", className="text-primary"),
            html.P(f"Symbol: {company_symbol}"),
            html.P(f"Number of domains: {len(company_composition)}"),
            html.P("Are you sure you want to save these changes?", className="mt-3")
        ])
        
        pending_save = {'type': 'company', 'data': company_data}
        return True, message, pending_save
    
    return False, "", {'type': None, 'data': None}

# Callback to handle confirmed deletions
@app.callback(
    [Output("domains-store", "data", allow_duplicate=True),
     Output("companies-store", "data", allow_duplicate=True),
     Output("delete-confirmation-modal", "is_open", allow_duplicate=True)],
    [Input("confirm-delete-btn", "n_clicks"),
     Input("cancel-delete-btn", "n_clicks")],
    [State("domains-store", "data"),
     State("companies-store", "data"),
     State("pending-delete", "data")],
    prevent_initial_call=True
)
def handle_confirmed_deletion(confirm_clicks, cancel_clicks, domains, companies, pending_delete):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, False
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == "cancel-delete-btn":
        return dash.no_update, dash.no_update, False
    
    elif trigger_id == "confirm-delete-btn" and pending_delete['type']:
        if pending_delete['type'] == 'domain':
            # Remove the domain and any company compositions that reference it
            updated_domains = [s for s in domains if s['id'] != pending_delete['id']]
            
            # Update companies to remove references to the deleted domain
            updated_companies = []
            for company in companies:
                updated_domains_list = [domain_id for domain_id in company['domains'] if domain_id != pending_delete['id']]
                updated_companies.append({**company, 'domains': updated_domains_list})
            
            return updated_domains, updated_companies, False
        
        elif pending_delete['type'] == 'company':
            # Remove only the company
            updated_companies = [e for e in companies if e['id'] != pending_delete['id']]
            return dash.no_update, updated_companies, False
    
    return dash.no_update, dash.no_update, False

# Callback to handle confirmed saves
@app.callback(
    [Output("domains-store", "data", allow_duplicate=True),
     Output("companies-store", "data", allow_duplicate=True),
     Output("save-confirmation-modal", "is_open", allow_duplicate=True),
     Output("editing-domain-id", "data", allow_duplicate=True),
     Output("editing-company-id", "data", allow_duplicate=True)],
    [Input("confirm-save-btn", "n_clicks"),
     Input("cancel-save-btn", "n_clicks")],
    [State("domains-store", "data"),
     State("companies-store", "data"),
     State("pending-save", "data")],
    prevent_initial_call=True
)
def handle_confirmed_save(confirm_clicks, cancel_clicks, domains, companies, pending_save):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, False, dash.no_update, dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == "cancel-save-btn":
        return dash.no_update, dash.no_update, False, dash.no_update, dash.no_update
    
    elif trigger_id == "confirm-save-btn" and pending_save['type']:
        # Handle error case (when company has no domains)
        if pending_save['type'] == 'error':
            return dash.no_update, dash.no_update, False, dash.no_update, dash.no_update
        
        if pending_save['type'] == 'domain':
            domain_data = pending_save['data']
            new_domain_data = {
                "symbol": domain_data['symbol']
            }
            
            if domain_data['editing_id']:
                # Update existing domain
                updated_domains = []
                for domain in domains:
                    if domain['id'] == domain_data['editing_id']:
                        updated_domains.append({**domain, **new_domain_data})
                    else:
                        updated_domains.append(domain)
                return updated_domains, dash.no_update, False, None, dash.no_update
            else:
                # Add new domain
                new_domain = {**new_domain_data, "id": str(uuid.uuid4())}
                return domains + [new_domain], dash.no_update, False, None, dash.no_update
        
        elif pending_save['type'] == 'company':
            company_data = pending_save['data']
            new_company_data = {
                "symbol": company_data['symbol'],
                "domains": company_data['domains']
            }
            
            if company_data['editing_id']:
                # Update existing company
                updated_companies = []
                for company in companies:
                    if company['id'] == company_data['editing_id']:
                        updated_companies.append({**company, **new_company_data})
                    else:
                        updated_companies.append(company)
                return dash.no_update, updated_companies, False, dash.no_update, None
            else:
                # Add new company
                new_company = {**new_company_data, "id": str(uuid.uuid4())}
                return dash.no_update, companies + [new_company], False, dash.no_update, None
    
    return dash.no_update, dash.no_update, False, dash.no_update, dash.no_update

# Callback to handle domain edit and form population
@app.callback(
    [Output("editing-domain-id", "data", allow_duplicate=True),
     Output("domain-symbol", "value", allow_duplicate=True),
     Output("domain-form-collapse", "is_open", allow_duplicate=True)],
    [Input({'type': 'edit-domain', 'index': dash.dependencies.ALL}, 'n_clicks')],
    [State("domains-store", "data")],
    prevent_initial_call=True
)
def handle_domain_edit(edit_clicks, domains):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    # Handle edit button clicks - check if it's a real click
    if 'edit-domain' in trigger_id and ctx.triggered[0]['value'] is not None:
        button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
        domain_id = button_id['index']
        
        # Find the domain to edit
        domain_to_edit = next((s for s in domains if s['id'] == domain_id), None)
        if domain_to_edit:
            return (domain_id, domain_to_edit['symbol'], True)
    
    return dash.no_update

# Callback to update domain selector options - only show domains not in any company
@app.callback(
    Output("domain-selector", "options"),
    [Input("domains-store", "data"),
     Input("companies-store", "data"),
     Input("company-composition", "data"),
     Input("editing-company-id", "data")]
)
def update_domain_selector_options(domains, companies, current_composition, editing_company_id):
    if not domains:
        return []
    
    # Get all domain IDs that are currently used in any company
    used_domain_ids = set()
    for company in companies:
        # If we're editing a company, exclude the domains that are currently in that company
        # (they will be shown in the current_composition instead)
        if editing_company_id and company['id'] == editing_company_id:
            continue
        used_domain_ids.update(company['domains'])
    
    # Also exclude domains that are already in the current composition
    used_domain_ids.update(current_composition)
    
    # Create options only for domains that are not used
    available_domains = []
    for domain in domains:
        if domain['id'] not in used_domain_ids:
            available_domains.append({
                "label": domain['symbol'],
                "value": domain['id']
            })
    
    return available_domains

# Callback to add domain to company composition
@app.callback(
    Output("company-composition", "data", allow_duplicate=True),
    Input("add-domain-to-company", "n_clicks"),
    [State("domain-selector", "value"),
     State("company-composition", "data")],
    prevent_initial_call=True
)
def add_domain_to_company(n_clicks, selected_domain_id, composition):
    if n_clicks and selected_domain_id:
        # Check if domain already in composition
        if selected_domain_id in composition:
            return dash.no_update
        
        new_composition = composition + [selected_domain_id]
        return new_composition
    
    return dash.no_update

# Callback to remove domain from company composition
@app.callback(
    Output("company-composition", "data", allow_duplicate=True),
    Input({"type": "remove-domain", "index": dash.dependencies.ALL}, "n_clicks"),
    State("company-composition", "data"),
    prevent_initial_call=True
)
def remove_domain_from_company(remove_clicks, composition):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    # Check if this is a real click
    if 'remove-domain' in trigger_id and ctx.triggered[0]['value'] is not None:
        button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
        index_to_remove = button_id['index']
        
        if 0 <= index_to_remove < len(composition):
            updated_composition = composition.copy()
            updated_composition.pop(index_to_remove)
            return updated_composition
    
    return dash.no_update

# Callback to update company composition display
@app.callback(
    Output("company-composition-container", "children"),
    [Input("company-composition", "data"), Input("domains-store", "data")]
)
def update_company_composition_display(composition, domains):
    if not composition:
        return html.Div([
            dbc.Alert("No domains added to this company yet. A company must contain at least one domain.", 
                     color="warning", className="mb-3"),
            html.P("Use the form below to add domains.")
        ], className="p-3")
    
    composition_elements = []
    for i, domain_id in enumerate(composition):
        domain = next((d for d in domains if d['id'] == domain_id), None)
        if domain:
            composition_elements.append(
                dbc.Row([
                    dbc.Col([
                        html.Strong(f"{domain['symbol']}"),
                    ], width=10),
                    dbc.Col([
                        dbc.Button("Remove", color="danger", size="sm", 
                                  id={"type": "remove-domain", "index": i}),
                    ], width=2)
                ], className="mb-2 align-items-center p-2 border rounded")
            )
    
    return html.Div(composition_elements)

# Callback to update company composition header
@app.callback(
    Output("company-composition-header", "children"),
    Input("company-composition", "data")
)
def update_company_composition_header(composition):
    domain_count = len(composition) if composition else 0
    if domain_count == 0:
        return html.H6("Domain Composition (0 domains - add at least one domain)", className="mt-4 mb-3 text-danger")
    else:
        return html.H6(f"Domain Composition ({domain_count} domains)", className="mt-4 mb-3 text-success")

# Callback to update companies table
@app.callback(
    Output("companies-table-container", "children"),
    [Input("companies-store", "data"), Input("domains-store", "data")]
)
def update_companies_table(companies, domains):
    if not companies:
        return html.P("No companies available. Add some companies to get started.", className="p-3")
    
    table_header = [
        html.Thead(html.Tr([
            html.Th("Symbol"), 
            html.Th("Domains"), 
            html.Th("Actions")
        ]))
    ]
    
    table_rows = []
    for company in companies:
        domain_count = len(company['domains'])
        
        row = html.Tr([
            html.Td(company['symbol']),
            html.Td(domain_count),
            html.Td([
                dbc.Button("Edit", id={'type': 'edit-company', 'index': company['id']}, 
                          color="warning", size="sm", className="me-1"),
                dbc.Button("Delete", id={'type': 'delete-company', 'index': company['id']}, 
                          color="danger", size="sm"),
            ])
        ])
        table_rows.append(row)
    
    table_body = [html.Tbody(table_rows)]
    
    return dbc.Table(table_header + table_body, bordered=True, hover=True, responsive=True, className="mb-0")

# Callback to handle company edit
@app.callback(
    [Output("editing-company-id", "data", allow_duplicate=True),
     Output("company-symbol", "value", allow_duplicate=True),
     Output("company-composition", "data", allow_duplicate=True),
     Output("company-form-collapse", "is_open", allow_duplicate=True)],
    [Input({'type': 'edit-company', 'index': dash.dependencies.ALL}, 'n_clicks')],
    [State("companies-store", "data")],
    prevent_initial_call=True
)
def handle_company_edit(edit_clicks, companies):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    # Handle edit button clicks - check if it's a real click
    if 'edit-company' in trigger_id and ctx.triggered[0]['value'] is not None:
        button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
        company_id = button_id['index']
        
        # Find the company to edit
        company_to_edit = next((e for e in companies if e['id'] == company_id), None)
        if company_to_edit:
            return (company_id, company_to_edit['symbol'], company_to_edit['domains'], True)
    
    return dash.no_update

# Callback to update portfolio overview
@app.callback(
    Output("portfolio-overview", "children"),
    [Input("domains-store", "data"), Input("companies-store", "data")]
)
def update_portfolio_overview(domains, companies):
    domain_count = len(domains)
    company_count = len(companies)
    total_domains_in_companies = sum(len(company['domains']) for company in companies)
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{domain_count}", className="card-title text-primary"),
                    html.P("Individual Domains", className="card-text")
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{company_count}", className="card-title text-success"),
                    html.P("Companies", className="card-text")
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{total_domains_in_companies}", className="card-title text-info"),
                    html.P("Total Domain Holdings in Companies", className="card-text")
                ])
            ])
        ], width=4),
    ])

if __name__ == "__main__":
    app.run(debug=True)