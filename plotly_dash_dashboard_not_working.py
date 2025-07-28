import dash
from dash import dcc, html, Input, Output, State, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sample data for charts
np.random.seed(42)
dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
analytics_data = pd.DataFrame({
    'date': dates,
    'users': np.random.randint(100, 1000, len(dates)),
    'revenue': np.random.randint(1000, 10000, len(dates)),
    'conversion_rate': np.random.uniform(0.02, 0.08, len(dates))
})

team_data = pd.DataFrame({
    'member': ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Eva Brown'],
    'tasks_completed': [23, 19, 31, 15, 27],
    'efficiency': [92, 88, 95, 82, 90]
})

# Custom CSS styles
custom_css = """
.header-container {
    background: white;
    box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
    border-bottom: 1px solid rgb(229 231 235);
    position: sticky;
    top: 0;
    z-index: 1000;
}

.logo-section {
    display: flex;
    align-items: center;
    gap: 12px;
}

.logo-text {
    font-size: 20px;
    font-weight: bold;
    color: #111827;
    text-decoration: none;
}

.nav-link {
    color: #374151;
    font-weight: 500;
    text-decoration: none;
    padding: 8px 16px;
    border-radius: 6px;
    transition: all 0.2s;
}

.nav-link:hover {
    color: #4f46e5;
    background-color: #f3f4f6;
}

.icon-button {
    padding: 8px;
    color: #6b7280;
    background: none;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
}

.icon-button:hover {
    color: #374151;
    background-color: #f3f4f6;
}

.notification-badge {
    position: absolute;
    top: -4px;
    right: -4px;
    width: 16px;
    height: 16px;
    background-color: #ef4444;
    color: white;
    border-radius: 50%;
    font-size: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.feature-card {
    background: white;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
    border: 1px solid rgb(229 231 235);
    transition: all 0.2s;
}

.feature-card:hover {
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.gradient-indigo {
    background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%);
    border-color: #c7d2fe;
}

.gradient-green {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    border-color: #bbf7d0;
}

.gradient-purple {
    background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
    border-color: #d8b4fe;
}

.main-content {
    background-color: #f9fafb;
    min-height: calc(100vh - 64px);
    padding: 32px 0;
}

.welcome-card {
    background: white;
    border-radius: 8px;
    padding: 32px;
    box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
    border: 1px solid rgb(229 231 235);
    margin-bottom: 32px;
}

.chart-card {
    background: white;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
    border: 1px solid rgb(229 231 235);
    margin-bottom: 24px;
}
"""

