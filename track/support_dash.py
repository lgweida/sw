import dash
from dash import dcc, html, Input, Output, callback, dash_table, State
import pandas as pd
import datetime
import sqlite3
import json
from datetime import datetime as dt
import uuid

# Initialize the Dash app
app = dash.Dash(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('support_activities.db')
    c = conn.cursor()
    
    # Create activities table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id TEXT PRIMARY KEY,
            date TEXT,
            title TEXT,
            category TEXT,
            details TEXT,
            links TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    # Create some sample data if the table is empty
    c.execute("SELECT COUNT(*) FROM activities")
    if c.fetchone()[0] == 0:
        sample_activities = [
            (
                str(uuid.uuid4()),
                '2023-10-15',
                'FIX Session Configuration',
                'Onboarding',
                'Configured FIX session parameters for new client. Used encryption and compression settings.',
                'https://www.fixtrading.org/online-specification/\nhttps://internalwiki/onboarding-checklist',
                dt.now().isoformat(),
                dt.now().isoformat()
            ),
            (
                str(uuid.uuid4()),
                '2023-10-16',
                'Production Issue Troubleshooting',
                'Troubleshooting',
                'Investigated order routing issue between client and exchange. Found misconfigured gateway.',
                'https://internalwiki/troubleshooting-guide\nhttps://internalwiki/gateway-configuration',
                dt.now().isoformat(),
                dt.now().isoformat()
            ),
            (
                str(uuid.uuid4()),
                '2023-10-17',
                'UAT Test Cases',
                'Testing',
                'Executed test cases for new order types. Verified execution reports and confirmations.',
                'https://internalwiki/uat-process\nhttps://internalwiki/order-types',
                dt.now().isoformat(),
                dt.now().isoformat()
            )
        ]
        c.executemany('''
            INSERT INTO activities (id, date, title, category, details, links, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_activities)
    
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Function to get activities from database
def get_activities():
    conn = sqlite3.connect('support_activities.db')
    df = pd.read_sql_query("SELECT * FROM activities ORDER BY date DESC", conn)
    conn.close()
    return df

# Function to add or update an activity
def save_activity(activity_id, date, title, category, details, links):
    conn = sqlite3.connect('support_activities.db')
    c = conn.cursor()
    now = dt.now().isoformat()
    
    if activity_id:  # Update existing activity
        c.execute('''
            UPDATE activities 
            SET date=?, title=?, category=?, details=?, links=?, updated_at=?
            WHERE id=?
        ''', (date, title, category, details, links, now, activity_id))
    else:  # Insert new activity
        activity_id = str(uuid.uuid4())
        c.execute('''
            INSERT INTO activities (id, date, title, category, details, links, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (activity_id, date, title, category, details, links, now, now))
    
    conn.commit()
    conn.close()
    return activity_id

# Function to delete an activity
def delete_activity(activity_id):
    conn = sqlite3.connect('support_activities.db')
    c = conn.cursor()
    c.execute('DELETE FROM activities WHERE id=?', (activity_id,))
    conn.commit()
    conn.close()

# Function to get an activity by ID
def get_activity(activity_id):
    conn = sqlite3.connect('support_activities.db')
    c = conn.cursor()
    c.execute('SELECT * FROM activities WHERE id=?', (activity_id,))
    activity = c.fetchone()
    conn.close()
    
    if activity:
        return {
            'id': activity[0],
            'date': activity[1],
            'title': activity[2],
            'category': activity[3],
            'details': activity[4],
            'links': activity[5],
            'created_at': activity[6],
            'updated_at': activity[7]
        }
    return None

# Quick links for top navigation
quick_links = [
    {'name': 'FIX Protocol Spec', 'url': 'https://www.fixtrading.org/'},
    {'name': 'Internal Wiki', 'url': 'https://www.example.com/wiki'},
    {'name': 'Trading Dashboard', 'url': 'https://www.example.com/trading'},
    {'name': 'Issue Tracker', 'url': 'https://www.example.com/issues'}
]

# Common procedures for reference
common_procedures = [
    {
        'title': 'FIX Session Setup',
        'steps': [
            'Obtain client FIX specification document',
            'Configure session parameters (SenderCompID, TargetCompID)',
            'Set up encryption and compression if required',
            'Coordinate session testing with client',
            'Document all settings in client profile'
        ]
    },
    {
        'title': 'Production Issue Troubleshooting',
        'steps': [
            'Gather details: timestamp, client, order ID, symptoms',
            'Check system logs for errors',
            'Verify session connectivity status',
            'Examine message sequence numbers',
            'Escalate to development if needed'
        ]
    }
]

# App layout
app.layout = html.Div([
    # Store for current activity being edited
    dcc.Store(id='current-activity', data={'id': None}),
    
    # Top Navigation Bar
    html.Div([
        html.Div([
            html.H1("FIX Support Tracker", className="text-xl font-bold text-white"),
            html.Div([
                html.A(link['name'], href=link['url'], className="text-blue-100 hover:text-white px-3 py-2 rounded-md text-sm font-medium", target="_blank")
                for link in quick_links
            ], className="flex space-x-4")
        ], className="flex items-center justify-between flex-wrap")
    ], className="bg-gradient-to-r from-blue-800 to-purple-800 p-4 shadow-lg"),
    
    # Main Content Area
    html.Div([
        # Left Navigation Sidebar
        html.Div([
            html.Div([
                html.H2("Daily Activities", className="text-lg font-semibold text-gray-700 mb-4"),
                html.Div([
                    dcc.Input(
                        id='search-activities',
                        type='text',
                        placeholder='Search activities...',
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
                    ),
                    html.Button(
                        "Clear Search", 
                        id='clear-search',
                        className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-md shadow-sm mb-4"
                    )
                ]),
                html.Ul(id='activities-sidebar', className="divide-y divide-gray-200")
            ], className="bg-white rounded-lg shadow-sm p-4 mb-6"),
            
            html.Div([
                html.H2("Categories", className="text-lg font-semibold text-gray-700 mb-4"),
                html.Ul([
                    html.Li([html.A("Onboarding", href="#", className="text-gray-700 hover:text-blue-600 block px-4 py-2 text-sm")]),
                    html.Li([html.A("Troubleshooting", href="#", className="text-gray-700 hover:text-blue-600 block px-4 py-2 text-sm")]),
                    html.Li([html.A("Testing", href="#", className="text-gray-700 hover:text-blue-600 block px-4 py-2 text-sm")]),
                    html.Li([html.A("Meetings", href="#", className="text-gray-700 hover:text-blue-600 block px-4 py-2 text-sm")]),
                    html.Li([html.A("Documentation", href="#", className="text-gray-700 hover:text-blue-600 block px-4 py-2 text-sm")])
                ], className="space-y-1")
            ], className="bg-white rounded-lg shadow-sm p-4")
        ], className="w-1/4 pr-4"),
        
        # Main Content
        html.Div([
            # Welcome Banner
            html.Div([
                html.H2("Daily Support Activities", className="text-2xl font-bold text-gray-800"),
                html.P("Track your FIX trading support tasks, issues, and solutions", className="text-gray-600")
            ], className="mb-6"),
            
            # Add/Edit Activity Section
            html.Div([
                html.H3("Add New Activity", className="text-lg font-semibold text-gray-700 mb-4"),
                html.Div([
                    html.Div([
                        html.Label("Date", className="block text-sm font-medium text-gray-700"),
                        dcc.DatePickerSingle(
                            id='activity-date',
                            date=dt.now().date(),
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 py-2"
                        )
                    ], className="col-span-1"),
                    
                    html.Div([
                        html.Label("Title", className="block text-sm font-medium text-gray-700"),
                        dcc.Input(
                            id='activity-title',
                            type='text',
                            placeholder='E.g., Client onboarding session',
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 py-2"
                        )
                    ], className="col-span-1"),
                    
                    html.Div([
                        html.Label("Category", className="block text-sm font-medium text-gray-700"),
                        dcc.Dropdown(
                            id='activity-category',
                            options=[
                                {'label': 'Onboarding', 'value': 'Onboarding'},
                                {'label': 'Troubleshooting', 'value': 'Troubleshooting'},
                                {'label': 'Testing', 'value': 'Testing'},
                                {'label': 'Meetings', 'value': 'Meetings'},
                                {'label': 'Documentation', 'value': 'Documentation'}
                            ],
                            className="mt-1"
                        )
                    ], className="col-span-1"),
                    
                    html.Div([
                        html.Label("Details", className="block text-sm font-medium text-gray-700"),
                        dcc.Textarea(
                            id='activity-details',
                            placeholder='Describe the activity, issues faced, and solutions...',
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 py-2",
                            rows=3
                        )
                    ], className="col-span-2"),
                    
                    html.Div([
                        html.Label("Related Links (one per line)", className="block text-sm font-medium text-gray-700"),
                        dcc.Textarea(
                            id='activity-links',
                            placeholder='https://example.com/resource1\nhttps://example.com/resource2',
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 py-2",
                            rows=2
                        )
                    ], className="col-span-2"),
                    
                    html.Div([
                        html.Button("Save Activity", id='save-activity-button', 
                                   className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md shadow-sm mr-2"),
                        html.Button("Clear Form", id='clear-form-button', 
                                   className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-md shadow-sm"),
                        html.Div(id='save-status', className="inline-block ml-4 text-sm text-green-600")
                    ], className="col-span-2 mt-4")
                ], className="grid grid-cols-2 gap-4")
            ], className="bg-white rounded-lg shadow-sm p-6 mb-6"),
            
            # Activity List
            html.Div([
                html.Div([
                    html.H3("Recent Activities", className="text-lg font-semibold text-gray-700"),
                    html.Button(
                        "Refresh", 
                        id='refresh-activities',
                        className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-1 px-3 rounded-md shadow-sm text-sm"
                    )
                ], className="flex justify-between items-center mb-4"),
                html.Div(id='activities-list')
            ]),
            
            # Common Procedures Section
            html.Div([
                html.H3("Common Procedures", className="text-lg font-semibold text-gray-700 mb-4"),
                html.Div([
                    html.Div([
                        html.H4(proc['title'], className="text-md font-medium text-gray-900 mb-2"),
                        html.Ol([
                            html.Li(step, className="text-gray-600 text-sm mb-1 ml-4")
                            for step in proc['steps']
                        ], className="list-decimal")
                    ], className="bg-gray-50 p-4 rounded-lg mb-4")
                    for proc in common_procedures
                ])
            ], className="mt-8")
        ], className="w-3/4")
    ], className="flex p-6 bg-gray-100 min-h-screen")
], className="antialiased text-gray-800")

# Callback to populate the sidebar with activities
@app.callback(
    Output('activities-sidebar', 'children'),
    [Input('search-activities', 'value'),
     Input('clear-search', 'n_clicks'),
     Input('refresh-activities', 'n_clicks')]
)
def update_sidebar(search_term, clear_clicks, refresh_clicks):
    df_activities = get_activities()
    
    # Filter activities if search term is provided
    if search_term:
        mask = df_activities['title'].str.contains(search_term, case=False) | \
               df_activities['details'].str.contains(search_term, case=False) | \
               df_activities['category'].str.contains(search_term, case=False)
        df_activities = df_activities[mask]
    
    # Create sidebar items
    sidebar_items = []
    for _, activity in df_activities.iterrows():
        sidebar_items.append(
            html.Li([
                html.Div([
                    html.Span(dt.strptime(activity['date'], '%Y-%m-%d').strftime('%b %d'), 
                             className="text-xs font-medium text-blue-600"),
                    html.P(activity['title'], className="text-sm font-medium text-gray-900 truncate"),
                    html.Span(activity['category'], className="text-xs text-gray-500"),
                    html.Div([
                        html.Button("Edit", 
                                   id={'type': 'edit-button', 'index': activity['id']},
                                   className="text-xs text-blue-600 hover:text-blue-800 mr-2"),
                        html.Button("Delete", 
                                   id={'type': 'delete-button', 'index': activity['id']},
                                   className="text-xs text-red-600 hover:text-red-800")
                    ], className="mt-1")
                ], className="px-4 py-3 hover:bg-gray-100 cursor-pointer", 
                   id={'type': 'activity-item', 'index': activity['id']})
            ])
        )
    
    return sidebar_items

# Callback to populate the main activities list
@app.callback(
    Output('activities-list', 'children'),
    [Input('refresh-activities', 'n_clicks'),
     Input('search-activities', 'value')]
)
def update_activities_list(refresh_clicks, search_term):
    df_activities = get_activities()
    
    # Filter activities if search term is provided
    if search_term:
        mask = df_activities['title'].str.contains(search_term, case=False) | \
               df_activities['details'].str.contains(search_term, case=False) | \
               df_activities['category'].str.contains(search_term, case=False)
        df_activities = df_activities[mask]
    
    activities = []
    for _, activity in df_activities.iterrows():
        # Parse links if they exist
        links_html = html.Div()
        if activity['links']:
            links = activity['links'].split('\n')
            links_html = html.Div([
                html.P("Related Links:", className="text-sm font-medium text-gray-700 mt-3"),
                html.Ul([
                    html.Li([
                        html.A(link, href=link, className="text-blue-600 hover:text-blue-800 text-sm", target="_blank")
                    ]) for link in links if link.strip()
                ], className="list-disc ml-5")
            ])
        
        activities.append(
            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span(activity['category'], 
                                     className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"),
                            html.Span(activity['date'], className="ml-2 text-sm text-gray-500"),
                            html.Span(f"Updated: {dt.fromisoformat(activity['updated_at']).strftime('%Y-%m-%d %H:%M')}", 
                                     className="ml-4 text-xs text-gray-400")
                        ], className="flex items-center"),
                        html.H4(activity['title'], className="text-lg font-medium text-gray-900 mt-1"),
                        html.P(activity['details'], className="mt-2 text-gray-600"),
                        links_html,
                        html.Div([
                            html.Button("Edit", 
                                       id={'type': 'edit-button', 'index': activity['id']},
                                       className="text-blue-600 hover:text-blue-800 text-sm font-medium mr-3"),
                            html.Button("Delete", 
                                       id={'type': 'delete-button', 'index': activity['id']},
                                       className="text-red-600 hover:text-red-800 text-sm font-medium")
                        ], className="mt-3")
                    ], className="p-4")
                ], className="bg-white rounded-lg shadow-sm border border-gray-200 mb-4")
            ], id={'type': 'activity-display', 'index': activity['id']})
        )
    
    return activities

