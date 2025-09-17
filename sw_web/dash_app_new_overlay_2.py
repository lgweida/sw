import dash
from dash import dcc, html, Input, Output, callback, State, clientside_callback
import plotly.express as px
import pandas as pd
import numpy as np
import time
import os
import threading
from datetime import datetime, timedelta
from flask import Flask
import shutil

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
        
        # Convert Date column from string to datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            print("Converted Date column to datetime")
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        # Return empty dataframe if there's an error
        return pd.DataFrame()

# Global variables for background task management
background_task_running = False
background_task_result = None
background_task_message = ""
background_task_start_time = None

# Helper functions for monthly update
def is_monthly_update_done():
    """Check if monthly update was already performed"""
    last_update_file = os.path.join(current_dir, "last_update.txt")
    current_month = datetime.now().strftime("%Y-%m")
    
    if os.path.exists(last_update_file):
        with open(last_update_file, 'r') as f:
            last_update_month = f.read().strip()
        return last_update_month == current_month
    return False

def is_api_data_available():
    """Check if API data is available"""
    # Simulate API availability check with 90% success rate
    return np.random.random() > 0.1  # 90% chance of success

def api_data_letter():
    """Call API data letter function"""
    try:
        # Simulate API call with 80% success rate
        time.sleep(2)  # Simulate API call delay
        return np.random.random() > 0.2  # 80% chance of success
    except Exception as e:
        print(f"API call failed: {e}")
        return False

def backup_master_excel():
    """Create backup of master Excel file"""
    try:
        # Create backups directory if it doesn't exist
        backups_dir = os.path.join(current_dir, "backups")
        if not os.path.exists(backups_dir):
            os.makedirs(backups_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backups_dir, f'monthly_data_backup_{timestamp}.xlsx')
        shutil.copy2(data_file, backup_file)
        print(f"Backup created: {backup_file}")
        return True
    except Exception as e:
        print(f"Backup failed: {e}")
        return False

def update_master_excel():
    """Update master Excel file with new data"""
    try:
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
        return True
    except Exception as e:
        print(f"Update master Excel failed: {e}")
        return False

def restart_reload_master_excel():
    """Restart and reload master Excel file"""
    # In a Dash app, we don't need to restart anything
    # The data will be reloaded when the callback triggers
    print("Data reload scheduled")
    return True

def monthly_update_handler():
    """Main monthly update handler function"""
    global background_task_message
    
    # Check if monthly update is already done
    if is_monthly_update_done():
        background_task_message = "Monthly update already completed"
        print("Monthly update already completed")
        return "already_updated"
   
    background_task_message = "Checking API data availability..."
    time.sleep(1)
    
    # Check if API data is available
    if not is_api_data_available():
        background_task_message = "API data not available"
        print("API data not available")
        return "api_unavailable"
   
    background_task_message = "Calling API data letter..."
    time.sleep(2)
    
    # Call API data letter function
    success = api_data_letter()
   
    if success:
        background_task_message = "Creating backup of master Excel..."
        time.sleep(1)
        
        # Backup master Excel file
        if not backup_master_excel():
            background_task_message = "Backup failed"
            return "backup_failed"
        
        background_task_message = "Updating master Excel file..."
        time.sleep(2)
        
        # Update master Excel file
        if not update_master_excel():
            background_task_message = "Update failed"
            return "update_failed"
        
        background_task_message = "Finalizing update..."
        time.sleep(1)
        
        # Record update time
        last_update_file = os.path.join(current_dir, "last_update.txt")
        current_month = datetime.now().strftime("%Y-%m")
        with open(last_update_file, 'w') as f:
            f.write(current_month)
        
        # Restart and reload master Excel file
        restart_reload_master_excel()
        
        background_task_message = f"Monthly update completed successfully for {current_month}"
        print("Monthly update completed successfully")
        return "success"
    else:
        background_task_message = "API data letter call failed"
        print("API data letter call failed")
        return "api_failed"

