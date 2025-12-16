import pandas as pd
from dash import Dash, dash_table, html

# --- 1. Prepare the Data ---
data = {
    'Origin': ['New York', 'London', 'Tokyo', 'Paris', 'Sydney'],
    'Destination': ['Los Angeles', 'Paris', 'Seoul', 'Rome', 'Melbourne']
}
df = pd.DataFrame(data)

# Using the long Unicode arrow (⟹)
df['===>'] = '⟹'
df['===>'] = '➛'

# Reorder the columns: Origin, Arrow, Destination
df = df[['Origin', '===>', 'Destination']]

# Define Tailwind-inspired colors (e.g., from the blue/gray palette)
TW_BLUE_500 = '#3B82F6'  # A bright, primary blue
TW_GRAY_100 = '#F3F4F6'  # A light gray for backgrounds/striping
TW_GRAY_800 = '#1F2937'  # A dark gray for text
TW_RED_500 = '#EF4444'   # A striking red for the arrow

# --- 2. Initialize the Dash App ---
app = Dash(__name__)

# --- 3. Define the Layout ---
app.layout = html.Div(
    # Outer div for global padding/margin
    style={'maxWidth': '900px', 'margin': '0 auto', 'padding': '20px'},
    children=[
        html.H1(
            "✈️ Tailwind-Inspired Flight Paths", 
            style={
                'textAlign': 'center', 
                'color': TW_GRAY_800, 
                'paddingBottom': '20px',
                'fontFamily': 'sans-serif'
            }
        ),
        
        # Dash DataTable with Tailwind-like Styling
        dash_table.DataTable(
            id='tailwind-table',
            
            columns=[
                {"name": "Origin", "id": "Origin"},
                {"name": "", "id": "===>", "type": "text"},
                {"name": "Destination", "id": "Destination"}
            ],
            
            data=df.to_dict('records'),
            
            # --- Tailwind-Inspired Styling ---
            
            # Header Styling (Blue background, White text)
            style_header={
                'backgroundColor': TW_BLUE_500,
                'color': 'white',
                'fontWeight': '600',
                'fontSize': '16px',
                'border': 'none',
                'textAlign': 'center',
                'textTransform': 'uppercase'
            },
            
            # Data Styling (Zebra striping on rows)
            style_data_conditional=[
                # Zebra striping (like 'bg-gray-100' for even rows)
                {
                    'if': {'row_index': 'even'},
                    'backgroundColor': TW_GRAY_100,
                },
            ],
            
            # Cell Styling for Alignment, Arrow, and Text
            style_cell_conditional=[
                # Style for the arrow column '===>' (Long, centered, red arrow)
                {
                    'if': {'column_id': '===>'},
                    'textAlign': 'center',
                    'width': '10%',
                    'fontWeight': 'extra-bold',
                    'fontSize': '28px',
                    'color': 'green',
                    'border': 'none',
                    'padding': '0px 4px'
                },
                # Center Origin and Destination text (Fixes the SyntaxError)
                *[
                    {
                        'if': {'column_id': c},
                        'textAlign': 'center',
                    } for c in ['Origin', 'Destination']
                ]
            ],
            
            # General Cell Styling (Padding, Font, Text color, No borders)
            style_cell={
                'fontFamily': 'sans-serif', 
                'padding': '12px 16px',
                'color': TW_GRAY_800,
                'border': 'none',
            },
            
            # Styling for the overall table container (Rounded corners and shadow)
            style_table={
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.06)', 
                'borderRadius': '8px', 
                'overflow': 'hidden',
            },
        ),
        
        html.Div([
            html.P("This table uses a modern, clean aesthetic inspired by Tailwind CSS design principles."),
            html.P("Run the application and navigate to http://127.0.0.1:8050/ in your browser.")
        ], style={'textAlign': 'center', 'marginTop': '30px', 'color': '#7F8C8D', 'fontFamily': 'sans-serif'})
    ]
)

# --- 4. Run the App ---
if __name__ == '__main__':
    app.run(debug=True)