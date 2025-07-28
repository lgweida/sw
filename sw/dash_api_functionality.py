import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import json
import pandas as pd
import requests
from datetime import datetime
import sqlite3
import os

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sample database setup (in-memory SQLite for demo)
def init_database():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    
    # Create sample table
    conn.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample data
    sample_users = [
        ('Alice Johnson', 'alice@example.com'),
        ('Bob Smith', 'bob@example.com'),
        ('Charlie Brown', 'charlie@example.com')
    ]
    
    conn.executemany('INSERT INTO users (name, email) VALUES (?, ?)', sample_users)
    conn.commit()
    return conn

# Global database connection (not recommended for production!)
db_conn = init_database()

# Data store for API-like functionality
data_store = {
    'users': [],
    'posts': [],
    'analytics': {'page_views': 0, 'api_calls': 0}
}

# Simulate external API calls
def fetch_external_data():
    """Simulate fetching data from external API"""
    try:
        # Using JSONPlaceholder as example external API
        response = requests.get('https://jsonplaceholder.typicode.com/users', timeout=5)
        if response.status_code == 200:
            return response.json()[:5]  # Get first 5 users
    except:
        pass
    
    # Fallback data if API call fails
    return [
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
    ]

def get_local_users():
    """Get users from local database"""
    cursor = db_conn.execute('SELECT * FROM users ORDER BY created_at DESC')
    columns = [description[0] for description in cursor.description]
    users = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return users

def add_user_to_db(name, email):
    """Add user to local database"""
    try:
        cursor = db_conn.execute(
            'INSERT INTO users (name, email) VALUES (?, ?)', 
            (name, email)
        )
        db_conn.commit()
        return cursor.lastrowid
    except Exception as e:
        return None

# Layout
app.layout = dbc.Container([
    html.H1("Dash API-like Functionality Demo", className="mb-4"),
    
    # API Analytics Card
    dbc.Card([
        dbc.CardHeader(html.H4("API Analytics")),
        dbc.CardBody([
            html.Div(id="analytics-display"),
            dbc.Button("Refresh Analytics", id="refresh-analytics", color="info", size="sm")
        ])
    ], className="mb-4"),
    
    # External API Integration
    dbc.Card([
        dbc.CardHeader(html.H4("External API Integration")),
        dbc.CardBody([
            dbc.Button("Fetch External Users", id="fetch-external", color="primary", className="mb-3"),
            html.Div(id="external-data-display"),
            dcc.Store(id="external-data-store")
        ])
    ], className="mb-4"),
    
    # Local Database Operations
    dbc.Card([
        dbc.CardHeader(html.H4("Local Database Operations (CRUD-like)")),
        dbc.CardBody([
            # Add User Form
            dbc.Row([
                dbc.Col([
                    dbc.Label("Name:"),
                    dbc.Input(id="user-name-input", placeholder="Enter name"),
                ], width=6),
                dbc.Col([
                    dbc.Label("Email:"),
                    dbc.Input(id="user-email-input", placeholder="Enter email", type="email"),
                ], width=6),
            ], className="mb-3"),
            
            dbc.Button("Add User", id="add-user-btn", color="success", className="mb-3"),
            html.Div(id="add-user-status"),
            
            # Display Users
            html.H5("Current Users:"),
            html.Div(id="users-display"),
            dbc.Button("Refresh Users", id="refresh-users", color="secondary", size="sm")
        ])
    ], className="mb-4"),
    
    # Data Export/Import Simulation
    dbc.Card([
        dbc.CardHeader(html.H4("Data Export/Import (API-like Endpoints)")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Button("Export Data (JSON)", id="export-json", color="warning"),
                    html.Div(id="export-status", className="mt-2")
                ], width=6),
                dbc.Col([
                    dcc.Upload(
                        id="upload-data",
                        children=dbc.Button("Import Data", color="info"),
                        multiple=False
                    ),
                    html.Div(id="import-status", className="mt-2")
                ], width=6)
            ])
        ])
    ], className="mb-4"),
    
    # Real-time Data Simulation
    dbc.Card([
        dbc.CardHeader(html.H4("Real-time Data Updates")),
        dbc.CardBody([
            dbc.Switch(id="realtime-toggle", label="Enable Real-time Updates", value=False),
            html.Div(id="realtime-data"),
            dcc.Interval(id="interval-component", interval=2000, n_intervals=0, disabled=True)
        ])
    ], className="mb-4"),
    
    # API Response Simulator
    dbc.Card([
        dbc.CardHeader(html.H4("API Response Simulator")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Endpoint:"),
                    dbc.Select(
                        id="endpoint-select",
                        options=[
                            {"label": "GET /users", "value": "get_users"},
                            {"label": "GET /posts", "value": "get_posts"},
                            {"label": "GET /analytics", "value": "get_analytics"},
                            {"label": "POST /users", "value": "post_users"}
                        ],
                        value="get_users"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("Parameters:"),
                    dbc.Input(id="api-params", placeholder='{"limit": 10}', value='{}')
                ], width=6)
            ], className="mb-3"),
            
            dbc.Button("Simulate API Call", id="simulate-api", color="primary"),
            html.Hr(),
            html.H6("Response:"),
            html.Pre(id="api-response", style={"background": "#f8f9fa", "padding": "10px"})
        ])
    ]),
    
    # Hidden stores for data management
    dcc.Store(id="users-store", data=[]),
    dcc.Store(id="analytics-store", data=data_store['analytics'])
])

