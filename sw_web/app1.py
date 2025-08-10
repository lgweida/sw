import dash
from dash import dcc, html, Input, Output, callback
# Initialize the Dash app with proper meta tags for responsiveness
app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}]
)
server = app.server  # For deployment compatibility

app.layout = html.Div([
    # Tailwind CSS CDN - properly formatted
    html.Link(
        href="https://cdn.tailwindcss.com",
        rel="stylesheet"
    ),
    
    # Main container
    html.Div([
        # Top navigation bar
        html.Header([
            html.Div([
                html.Img(
                    src="https://picsum.photos/40/40", 
                    alt="Dashboard Logo",  # Accessible alt text
                    className="h-8 w-8 rounded object-cover"  # Ensure proper image rendering
                ),
                html.H1("Dash App", className="ml-3 text-xl font-bold text-white")
            ], className="flex items-center"),
            
            html.Nav([
                html.Ul([
                    html.Li(html.A("Home", href="#", className="px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors")),
                    html.Li(html.A("Dashboard", href="#", className="px-3 py-2 rounded-md text-sm font-medium bg-blue-700")),  # Active page indicator
                    html.Li(html.A("Settings", href="#", className="px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors")),
                ], className="flex space-x-4")
            ])
        ], className="bg-blue-800 text-white px-4 py-3 flex justify-between items-center shadow-md z-10"),
        
        # Main content area with sidebar
        html.Div([
            # Left sidebar - fixed positioning with proper spacing
            html.Aside([
                html.Nav([
                    html.Ul([
                        html.Li(html.A("Overview", href="#", className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-100 border-l-4 border-blue-500")),
                        html.Li(html.A("Analytics", href="#", className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-100 border-l-4 border-transparent hover:border-blue-300")),
                        html.Li(html.A("Reports", href="#", className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-100 border-l-4 border-transparent hover:border-blue-300")),
                        html.Li(html.A("Users", href="#", className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-100 border-l-4 border-transparent hover:border-blue-300")),
                        html.Li(html.A("Logs", href="#", className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-100 border-l-4 border-transparent hover:border-blue-300")),
                    ], className="space-y-1")  # Better spacing between menu items
                ])
            ], className="bg-white w-64 shadow-lg h-[calc(100vh-64px)] fixed left-0 top-16 overflow-y-auto"),
            
            # Main content - properly offset from sidebar
            html.Main([
                html.Div([
                    html.H2("Welcome to the Dashboard", className="text-2xl font-bold mb-4"),
                    html.P("This is the main content area. You can add your Dash components here.", className="mb-6 text-gray-600"),
                    
                    # Example Dash component with improved styling
                    dcc.Graph(
                        id='example-graph',
                        figure={
                            'data': [
                                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'Series 1'},
                                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'Series 2'},
                            ],
                            'layout': {
                                'title': 'Sample Bar Chart',
                                'paper_bgcolor': 'rgba(0,0,0,0)',
                                'plot_bgcolor': 'rgba(0,0,0,0)',
                                'height': 400,  # Consistent sizing
                                'margin': {'l': 40, 'r': 40, 't': 60, 'b': 40}  # Better spacing
                            }
                        },
                        className="bg-white p-4 rounded-lg shadow-md w-full"
                    ),
                    
                    # Interactive component with improved UX
                    html.Div([
                        dcc.Dropdown(
                            id='demo-dropdown',
                            options=[
                                {'label': 'New York City', 'value': 'NYC'},
                                {'label': 'Montreal', 'value': 'MTL'},
                                {'label': 'San Francisco', 'value': 'SF'}
                            ],
                            value='NYC',
                            clearable=False,  # Prevent accidental clearing
                            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        ),
                        html.Div(id='dd-output-container', className="mt-4 p-3 bg-blue-50 rounded")
                    ], className="mt-6 w-full max-w-md")  # Restrict width for better readability
                ], className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6")
            ], className="ml-64 pt-4 pb-12 min-h-screen bg-gray-50")  # Better background and spacing
        ])
    ])
])

# Callback for dropdown interaction with type hinting
@callback(
    Output('dd-output-container', 'children'),
    Input('demo-dropdown', 'value')
)
def update_output(value: str) -> str:
    """Update the output based on dropdown selection"""
    if value:  # Add basic validation
        return f'You have selected {value}'
    return "Please select a city from the dropdown"

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=9090)