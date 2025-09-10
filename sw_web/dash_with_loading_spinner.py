import dash
from dash import dcc, html, Input, Output, callback, State, clientside_callback
import plotly.express as px
import pandas as pd
import numpy as np
import time

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

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout with Tailwind CSS
app.layout = html.Div([
    # Header with update button
    html.Div([
        html.Div([
            html.H1("Dashboard Analytics", className="text-3xl font-bold text-gray-800 mb-2"),
            html.P("Interactive data visualization with three tabs", className="text-gray-600")
        ], className="flex-1"),
        
        # Update button and status
        html.Div([
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
    
    # Tabs
    dcc.Tabs(id="tabs", value='tab-1', className="mb-6", children=[
        dcc.Tab(label='Overview', value='tab-1', className="px-4 py-2 font-semibold"),
        dcc.Tab(label='Charts', value='tab-2', className="px-4 py-2 font-semibold"),
        dcc.Tab(label='Data Table', value='tab-3', className="px-4 py-2 font-semibold"),
    ]),
    
    # Tab content
    html.Div(id='tabs-content', className="bg-white p-6 rounded-lg shadow-sm"),
    
    # Store components
    dcc.Store(id='data-store', data=df.to_dict('records')),
    dcc.Store(id='loading-state', data=False)
], className="min-h-screen bg-gray-50 p-6", id="main-container")

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
          Input('tabs', 'value'),
          Input('data-store', 'data'))
def render_content(tab, data):
    df = pd.DataFrame(data)
    
    # Convert Date column from string to datetime if needed
    if 'Date' in df.columns and df['Date'].dtype == 'object':
        try:
            df['Date'] = pd.to_datetime(df['Date'])
        except:
            pass
    
    if tab == 'tab-1':
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
            ], className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6"),
            
            # Quick summary
            html.Div([
                html.H3("Data Summary", className="text-xl font-semibold text-gray-800 mb-4"),
                html.P(f"Dataset contains {len(df)} records across {df['Category'].nunique()} categories."),
                html.P(f"Date range: {date_range}"),
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
            /* Ensure loading overlay appears above everything */
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