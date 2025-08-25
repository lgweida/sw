import dash
from dash import dcc, html, Input, Output, callback, dash_table
import pandas as pd
import datetime
import json
from datetime import datetime as dt

# Initialize the Dash app
app = dash.Dash(__name__)

# Sample data for activities
activities_data = {
    'date': ['2023-10-15', '2023-10-16', '2023-10-17'],
    'title': ['FIX Session Configuration', 'Production Issue Troubleshooting', 'UAT Test Cases'],
    'category': ['Onboarding', 'Troubleshooting', 'Testing'],
    'details': [
        'Configured FIX session parameters for new client. Used encryption and compression settings.',
        'Investigated order routing issue between client and exchange. Found misconfigured gateway.',
        'Executed test cases for new order types. Verified execution reports and confirmations.'
    ]
}

# Convert to DataFrame
df_activities = pd.DataFrame(activities_data)

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
                html.Ul([
                    html.Li([
                        html.Div([
                            html.Span(dt.strptime(date, '%Y-%m-%d').strftime('%b %d'), 
                                     className="text-xs font-medium text-blue-600"),
                            html.P(title, className="text-sm font-medium text-gray-900 truncate"),
                            html.Span(category, className="text-xs text-gray-500")
                        ], className="px-4 py-3 hover:bg-gray-100 cursor-pointer", id={'type': 'activity-item', 'index': i})
                    ]) for i, (date, title, category) in enumerate(zip(df_activities['date'], df_activities['title'], df_activities['category']))
                ], className="divide-y divide-gray-200")
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
            
            # Add New Activity Section
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
                        html.Button("Add Activity", id='add-activity-button', 
                                   className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md shadow-sm")
                    ], className="col-span-2 mt-4")
                ], className="grid grid-cols-2 gap-4")
            ], className="bg-white rounded-lg shadow-sm p-6 mb-6"),
            
            # Activity List
            html.Div([
                html.H3("Recent Activities", className="text-lg font-semibold text-gray-700 mb-4"),
                html.Div(id='activities-list', children=[
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Span(activity['category'], 
                                         className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"),
                                html.Span(activity['date'], className="ml-2 text-sm text-gray-500")
                            ], className="flex items-center"),
                            html.H4(activity['title'], className="text-lg font-medium text-gray-900 mt-1"),
                            html.P(activity['details'], className="mt-2 text-gray-600"),
                            html.Div([
                                html.A("Open", href="#", className="text-blue-600 hover:text-blue-800 text-sm font-medium")
                            ], className="mt-3")
                        ], className="p-4")
                    ], className="bg-white rounded-lg shadow-sm border border-gray-200 mb-4") 
                    for _, activity in df_activities.iterrows()
                ])
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

# Callback to add new activity
@callback(
    Output('activities-list', 'children'),
    Input('add-activity-button', 'n_clicks'),
    [Input('activity-date', 'date'),
     Input('activity-title', 'value'),
     Input('activity-category', 'value'),
     Input('activity-details', 'value'),
     Input('activity-links', 'value')],
    prevent_initial_call=True
)
def add_activity(n_clicks, date, title, category, details, links):
    if n_clicks and title and details:
        # Format the date
        formatted_date = dt.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')
        
        # Create new activity element
        new_activity = html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Span(category, 
                                 className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"),
                        html.Span(formatted_date, className="ml-2 text-sm text-gray-500")
                    ], className="flex items-center"),
                    html.H4(title, className="text-lg font-medium text-gray-900 mt-1"),
                    html.P(details, className="mt-2 text-gray-600"),
                    html.Div([
                        html.A("Open", href="#", className="text-blue-600 hover:text-blue-800 text-sm font-medium")
                    ], className="mt-3")
                ], className="p-4")
            ], className="bg-white rounded-lg shadow-sm border border-gray-200 mb-4")
        ])
        
        # Prepend the new activity to the list
        return [new_activity] + dash.no_update
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
    app.run_server(debug=True, port=8050)