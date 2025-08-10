import dash
from dash import dcc, html, Input, Output, callback

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    # Tailwind CSS CDN
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
                    alt="Logo",
                    className="h-8 w-8 rounded"
                ),
                html.H1("Dash App", className="ml-3 text-xl font-bold text-white")
            ], className="flex items-center"),
            
            html.Nav([
                html.Ul([
                    html.Li(html.A("Home", href="#", className="px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700")),
                    html.Li(html.A("Dashboard", href="#", className="px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700")),
                    html.Li(html.A("Settings", href="#", className="px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700")),
                ], className="flex space-x-4")
            ])
        ], className="bg-blue-800 text-white px-4 py-3 flex justify-between items-center shadow-md z-10"),
        
        # Main content area with sidebar
        html.Div([
            # Left sidebar
            html.Aside([
                html.Nav([
                    html.Ul([
                        html.Li(html.A("Overview", href="#", className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-100 border-l-4 border-blue-500")),
                        html.Li(html.A("Analytics", href="#", className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-100 border-l-4 border-transparent hover:border-blue-300")),
                        html.Li(html.A("Reports", href="#", className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-100 border-l-4 border-transparent hover:border-blue-300")),
                        html.Li(html.A("Users", href="#", className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-100 border-l-4 border-transparent hover:border-blue-300")),
                        html.Li(html.A("Logs", href="#", className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-100 border-l-4 border-transparent hover:border-blue-300")),
                    ])
                ])
            ], className="bg-white w-64 shadow-lg h-[calc(100vh-64px)] fixed left-0 top-16 overflow-y-auto"),
            
            # Main content
            html.Main([
                html.Div([
                    html.H2("Welcome to the Dashboard", className="text-2xl font-bold mb-4"),
                    html.P("This is the main content area. You can add your Dash components here.", className="mb-6 text-gray-600"),
                    
                    # Example Dash component
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
                            }
                        },
                        className="bg-white p-4 rounded-lg shadow-md"
                    ),
                    
                    # Interactive component
                    html.Div([
                        dcc.Dropdown(
                            id='demo-dropdown',
                            options=[
                                {'label': 'New York City', 'value': 'NYC'},
                                {'label': 'Montreal', 'value': 'MTL'},
                                {'label': 'San Francisco', 'value': 'SF'}
                            ],
                            value='NYC',
                            className="w-full p-2 border rounded"
                        ),
                        html.Div(id='dd-output-container', className="mt-4 p-3 bg-blue-50 rounded")
                    ], className="mt-6")
                ], className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6")
            ], className="ml-64 pt-4 pb-12")
        ])
    ])
])

# Callback for dropdown interaction
@callback(
    Output('dd-output-container', 'children'),
    Input('demo-dropdown', 'value')
)
def update_output(value):
    return f'You have selected {value}'

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=9090)
