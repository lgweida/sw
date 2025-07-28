import dash
from dash import dcc, html, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Initialize app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sample data
np.random.seed(42)
sales_data = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=100, freq='D'),
    'sales': np.random.randint(100, 1000, 100),
    'profit': np.random.randint(50, 500, 100),
    'category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home'], 100),
    'region': np.random.choice(['North', 'South', 'East', 'West'], 100)
})

# Navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard", href="#")),
        dbc.NavItem(dbc.NavLink("Analytics", href="#")),
        dbc.NavItem(dbc.NavLink("Reports", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Settings", href="#"),
                dbc.DropdownMenuItem("Profile", href="#"),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Logout", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="Menu",
        ),
    ],
    brand="📊 Sales Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
    className="mb-4"
)

# Cards for KPIs
def create_kpi_card(title, value, icon, color):
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.H2(value, className="text-nowrap"),
                    html.P(title, className="card-text")
                ], className="col"),
                html.Div([
                    html.I(className=f"fas {icon} fa-2x text-{color}")
                ], className="col-auto")
            ], className="row align-items-center")
        ])
    ], color=f"light", outline=True, className="mb-3")

# Modal for data details
modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Data Details")),
    dbc.ModalBody([
        html.P("This modal shows detailed information about the selected data point."),
        html.Div(id="modal-content")
    ]),
    dbc.ModalFooter(
        dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0)
    ),
], id="modal", is_open=False)

# Alert for notifications
alert = dbc.Alert(
    "Data updated successfully! 📈",
    id="alert",
    is_open=False,
    duration=3000,
    color="success",
    className="mb-3"
)

# Offcanvas for filters
offcanvas = dbc.Offcanvas([
    html.H4("Filters"),
    html.Hr(),
    
    # Date Range
    html.Label("Date Range", className="fw-bold"),
    dcc.DatePickerRange(
        id='date-range-filter',
        start_date=sales_data['date'].min(),
        end_date=sales_data['date'].max(),
        display_format='YYYY-MM-DD',
        className="mb-3"
    ),
    
    # Category Filter
    html.Label("Category", className="fw-bold"),
    dbc.Checklist(
        id="category-filter",
        options=[{"label": cat, "value": cat} for cat in sales_data['category'].unique()],
        value=list(sales_data['category'].unique()),
        className="mb-3"
    ),
    
    # Region Filter
    html.Label("Region", className="fw-bold"),
    dbc.RadioItems(
        id="region-filter",
        options=[{"label": "All Regions", "value": "all"}] + 
                [{"label": region, "value": region} for region in sales_data['region'].unique()],
        value="all",
        className="mb-3"
    ),
    
    # Sales Range
    html.Label("Sales Range", className="fw-bold"),
    dcc.RangeSlider(
        id='sales-range-slider',
        min=sales_data['sales'].min(),
        max=sales_data['sales'].max(),
        value=[sales_data['sales'].min(), sales_data['sales'].max()],
        marks={i: f'${i}' for i in range(0, 1001, 200)},
        className="mb-4"
    ),
    
    dbc.Button("Apply Filters", id="apply-filters", color="primary", className="w-100"),
    
], id="offcanvas", title="Filter Data", is_open=False)

# Main layout
app.layout = dbc.Container([
    navbar,
    alert,
    offcanvas,
    modal,
    
    # Top controls row
    dbc.Row([
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button("📊 Dashboard", color="primary", size="sm"),
                dbc.Button("📈 Analytics", color="outline-primary", size="sm"),
                dbc.Button("📋 Reports", color="outline-primary", size="sm"),
            ])
        ], width=6),
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button("🔍 Filters", id="open-offcanvas", color="info", size="sm"),
                dbc.Button("📥 Export", color="success", size="sm"),
                dbc.Button("🔄 Refresh", id="refresh-btn", color="warning", size="sm"),
            ], className="float-end")
        ], width=6)
    ], className="mb-4"),
    
    # KPI Cards
    dbc.Row([
        dbc.Col([
            create_kpi_card("Total Sales", "$2.4M", "fa-dollar-sign", "success")
        ], width=3),
        dbc.Col([
            create_kpi_card("Total Orders", "1,234", "fa-shopping-cart", "info")
        ], width=3),
        dbc.Col([
            create_kpi_card("Avg Order Value", "$432", "fa-chart-line", "warning")
        ], width=3),
        dbc.Col([
            create_kpi_card("Growth Rate", "+12.5%", "fa-arrow-up", "primary")
        ], width=3),
    ], className="mb-4"),
    
    # Charts Row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Sales Trend", className="mb-0"),
                    dbc.Button("ℹ️", id="open-modal", size="sm", color="link", className="float-end")
                ]),
                dbc.CardBody([
                    dcc.Graph(id="sales-chart")
                ])
            ])
        ], width=8),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Category Distribution", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id="category-chart")
                ])
            ])
        ], width=4),
    ], className="mb-4"),
    
    # Progress and Accordion Row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Monthly Targets", className="mb-0")),
                dbc.CardBody([
                    html.Label("Sales Target Progress"),
                    dbc.Progress(value=75, color="success", className="mb-3"),
                    html.Label("Profit Target Progress"),
                    dbc.Progress(value=60, color="warning", className="mb-3"),
                    html.Label("Customer Acquisition"),
                    dbc.Progress(value=90, color="info"),
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Accordion([
                dbc.AccordionItem([
                    html.P("Regional performance metrics and analysis for the current quarter."),
                    dbc.ListGroup([
                        dbc.ListGroupItem("North: $580K (+15%)", color="success"),
                        dbc.ListGroupItem("South: $420K (+8%)", color="info"),
                        dbc.ListGroupItem("East: $380K (-2%)", color="warning"),
                        dbc.ListGroupItem("West: $320K (-5%)", color="danger"),
                    ])
                ], title="Regional Performance"),
                
                dbc.AccordionItem([
                    html.P("Top performing products and categories."),
                    dbc.Badge("Electronics", color="primary", className="me-2"),
                    dbc.Badge("Clothing", color="success", className="me-2"),
                    dbc.Badge("Books", color="info", className="me-2"),
                    dbc.Badge("Home", color="warning"),
                ], title="Product Categories"),
                
                dbc.AccordionItem([
                    html.P("Recent alerts and notifications."),
                    dbc.Alert("Low inventory warning for Electronics", color="warning", className="mb-2"),
                    dbc.Alert("New high-value customer acquired", color="success"),
                ], title="Alerts & Notifications"),
            ], start_collapsed=True)
        ], width=6)
    ], className="mb-4"),
    
    # Data Table
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Recent Transactions", className="mb-0"),
                    dbc.InputGroup([
                        dbc.Input(id="search-input", placeholder="Search transactions..."),
                        dbc.InputGroupText("🔍")
                    ], size="sm", className="w-50 float-end")
                ]),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='transactions-table',
                        columns=[
                            {"name": "Date", "id": "date", "type": "datetime"},
                            {"name": "Sales", "id": "sales", "type": "numeric", "format": {"specifier": "$,.0f"}},
                            {"name": "Profit", "id": "profit", "type": "numeric", "format": {"specifier": "$,.0f"}},
                            {"name": "Category", "id": "category"},
                            {"name": "Region", "id": "region"},
                        ],
                        data=sales_data.head(10).to_dict('records'),
                        style_cell={'textAlign': 'left'},
                        style_data_conditional=[
                            {
                                'if': {'filter_query': '{profit} > 400'},
                                'backgroundColor': '#d4edda',
                                'color': 'black',
                            }
                        ],
                        page_size=10,
                        sort_action="native",
                        filter_action="native"
                    )
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Toast notifications
    html.Div([
        dbc.Toast(
            "This is a success message!",
            id="success-toast",
            header="Success",
            is_open=False,
            dismissable=True,
            icon="success",
            duration=4000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 9999},
        ),
    ]),
    
], fluid=True)