# Callback to handle activity selection for editing
@app.callback(
    [Output('current-activity', 'data'),
     Output('activity-date', 'date'),
     Output('activity-title', 'value'),
     Output('activity-category', 'value'),
     Output('activity-details', 'value'),
     Output('activity-links', 'value')],
    [Input({'type': 'edit-button', 'index': dash.dependencies.ALL}, 'n_clicks')],
    [State({'type': 'edit-button', 'index': dash.dependencies.ALL}, 'id')],
    prevent_initial_call=True
)
def edit_activity(n_clicks, button_ids):
    if not any(n_clicks):
        return dash.no_update
    
    # Find which button was clicked
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id:
        button_id = json.loads(button_id)
        activity_id = button_id['index']
        
        # Get the activity from database
        activity = get_activity(activity_id)
        if activity:
            return (
                {'id': activity_id},
                activity['date'],
                activity['title'],
                activity['category'],
                activity['details'],
                activity['links']
            )
    
    return dash.no_update

# Callback to save activity
@app.callback(
    [Output('save-status', 'children'),
     Output('save-status', 'className')],
    [Input('save-activity-button', 'n_clicks')],
    [State('current-activity', 'data'),
     State('activity-date', 'date'),
     State('activity-title', 'value'),
     State('activity-category', 'value'),
     State('activity-details', 'value'),
     State('activity-links', 'value')],
    prevent_initial_call=True
)
def save_activity_callback(n_clicks, current_activity, date, title, category, details, links):
    if n_clicks:
        if not all([date, title, category, details]):
            return "Please fill in all required fields", "inline-block ml-4 text-sm text-red-600"
        
        # Save the activity
        activity_id = save_activity(
            current_activity['id'] if current_activity else None,
            date,
            title,
            category,
            details,
            links
        )
        
        if current_activity and current_activity['id']:
            return "Activity updated successfully!", "inline-block ml-4 text-sm text-green-600"
        else:
            return "Activity saved successfully!", "inline-block ml-4 text-sm text-green-600"
    
    return "", "inline-block ml-4 text-sm text-green-600"

