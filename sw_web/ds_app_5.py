import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import numpy as np

# Initialize the Dash app with dark theme support
app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    dbc.icons.BOOTSTRAP
])

# Load JSON data from files dynamically
def load_json_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        with open(os.path.join(script_dir, 'domains.json'), 'r') as f:
            domains = json.load(f)
        with open(os.path.join(script_dir, 'timeperiod_cmp.json'), 'r') as f:
            time_periods = json.load(f)
        with open(os.path.join(script_dir, 'cat.json'), 'r') as f:
            categories = json.load(f)
        
        return domains, time_periods, categories
    
    except FileNotFoundError as e:
        print(f"Error loading JSON files: {e}")
        return (
            ["adobe.com", "gemini.google.com", "www.google.com", "github.microsoft.com", "linkedin.microsoft.com", "oracal.com"],
            ["M/M % Change", "Q/Q % Change", "Y/Y % Change", "T3M", "Q/Q (T3M) % Change", "Y/Y (T3M) % Change"],
            ["Traffic and Engagements", "Paid Search"]
        )

domains, time_periods, categories = load_json_data()

# Generate sample data for visualization
def generate_sample_data(selected_domains):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    date_range = pd.date_range(start_date, end_date, freq='M')
    
    data = []
    for domain in selected_domains:
        for date in date_range:
            visits = np.random.randint(10000, 50000)
            engagement = round(np.random.uniform(1.5, 5.0), 2)
            bounce_rate = round(np.random.uniform(0.2, 0.6), 2)
            
            data.append({
                'Date': date.strftime('%Y-%m'),
                'Domain': domain,
                'Visits': visits,
                'Engagement (min)': engagement,
                'Bounce Rate': bounce_rate,
                'Pages/Visit': round(np.random.uniform(2.0, 8.0), 1),
                'Conversion Rate': round(np.random.uniform(0.01, 0.05), 3)
            })
    
    return pd.DataFrame(data)

# Theme toggle switch component
def theme_switch(theme):
    return html.Div(
        [
            dbc.Label(className="fa fa-moon", html_for="theme-switch"),
            dbc.Switch(
                id="theme-switch",
                value=theme == "dark",
                className="d-inline-block ms-1",
            ),
            dbc.Label(className="fa fa-sun", html_for="theme-switch"),
        ],
        className="d-flex align-items-center",
        style={"marginLeft": "10px"}
    )

# Top navigation bar with theme toggle
def create_top_nav(theme):
    return dbc.Navbar(
        dbc.Container(
            [
                # Logo
                dbc.NavbarBrand(
                    html.Img(
                        src="https://www.anaconda.com/wp-content/uploads/2024/11/2020_Anaconda_Logo_RGB_Corporate.png",
                        height="30px",
                        className="me-2"
                    ),
                    href="/"
                ),
                
                # Main navigation links
                dbc.Nav(
                    [
                        dbc.NavLink("Products", href="#", active="exact"),
                        dbc.NavLink("Solutions", href="#", active="exact"),
                        dbc.NavLink("Resources", href="#", active="exact"),
                        dbc.NavLink("Company", href="#", active="exact"),
                    ],
                    className="me-auto",
                    navbar=True
                ),
                
                # Right side buttons
                dbc.Nav(
                    [
                        # Free Download button
                        dbc.Button(
                            "Free Download",
                            href="https://www.anaconda.com/download",
                            color="link",
                            className="me-2"
                        ),
                        
                        # Theme toggle
                        theme_switch(theme),
                        
                        # Get Demo button
                        dbc.Button(
                            "Get Demo",
                            href="https://www.anaconda.com/request-a-demo",
                            color="primary",
                            className="ms-2"
                        )
                    ],
                    navbar=True
                )
            ],
            fluid=True
        ),
        color="primary" if theme == "dark" else "light",
        dark=theme == "dark",
        className="mb-4"
    )

# Left sidebar with filters
def create_sidebar(theme):
    return dbc.Col(
        [
            dbc.Card(
                [
                    dbc.CardHeader("Filters", className="h5"),
                    dbc.CardBody(
                        [
                            # Category dropdown
                            dbc.Label("Category", className="mt-2"),
                            dcc.Dropdown(
                                id='category-dropdown',
                                options=[{'label': cat, 'value': cat} for cat in categories],
                                value=categories[0],
                                clearable=False,
                                className="mb-3"
                            ),
                            
                            # Time Period dropdown
                            dbc.Label("Time Period"),
                            dcc.Dropdown(
                                id='timeperiod-dropdown',
                                options=[{'label': tp, 'value': tp} for tp in time_periods],
                                value=time_periods[0],
                                clearable=False,
                                className="mb-3"
                            ),
                            
                            # Domains multi-select dropdown
                            dbc.Label("Domains (Select multiple)"),
                            dcc.Dropdown(
                                id='domains-dropdown',
                                options=[{'label': domain, 'value': domain} for domain in domains],
                                value=[domains[0]],
                                multi=True,
                                className="mb-3"
                            )
                        ]
                    )
                ],
                className="h-100"
            )
        ],
        md=3,
        className="pe-0"
    )

