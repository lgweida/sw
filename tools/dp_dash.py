import dash
from dash import html, dcc, Input, Output
import subprocess
import pandas as pd

app = dash.Dash(__name__)

# Include Tailwind CSS
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
                            secondary: '#10B981',
                            accent: '#F59E0B',
                        }
                    }
                }
            }
        </script>
    </head>
    <body class="bg-gray-100">
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Data Dashboard", className="text-3xl font-bold text-gray-800"),
        html.P("Monitor and update your data in real-time", className="text-gray-600")
    ], className="text-center mb-8"),
    
    # Control Panel
    html.Div([
        html.Div([
            html.Button(
                "Manual Update", 
                id="update-button", 
                n_clicks=0,
                className="bg-primary hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg flex items-center transition duration-200"
            ),
            # Tooltip container
            html.Div(
                "Click to manually fetch the latest data",
                className="invisible absolute bg-gray-800 text-white text-sm px-2 py-1 rounded mt-2 group-hover:visible",
                style={"transform": "translateX(-50%)", "left": "50%"}
            ),
        ], className="relative group flex justify-center mb-4"),
        
        html.Div(id="update-status", className="text-center text-gray-700 font-medium")
    ], className="bg-white p-6 rounded-xl shadow-md mb-8"),
    
    # Data Visualization
    html.Div([
        dcc.Graph(id="data-plot", className="bg-white rounded-xl shadow-md p-4")
    ])
], className="container mx-auto px-4 py-8")

@app.callback(
    Output("update-status", "children"),
    Input("update-button", "n_clicks")
)
def trigger_data_fetch(n_clicks):
    if n_clicks > 0:
        # Run the external data fetcher script
        subprocess.run(["python", "data_fetcher.py"])
        return html.Div([
            html.Span("✅ ", className="text-secondary"),
            "Data updated manually!"
        ], className="text-lg")
    return "Click the button to update data."

@app.callback(
    Output("data-plot", "figure"),
    Input("update-status", "children")
)
def display_data(status):
    # Load the fetched data (from data_fetcher.py)
    try:
        df = pd.read_csv("web_data.csv")
        # Example: Plot the count of posts by user ID
        post_counts = df["userId"].value_counts().reset_index()
        post_counts.columns = ["User ID", "Post Count"]
        
        return {
            "data": [{
                "x": post_counts["User ID"], 
                "y": post_counts["Post Count"], 
                "type": "bar",
                "marker": {
                    "color": post_counts["Post Count"],
                    "colorscale": "Viridis"
                }
            }],
            "layout": {
                "title": {
                    "text": "Posts by User ID",
                    "font": {"size": 24, "family": "Inter, sans-serif"}
                },
                "plot_bgcolor": "rgba(0,0,0,0)",
                "paper_bgcolor": "rgba(0,0,0,0)",
                "font": {"family": "Inter, sans-serif"},
                "xaxis": {
                    "title": {"text": "User ID", "font": {"size": 16}}
                },
                "yaxis": {
                    "title": {"text": "Post Count", "font": {"size": 16}}
                }
            }
        }
    except FileNotFoundError:
        return {
            "data": [], 
            "layout": {
                "title": {
                    "text": "No data available. Click 'Manual Update'.",
                    "font": {"size": 20, "family": "Inter, sans-serif"}
                },
                "plot_bgcolor": "rgba(0,0,0,0)",
                "paper_bgcolor": "rgba(0,0,0,0)",
                "font": {"family": "Inter, sans-serif"}
            }
        }

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9999)