# Function to simulate API call and update Excel file (runs in background)
def update_data_via_api_background():
    global background_task_running, background_task_result, background_task_message, background_task_start_time
    
    try:
        # Record start time
        background_task_start_time = datetime.now()
        
        # Call the monthly update handler
        result = monthly_update_handler()
        
        # Set the result based on the handler's return value
        if result == "success":
            background_task_result = "success"
        elif result == "already_updated":
            background_task_result = "already_updated"
        else:
            background_task_result = "error"
            
    except Exception as e:
        print(f"Error in update_data_via_api: {e}")
        background_task_result = "error"
        background_task_message = f"Error updating data: {str(e)}"
    finally:
        background_task_running = False

# Initialize the Dash app
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

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
                className="bg-blue-500 hover:bg-blue-700 disabled:bg-blue-300 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
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
                className="bg-white p-6 rounded-lg shadow-lg text-center min-w-96 max-w-md",
                children=[
                    # Time display with eclipse-like progress
                    html.Div(
                        className="text-4xl font-mono font-bold text-blue-600 mb-4",
                        id="time-eclipse-display"
                    ),
                    html.Div("Updating monthly data...", className="text-lg font-semibold mb-2 text-gray-800"),
                    html.Div("Background process running", className="text-gray-600 mb-4"),
                    
                    # Progress steps (like Adobe download process)
                    html.Div([
                        html.Div([
                            html.Span("1", className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-800 text-xs font-bold mr-2"),
                            html.Span("Checking monthly update status", className="text-sm", id="step-1-text"),
                            html.Span("✓", className="ml-2 text-green-500 hidden", id="step-1-check")
                        ], className="flex items-center mb-2", id="step-1"),
                        
                        html.Div([
                            html.Span("2", className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-gray-100 text-gray-800 text-xs font-bold mr-2"),
                            html.Span("Checking API availability", className="text-sm", id="step-2-text"),
                            html.Span("✓", className="ml-2 text-green-500 hidden", id="step-2-check")
                        ], className="flex items-center mb-2", id="step-2"),
                        
                        html.Div([
                            html.Span("3", className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-gray-100 text-gray-800 text-xs font-bold mr-2"),
                            html.Span("Calling API data letter", className="text-sm", id="step-3-text"),
                            html.Span("✓", className="ml-2 text-green-500 hidden", id="step-3-check")
                        ], className="flex items-center mb-2", id="step-3"),
                        
                        html.Div([
                            html.Span("4", className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-gray-100 text-gray-800 text-xs font-bold mr-2"),
                            html.Span("Backing up data", className="text-sm", id="step-4-text"),
                            html.Span("✓", className="ml-2 text-green-500 hidden", id="step-4-check")
                        ], className="flex items-center mb-2", id="step-4"),
                        
                        html.Div([
                            html.Span("5", className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-gray-100 text-gray-800 text-xs font-bold mr-2"),
                            html.Span("Updating master Excel", className="text-sm", id="step-5-text"),
                            html.Span("✓", className="ml-2 text-green-500 hidden", id="step-5-check")
                        ], className="flex items-center", id="step-5"),
                    ], className="text-left mb-4", id="progress-steps"),
                    
                    # Progress display
                    html.Div(id="progress-message", className="text-sm text-blue-600 font-medium mb-3"),
                    
                    # Progress indicator with dots that animate
                    html.Div([
                        html.Span("●", className="text-blue-500 mx-1 animate-pulse", id="dot-1"),
                        html.Span("●", className="text-blue-500 mx-1 animate-pulse delay-150", id="dot-2"),
                        html.Span("●", className="text-blue-500 mx-1 animate-pulse delay-300", id="dot-3"),
                    ], className="text-2xl"),
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
    dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0),  # Check every minute
    
    # Interval component to update time display during loading
    dcc.Interval(id='time-update-interval', interval=100, n_intervals=0, disabled=True),
    
    # Interval to check background task status
    dcc.Interval(id='task-check-interval', interval=1000, n_intervals=0, disabled=True)
], className="min-h-screen bg-gray-50 p-6", id="main-container")

# Callback to update progress steps based on elapsed time
@callback(
    [Output('step-1', 'className'),
     Output('step-2', 'className'),
     Output('step-3', 'className'),
     Output('step-4', 'className'),
     Output('step-5', 'className'),
     Output('step-1-check', 'className'),
     Output('step-2-check', 'className'),
     Output('step-3-check', 'className'),
     Output('step-4-check', 'className'),
     Output('step-5-check', 'className'),
     Output('step-1-text', 'className'),
     Output('step-2-text', 'className'),
     Output('step-3-text', 'className'),
     Output('step-4-text', 'className'),
     Output('step-5-text', 'className')],
    Input('time-update-interval', 'n_intervals'),
    State('loading-state', 'data')
)
def update_progress_steps(n_intervals, loading):
    if not loading or not background_task_start_time:
        # Reset all steps to inactive state
        return (["flex items-center mb-2"] * 5 + 
                ["ml-2 text-green-500 hidden"] * 5 +
                ["text-sm"] * 5)
    
    elapsed = (datetime.now() - background_task_start_time).total_seconds()
    
    # Define step completion thresholds (in seconds)
    step_thresholds = [2, 4, 6, 8, 10]
    
    # Determine which steps are completed
    steps_completed = [elapsed >= threshold for threshold in step_thresholds]
    
    # Generate class names based on completion status
    step_classes = []
    check_classes = []
    text_classes = []
    
    for i, completed in enumerate(steps_completed):
        if completed:
            step_classes.append("flex items-center mb-2")
            check_classes.append("ml-2 text-green-500")
            text_classes.append("text-sm font-medium text-green-700")
        else:
            step_classes.append("flex items-center mb-2")
            check_classes.append("ml-2 text-green-500 hidden")
            text_classes.append("text-sm")
    
    return step_classes + check_classes + text_classes

# Callback to update progress message with more detailed information
@callback(
    Output('progress-message', 'children'),
    Input('time-update-interval', 'n_intervals'),
    State('loading-state', 'data')
)
def update_progress_message(n_intervals, loading):
    if not loading or not background_task_start_time:
        return ""
    
    elapsed = datetime.now() - background_task_start_time
    elapsed_seconds = int(elapsed.total_seconds())
    
    # Show the current task message
    return html.Div([
        html.Div(f"Status: {background_task_message}", className="font-semibold"),
        html.Div(f"Elapsed: {elapsed_seconds}s", className="text-xs text-gray-500 mt-1")
    ])

# Callback to update time display with eclipse-like effect
@callback(
    Output('time-eclipse-display', 'children'),
    Input('time-update-interval', 'n_intervals'),
    State('loading-state', 'data')
)
def update_time_eclipse(n_intervals, loading):
    if not loading:
        return ""
    
    now = datetime.now()
    current_time = now.strftime('%H:%M:%S')
    milliseconds = now.microsecond // 1000
    
    # Create eclipse-like effect by alternating between different time formats
    if milliseconds < 250:
        # Normal time display
        return current_time
    elif milliseconds < 500:
        # Partial eclipse - show with dimmed opacity
        return html.Span(current_time, className="opacity-70")
    elif milliseconds < 750:
        # Full eclipse - show with very dim opacity
        return html.Span(current_time, className="opacity-40")
    else:
        # Coming out of eclipse
        return html.Span(current_time, className="opacity-70")

# Fixed clientside callback to handle cursor change and loading overlay
clientside_callback(
    """
    function(loading) {
        const loadingOverlay = document.getElementById('loading-overlay');
        const updateButton = document.getElementById('update-button');
        const mainContainer = document.getElementById('main-container');
        const timeInterval = document.getElementById('time-update-interval');
        const taskInterval = document.getElementById('task-check-interval');
        
        if (loading) {
            // Show loading cursor
            document.body.classList.add('loading-cursor');
            mainContainer.classList.add('loading-cursor');
            
            // Show loading overlay
            loadingOverlay.classList.remove('hidden');
            
            // Disable button
            updateButton.disabled = true;
            
            // Enable time update interval if it exists
            if (timeInterval) {
                timeInterval.disabled = false;
            }
            
            // Enable task check interval if it exists
            if (taskInterval) {
                taskInterval.disabled = false;
            }
            
            return 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50';
        } else {
            // Remove loading cursor
            document.body.classList.remove('loading-cursor');
            mainContainer.classList.remove('loading-cursor');
            
            // Hide loading overlay
            loadingOverlay.classList.add('hidden');
            
            // Enable button
            updateButton.disabled = false;
            
            // Disable time update interval if it exists
            if (timeInterval) {
                timeInterval.disabled = true;
            }
            
            // Disable task check interval if it exists
            if (taskInterval) {
                taskInterval.disabled = true;
            }
            
            return 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 hidden';
        }
    }
    """,
    Output('loading-overlay', 'className'),
    Input('loading-state', 'data'),
    prevent_initial_call=True
)

# Combined callback to handle both button click and task checking
@app.callback(
    [Output('data-store', 'data', allow_duplicate=True),
     Output('update-attempts', 'data', allow_duplicate=True),
     Output('loading-state', 'data', allow_duplicate=True),
     Output('update-status', 'children', allow_duplicate=True),
     Output('time-update-interval', 'disabled', allow_duplicate=True),
     Output('task-check-interval', 'disabled', allow_duplicate=True)],
    [Input('update-button', 'n_clicks'),
     Input('task-check-interval', 'n_intervals')],
    [State('update-attempts', 'data'),
     State('loading-state', 'data')],
    prevent_initial_call=True
)
def handle_update_and_check(n_clicks, n_intervals, attempts, loading):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    global background_task_running, background_task_result, background_task_message, background_task_start_time
    
    if trigger_id == 'update-button' and n_clicks > 0 and not loading:
        # Start background task
        print(f"Starting background update process for click #{n_clicks}")
        
        # Reset background task variables
        background_task_running = True
        background_task_result = None
        background_task_message = "Starting background process..."
        background_task_start_time = None
        
        # Start background thread
        thread = threading.Thread(target=update_data_via_api_background)
        thread.daemon = True
        thread.start()
        
        # Set loading state and show loading message
        loading_status = html.Div([
            html.Span(
                className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500 inline-block mr-2"
            ),
            html.Span("Starting background process...", className="text-blue-600")
        ])
        
        # Return loading state first and enable time interval
        return dash.no_update, dash.no_update, True, loading_status, False, False
    
    elif trigger_id == 'task-check-interval' and not background_task_running and background_task_result is not None:
        # Task completed
        if background_task_result == "success":
            updated_df = load_data_from_excel()
            status = html.Div([
                html.Span("✅", className="mr-2"),
                html.Span(background_task_message, className="text-green-600")
            ])
            print("Background task successful, returning data")
            return updated_df.to_dict('records'), attempts + 1, False, status, True, True
        elif background_task_result == "already_updated":
            status = html.Div([
                html.Span("ℹ️", className="mr-2"),
                html.Span(background_task_message, className="text-yellow-600")
            ])
            print("Data already updated this month")
            return dash.no_update, attempts + 1, False, status, True, True
        else:  # error or other status
            status = html.Div([
                html.Span("❌", className="mr-2"),
                html.Span(background_task_message, className="text-red-600")
            ])
            print("Background task failed")
            return dash.no_update, attempts + 1, False, status, True, True
    
    # Task still running or no relevant trigger, continue checking
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, False, False

# Callback to update file info
@callback(
    Output('file-info', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_file_info(n_intervals):
    file_exists = os.path.exists(data_file)
    file_size = os.path.getsize(data_file) if file_exists else 0
    file_time = datetime.fromtimestamp(os.path.getmtime(data_file)).strftime('%Y-%m-%d %H:%M:%S') if file_exists else "N/A"
    
    # Check if backups directory exists
    backups_dir = os.path.join(current_dir, "backups")
    backups_exist = os.path.exists(backups_dir) and len(os.listdir(backups_dir)) > 0 if os.path.exists(backups_dir) else False
    
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
        html.Span(f"{file_time}", className="text-gray-600"),
        html.Span(" | ", className="mx-2"),
        html.Span("Backups: ", className="font-semibold"),
        html.Span(f"{'Available' if backups_exist else 'None'}", className="text-green-600" if backups_exist else "text-gray-600")
    ])

# Callback to update last update info - triggers immediately on data changes
@callback(
    Output('last-update-info', 'children'),
    [Input('data-store', 'data'),        # Primary trigger - data changes
     Input('interval-component', 'n_intervals')]  # Secondary trigger - periodic update
)
def update_last_update_info(data, n_intervals):
    last_update_file = os.path.join(current_dir, "last_update.txt")
    current_month = datetime.now().strftime("%Y-%m")
    
    if os.path.exists(last_update_file):
        with open(last_update_file, 'r') as f:
            last_update_month = f.read().strip()
            
        # Check if it's current month
        is_current_month = last_update_month == current_month
        month_status = "✅ Current month" if is_current_month else "⏳ Previous month"
        month_color = "text-green-600" if is_current_month else "text-yellow-600"
        
        return html.Div([
            html.Div([
                html.Span("Last update: ", className="font-semibold"),
                html.Span(f"{last_update_month}", className="text-blue-600 mr-2"),
                html.Span(f"({month_status})", className=f"{month_color} text-sm"),
            ], className="mb-2"),
            html.Div([
                html.Span("Total records: ", className="font-semibold"),
                html.Span(f"{len(data) if data else 0:,}", className="text-green-600 mr-4"),
                html.Span("Current month: ", className="font-semibold"),
                html.Span(f"{current_month}", className="text-gray-600")
            ])
        ])
    else:
        return html.Div([
            html.Div([
                html.Span("⚠️ No monthly updates yet", className="font-semibold text-orange-600"),
            ], className="mb-2"),
            html.Div([
                html.Span("Click 'Update Monthly Data' to fetch data for ", className="text-gray-600"),
                html.Span(f"{current_month}", className="font-semibold text-blue-600")
            ])
        ])

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
                            html.Th("Index", className="px-4 py-2 bg-gray-50 font-medium text-gray-500 uppercase tracking-wider border-b border-gray-200"),
                            html.Th("Category", className="px-4 py-2 bg-gray-50 font-medium text-gray-500 uppercase tracking-wider border-b border-gray-200"),
                            html.Th("Value", className="px-4 py-2 bg-gray-50 font-medium text-gray-500 uppercase tracking-wider border-b border-gray-200"),
                            html.Th("Date", className="px-4 py-2 bg-gray-50 font-medium text-gray-500 uppercase tracking-wider border-b border-gray-200")
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td(i, className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-200"),
                            html.Td(row['Category'], className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-200"),
                            html.Td(f"{row['Value']:.2f}", className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-200"),
                            html.Td(safe_date_format(row['Date']), className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-200")
                        ], className="hover:bg-gray-50") for i, row in df.head(10).iterrows()
                    ])
                ], className="min-w-full divide-y divide-gray-200")
            ], className="bg-white rounded-lg shadow ring-1 ring-black ring-opacity-5 overflow-hidden"),
            
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
                        },
                        animation: {
                            'pulse': 'pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                        }
                    }
                }
            }
        </script>
        <style>
            .loading-cursor, .loading-cursor * {
                cursor: wait !important;
            }
            
            /* Ensure loading overlay appears above everything */
            .z-50 {
                z-index: 50;
            }
            
            /* Smooth transitions */
            .transition-colors {
                transition-property: background-color, border-color, color, fill, stroke;
                transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
                transition-duration: 200ms;
            }
            
            /* Custom animation delays */
            .delay-150 {
                animation-delay: 150ms;
            }
            .delay-300 {
                animation-delay: 300ms;
            }
            
            /* Step animation */
            @keyframes step-pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .step-active {
                animation: step-pulse 2s infinite;
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