# Define the layout
app.layout = html.Div([
    # Custom CSS
    html.Style(custom_css),
    
    # Header
    html.Header([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    # Logo Section
                    html.Div([
                        html.A([
                            html.Img(
                                src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=indigo&shade=300",
                                style={'height': '32px', 'width': '32px'}
                            ),
                            html.Span("Your Company", className="logo-text")
                        ], href="#", className="logo-section", style={'textDecoration': 'none'})
                    ])
                ], width="auto"),
                
                dbc.Col([
                    # Navigation (Desktop)
                    html.Nav([
                        html.A("Dashboard", href="#", className="nav-link"),
                        html.A("Projects", href="#", className="nav-link"),
                        html.A("Team", href="#", className="nav-link"),
                        html.A("Calendar", href="#", className="nav-link"),
                    ], className="d-none d-md-flex align-items-center", style={'gap': '8px'})
                ], className="d-flex justify-content-center"),
                
                dbc.Col([
                    # Right Section
                    html.Div([
                        # Search Button
                        dbc.Button([
                            html.I(className="fas fa-search")
                        ], color="light", className="icon-button me-2", id="search-btn", outline=True),
                        
                        # Notifications Button
                        html.Div([
                            dbc.Button([
                                html.I(className="fas fa-bell")
                            ], color="light", className="icon-button", id="notifications-btn", outline=True),
                            html.Span("3", className="notification-badge")
                        ], style={'position': 'relative', 'display': 'inline-block'}),
                        
                        # Profile Dropdown
                        dbc.DropdownMenu([
                            dbc.DropdownMenuItem("Your Profile"),
                            dbc.DropdownMenuItem("Settings"),
                            dbc.DropdownMenuItem("Billing"),
                            dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem("Sign out"),
                        ], 
                        toggle_style={'border': 'none', 'background': 'none', 'padding': '8px'},
                        label=[
                            html.Img(
                                src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80",
                                style={'width': '32px', 'height': '32px', 'borderRadius': '50%', 'objectFit': 'cover'}
                            ),
                            html.I(className="fas fa-chevron-down ms-2", style={'fontSize': '12px'})
                        ],
                        className="ms-3")
                    ], className="d-flex align-items-center")
                ], width="auto")
            ], className="align-items-center justify-content-between", style={'height': '64px'})
        ], fluid=True)
    ], className="header-container"),
    
    # Search Bar (Collapsible)
    dbc.Collapse([
        html.Div([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.InputGroupText(html.I(className="fas fa-search")),
                            dbc.Input(placeholder="Search...", type="text")
                        ])
                    ], md=6, className="mx-auto")
                ])
            ])
        ], style={'background': '#f9fafb', 'borderTop': '1px solid #e5e7eb', 'padding': '12px 0'})
    ], id="search-collapse"),
    
    # Notifications Panel (Offcanvas)
    dbc.Offcanvas([
        html.H4("Notifications", className="mb-3"),
        html.Div([
            html.Div([
                html.Div([
                    html.Div(style={'width': '8px', 'height': '8px', 'backgroundColor': '#3b82f6', 'borderRadius': '50%'}),
                    html.Div([
                        html.P("New project assigned to you", className="mb-1", style={'fontSize': '14px'}),
                        html.Small("2 minutes ago", style={'color': '#6b7280'})
                    ], className="flex-grow-1")
                ], className="d-flex align-items-start", style={'gap': '12px'})
            ], className="p-3 border-bottom"),
            
            html.Div([
                html.Div([
                    html.Div(style={'width': '8px', 'height': '8px', 'backgroundColor': '#10b981', 'borderRadius': '50%'}),
                    html.Div([
                        html.P("Meeting reminder: Team standup", className="mb-1", style={'fontSize': '14px'}),
                        html.Small("15 minutes ago", style={'color': '#6b7280'})
                    ], className="flex-grow-1")
                ], className="d-flex align-items-start", style={'gap': '12px'})
            ], className="p-3 border-bottom"),
            
            html.Div([
                html.Div([
                    html.Div(style={'width': '8px', 'height': '8px', 'backgroundColor': '#f59e0b', 'borderRadius': '50%'}),
                    html.Div([
                        html.P("System maintenance scheduled", className="mb-1", style={'fontSize': '14px'}),
                        html.Small("1 hour ago", style={'color': '#6b7280'})
                    ], className="flex-grow-1")
                ], className="d-flex align-items-start", style={'gap': '12px'})
            ], className="p-3"),
            
            html.Hr(),
            dbc.Button("View all notifications", color="primary", outline=True, className="w-100")
        ])
    ], id="notifications-offcanvas", title="", placement="end", style={'width': '320px'}),
    
    # Main Content
    html.Main([
        dbc.Container([
            # Welcome Section
            html.Div([
                html.H1("Welcome to Your Dashboard", className="mb-3", style={'fontSize': '30px', 'fontWeight': 'bold', 'color': '#111827'}),
                html.P("This is a modern, responsive dashboard built with Python, Plotly, and Dash. Explore the interactive charts and features below!", 
                       className="mb-4", style={'color': '#6b7280'})
            ], className="welcome-card"),
            
            # Feature Cards
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-chart-bar", style={'fontSize': '32px', 'color': '#4f46e5'}),
                            html.H5("Analytics", className="ms-3", style={'color': '#312e81'})
                        ], className="d-flex align-items-center mb-3"),
                        html.P("Track your performance with detailed analytics and insights.", style={'color': '#4338ca'})
                    ], className="feature-card gradient-indigo")
                ], md=4, className="mb-4"),
                
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-users", style={'fontSize': '32px', 'color': '#059669'}),
                            html.H5("Team Management", className="ms-3", style={'color': '#064e3b'})
                        ], className="d-flex align-items-center mb-3"),
                        html.P("Collaborate effectively with your team members and manage projects.", style={'color': '#047857'})
                    ], className="feature-card gradient-green")
                ], md=4, className="mb-4"),
                
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-cog", style={'fontSize': '32px', 'color': '#7c3aed'}),
                            html.H5("Settings", className="ms-3", style={'color': '#581c87'})
                        ], className="d-flex align-items-center mb-3"),
                        html.P("Customize your experience with advanced settings and preferences.", style={'color': '#6d28d9'})
                    ], className="feature-card gradient-purple")
                ], md=4, className="mb-4")
            ]),
            
            # Charts Section
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("Analytics Overview", className="mb-3"),
                        dcc.Graph(id="analytics-chart")
                    ], className="chart-card")
                ], md=8),
                
                dbc.Col([
                    html.Div([
                        html.H4("Team Performance", className="mb-3"),
                        dcc.Graph(id="team-chart")
                    ], className="chart-card")
                ], md=4)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("Revenue Trends", className="mb-3"),
                        dcc.Graph(id="revenue-chart")
                    ], className="chart-card")
                ], md=6),
                
                dbc.Col([
                    html.Div([
                        html.H4("Conversion Rate", className="mb-3"),
                        dcc.Graph(id="conversion-chart")
                    ], className="chart-card")
                ], md=6)
            ])
        ], fluid=True)
    ], className="main-content"),
    
    # Font Awesome for icons
    html.Link(
        rel='stylesheet',
        href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    )
])

