import pandas as pd
from dash import Dash, dash_table, html, dcc

# --- 1. Prepare the Data ---
# Create the initial DataFrame with Origin and Destination columns
data = {
    'Origin': ['New York', 'London', 'Tokyo', 'Paris', 'Sydney'],
    'Destination': ['Los Angeles', 'Paris', 'Seoul', 'Rome', 'Melbourne']
}
df = pd.DataFrame(data)

# Create a middle column with the arrow symbol
# Using the Unicode right arrow U+2192 (→)
df['->'] = '→'

# Reorder the columns to be Origin, Arrow, Destination
df = df[['Origin', '->', 'Destination']]

# --- 2. Initialize the Dash App ---
app = Dash(__name__)

# --- 3. Define the Layout ---
app.layout = html.Div([
    html.H1("✈️ Flight Paths: Origin → Destination", style={'textAlign': 'center', 'color': '#2C3E50'}),
    
    # Dash DataTable Component
    dash_table.DataTable(
        id='origin-destination-table',
        
        # Define the columns that will be displayed
        columns=[
            {"name": "Origin", "id": "Origin"},
            {"name": "", "id": "->", "type": "text"}, # The arrow column has no header name
            {"name": "Destination", "id": "Destination"}
        ],
        
        # Pass the DataFrame to the table in a dictionary format
        data=df.to_dict('records'),
        
        # --- Styling Options ---
        style_header={
            'backgroundColor': '#3498DB',  # Blue header background
            'color': 'white',               # White text
            'fontWeight': 'bold',
            'fontSize': '16px'
        },
        style_data={
            'backgroundColor': 'white',
            'color': '#2C3E50',             # Dark text
            'border': '1px solid #D7DBDD'   # Light border
        },
        # Center the text in the Arrow column for better visual balance
        style_cell_conditional=[
            {
                'if': {'column_id': '->'},
                'textAlign': 'center',
                'width': '5%', # Make the arrow column narrow
                'fontWeight': 'bolder'
            }
        ],
        
        # Styling for the overall table container
        style_table={
            'overflowX': 'auto',
            'minWidth': '500px', # Ensure a minimum width
            'margin': '20px auto',
            'width': '60%' # Set table width to 60% of container
        },
    ),
    
    # Optional: Add a simple text note
    html.Div([
        html.P("Each row visually represents a route from the specified origin to its destination.")
    ], style={'textAlign': 'center', 'marginTop': '20px', 'color': '#7F8C8D'})
])

# --- 4. Run the App ---
if __name__ == '__main__':
    # You can change the port if needed, e.g., port=8051
    app.run(debug=True)