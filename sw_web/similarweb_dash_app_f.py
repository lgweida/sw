import dash
from dash import dcc, html, Input, Output, callback, State, clientside_callback
import plotly.express as px
import pandas as pd
import numpy as np
import time
import os
from datetime import datetime, timedelta

# Get the current working directory
current_dir = os.getcwd()
print(f"Current working directory: {current_dir}")

# Check if data file exists, if not create sample data
data_file = os.path.join(current_dir, "monthly_data.xlsx")
print(f"Data file path: {data_file}")

if not os.path.exists(data_file):
    # Create sample data
    np.random.seed(42)
    df = pd.DataFrame({
        'Category': ['A', 'B', 'C', 'D', 'E'] * 20,
        'Value': np.random.randn(100),
        'Date': pd.date_range('2023-01-01', periods=100, freq='D')
    })
    df.to_excel(data_file, index=False)
    print(f"Created sample data file: {data_file}")
else:
    print(f"Data file already exists: {data_file}")

# Function to load data from Excel
def load_data_from_excel():
    try:
        df = pd.read_excel(data_file)
        print(f"Loaded data from {data_file}, shape: {df.shape}")
        print(df)
        
        # Convert Date column from string to datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            print("Converted Date column to datetime")
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        # Return empty dataframe if there's an error
        return pd.DataFrame()

# Function to simulate API call and update Excel file
def update_data_via_api():
    try:
        # Simulate API call delay
        time.sleep(2)
        
        # Check if we already updated this month
        last_update_file = os.path.join(current_dir, "last_update.txt")
        current_month = datetime.now().strftime("%Y-%m")
        print(f"Current month: {current_month}")
        
        if os.path.exists(last_update_file):
            with open(last_update_file, 'r') as f:
                last_update_month = f.read().strip()
            print(f"Last update month: {last_update_month}")
            if last_update_month == current_month:
                return "already_updated", "Data already updated this month."
        
        # Load existing data
        if os.path.exists(data_file):
            existing_df = pd.read_excel(data_file)
            print(f"Existing data shape: {existing_df.shape}")
        else:
            existing_df = pd.DataFrame()
            print("No existing data file found")
        
        # Simulate API response - generate new monthly data
        new_month_data = pd.DataFrame({
            'Category': ['A', 'B', 'C', 'D', 'E'] * 4,
            'Value': np.random.randn(20),
            'Date': pd.date_range(datetime.now().replace(day=1), periods=20, freq='D')
        })
        print(f"New monthly data shape: {new_month_data.shape}")
        
        # Combine with existing data
        if not existing_df.empty:
            updated_df = pd.concat([existing_df, new_month_data], ignore_index=True)
        else:
            updated_df = new_month_data
        
        # Save to Excel
        updated_df.to_excel(data_file, index=False)
        print(f"Saved updated data to {data_file}, shape: {updated_df.shape}")
        
        # Record update time
        with open(last_update_file, 'w') as f:
            f.write(current_month)
        print(f"Recorded update time: {current_month}")
        
        return "success", f"Data updated successfully for {current_month}! Added {len(new_month_data)} new records."
    
    except Exception as e:
        print(f"Error in update_data_via_api: {e}")
        return "error", f"Error updating data: {str(e)}"

# Initialize the Dash app
app = dash.Dash(__name__)

# Load initial data
initial_df = load_data_from_excel()
print(f"Initial data shape: {initial_df.shape}")

