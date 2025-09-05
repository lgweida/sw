import dash
from dash import html, dcc, Input, Output
import subprocess
import pandas as pd

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Button(
        "Manual Update", 
        id="update-button", 
        n_clicks=0,
        title="Click to manually fetch and update the data from the external source"
    ),
    html.Div(id="update-status"),
    # Example: Display fetched data in a table
    dcc.Graph(id="data-plot")
])

@app.callback(
    Output("update-status", "children"),
    Input("update-button", "n_clicks"))
def trigger_data_fetch(n_clicks):
    if n_clicks > 0:
        # Run the external data fetcher script
        subprocess.run(["python", "data_fetcher.py"])
        return "Data updated manually!"
    return "Click the button to update data."

@app.callback(
    Output("data-plot", "figure"),
    Input("update-status", "children"))
def display_data(status):
    # Load the fetched data (from data_fetcher.py)
    try:
        df = pd.read_csv("web_data.csv")
        # Example: Plot the count of posts by user ID
        post_counts = df["userId"].value_counts().reset_index()
        post_counts.columns = ["User ID", "Post Count"]
               
        return {
            "data": [{"x": post_counts["User ID"], "y": post_counts["Post Count"], "type": "bar"}],
            "layout": {"title": "Posts by User ID"}
        }
    except FileNotFoundError:
        return {"data": [], "layout": {"title": "No data available. Click 'Manual Update'."}}

if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0", port= 9999)