# Callbacks

# Update analytics
@app.callback(
    [Output("analytics-display", "children"),
     Output("analytics-store", "data")],
    [Input("refresh-analytics", "n_clicks"),
     Input("fetch-external", "n_clicks"),
     Input("add-user-btn", "n_clicks")],
    State("analytics-store", "data")
)
def update_analytics(refresh_clicks, fetch_clicks, add_clicks, analytics_data):
    # Increment counters based on actions
    if fetch_clicks:
        analytics_data['api_calls'] = analytics_data.get('api_calls', 0) + 1
    if add_clicks:
        analytics_data['page_views'] = analytics_data.get('page_views', 0) + 1
    
    display = dbc.Row([
        dbc.Col([
            html.H5(f"{analytics_data.get('page_views', 0)}", className="text-primary"),
            html.P("Page Views")
        ], width=6),
        dbc.Col([
            html.H5(f"{analytics_data.get('api_calls', 0)}", className="text-success"),
            html.P("API Calls")
        ], width=6)
    ])
    
    return display, analytics_data

# Fetch external data
@app.callback(
    [Output("external-data-display", "children"),
     Output("external-data-store", "data")],
    Input("fetch-external", "n_clicks")
)
def fetch_and_display_external_data(n_clicks):
    if not n_clicks:
        return "Click the button to fetch external data.", []
    
    try:
        external_users = fetch_external_data()
        
        # Create display
        cards = []
        for user in external_users:
            card = dbc.Card([
                dbc.CardBody([
                    html.H6(user.get('name', 'Unknown')),
                    html.P(user.get('email', 'No email'), className="text-muted"),
                    dbc.Badge(f"ID: {user.get('id', 'N/A')}", color="info")
                ])
            ], className="mb-2")
            cards.append(card)
        
        return cards, external_users
    
    except Exception as e:
        return dbc.Alert(f"Error fetching data: {str(e)}", color="danger"), []

# Add user to database
@app.callback(
    [Output("add-user-status", "children"),
     Output("user-name-input", "value"),
     Output("user-email-input", "value")],
    Input("add-user-btn", "n_clicks"),
    [State("user-name-input", "value"),
     State("user-email-input", "value")]
)
def add_user(n_clicks, name, email):
    if not n_clicks or not name or not email:
        return "", "", ""
    
    user_id = add_user_to_db(name, email)
    
    if user_id:
        return dbc.Alert(f"User added successfully! ID: {user_id}", color="success", dismissable=True), "", ""
    else:
        return dbc.Alert("Error adding user.", color="danger", dismissable=True), name, email

