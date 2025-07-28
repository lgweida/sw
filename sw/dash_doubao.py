import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

# Initialize the Dash app
app = dash.Dash(__name__)

# Sample data for the charts (you would replace this with real data)
line_chart_data = go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[10, 12, 11, 13, 14],
    mode='lines',
    name='Line Chart'
)

bar_chart_data = go.Bar(
    x=['A', 'B', 'C', 'D', 'E'],
    y=[5, 7, 6, 8, 9],
    name='Bar Chart'
)

pie_chart_data = go.Pie(
    labels=['Label 1', 'Label 2', 'Label 3'],
    values=[30, 40, 30]
)

# Layout of the app
app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Graph(figure=go.Figure(data=[line_chart_data]), style={'width': '300px', 'height': '200px'})
        ], className='four columns'),
        html.Div([
            html.H3('$72,408'),
            html.P('Some financial metric')
        ], className='four columns'),
        html.Div([
            html.H3('17%'),
            html.P('Growth percentage')
        ], className='four columns'),
        html.Div([
            html.H3('2,534'),
            html.P('Some count metric')
        ], className='four columns')
    ], className='row'),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='start - date - dropdown',
                options=[
                    {'label': 'Option 1', 'value': 'opt1'},
                    {'label': 'Option 2', 'value': 'opt2'}
                ],
                placeholder='Start Date'
            )
        ], className='four columns'),
        html.Div([
            dcc.Dropdown(
                id='category - dropdown',
                options=[
                    {'label': 'Cat A', 'value': 'catA'},
                    {'label': 'Cat B', 'value': 'catB'}
                ],
                placeholder='Category'
            )
        ], className='four columns')
    ], className='row'),
    html.Div([
        html.Div([
            dcc.Graph(figure=go.Figure(data=[bar_chart_data]), style={'width': '400px', 'height': '300px'})
        ], className='six columns'),
        html.Div([
            dcc.Graph(figure=go.Figure(data=[pie_chart_data]), style={'width': '400px', 'height': '300px'})
        ], className='six columns')
    ], className='row')
])

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port = 8090)

