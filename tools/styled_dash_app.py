import dash
from dash import html, dcc, Input, Output, State
import subprocess
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Initialize the Dash app with Tailwind CSS
app = dash.Dash(__name__)

# Add Tailwind CSS and custom styles
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        animation: {
                            'spin-slow': 'spin 2s linear infinite',
                            'pulse-soft': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                        }
                    }
                }
            }
        </script>
        {%css%}
        <style>
            body {
                margin: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            }
            
            .tooltip {
                visibility: hidden;
                opacity: 0;
                transition: opacity 0.3s, visibility 0.3s;
            }
            
            .tooltip-trigger:hover .tooltip {
                visibility: visible;
                opacity: 1;
            }
            
            .glass-card {
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .animate-fadeIn {
                animation: fadeIn 0.5s ease-in-out;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
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

app.layout = html.Div([
    # Background Container
    html.Div([
        # Header Section
        html.Div([
            html.H1([
                html.I(className="fas fa-chart-line mr-4 text-blue-400"),
                "Data Dashboard"
            ], className="text-5xl font-bold text-white mb-4 drop-shadow-lg"),
            html.P("Monitor and analyze your data in real-time", 
                   className="text-xl text-blue-100 opacity-90")
        ], className="text-center mb-12"),
        
        # Control Panel Card
        html.Div([
            html.Div([
                # Card Header
                html.Div([
                    html.Div([
                        html.H3([
                            html.I(className="fas fa-cog mr-3 text-blue-600"),
                            "Data Controls"
                        ], className="text-2xl font-semibold text-gray-800"),
                        html.P("Manage your data updates and refresh cycles", 
                               className="text-gray-600 mt-1")
                    ], className="flex-1"),
                    
                    # Control Section
                    html.Div([
                        # Manual Update Button with Tooltip
                        html.Div([
                            html.Button([
                                html.I(id="update-icon", className="fas fa-sync-alt mr-2 transition-transform duration-300"),
                                "Manual Update"
                            ], 
                            id="update-button",
                            n_clicks=0,
                            className="relative bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-6 py-3 rounded-xl font-medium transition-all duration-300 transform hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-4 focus:ring-blue-300 flex items-center"),
                            
                            # Custom Tooltip
                            html.Div([
                                "Click to manually fetch and update the data from external source",
                                html.Div(className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900")
                            ], className="tooltip absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-sm rounded-lg py-2 px-3 whitespace-nowrap z-10")
                        ], className="tooltip-trigger relative"),
                        
                        # Status Indicator
                        html.Div([
                            html.Div(id="status-dot", className="w-3 h-3 rounded-full bg-gray-400 transition-all duration-300"),
                            html.Span(id="status-text", children="Ready", className="text-sm font-medium text-gray-600 ml-2")
                        ], className="flex items-center mt-4")
                    ], className="flex flex-col items-end")
                ], className="flex items-center justify-between")
            ], className="p-6")
        ], className="glass-card rounded-2xl shadow-xl mb-8"),
        
        # Status Alert Container
        html.Div(id="alert-container", className="mb-6"),
        
        # Chart Card
        html.Div([
            # Chart Header
            html.Div([
                html.H3([
                    html.I(className="fas fa-chart-bar mr-3 text-blue-600"),
                    "Posts by User ID"
                ], className="text-2xl font-semibold text-gray-800"),
                html.P("Distribution of posts across different users", 
                       className="text-gray-600 mt-2")
            ], className="p-6 border-b border-gray-100"),
            
            # Chart Container
            html.Div([
                dcc.Graph(
                    id="data-plot",
                    config={'displayModeBar': False},
                    className="w-full"
                )
            ], className="p-6", style={'height': '500px'})
        ], className="glass-card rounded-2xl shadow-xl"),
        
        # Loading Overlay
        html.Div([
            html.Div([
                html.Div(className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"),
                html.H4("Updating Data...", className="text-xl font-semibold text-gray-800 mt-4"),
                html.P("Please wait while we fetch the latest data", 
                       className="text-gray-600 mt-2")
            ], className="bg-white rounded-2xl p-8 shadow-2xl flex flex-col items-center")
        ], id="loading-overlay", className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 opacity-0 pointer-events-none transition-opacity duration-300"),
        
        # Store component for managing state
        dcc.Store(id='update-store', data={'clicks': 0}),
        
    ], className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6")
], className="font-sans")

# Callback for handling manual updates
@app.callback(
    [Output("alert-container", "children"),
     Output("status-dot", "className"),
     Output("status-text", "children"),
     Output("loading-overlay", "className"),
     Output("update-icon", "className"),
     Output("update-store", "data")],
    [Input("update-button", "n_clicks")],
    [State("update-store", "data")],
    prevent_initial_call=True
)
def trigger_data_fetch(n_clicks, store_data):
    if n_clicks > store_data.get('clicks', 0):
        try:
            # Show loading state
            loading_overlay_class = "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 opacity-100 transition-opacity duration-300"
            loading_icon_class = "fas fa-spinner animate-spin mr-2 transition-transform duration-300"
            loading_dot_class = "w-3 h-3 rounded-full bg-yellow-400 animate-pulse transition-all duration-300"
            
            # Simulate the subprocess call (you can uncomment the real call)
            # subprocess.run(["python", "data_fetcher.py"])
            
            # Success state
            alert = html.Div([
                html.Div([
                    html.I(className="fas fa-check-circle text-green-500 mr-3"),
                    html.Span("Data updated successfully!", className="font-medium"),
                    html.Button([
                        html.I(className="fas fa-times")
                    ], className="ml-auto text-green-700 hover:text-green-900 transition-colors", 
                    id="close-alert", style={"background": "none", "border": "none"})
                ], className="flex items-center")
            ], className="animate-fadeIn bg-green-50 border border-green-200 rounded-xl p-4 text-green-800")
            
            success_dot_class = "w-3 h-3 rounded-full bg-green-400 transition-all duration-300"
            success_icon_class = "fas fa-sync-alt mr-2 transition-transform duration-300"
            normal_overlay_class = "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 opacity-0 pointer-events-none transition-opacity duration-300"
            
            return alert, success_dot_class, "Updated", normal_overlay_class, success_icon_class, {'clicks': n_clicks}
            
        except Exception as e:
            # Error state
            alert = html.Div([
                html.Div([
                    html.I(className="fas fa-exclamation-triangle text-red-500 mr-3"),
                    html.Span(f"Update failed: {str(e)}", className="font-medium"),
                    html.Button([
                        html.I(className="fas fa-times")
                    ], className="ml-auto text-red-700 hover:text-red-900 transition-colors",
                    id="close-alert", style={"background": "none", "border": "none"})
                ], className="flex items-center")
            ], className="animate-fadeIn bg-red-50 border border-red-200 rounded-xl p-4 text-red-800")
            
            error_dot_class = "w-3 h-3 rounded-full bg-red-400 transition-all duration-300"
            error_icon_class = "fas fa-sync-alt mr-2 transition-transform duration-300"
            normal_overlay_class = "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 opacity-0 pointer-events-none transition-opacity duration-300"
            
            return alert, error_dot_class, "Error", normal_overlay_class, error_icon_class, {'clicks': n_clicks}
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Callback for updating the chart
@app.callback(
    Output("data-plot", "figure"),
    [Input("update-store", "data")]
)
def display_data(store_data):
    try:
        # Try to load the fetched data
        df = pd.read_csv("web_data.csv")
        
        # Create post counts
        post_counts = df["userId"].value_counts().reset_index()
        post_counts.columns = ["User ID", "Post Count"]
        post_counts = post_counts.sort_values("User ID")
        
        # Create an enhanced bar chart with Tailwind-inspired colors
        fig = px.bar(
            post_counts, 
            x="User ID", 
            y="Post Count",
            title="",
            text="Post Count"
        )
        
        # Customize with Tailwind-inspired styling
        fig.update_traces(
            marker_color='#3B82F6',  # Tailwind blue-500
            marker_line_width=0,
            textposition='outside',
            textfont_size=12,
            hovertemplate='<b>User %{x}</b><br>Posts: %{y}<extra></extra>'
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="system-ui, -apple-system, sans-serif", size=12, color="#374151"),
            xaxis=dict(
                title="User ID",
                showgrid=False,
                zeroline=False,
                title_font=dict(size=14, color="#6B7280")
            ),
            yaxis=dict(
                title="Number of Posts",
                showgrid=True,
                gridcolor='rgba(229, 231, 235, 0.8)',  # Tailwind gray-200
                zeroline=False,
                title_font=dict(size=14, color="#6B7280")
            ),
            margin=dict(t=20, l=60, r=20, b=60),
            height=450
        )
        
        return fig
        
    except FileNotFoundError:
        # Create a no-data state
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            text="<span style='font-size: 48px;'>📊</span><br><br><b>No Data Available</b><br><span style='color: #6B7280;'>Click 'Manual Update' to fetch data</span>",
            showarrow=False,
            font=dict(size=18, color="#374151"),
            align="center"
        )
        fig.update_layout(
            plot_bgcolor='rgba(249, 250, 251, 0.5)',  # Tailwind gray-50
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(t=20, l=20, r=20, b=20),
            height=450
        )
        return fig
    
    except Exception as e:
        # Create an error state
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            text=f"<span style='font-size: 48px;'>❌</span><br><br><b>Error Loading Data</b><br><span style='color: #DC2626;'>{str(e)}</span>",
            showarrow=False,
            font=dict(size=18, color="#374151"),
            align="center"
        )
        fig.update_layout(
            plot_bgcolor='rgba(254, 242, 242, 0.5)',  # Tailwind red-50
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(t=20, l=20, r=20, b=20),
            height=450
        )
        return fig

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9991)
