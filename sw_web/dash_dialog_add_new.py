import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import sqlite3
import os
from datetime import datetime

# Initialize the Dash app with Tailwind CSS
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"
    ]
)

# Function to remove http/https from URL for display
def clean_url_display(url):
    """Remove http:// or https:// from URL for display purposes"""
    if url.startswith('https://'):
        return url[8:]
    elif url.startswith('http://'):
        return url[7:]
    return url

# SQLite database setup with sample data
def init_db():
    conn = sqlite3.connect('websites.db')
    cursor = conn.cursor()
    
    # Drop table if exists to ensure clean start with new schema
    cursor.execute('DROP TABLE IF EXISTS websites')
    
    # Create new table with correct schema
    cursor.execute('''
        CREATE TABLE websites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert 20 sample websites (stored with https:// but displayed without)
    sample_websites = [
        'https://google.com',
        'https://youtube.com',
        'https://facebook.com',
        'https://amazon.com',
        'https://twitter.com',
        'https://instagram.com',
        'https://linkedin.com',
        'https://microsoft.com',
        'https://apple.com',
        'https://netflix.com',
        'https://github.com',
        'https://stackoverflow.com',
        'https://wikipedia.org',
        'https://reddit.com',
        'https://adobe.com',
        'https://spotify.com',
        'https://wordpress.org',
        'https://pinterest.com',
        'https://tumblr.com',
        'https://medium.com'
    ]
    
    for website in sample_websites:
        cursor.execute('INSERT INTO websites (url) VALUES (?)', (website,))
    
    conn.commit()
    conn.close()

# Initialize database with sample data
init_db()

# Function to get all websites from database
def get_websites():
    conn = sqlite3.connect('websites.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, url FROM websites ORDER BY created_at DESC')
    websites = cursor.fetchall()
    conn.close()
    return websites

# Function to add a website to database
def add_website(url):
    conn = sqlite3.connect('websites.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO websites (url) VALUES (?)', (url,))
    conn.commit()
    conn.close()

# Modal component with 100% opacity
modal = dbc.Modal(
    [
        dbc.ModalHeader("Manage Websites", className="border-b border-gray-200 px-6 py-4 bg-white"),
        dbc.ModalBody(
            html.Div(
                className="flex h-96 bg-white",
                children=[
                    # Left side - Website list with scroll
                    html.Div(
                        className="w-1/2 border-r border-gray-200 pr-4",
                        children=[
                            html.H3("Existing Websites", className="text-lg font-semibold mb-3 text-gray-700"),
                            html.Div(
                                id="website-list",
                                className="overflow-y-auto h-full border border-gray-200 rounded-lg p-3 bg-gray-50",
                                style={"maxHeight": "320px"}
                            )
                        ]
                    ),
                    # Right side - Add new website form
                    html.Div(
                        className="w-1/2 pl-4",
                        children=[
                            html.H3("Add New Website", className="text-lg font-semibold mb-3 text-gray-700"),
                            dcc.Input(
                                id="website-url-input",
                                type="url",
                                placeholder="Enter website URL (e.g., example.com)",
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-3",
                                style={"border": "1px solid #d1d5db"}
                            ),
                            dbc.Button(
                                "Add Website",
                                id="add-website-btn",
                                color="primary",
                                className="w-full mb-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition duration-200"
                            ),
                            html.Div(id="add-status", className="text-sm")
                        ]
                    )
                ]
            )
        ),
        dbc.ModalFooter(
            dbc.Button(
                "Close",
                id="close-modal",
                className="bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition duration-200"
            ),
            className="bg-white border-t border-gray-200"
        ),
    ],
    id="website-modal",
    size="lg",
    is_open=False,
    backdrop=True,
    style={"opacity": 1}  # 100% opacity
)

# App layout
app.layout = html.Div(
    className="min-h-screen bg-gray-100 p-8",
    children=[
        # Header
        html.Div(
            className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-6",
            children=[
                html.H1(
                    "Website Manager",
                    className="text-2xl font-bold text-gray-800 mb-6"
                ),
                
                # Add New Website Button
                dbc.Button(
                    "Add New Website",
                    id="open-modal",
                    className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition duration-200 mb-6"
                ),
                
                # Current Websites Section
                html.Div(
                    className="mt-6",
                    children=[
                        html.H2(
                            "Current Websites",
                            className="text-xl font-semibold text-gray-700 mb-4"
                        ),
                        html.Div(
                            id="current-websites",
                            className="space-y-2"
                        )
                    ]
                )
            ]
        ),
        
        # Modal
        modal,
        
        # Store for tracking changes
        dcc.Store(id='website-store')
    ]
)

# Callback to open/close modal
@app.callback(
    Output("website-modal", "is_open"),
    [Input("open-modal", "n_clicks"), Input("close-modal", "n_clicks")],
    [State("website-modal", "is_open")],
)
def toggle_modal(open_clicks, close_clicks, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return False
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "open-modal":
            return True
        elif button_id == "close-modal":
            return False
    return is_open

# Callback to update website list in modal
@app.callback(
    Output("website-list", "children"),
    Input("add-website-btn", "n_clicks"),
    Input("close-modal", "n_clicks")
)
def update_website_list(add_clicks, close_clicks):
    websites = get_websites()
    
    if not websites:
        return html.P("No websites added yet.", className="text-gray-500 text-center py-8")
    
    website_items = []
    for id, url in websites:
        display_url = clean_url_display(url)
        website_items.append(
            html.Div(
                className="p-3 mb-2 bg-white border border-gray-200 rounded-md hover:bg-gray-50 transition duration-150",
                children=[
                    html.Div(
                        className="flex items-center justify-between",
                        children=[
                            html.A(
                                display_url,
                                href=url,
                                target="_blank",
                                className="text-blue-600 hover:text-blue-800 break-words flex-1",
                                style={"wordBreak": "break-word"}
                            ),
                            html.Span(
                                f"ID: {id}",
                                className="text-xs text-gray-500 ml-2"
                            )
                        ]
                    )
                ]
            )
        )
    
    return website_items

# Callback to add new website
@app.callback(
    [Output("add-status", "children"),
     Output("website-url-input", "value")],
    Input("add-website-btn", "n_clicks"),
    State("website-url-input", "value")
)
def add_website_callback(n_clicks, url):
    if n_clicks is None or n_clicks == 0:
        return "", ""
    
    if not url:
        return html.Div("Please enter a website URL.", className="text-red-500"), ""
    
    # Basic URL validation - add https:// if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        add_website(url)
        return html.Div("Website added successfully!", className="text-green-500"), ""
    except Exception as e:
        return html.Div(f"Error adding website: {str(e)}", className="text-red-500"), url

# Callback to update current websites display
@app.callback(
    Output("current-websites", "children"),
    Input("add-website-btn", "n_clicks"),
    Input("close-modal", "n_clicks")
)
def update_current_websites(add_clicks, close_clicks):
    websites = get_websites()
    
    if not websites:
        return html.P("No websites have been added yet.", className="text-gray-500 italic")
    
    website_cards = []
    for id, url in websites:
        display_url = clean_url_display(url)
        website_cards.append(
            html.Div(
                className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition duration-200",
                children=[
                    html.Div(
                        className="flex items-center justify-between",
                        children=[
                            html.A(
                                display_url,
                                href=url,
                                target="_blank",
                                className="text-blue-600 hover:text-blue-800 font-medium break-words",
                                style={"wordBreak": "break-word"}
                            ),
                            html.Span(
                                f"ID: {id}",
                                className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded"
                            )
                        ]
                    )
                ]
            )
        )
    
    return website_cards

if __name__ == "__main__":
    app.run(debug=True)