# Callback to clear the form
@app.callback(
    [Output('activity-date', 'date', allow_duplicate=True),
     Output('activity-title', 'value', allow_duplicate=True),
     Output('activity-category', 'value', allow_duplicate=True),
     Output('activity-details', 'value', allow_duplicate=True),
     Output('activity-links', 'value', allow_duplicate=True),
     Output('current-activity', 'data', allow_duplicate=True),
     Output('save-status', 'children', allow_duplicate=True)],
    [Input('clear-form-button', 'n_clicks'),
     Input('clear-search', 'n_clicks')],
    prevent_initial_call=True
)
def clear_form(clear_clicks, clear_search_clicks):
    return dt.now().date(), "", None, "", "", {'id': None}, ""

# Callback to delete an activity
@app.callback(
    Output('activities-list', 'children', allow_duplicate=True),
    [Input({'type': 'delete-button', 'index': dash.dependencies.ALL}, 'n_clicks')],
    [State({'type': 'delete-button', 'index': dash.dependencies.ALL}, 'id')],
    prevent_initial_call=True
)
def delete_activity_callback(n_clicks, button_ids):
    if not any(n_clicks):
        return dash.no_update
    
    # Find which button was clicked
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id:
        button_id = json.loads(button_id)
        activity_id = button_id['index']
        
        # Delete the activity
        delete_activity(activity_id)
        
        # Return updated activities list
        return update_activities_list(None, None)
    
    return dash.no_update

# Add Tailwind CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>FIX Support Activity Tracker</title>
        {%favicon%}
        {%css%}
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        colors: {
                            primary: {
                                50: '#eff6ff',
                                100: '#dbeafe',
                                500: '#3b82f6',
                                600: '#2563eb',
                                700: '#1d4ed8',
                                800: '#1e40af',
                                900: '#1e3a8a',
                            }
                        }
                    }
                }
            }
        </script>
        <style>
            body {
                font-family: 'Inter', sans-serif;
            }
            .dash-table-container {
                border-radius: 0.5rem;
                overflow: hidden;
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            }
            .dash-spreadsheet-container .dash-spreadsheet-inner table {
                border-collapse: separate;
                border-spacing: 0;
            }
            .dash-spreadsheet-container .dash-spreadsheet-inner th {
                background-color: #f8fafc;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                font-size: 0.75rem;
                color: #64748b;
            }
        </style>
    </head>
    <body class="antialiased bg-gray-50">
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
    app.run(debug=True, host='0.0.0.0', port=8060)