# Display users from database
@app.callback(
    Output("users-display", "children"),
    [Input("refresh-users", "n_clicks"),
     Input("add-user-btn", "n_clicks")]
)
def display_users(refresh_clicks, add_clicks):
    users = get_local_users()
    
    if not users:
        return dbc.Alert("No users found.", color="info")
    
    table_rows = []
    for user in users:
        row = html.Tr([
            html.Td(user['id']),
            html.Td(user['name']),
            html.Td(user['email']),
            html.Td(user.get('created_at', 'Unknown'))
        ])
        table_rows.append(row)
    
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("ID"),
                html.Th("Name"),
                html.Th("Email"),
                html.Th("Created At")
            ])
        ]),
        html.Tbody(table_rows)
    ], striped=True, bordered=True, hover=True, size="sm")
    
    return table

# Export data
@app.callback(
    Output("export-status", "children"),
    Input("export-json", "n_clicks")
)
def export_data(n_clicks):
    if not n_clicks:
        return ""
    
    try:
        users = get_local_users()
        export_data = {
            "users": users,
            "exported_at": datetime.now().isoformat(),
            "total_records": len(users)
        }
        
        # In a real app, you'd save this to a file or return it via a download
        json_str = json.dumps(export_data, indent=2)
        
        return dbc.Alert([
            html.P("Data exported successfully!"),
            html.Details([
                html.Summary("View JSON"),
                html.Pre(json_str[:500] + "..." if len(json_str) > 500 else json_str)
            ])
        ], color="success")
    
    except Exception as e:
        return dbc.Alert(f"Export failed: {str(e)}", color="danger")

# Real-time data updates
@app.callback(
    Output("interval-component", "disabled"),
    Input("realtime-toggle", "value")
)
def toggle_realtime(enabled):
    return not enabled

@app.callback(
    Output("realtime-data", "children"),
    Input("interval-component", "n_intervals")
)
def update_realtime_data(n_intervals):
    if n_intervals == 0:
        return "Real-time updates disabled."
    
    # Simulate real-time data
    current_time = datetime.now().strftime("%H:%M:%S")
    random_value = pd.np.random.randint(1, 100)
    
    return dbc.Card([
        dbc.CardBody([
            html.H6(f"Live Data Update #{n_intervals}"),
            html.P(f"Time: {current_time}"),
            html.P(f"Random Value: {random_value}"),
            dbc.Progress(value=random_value, color="success")
        ])
    ])

# API Response Simulator
@app.callback(
    Output("api-response", "children"),
    Input("simulate-api", "n_clicks"),
    [State("endpoint-select", "value"),
     State("api-params", "value")]
)
def simulate_api_response(n_clicks, endpoint, params_str):
    if not n_clicks:
        return "Click 'Simulate API Call' to see response"
    
    try:
        params = json.loads(params_str) if params_str else {}
    except:
        params = {}
    
    # Simulate different API endpoints
    if endpoint == "get_users":
        users = get_local_users()
        limit = params.get('limit', len(users))
        response = {
            "status": "success",
            "data": users[:limit],
            "total": len(users),
            "timestamp": datetime.now().isoformat()
        }
    
    elif endpoint == "get_posts":
        response = {
            "status": "success",
            "data": [
                {"id": 1, "title": "Sample Post", "content": "This is a sample post"},
                {"id": 2, "title": "Another Post", "content": "Another sample post"}
            ],
            "total": 2,
            "timestamp": datetime.now().isoformat()
        }
    
    elif endpoint == "get_analytics":
        response = {
            "status": "success",
            "data": data_store['analytics'],
            "timestamp": datetime.now().isoformat()
        }
    
    elif endpoint == "post_users":
        response = {
            "status": "success",
            "message": "User would be created",
            "data": {"id": 999, "name": "New User", "email": "new@example.com"},
            "timestamp": datetime.now().isoformat()
        }
    
    else:
        response = {"status": "error", "message": "Unknown endpoint"}
    
    return json.dumps(response, indent=2)

if __name__ == '__main__':
    app.run_server(debug=True)