# Main content area
def create_main_content(theme):
    return dbc.Col(
        [
            # Current selections
            dbc.Card(
                [
                    dbc.CardHeader("Current Selections", className="h5"),
                    dbc.CardBody(
                        id='current-selections',
                        children=[
                            html.Ul(
                                className="list-unstyled",
                                children=[
                                    html.Li("Category: Traffic and Engagements"),
                                    html.Li("Time Period: M/M % Change"),
                                    html.Li("Domains: adobe.com")
                                ]
                            )
                        ]
                    )
                ],
                className="mb-4"
            ),
            
            # Results container
            html.Div(id='results-container')
        ],
        md=9
    )

# App layout
app.layout = dbc.Container(
    [
        dcc.Store(id='theme-store', storage_type='local'),
        html.Div(id='theme-container')
    ],
    fluid=True,
    className="dbc p-0",
    style={"minHeight": "100vh"}
)

# Theme container callback
@app.callback(
    Output('theme-container', 'children'),
    Input('theme-store', 'data'),
    prevent_initial_call=False
)
def update_theme(theme):
    theme = theme or "light"
    return [
        create_top_nav(theme),
        dbc.Container(
            dbc.Row(
                [
                    create_sidebar(theme),
                    create_main_content(theme)
                ],
                className="g-0"
            ),
            fluid=True,
            className="px-4"
        )
    ]

# Theme switch callback
@app.callback(
    Output('theme-store', 'data'),
    Input('theme-switch', 'value'),
    State('theme-store', 'data'),
    prevent_initial_call=True
)
def update_theme_store(switch_on, current_theme):
    return "dark" if switch_on else "light"

# Callback to update current selections
@app.callback(
    Output('current-selections', 'children'),
    [Input('category-dropdown', 'value'),
     Input('timeperiod-dropdown', 'value'),
     Input('domains-dropdown', 'value')]
)
def update_current_selections(category, time_period, selected_domains):
    if not selected_domains:
        return dbc.Alert("Please select at least one domain.", color="danger")
    
    return [
        html.Ul(
            className="list-unstyled",
            children=[
                html.Li(f"Category: {category}"),
                html.Li(f"Time Period: {time_period}"),
                html.Li(f"Domains: {', '.join(selected_domains)}")
            ]
        )
    ]

# Callback to update results based on filters
@app.callback(
    Output('results-container', 'children'),
    [Input('category-dropdown', 'value'),
     Input('timeperiod-dropdown', 'value'),
     Input('domains-dropdown', 'value')],
    Input('theme-store', 'data')
)
def update_results(category, time_period, selected_domains, theme):
    if not selected_domains:
        return dbc.Alert("Please select at least one domain.", color="danger")
    
    df = generate_sample_data(selected_domains)
    
    if category == "Traffic and Engagements":
        metrics = ['Visits', 'Engagement (min)', 'Pages/Visit', 'Bounce Rate']
    else:
        metrics = ['Visits', 'Conversion Rate', 'Pages/Visit', 'Bounce Rate']
    
    # Create visualizations with theme-appropriate colors
    line_color = "#636EFA" if theme == "light" else "#FECB52"
    bar_colors = px.colors.qualitative.Plotly if theme == "light" else px.colors.qualitative.Dark24
    
    fig1 = px.line(df, x='Date', y=metrics[0], color='Domain',
                 title=f"{metrics[0]} by Domain Over Time",
                 color_discrete_sequence=[line_color] if len(selected_domains) == 1 else bar_colors)
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='black' if theme == "light" else 'white'
    )
    
    latest_data = df[df['Date'] == df['Date'].max()]
    fig2 = px.bar(latest_data, x='Domain', y=metrics[0],
                 title=f"{metrics[0]} by Domain (Latest Period)",
                 color='Domain',
                 color_discrete_sequence=bar_colors)
    fig2.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='black' if theme == "light" else 'white'
    )
    
    # Create metric cards
    metric_cards = []
    for metric in metrics:
        avg_value = df[metric].mean()
        if metric == 'Bounce Rate' or metric == 'Conversion Rate':
            avg_value = f"{avg_value:.1%}"
        elif isinstance(avg_value, float):
            avg_value = f"{avg_value:.2f}"
        else:
            avg_value = f"{int(avg_value):,}"
        
        metric_cards.append(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(metric, className="h6"),
                        dbc.CardBody(
                            html.P(avg_value, className="card-text display-6")
                        )
                    ],
                    className="h-100"
                )
            )
        )
    
    # Create data table
    table = dash.dash_table.DataTable(
        id='data-table',
        columns=[{"name": col, "id": col} for col in df.columns],
        data=df.to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={
            'padding': '10px',
            'textAlign': 'left',
            'backgroundColor': 'transparent'
        },
        style_header={
            'backgroundColor': '#6c757d' if theme == "dark" else '#f8f9fa',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgba(0, 0, 0, 0.03)' if theme == "light" else 'rgba(255, 255, 255, 0.05)'
            }
        ]
    )
    
    return [
        dbc.Row(
            metric_cards,
            className="g-4 mb-4"
        ),
        
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(figure=fig1),
                    md=6
                ),
                dbc.Col(
                    dcc.Graph(figure=fig2),
                    md=6
                )
            ],
            className="g-4 mb-4"
        ),
        
        dbc.Card(
            [
                dbc.CardHeader("Detailed Data", className="h5"),
                dbc.CardBody(table)
            ]
        )
    ]

if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run(debug=True, host="0.0.0.0", port=9090)