# Define the layout with Tailwind CSS
app.layout = html.Div([
    # Header with update button
    html.Div([
        html.Div([
            html.H1("Monthly Data Analytics", className="text-3xl font-bold text-gray-800 mb-2"),
            html.P("Data updated monthly from API", className="text-gray-600")
        ], className="flex-1"),
        
        # Update button and status
        html.Div([
            html.Button(
                "Update Monthly Data", 
                id="update-button", 
                n_clicks=0,
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            ),
            html.Div(id="update-status", className="ml-4 text-sm")
        ], className="flex items-center")
    ], className="bg-white p-6 shadow-sm mb-6 flex justify-between items-center"),
    
    # Last update info
    html.Div(id="last-update-info", className="bg-blue-50 p-4 rounded-lg mb-6"),
    
    # File info
    html.Div(id="file-info", className="bg-gray-50 p-4 rounded-lg mb-6"),
    
    # Loading overlay (initially hidden)
    html.Div(
        id="loading-overlay",
        className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 hidden",
        children=[
            html.Div(
                className="bg-white p-6 rounded-lg shadow-lg text-center",
                children=[
                    html.Div("Updating monthly data...", className="text-lg font-semibold mb-2"),
                    html.Div("Calling API and updating Excel file", className="text-gray-600")
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
    
    # Store component to keep track of the data
    dcc.Store(id='data-store', data=initial_df.to_dict('records')),
    
    # Store to track update attempts
    dcc.Store(id='update-attempts', data=0),
    
    # Store to track loading state
    dcc.Store(id='loading-state', data=False),
    
    # Interval component to check for data updates
    dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0)  # Check every minute
], className="min-h-screen bg-gray-50 p-6", id="main-container")

# Clientside callback to handle cursor change
clientside_callback(
    """
    function(loading) {
        if (loading) {
            document.body.style.cursor = 'wait';
            document.getElementById('update-button').style.cursor = 'wait';
            document.getElementById('main-container').style.cursor = 'wait';
            return 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50';
        } else {
            document.body.style.cursor = 'default';
            document.getElementById('update-button').style.cursor = 'pointer';
            document.getElementById('main-container').style.cursor = 'default';
            return 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 hidden';
        }
    }
    """,
    Output('loading-overlay', 'className'),
    Input('loading-state', 'data'),
    prevent_initial_call=True
)

# Callback to update file info
@callback(
    Output('file-info', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_file_info(n_intervals):
    file_exists = os.path.exists(data_file)
    file_size = os.path.getsize(data_file) if file_exists else 0
    file_time = datetime.fromtimestamp(os.path.getmtime(data_file)).strftime('%Y-%m-%d %H:%M:%S') if file_exists else "N/A"
    
    return html.Div([
        html.Span("File: ", className="font-semibold"),
        html.Span(f"{data_file}", className="text-blue-600"),
        html.Span(" | ", className="mx-2"),
        html.Span("Exists: ", className="font-semibold"),
        html.Span(f"{'Yes' if file_exists else 'No'}", className="text-green-600" if file_exists else "text-red-600"),
        html.Span(" | ", className="mx-2"),
        html.Span("Size: ", className="font-semibold"),
        html.Span(f"{file_size} bytes", className="text-purple-600"),
        html.Span(" | ", className="mx-2"),
        html.Span("Modified: ", className="font-semibold"),
        html.Span(f"{file_time}", className="text-gray-600")
    ])

# Callback to update last update info
@callback(
    Output('last-update-info', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('data-store', 'data')
)
def update_last_update_info(n_intervals, data):
    last_update_file = os.path.join(current_dir, "last_update.txt")
    if os.path.exists(last_update_file):
        with open(last_update_file, 'r') as f:
            last_update_month = f.read().strip()
        return html.Div([
            html.Span("Last update: ", className="font-semibold"),
            html.Span(f"{last_update_month}", className="text-blue-600"),
            html.Span(" | ", className="mx-2"),
            html.Span("Total records: ", className="font-semibold"),
            html.Span(f"{len(data)}", className="text-green-600")
        ])
    else:
        return html.Div([
            html.Span("No monthly updates yet. ", className="font-semibold"),
            html.Span("Click 'Update Monthly Data' to fetch the first month.", className="text-gray-600")
        ])

# Callback to update data and loading state
@app.callback(
    [Output('data-store', 'data'),
     Output('update-attempts', 'data'),
     Output('loading-state', 'data'),
     Output('update-status', 'children')],
    Input('update-button', 'n_clicks'),
    [State('update-attempts', 'data'),
     State('loading-state', 'data')],
    prevent_initial_call=True
)
def update_monthly_data(n_clicks, attempts, loading):
    if n_clicks > 0 and not loading:
        # Set loading state to true
        loading = True
        
        # Show loading status
        status = html.Span("Calling API to fetch monthly data...", className="text-blue-600")
        
        # Call the API and update Excel file
        result, message = update_data_via_api()
        
        # Load updated data
        if result == "success":
            updated_df = load_data_from_excel()
            status = html.Span(message, className="text-green-600")
            loading = False
            return updated_df.to_dict('records'), attempts + 1, loading, status
        elif result == "already_updated":
            status = html.Span(message, className="text-yellow-600")
            loading = False
            return dash.no_update, attempts + 1, loading, status
        else:  # error
            status = html.Span(message, className="text-red-600")
            loading = False
            return dash.no_update, attempts + 1, loading, status
    
    return dash.no_update, attempts, loading, ""

# Helper function to safely format dates
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

# Callback to update tab content
@callback(Output('tabs-content', 'children'),
          Input('tabs', 'value'),
          Input('data-store', 'data'))
def render_content(tab, data):
    if not data:
        return html.Div("No data available. Please update monthly data.", className="text-center text-gray-500 p-8")
    
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
            html.H2("Monthly Data Overview", className="text-2xl font-bold text-gray-800 mb-6"),
            
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
        # Ensure Date column is datetime for plotting
        if 'Date' in df.columns and df['Date'].dtype == 'object':
            try:
                df['Date'] = pd.to_datetime(df['Date'])
            except:
                pass
                
        return html.Div([
            html.H2("Monthly Data Visualization", className="text-2xl font-bold text-gray-800 mb-6"),
            
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
                
                # Scatter plot (only if Date is datetime)
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
            html.H2("Monthly Data Table", className="text-2xl font-bold text-gray-800 mb-6"),
            
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
                            html.Th("Index", className="px-4 py-2 border-b"),
                            html.Th("Category", className="px-4 py-2 border-b"),
                            html.Th("Value", className="px-4 py-2 border-b"),
                            html.Th("Date", className="px-4 py-2 border-b")
                        ], className="bg-gray-50")
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td(i, className="px-4 py-2 border-b"),
                            html.Td(row['Category'], className="px-4 py-2 border-b"),
                            html.Td(f"{row['Value']:.2f}", className="px-4 py-2 border-b"),
                            html.Td(safe_date_format(row['Date']), className="px-4 py-2 border-b")
                        ], className="hover:bg-gray-50") for i, row in df.head(10).iterrows()
                    ])
                ], className="w-full border-collapse border")
            ], className="bg-white p-4 rounded-lg shadow-sm overflow-x-auto"),
            
            # Summary
            html.Div([
                html.P(f"Showing 1 to 10 of {len(df)} entries", className="text-sm text-gray-600 mt-4")
            ])
        ])

# Add Tailwind CSS and custom CSS for cursor
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
            body.waiting, body.waiting * {
                cursor: wait !important;
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