# Callbacks for interactivity
@app.callback(
    Output("search-collapse", "is_open"),
    Input("search-btn", "n_clicks"),
    State("search-collapse", "is_open"),
)
def toggle_search(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

@app.callback(
    Output("notifications-offcanvas", "is_open"),
    Input("notifications-btn", "n_clicks"),
    State("notifications-offcanvas", "is_open"),
)
def toggle_notifications(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

# Chart callbacks
@app.callback(
    Output("analytics-chart", "figure"),
    Input("analytics-chart", "id")  # Dummy input to trigger on load
)
def update_analytics_chart(_):
    fig = px.line(analytics_data.tail(30), x='date', y='users', 
                  title="Daily Active Users (Last 30 Days)",
                  color_discrete_sequence=['#4f46e5'])
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#374151',
        title_font_size=16,
        title_font_color='#111827'
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
    return fig

@app.callback(
    Output("team-chart", "figure"),
    Input("team-chart", "id")
)
def update_team_chart(_):
    fig = px.bar(team_data, x='tasks_completed', y='member', 
                 orientation='h',
                 title="Tasks Completed by Team Member",
                 color='efficiency',
                 color_continuous_scale='Viridis')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#374151',
        title_font_size=16,
        title_font_color='#111827',
        height=400
    )
    return fig

@app.callback(
    Output("revenue-chart", "figure"),
    Input("revenue-chart", "id")
)
def update_revenue_chart(_):
    monthly_revenue = analytics_data.groupby(analytics_data['date'].dt.to_period('M'))['revenue'].sum().reset_index()
    monthly_revenue['date'] = monthly_revenue['date'].astype(str)
    
    fig = px.area(monthly_revenue, x='date', y='revenue',
                  title="Monthly Revenue Trend",
                  color_discrete_sequence=['#059669'])
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#374151',
        title_font_size=16,
        title_font_color='#111827'
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
    return fig

@app.callback(
    Output("conversion-chart", "figure"),
    Input("conversion-chart", "id")
)
def update_conversion_chart(_):
    # Create a gauge chart for conversion rate
    avg_conversion = analytics_data['conversion_rate'].mean()
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = avg_conversion * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Average Conversion Rate (%)"},
        delta = {'reference': 5.0},
        gauge = {
            'axis': {'range': [None, 10]},
            'bar': {'color': "#7c3aed"},
            'steps': [
                {'range': [0, 2.5], 'color': "#fef3c7"},
                {'range': [2.5, 5], 'color': "#fde68a"},
                {'range': [5, 7.5], 'color': "#fcd34d"},
                {'range': [7.5, 10], 'color': "#f59e0b"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 7.5
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#374151',
        title_font_size=16,
        title_font_color='#111827',
        height=300
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8050)
