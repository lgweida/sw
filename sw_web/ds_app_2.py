import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[
    # Tailwind CSS via CDN
    "https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css",
    dbc.themes.BOOTSTRAP
])

# Top navigation bar (same as before)
top_nav = html.Nav(
    className="bg-white shadow-sm",
    children=[
        html.Div(
            className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
            children=[
                html.Div(
                    className="flex justify-between h-16",
                    children=[
                        # Logo
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
                        # Main navigation
                        html.Div(
                            className="hidden sm:ml-6 sm:flex sm:space-x-8",
                            children=[
                                dcc.Link("Products", href="#", className="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"),
                                dcc.Link("Solutions", href="#", className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"),
                                dcc.Link("Resources", href="#", className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"),
                                dcc.Link("Company", href="#", className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"),
                            ]
                        ),
                        # Right side buttons
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

# Dropdown options (from your JSON files)
categories = ["Traffic and Engagements", "Paid Search"]
time_periods = ["M/M % Change", "Q/Q % Change", "Y/Y % Change", "T3M", "Q/Q (T3M) % Change", "Y/Y (T3M) % Change"]
domains = ["adobe.com", "gemini.google.com", "www.google.com", "github.microsoft.com", "linkedin.microsoft.com", "oracal.com"]

# Main content with dropdown filters
main_content = html.Div(
    className="flex-1 overflow-auto focus:outline-none",
    children=[
        html.Div(
            className="pt-8 pb-12",
            children=[
                html.Div(
                    className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8",
                    children=[
                        # Title
                        html.H1(
                            "Website Analytics Dashboard",
                            className="text-3xl font-bold text-gray-900 text-center mb-8"
                        ),
                        
                        # Filters section
                        html.Div(
                            className="bg-white shadow rounded-lg p-6 mb-8",
                            children=[
                                html.H2(
                                    "Filters",
                                    className="text-xl font-semibold text-gray-900 mb-4"
                                ),
                                html.Div(
                                    className="grid grid-cols-1 md:grid-cols-3 gap-6",
                                    children=[
                                        # Category dropdown
                                        html.Div(
                                            className="space-y-2",
                                            children=[
                                                html.Label(
                                                    "Category",
                                                    className="block text-sm font-medium text-gray-700"
                                                ),
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
                                                html.Label(
                                                    "Time Period",
                                                    className="block text-sm font-medium text-gray-700"
                                                ),
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
                                                html.Label(
                                                    "Domains (Select multiple)",
                                                    className="block text-sm font-medium text-gray-700"
                                                ),
                                                dcc.Dropdown(
                                                    id='domains-dropdown',
                                                    options=[{'label': domain, 'value': domain} for domain in domains],
                                                    value=[domains[0]],  # Default to first domain
                                                    multi=True,
                                                    className="w-full"
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        
                        # Results section
                        html.Div(
                            className="bg-white shadow rounded-lg p-6",
                            children=[
                                html.H2(
                                    "Analytics Results",
                                    className="text-xl font-semibold text-gray-900 mb-4"
                                ),
                                html.Div(
                                    id='results-container',
                                    className="mt-4",
                                    children=[
                                        html.P(
                                            "Select filters above to view analytics data.",
                                            className="text-gray-500"
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

# App layout
app.layout = html.Div(
    className="h-screen flex flex-col",
    children=[
        top_nav,
        main_content
    ]
)

# Callback to update results based on filters
@app.callback(
    Output('results-container', 'children'),
    [Input('category-dropdown', 'value'),
     Input('timeperiod-dropdown', 'value'),
     Input('domains-dropdown', 'value')]
)
def update_results(category, time_period, selected_domains):
    return [
        html.H3(
            f"Selected Filters:",
            className="text-lg font-medium text-gray-900 mb-2"
        ),
        html.Ul(
            className="list-disc pl-5 mb-4",
            children=[
                html.Li(f"Category: {category}"),
                html.Li(f"Time Period: {time_period}"),
                html.Li(f"Domains: {', '.join(selected_domains)}")
            ]
        ),
        html.P(
            "This is where your analytics results would be displayed based on the selected filters.",
            className="text-gray-700"
        ),
        # You would replace this with your actual data visualization components
        html.Div(
            className="mt-6 p-4 bg-gray-100 rounded-lg",
            children=[
                html.P(
                    "Sample visualization area for the selected data.",
                    className="text-gray-600 text-center"
                )
            ]
        )
    ]

if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run(debug=True, host="0.0.0.0", port=9090)