# Callbacks

# Toggle offcanvas
@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    State("offcanvas", "is_open"),
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

# Toggle modal
@app.callback(
    Output("modal", "is_open"),
    [Input("open-modal", "n_clicks"), Input("close-modal", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Update modal content
@app.callback(
    Output("modal-content", "children"),
    Input("open-modal", "n_clicks")
)
def update_modal_content(n_clicks):
    if n_clicks:
        return dbc.ListGroup([
            dbc.ListGroupItem(f"Total Data Points: {len(sales_data)}"),
            dbc.ListGroupItem(f"Date Range: {sales_data['date'].min().strftime('%Y-%m-%d')} to {sales_data['date'].max().strftime('%Y-%m-%d')}"),
            dbc.ListGroupItem(f"Average Sales: ${sales_data['sales'].mean():.0f}"),
            dbc.ListGroupItem(f"Average Profit: ${sales_data['profit'].mean():.0f}"),
        ])
    return "Click the info button to see details."

# Update charts based on filters
@app.callback(
    [Output("sales-chart", "figure"),
     Output("category-chart", "figure")],
    [Input("apply-filters", "n_clicks"),
     Input("date-range-filter", "start_date"),
     Input("date-range-filter", "end_date"),
     Input("category-filter", "value"),
     Input("region-filter", "value"),
     Input("sales-range-slider", "value")]
)
def update_charts(n_clicks, start_date, end_date, categories, region, sales_range):
    # Filter data
    filtered_data = sales_data.copy()
    
    if start_date and end_date:
        filtered_data = filtered_data[
            (filtered_data['date'] >= start_date) & 
            (filtered_data['date'] <= end_date)
        ]
    
    if categories:
        filtered_data = filtered_data[filtered_data['category'].isin(categories)]
    
    if region != "all":
        filtered_data = filtered_data[filtered_data['region'] == region]
    
    if sales_range:
        filtered_data = filtered_data[
            (filtered_data['sales'] >= sales_range[0]) & 
            (filtered_data['sales'] <= sales_range[1])
        ]
    
    # Sales trend chart
    sales_fig = px.line(
        filtered_data, 
        x='date', 
        y='sales',
        title='Sales Trend Over Time',
        template='plotly_white'
    )
    sales_fig.update_traces(line_color='#0d6efd')
    sales_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    # Category distribution chart
    category_data = filtered_data.groupby('category')['sales'].sum().reset_index()
    category_fig = px.pie(
        category_data, 
        values='sales', 
        names='category',
        title='Sales by Category',
        template='plotly_white',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    category_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return sales_fig, category_fig

# Show success toast on refresh
@app.callback(
    Output("success-toast", "is_open"),
    Input("refresh-btn", "n_clicks")
)
def show_toast(n_clicks):
    if n_clicks:
        return True
    return False

# Show alert on filter apply
@app.callback(
    Output("alert", "is_open"),
    Input("apply-filters", "n_clicks")
)
def show_alert(n_clicks):
    if n_clicks:
        return True
    return False

# Filter table based on search
@app.callback(
    Output("transactions-table", "data"),
    Input("search-input", "value")
)
def filter_table(search_value):
    if search_value:
        filtered_data = sales_data[
            sales_data['category'].str.contains(search_value, case=False, na=False) |
            sales_data['region'].str.contains(search_value, case=False, na=False)
        ].head(10)
        return filtered_data.to_dict('records')
    return sales_data.head(10).to_dict('records')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
