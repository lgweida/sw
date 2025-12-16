import pandas as pd
from dash import Dash, dash_table, html

# --- 1. Prepare the Data ---
data = {
    'Origin': ['New York', 'London', 'Tokyo', 'Paris', 'Sydney'],
    'Destination': ['Los Angeles', 'Paris', 'Seoul', 'Rome', 'Melbourne']
}
df = pd.DataFrame(data)

# Use a longer, more prominent Unicode arrow (U+21D2: Double Rightwards Arrow)
# Or U+27F9 (Long Right Arrow)
df['===>'] = '⟹'

# Reorder the columns
df = df[['Origin', '===>', 'Destination']]

# --- 2. Initialize the Dash App ---
app = Dash(__name__)

# --- 3. Define the Layout ---
app.layout = html.Div([
    html.H1("✈️ Enhanced Flight Paths: Origin ⟹ Destination", style={'textAlign': 'center', 'color': '#2C3E50'}),
    
    dash_table.DataTable(
        id='origin-destination-table',
        
        columns=[
            {"name": "Origin", "id": "Origin"},
            {"name": "", "id": "===>", "type": "text"}, # The arrow column
            {"name": "Destination", "id": "Destination"}
        ],
        
        data=df.to_dict('records'),
        
        # --- Styling Options ---
        style_header={
            'backgroundColor': '#3498DB',
            'color': 'white',
            'fontWeight': 'bold',
            'fontSize': '16px'
        },
        style_data={
            'backgroundColor': 'white',
            'color': '#2C3E50',
            'border': '1px solid #D7DBDD'
        },
        
        # CSS to make the arrow longer, bolder, and centered
        style_cell_conditional=[
            # Style for the arrow column '===>'
            {
                'if': {'column_id': '===>'},
                'textAlign': 'center',       # Center the content horizontally
                'width': '10%',              # Allocate more space for the arrow column
                'fontWeight': 'bolder',
                'fontSize': '52px',          # Make the arrow significantly larger
                'color': '#E74C3C'           # Change the arrow color to red for emphasis
            },
            # Center the Origin and Destination text as well
            {
                'if': {'column_id': 'Origin'},
                'textAlign': 'center',
            },
            {
                'if': {'column_id': 'Destination'},
                'textAlign': 'center',
            }
        ],
        
        # Styling for the overall table container
        style_table={
            'overflowX': 'auto',
            'minWidth': '500px',
            'margin': '20px auto',
            'width': '70%' # Increase table width for better visibility
        },
    ),
    
    html.Div([
        html.P("Using a Unicode Double Rightwards Arrow (⟹) and custom CSS for alignment and size.")
    ], style={'textAlign': 'center', 'marginTop': '20px', 'color': '#7F8C8D'})
])

# --- 4. Run the App ---
if __name__ == '__main__':
    app.run(debug=True)