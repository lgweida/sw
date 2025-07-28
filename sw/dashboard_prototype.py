import dash
from dash import dcc, html, dash_table, Input, Output, callback
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate sample data
np.random.seed(42)

# Sample data for the line chart
dates = pd.date_range(start='2024-01-01', end='2024-07-27', freq='D')
line_data = pd.DataFrame({
    'date': dates,
    'value': np.cumsum(np.random.randn(len(dates)) * 10) + 50000
})

# Sample data for the bar chart
categories = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7']
bar_values = [45000, 52000, 48000, 49000, 56000, 62000, 58000]

# Sample data for the pie chart
pie_data = pd.DataFrame({
    'category': ['Stocks', 'Bonds', 'Real Estate', 'Cash'],
    'value': [45, 25, 20, 10],
    'colors': ['#4A90E2', '#F5A623', '#7ED321', '#D0021B']
})

# Sample data for the table
table_data = pd.DataFrame({
    'Asset': ['Apple Inc.', 'Microsoft Corp.', 'Amazon.com Inc.', 'Tesla Inc.', 'Meta Platforms'],
    'Symbol': ['AAPL', 'MSFT', 'AMZN', 'TSLA', 'META'],
    'Price': [175.84, 338.56, 145.86, 248.50, 305.16],
    'Change': [2.45, -1.23, 3.67, -5.12, 8.94],
    'Change %': [1.41, -0.36, 2.58, -2.02, 3.02]
})

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    # Sidebar
    html.Div([
        html.Div([
            html.Div(className="menu-icon", style={
                'width': '30px',
                'height': '20px',
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'space-between',
                'margin': '20px'
            }, children=[
                html.Div(style={'height': '3px', 'backgroundColor': '#666', 'borderRadius': '2px'}),
                html.Div(style={'height': '3px', 'backgroundColor': '#666', 'borderRadius': '2px'}),
                html.Div(style={'height': '3px', 'backgroundColor': '#666', 'borderRadius': '2px'})
            ])
        ], style={'borderBottom': '1px solid #e0e0e0', 'paddingBottom': '20px'}),
        
        # Menu items (placeholder)
        html.Div([
            html.Div(style={'height': '15px', 'backgroundColor': '#e0e0e0', 'borderRadius': '8px', 'margin': '15px 20px'}),
            html.Div(style={'height': '15px', 'backgroundColor': '#e0e0e0', 'borderRadius': '8px', 'margin': '15px 20px'}),
            html.Div(style={'height': '15px', 'backgroundColor': '#e0e0e0', 'borderRadius': '8px', 'margin': '15px 20px'}),
            html.Div(style={'height': '15px', 'backgroundColor': '#e0e0e0', 'borderRadius': '8px', 'margin': '15px 20px'}),
            html.Div(style={'height': '15px', 'backgroundColor': '#e0e0e0', 'borderRadius': '8px', 'margin': '15px 20px'}),
        ])
    ], style={
        'width': '200px',
        'height': '100vh',
        'backgroundColor': '#f8f9fa',
        'position': 'fixed',
        'left': '0',
        'top': '0',
        'borderRight': '1px solid #e0e0e0'
    }),
    
    # Main content
    html.Div([
        # Top section with metrics and charts
        html.Div([
            # Line chart
            html.Div([
                dcc.Graph(
                    id='line-chart',
                    figure={
                        'data': [
                            go.Scatter(
                                x=line_data['date'],
                                y=line_data['value'],
                                mode='lines',
                                line=dict(color='#4A90E2', width=3),
                                fill='tonexty',
                                fillcolor='rgba(74, 144, 226, 0.1)'
                            )
                        ],
                        'layout': go.Layout(
                            showlegend=False,
                            xaxis=dict(showgrid=False, showticklabels=False),
                            yaxis=dict(showgrid=False, showticklabels=False),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=0, r=0, t=0, b=0),
                            height=120
                        )
                    },
                    config={'displayModeBar': False}
                )
            ], style={
                'width': '280px',
                'backgroundColor': 'white',
                'borderRadius': '15px',
                'padding': '20px',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                'margin': '20px'
            }),
            
            # Metrics
            html.Div([
                html.H1('$72,408', style={
                    'fontSize': '36px',
                    'fontWeight': 'bold',
                    'color': '#333',
                    'margin': '0'
                }),
                html.Div([
                    html.Span('↗', style={'color': '#4CAF50', 'fontSize': '20px', 'marginRight': '5px'}),
                    html.Span('17%', style={'color': '#4CAF50', 'fontSize': '24px', 'fontWeight': 'bold'})
                ], style={'margin': '10px 0'}),
                html.H2('2,534', style={
                    'fontSize': '28px',
                    'fontWeight': 'bold',
                    'color': '#666',
                    'margin': '10px 0'
                })
            ], style={
                'padding': '20px',
                'textAlign': 'center'
            })
        ], style={
            'display': 'flex',
            'alignItems': 'center'
        }),
        
        # Charts section
        html.Div([
            # Bar chart
            html.Div([
                dcc.Graph(
                    id='bar-chart',
                    figure={
                        'data': [
                            go.Bar(
                                x=categories,
                                y=bar_values,
                                marker_color='#4A90E2',
                                marker_line_width=0
                            )
                        ],
                        'layout': go.Layout(
                            showlegend=False,
                            xaxis=dict(showgrid=False),
                            yaxis=dict(showgrid=False, showticklabels=False),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=0, r=0, t=20, b=40),
                            height=200
                        )
                    },
                    config={'displayModeBar': False}
                )
            ], style={
                'width': '350px',
                'backgroundColor': 'white',
                'borderRadius': '15px',
                'padding': '20px',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                'margin': '20px'
            }),
            
            # Pie chart
            html.Div([
                dcc.Graph(
                    id='pie-chart',
                    figure={
                        'data': [
                            go.Pie(
                                labels=pie_data['category'],
                                values=pie_data['value'],
                                hole=0.6,
                                marker_colors=pie_data['colors'],
                                textinfo='none',
                                hovertemplate='<b>%{label}</b><br>%{percent}<extra></extra>'
                            )
                        ],
                        'layout': go.Layout(
                            showlegend=False,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=0, r=0, t=0, b=0),
                            height=200
                        )
                    },
                    config={'displayModeBar': False}
                )
            ], style={
                'width': '200px',
                'backgroundColor': 'white',
                'borderRadius': '15px',
                'padding': '20px',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                'margin': '20px'
            })
        ], style={
            'display': 'flex'
        }),
        
        # Filters and table section
        html.Div([
            # Filters
            html.Div([
                html.Div([
                    html.Label('Start Date', style={'marginBottom': '5px', 'display': 'block'}),
                    dcc.Dropdown(
                        id='start-date',
                        options=[
                            {'label': 'Last 30 days', 'value': '30'},
                            {'label': 'Last 90 days', 'value': '90'},
                            {'label': 'Last year', 'value': '365'}
                        ],
                        value='30',
                        style={'width': '200px'}
                    )
                ], style={'margin': '20px'}),
                
                html.Div([
                    html.Label('Category', style={'marginBottom': '5px', 'display': 'block'}),
                    dcc.Dropdown(
                        id='category',
                        options=[
                            {'label': 'All Categories', 'value': 'all'},
                            {'label': 'Stocks', 'value': 'stocks'},
                            {'label': 'Bonds', 'value': 'bonds'},
                            {'label': 'Real Estate', 'value': 'real_estate'}
                        ],
                        value='all',
                        style={'width': '200px'}
                    )
                ], style={'margin': '20px'})
            ], style={
                'display': 'flex',
                'backgroundColor': 'white',
                'borderRadius': '15px',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                'margin': '20px',
                'padding': '10px'
            }),
            
            # Data table
            html.Div([
                dash_table.DataTable(
                    id='data-table',
                    columns=[
                        {'name': 'Asset', 'id': 'Asset'},
                        {'name': 'Symbol', 'id': 'Symbol'},
                        {'name': 'Price', 'id': 'Price', 'type': 'numeric', 'format': {'specifier': '$.2f'}},
                        {'name': 'Change', 'id': 'Change', 'type': 'numeric', 'format': {'specifier': '$.2f'}},
                        {'name': 'Change %', 'id': 'Change %', 'type': 'numeric', 'format': {'specifier': '.2f'}}
                    ],
                    data=table_data.to_dict('records'),
                    style_cell={
                        'textAlign': 'left',
                        'padding': '12px',
                        'fontFamily': 'Arial, sans-serif',
                        'border': 'none'
                    },
                    style_header={
                        'backgroundColor': '#f8f9fa',
                        'fontWeight': 'bold',
                        'color': '#666'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f8f9fa'
                        }
                    ],
                    style_table={'overflowX': 'auto'}
                )
            ], style={
                'backgroundColor': 'white',
                'borderRadius': '15px',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                'margin': '20px',
                'padding': '20px'
            })
        ])
        
    ], style={
        'marginLeft': '200px',
        'backgroundColor': '#f0f2f5',
        'minHeight': '100vh',
        'fontFamily': 'Arial, sans-serif'
    })
])

# Callback for updating charts based on filters (optional enhancement)
@app.callback(
    [Output('line-chart', 'figure'),
     Output('bar-chart', 'figure')],
    [Input('start-date', 'value'),
     Input('category', 'value')]
)
def update_charts(start_date, category):
    # This is a placeholder - in a real app, you'd filter your data based on these inputs
    
    # Update line chart
    line_fig = {
        'data': [
            go.Scatter(
                x=line_data['date'],
                y=line_data['value'],
                mode='lines',
                line=dict(color='#4A90E2', width=3),
                fill='tonexty',
                fillcolor='rgba(74, 144, 226, 0.1)'
            )
        ],
        'layout': go.Layout(
            showlegend=False,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            height=120
        )
    }
    
    # Update bar chart
    bar_fig = {
        'data': [
            go.Bar(
                x=categories,
                y=bar_values,
                marker_color='#4A90E2',
                marker_line_width=0
            )
        ],
        'layout': go.Layout(
            showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=20, b=40),
            height=200
        )
    }
    
    return line_fig, bar_fig

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
