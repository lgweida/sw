import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import numpy as np

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[
    "https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css",
    dbc.themes.BOOTSTRAP
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

# Top navigation bar
top_nav = html.Nav(
    className="bg-white shadow-sm",
    children=[
        html.Div(
            className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
            children=[
                html.Div(
                    className="flex justify-between h-16",
                    children=[
                        html.Div(
                            className="flex-shrink-0 flex items-center",
                            children=[
                                html.Img(
                                    className="h-8 w-auto",
                                    src="https://www.anaconda.com/wp-content/uploads/2024/11/2020_Anaconda_Logo_RGB_Corporate.png",
                                    alt="Anaconda Logo"
                                )
                            ]
                        ),
                        html.Div(
                            className="hidden sm:ml-6 sm:flex sm:space-x-8",
                            children=[
                                dcc.Link("Products", href="#", className="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"),
                                dcc.Link("Solutions", href="#", className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"),
                                dcc.Link("Resources", href="#", className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"),
                                dcc.Link("Company", href="#", className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"),
                            ]
                        ),
                        html.Div(
                            className="hidden sm:ml-6 sm:flex sm:items-center space-x-4",
                            children=[
                                dcc.Link(
                                    "Free Download",
                                    href="https://www.anaconda.com/download",
                                    className="bg-white text-indigo-600 px-4 py-2 rounded-md text-sm font-medium border border-indigo-600 hover:bg-indigo-50"
                                ),
                                dcc.Link(
                                    "Sign In",
                                    href="https://auth.anaconda.com/ui/login",
                                    className="bg-white text-gray-500 px-4 py-2 rounded-md text-sm font-medium hover:text-gray-700"
                                ),
                                dcc.Link(
                                    "Get Demo",
                                    href="https://www.anaconda.com/request-a-demo",
                                    className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# Left sidebar with filters
sidebar = html.Div(
    className="hidden md:flex md:flex-shrink-0",
    children=[
        html.Div(
            className="flex flex-col w-64 border-r border-gray-200 bg-white",
            children=[
                html.Div(
                    className="h-0 flex-1 flex flex-col pt-5 pb-4 overflow-y-auto",
                    children=[
                        html.Div(
                            className="flex-1 px-4 space-y-4",
                            children=[
                                html.H3("Filters", className="text-lg font-medium text-gray-900"),
                                
                                # Category dropdown
                                html.Div(
                                    className="space-y-2",
                                    children=[
                                        html.Label("Category", className="block text-sm font-medium text-gray-700"),
                                        dcc.Dropdown(
                                            id='category-dropdown',
                                            options=[{'label': cat, 'value': cat} for cat in categories],
                                            value=categories[0],
                                            clearable=False,
                                            className="w-full"
                                        )
                                    ]
                                ),
                                
                                # Time Period dropdown
                                html.Div(
                                    className="space-y-2",
                                    children=[
                                        html.Label("Time Period", className="block text-sm font-medium text-gray-700"),
                                        dcc.Dropdown(
                                            id='timeperiod-dropdown',
                                            options=[{'label': tp, 'value': tp} for tp in time_periods],
                                            value=time_periods[0],
                                            clearable=False,
                                            className="w-full"
                                        )
                                    ]
                                ),
                                
                                # Domains multi-select dropdown
                                html.Div(
                                    className="space-y-2",
                                    children=[
                                        html.Label("Domains (Select multiple)", className="block text-sm font-medium text-gray-700"),
                                        dcc.Dropdown(
                                            id='domains-dropdown',
                                            options=[{'label': domain, 'value': domain} for domain in domains],
                                            value=[domains[0]],
                                            multi=True,
                                            className="w-full"
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# Main content area
main_content = html.Div(
    className="flex-1 overflow-auto focus:outline-none",
    children=[
        html.Div(
            className="pt-8 pb-12",
            children=[
                html.Div(
                    className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8",
                    children=[
                        # Title and current selections
                        html.Div(
                            className="mb-8",
                            children=[
                                html.H1(
                                    "Website Analytics Dashboard",
                                    className="text-3xl font-bold text-gray-900 mb-2"
                                ),
                                html.Div(
                                    id='current-selections',
                                    className="bg-blue-50 rounded-lg p-4",
                                    children=[
                                        html.H3("Current Selections", className="text-lg font-semibold text-blue-800 mb-2"),
                                        html.Ul(
                                            className="list-disc pl-5",
                                            children=[
                                                html.Li("Category: Traffic and Engagements", className="text-blue-700"),
                                                html.Li("Time Period: M/M % Change", className="text-blue-700"),
                                                html.Li("Domains: adobe.com", className="text-blue-700")
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        
                        # Results section
                        html.Div(
                            id='results-container',
                            className="space-y-6"
                        )
                    ]
                )
            ]
        )
    ]
)

# App layout
app.layout = html.Div(
    className="h-screen flex flex-col",
    children=[
        top_nav,
        html.Div(
            className="flex flex-1 overflow-hidden",
            children=[
                sidebar,
                main_content
            ]
        )
    ]
)

# Callback to update current selections
@app.callback(
    Output('current-selections', 'children'),
    [Input('category-dropdown', 'value'),
     Input('timeperiod-dropdown', 'value'),
     Input('domains-dropdown', 'value')]
)
def update_current_selections(category, time_period, selected_domains):
    if not selected_domains:
        return html.Div("Please select at least one domain.", className="text-red-500")
    
    return [
        html.H3("Current Selections", className="text-lg font-semibold text-blue-800 mb-2"),
        html.Ul(
            className="list-disc pl-5",
            children=[
                html.Li(f"Category: {category}", className="text-blue-700"),
                html.Li(f"Time Period: {time_period}", className="text-blue-700"),
                html.Li(f"Domains: {', '.join(selected_domains)}", className="text-blue-700")
            ]
        )
    ]

# Callback to update results based on filters
@app.callback(
    Output('results-container', 'children'),
    [Input('category-dropdown', 'value'),
     Input('timeperiod-dropdown', 'value'),
     Input('domains-dropdown', 'value')]
)
def update_results(category, time_period, selected_domains):
    if not selected_domains:
        return html.Div("Please select at least one domain.", className="text-red-500")
    
    df = generate_sample_data(selected_domains)
    
    if category == "Traffic and Engagements":
        metrics = ['Visits', 'Engagement (min)', 'Pages/Visit', 'Bounce Rate']
    else:
        metrics = ['Visits', 'Conversion Rate', 'Pages/Visit', 'Bounce Rate']
    
    # Create visualizations
    fig1 = px.line(df, x='Date', y=metrics[0], color='Domain',
                  title=f"{metrics[0]} by Domain Over Time",
                  labels={metrics[0]: metrics[0]})
    fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    
    latest_data = df[df['Date'] == df['Date'].max()]
    fig2 = px.bar(latest_data, x='Domain', y=metrics[0],
                 title=f"{metrics[0]} by Domain (Latest Period)",
                 color='Domain')
    fig2.update_layout(showlegend=False, plot_bgcolor='white', paper_bgcolor='white')
    
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
            html.Div(
                className="bg-white shadow rounded-lg p-4",
                children=[
                    html.H3(metric, className="text-sm font-medium text-gray-500"),
                    html.P(avg_value, className="mt-1 text-2xl font-semibold text-gray-900")
                ]
            )
        )
    
    table = dash.dash_table.DataTable(
        id='data-table',
        columns=[{"name": col, "id": col} for col in df.columns],
        data=df.to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={
            'padding': '10px',
            'textAlign': 'left',
            'border': '1px solid #e5e7eb'
        },
        style_header={
            'backgroundColor': '#f3f4f6',
            'fontWeight': 'bold'
        }
    )
    
    return [
        html.Div(
            className="grid grid-cols-1 md:grid-cols-4 gap-4",
            children=metric_cards
        ),
        
        html.Div(
            className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6",
            children=[
                dcc.Graph(figure=fig1, className="bg-white p-4 shadow rounded-lg"),
                dcc.Graph(figure=fig2, className="bg-white p-4 shadow rounded-lg")
            ]
        ),
        
        html.Div(
            className="mt-6 bg-white shadow rounded-lg p-4",
            children=[
                html.H3("Detailed Data", className="text-lg font-semibold text-gray-900 mb-4"),
                table
            ]
        )
    ]

if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run(debug=True, host="0.0.0.0", port=9090)