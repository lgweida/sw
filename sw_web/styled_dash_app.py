import dash
from dash import dcc, html, Input, Output, callback_context
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
from flask import Flask, jsonify, request
import threading
import time
import json
import os
from datetime import datetime

# Create Flask server for API
server = Flask(__name__)

# Initialize domains.json file if it doesn't exist
def initialize_domains_file():
    if not os.path.exists('domains.json'):
        initial_data = {
            'domains': [
                {'id': 1, 'domain': 'adobe.com', 'category': 'Design', 'status': 'active', 'added_date': '2024-01-01'},
                {'id': 2, 'domain': 'openai.com', 'category': 'AI', 'status': 'active', 'added_date': '2024-01-02'},
                {'id': 3, 'domain': 'github.com', 'category': 'Development', 'status': 'active', 'added_date': '2024-01-03'},
                {'id': 4, 'domain': 'tailwindcss.com', 'category': 'Design', 'status': 'active', 'added_date': '2024-01-04'}
            ],
            'metrics': [
                {'date': '2024-01-01', 'value': 100, 'metric_type': 'page_views'},
                {'date': '2024-01-02', 'value': 120, 'metric_type': 'page_views'},
                {'date': '2024-01-03', 'value': 90, 'metric_type': 'page_views'},
                {'date': '2024-01-04', 'value': 150, 'metric_type': 'page_views'},
                {'date': '2024-01-05', 'value': 130, 'metric_type': 'page_views'}
            ]
        }
        with open('domains.json', 'w') as f:
            json.dump(initial_data, f, indent=2)

# Load data from domains.json
def load_data():
    try:
        with open('domains.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        initialize_domains_file()
        with open('domains.json', 'r') as f:
            return json.load(f)

# Save data to domains.json
def save_data(data):
    with open('domains.json', 'w') as f:
        json.dump(data, f, indent=2)

# Initialize the data store
initialize_domains_file()
data_store = load_data()

# Flask API Routes for Domains
@server.route('/api/domains', methods=['GET', 'POST'])
def handle_domains():
    global data_store
    data_store = load_data()  # Reload from file
    
    if request.method == 'GET':
        return jsonify(data_store['domains'])
    
    elif request.method == 'POST':
        new_domain = request.json
        new_domain['id'] = max([d['id'] for d in data_store['domains']]) + 1 if data_store['domains'] else 1
        new_domain['added_date'] = datetime.now().strftime('%Y-%m-%d')
        data_store['domains'].append(new_domain)
        save_data(data_store)
        return jsonify(new_domain), 201

@server.route('/api/domains/<int:domain_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_domain(domain_id):
    global data_store
    data_store = load_data()  # Reload from file
    domain = next((d for d in data_store['domains'] if d['id'] == domain_id), None)
    
    if request.method == 'GET':
        if domain:
            return jsonify(domain)
        return jsonify({'error': 'Domain not found'}), 404
    
    elif request.method == 'PUT':
        if domain:
            domain.update(request.json)
            save_data(data_store)
            return jsonify(domain)
        return jsonify({'error': 'Domain not found'}), 404
    
    elif request.method == 'DELETE':
        if domain:
            data_store['domains'].remove(domain)
            save_data(data_store)
            return jsonify({'message': 'Domain deleted'})
        return jsonify({'error': 'Domain not found'}), 404

@server.route('/api/metrics', methods=['GET', 'POST'])
def handle_metrics():
    global data_store
    data_store = load_data()  # Reload from file
    
    if request.method == 'GET':
        return jsonify(data_store['metrics'])
    
    elif request.method == 'POST':
        new_metric = request.json
        data_store['metrics'].append(new_metric)
        save_data(data_store)
        return jsonify(new_metric), 201

@server.route('/api/stats', methods=['GET'])
def get_stats():
    data_store = load_data()  # Reload from file
    total_domains = len(data_store['domains'])
    active_domains = len([d for d in data_store['domains'] if d.get('status') == 'active'])
    categories = {}
    for domain in data_store['domains']:
        category = domain.get('category', 'Other')
        categories[category] = categories.get(category, 0) + 1
    
    total_metrics = len(data_store['metrics'])
    avg_metric_value = sum(m['value'] for m in data_store['metrics']) / total_metrics if total_metrics > 0 else 0
    
    return jsonify({
        'total_domains': total_domains,
        'active_domains': active_domains,
        'categories': categories,
        'total_metrics': total_metrics,
        'average_metric_value': round(avg_metric_value, 2)
    })

# Create Dash app with custom CSS
app = dash.Dash(__name__, server=server, external_stylesheets=[
    'https://cdn.tailwindcss.com',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
])

# Custom CSS for enhanced styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .glass-card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            }
            .tab-content {
                animation: fadeIn 0.3s ease-in-out;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .hover-scale:hover {
                transform: scale(1.05);
                transition: transform 0.2s ease-in-out;
            }
            .gradient-text {
                background: linear-gradient(45deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .domain-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
            }
            .status-active { background-color: rgba(34, 197, 94, 0.2); color: #22c55e; }
            .status-inactive { background-color: rgba(239, 68, 68, 0.2); color: #ef4444; }
            .category-design { background-color: rgba(168, 85, 247, 0.2); color: #a855f7; }
            .category-ai { background-color: rgba(59, 130, 246, 0.2); color: #3b82f6; }
            .category-development { background-color: rgba(34, 197, 94, 0.2); color: #22c55e; }
            .category-other { background-color: rgba(156, 163, 175, 0.2); color: #9ca3af; }
        </style>
    </head>
    <body class="bg-gradient-to-br from-blue-500 via-purple-500 to-purple-700">
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Enhanced Dash layout with Tailwind styling
app.layout = html.Div(className="min-h-screen p-4 md:p-8", children=[
    # Header
    html.Div(className="text-center mb-8", children=[
        html.H1("🌐 Domain Manager Dashboard", 
                className="text-5xl font-bold text-white mb-4 gradient-text"),
        html.P("Manage and Monitor Your Website Domains with Analytics", 
               className="text-xl text-white/80 max-w-2xl mx-auto")
    ]),
    
    # Main container
    html.Div(className="max-w-7xl mx-auto glass-card p-6 md:p-8", children=[
        # Navigation Tabs
        dcc.Tabs(id="tabs", value='dashboard', className="mb-8", children=[
            dcc.Tab(label='📊 Dashboard', value='dashboard', 
                   className="text-white font-semibold px-6 py-3 mx-1 rounded-lg bg-white/10 hover:bg-white/20 transition-all"),
            dcc.Tab(label='🌐 Domains', value='domains',
                   className="text-white font-semibold px-6 py-3 mx-1 rounded-lg bg-white/10 hover:bg-white/20 transition-all"),
            dcc.Tab(label='📈 Metrics', value='metrics',
                   className="text-white font-semibold px-6 py-3 mx-1 rounded-lg bg-white/10 hover:bg-white/20 transition-all"),
            dcc.Tab(label='🔧 API Test', value='api-test',
                   className="text-white font-semibold px-6 py-3 mx-1 rounded-lg bg-white/10 hover:bg-white/20 transition-all")
        ]),
        
        # Tab content
        html.Div(id='tab-content', className='tab-content')
    ])
])

# Enhanced callback for tab content with beautiful styling
@app.callback(Output('tab-content', 'children'), [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'dashboard':
        return html.Div(className="space-y-6", children=[
            html.H2("📊 Dashboard Overview", 
                   className="text-3xl font-bold text-white mb-6 flex items-center"),
            
            # Stats cards container
            html.Div(id='stats-cards', className='grid grid-cols-1 md:grid-cols-4 gap-6 mb-8'),
            
            # Charts container
            html.Div(className="grid grid-cols-1 lg:grid-cols-2 gap-6", children=[
                html.Div(className="glass-card p-6", children=[
                    dcc.Graph(id='metrics-chart', className="w-full h-full")
                ]),
                html.Div(className="glass-card p-6", children=[
                    dcc.Graph(id='domains-chart', className="w-full h-full")
                ])
            ]),
            
            dcc.Interval(id='interval-component', interval=5000, n_intervals=0)
        ])
    
    elif tab == 'domains':
        return html.Div(className="space-y-6", children=[
            html.H2("🌐 Domain Management", 
                   className="text-3xl font-bold text-white mb-6"),
            
            # Add domain form
            html.Div(className="glass-card p-6 mb-6", children=[
                html.H3("✨ Add New Domain", 
                       className="text-xl font-semibold text-white mb-4"),
                html.Div(className="grid grid-cols-1 md:grid-cols-4 gap-4", children=[
                    dcc.Input(id='domain-name', type='text', placeholder='🌐 Domain (e.g., example.com)',
                             className='px-4 py-3 bg-white/20 text-white placeholder-white/70 rounded-lg border border-white/30 focus:border-white/60 focus:outline-none'),
                    dcc.Dropdown(id='domain-category',
                               options=[
                                   {'label': '🎨 Design', 'value': 'Design'},
                                   {'label': '🤖 AI', 'value': 'AI'},
                                   {'label': '💻 Development', 'value': 'Development'},
                                   {'label': '📱 Technology', 'value': 'Technology'},
                                   {'label': '📊 Analytics', 'value': 'Analytics'},
                                   {'label': '🛍️ E-commerce', 'value': 'E-commerce'},
                                   {'label': '📰 Media', 'value': 'Media'},
                                   {'label': '🏢 Business', 'value': 'Business'},
                                   {'label': '📚 Education', 'value': 'Education'},
                                   {'label': '🎯 Other', 'value': 'Other'}
                               ],
                               placeholder='📂 Select Category',
                               className='text-gray-800',
                               style={'borderRadius': '8px'}),
                    dcc.Dropdown(id='domain-status',
                               options=[
                                   {'label': '✅ Active', 'value': 'active'},
                                   {'label': '⏸️ Inactive', 'value': 'inactive'}
                               ],
                               value='active',
                               className='text-gray-800',
                               style={'borderRadius': '8px'}),
                    html.Button('➕ Add Domain', id='add-domain-btn',
                               className='px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold rounded-lg hover-scale shadow-lg')
                ])
            ]),
            
            # Domains table
            html.Div(className="glass-card p-6", children=[
                html.Div(id='domains-table')
            ]),
            
            html.Div(id='domain-message', className="mt-4")
        ])
    
    elif tab == 'metrics':
        return html.Div(className="space-y-6", children=[
            html.H2("📈 Metrics Management", 
                   className="text-3xl font-bold text-white mb-6"),
            
            # Add metric form
            html.Div(className="glass-card p-6 mb-6", children=[
                html.H3("📊 Add New Metric", 
                       className="text-xl font-semibold text-white mb-4"),
                html.Div(className="grid grid-cols-1 md:grid-cols-4 gap-4", children=[
                    dcc.Input(id='metric-date', type='text', placeholder='📅 Date (YYYY-MM-DD)',
                             className='px-4 py-3 bg-white/20 text-white placeholder-white/70 rounded-lg border border-white/30 focus:border-white/60 focus:outline-none'),
                    dcc.Input(id='metric-value', type='number', placeholder='🔢 Value',
                             className='px-4 py-3 bg-white/20 text-white placeholder-white/70 rounded-lg border border-white/30 focus:border-white/60 focus:outline-none'),
                    dcc.Dropdown(id='metric-type',
                               options=[
                                   {'label': '👁️ Page Views', 'value': 'page_views'},
                                   {'label': '👥 Visitors', 'value': 'visitors'},
                                   {'label': '⏱️ Session Duration', 'value': 'session_duration'},
                                   {'label': '📊 Conversion Rate', 'value': 'conversion_rate'},
                                   {'label': '💰 Revenue', 'value': 'revenue'}
                               ],
                               value='page_views',
                               className='text-gray-800',
                               style={'borderRadius': '8px'}),
                    html.Button('📊 Add Metric', id='add-metric-btn',
                               className='px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-500 text-white font-semibold rounded-lg hover-scale shadow-lg')
                ])
            ]),
            
            # Metrics table
            html.Div(className="glass-card p-6", children=[
                html.Div(id='metrics-table')
            ]),
            
            html.Div(id='metric-message', className="mt-4")
        ])
    
    elif tab == 'api-test':
        return html.Div(className="space-y-6", children=[
            html.H2("🔧 API Testing Interface", 
                   className="text-3xl font-bold text-white mb-6"),
            
            # API testing form
            html.Div(className="glass-card p-6 mb-6", children=[
                html.H3("🚀 Test API Endpoints", 
                       className="text-xl font-semibold text-white mb-4"),
                html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-4", children=[
                    dcc.Dropdown(
                        id='api-endpoint',
                        options=[
                            {'label': '🌐 GET /api/domains', 'value': 'GET /api/domains'},
                            {'label': '📊 GET /api/metrics', 'value': 'GET /api/metrics'},
                            {'label': '📈 GET /api/stats', 'value': 'GET /api/stats'}
                        ],
                        value='GET /api/domains',
                        className='text-gray-800',
                        style={'borderRadius': '8px'}
                    ),
                    html.Button('🧪 Test API', id='test-api-btn',
                               className='px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-lg hover-scale shadow-lg')
                ])
            ]),
            
            # API response
            html.Div(className="glass-card p-6", children=[
                html.H4("📝 API Response:", className="text-lg font-semibold text-white mb-4"),
                html.Pre(id='api-response', 
                        className='bg-gray-900/50 text-green-300 p-4 rounded-lg overflow-x-auto border border-white/20 font-mono text-sm',
                        children="Click 'Test API' to see response")
            ])
        ])

# Enhanced dashboard callbacks with beautiful stats cards
@app.callback([Output('stats-cards', 'children'),
               Output('metrics-chart', 'figure'),
               Output('domains-chart', 'figure')],
              [Input('interval-component', 'n_intervals')])
def update_dashboard(n):
    data_store = load_data()  # Reload from file
    
    # Enhanced stats cards with gradients and icons
    total_domains = len(data_store['domains'])
    active_domains = len([d for d in data_store['domains'] if d.get('status') == 'active'])
    categories = {}
    for domain in data_store['domains']:
        category = domain.get('category', 'Other')
        categories[category] = categories.get(category, 0) + 1
    most_common_category = max(categories.items(), key=lambda x: x[1])[0] if categories else 'None'
    
    total_metrics = len(data_store['metrics'])
    
    stats_cards = [
        html.Div(className='glass-card p-6 text-center hover-scale', children=[
            html.Div(className='text-4xl mb-2', children='🌐'),
            html.H3(f"{total_domains}", className='text-3xl font-bold text-white'),
            html.P("Total Domains", className='text-white/80 font-medium')
        ]),
        
        html.Div(className='glass-card p-6 text-center hover-scale', children=[
            html.Div(className='text-4xl mb-2', children='✅'),
            html.H3(f"{active_domains}", className='text-3xl font-bold text-white'),
            html.P("Active Domains", className='text-white/80 font-medium')
        ]),
        
        html.Div(className='glass-card p-6 text-center hover-scale', children=[
            html.Div(className='text-4xl mb-2', children='📂'),
            html.H3(f"{most_common_category}", className='text-xl font-bold text-white'),
            html.P("Top Category", className='text-white/80 font-medium')
        ]),
        
        html.Div(className='glass-card p-6 text-center hover-scale', children=[
            html.Div(className='text-4xl mb-2', children='📊'),
            html.H3(f"{total_metrics}", className='text-3xl font-bold text-white'),
            html.P("Total Metrics", className='text-white/80 font-medium')
        ])
    ]
    
    # Enhanced charts with better styling
    df_metrics = pd.DataFrame(data_store['metrics'])
    metrics_fig = px.line(df_metrics, x='date', y='value', 
                         title='📈 Metrics Trend Over Time',
                         color_discrete_sequence=['#10B981'])
    metrics_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_size=18,
        title_x=0.5
    )
    
    # Categories pie chart
    if categories:
        categories_df = pd.DataFrame(list(categories.items()), columns=['category', 'count'])
        domains_fig = px.pie(categories_df, values='count', names='category',
                           title='🌐 Domains by Category',
                           color_discrete_sequence=px.colors.qualitative.Set3)
        domains_fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_size=18,
            title_x=0.5
        )
    else:
        domains_fig = px.bar(title='🌐 No Domain Data Available')
        domains_fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
    
    return stats_cards, metrics_fig, domains_fig

# Enhanced domain management with styled tables
@app.callback([Output('domains-table', 'children'),
               Output('domain-message', 'children')],
              [Input('add-domain-btn', 'n_clicks')],
              [dash.dependencies.State('domain-name', 'value'),
               dash.dependencies.State('domain-category', 'value'),
               dash.dependencies.State('domain-status', 'value')])
def manage_domains(n_clicks, domain, category, status):
    message = ""
    
    if n_clicks and domain and category and status:
        data_store = load_data()
        new_domain = {
            'domain': domain,
            'category': category,
            'status': status,
            'added_date': datetime.now().strftime('%Y-%m-%d')
        }
        new_id = max([d['id'] for d in data_store['domains']]) + 1 if data_store['domains'] else 1
        new_domain['id'] = new_id
        data_store['domains'].append(new_domain)
        save_data(data_store)
        message = html.Div(f"✅ Domain {domain} added successfully!", 
                          className='bg-emerald-500/20 border border-emerald-400 text-emerald-200 px-4 py-3 rounded-lg')
    
    # Load current data for table
    current_data = load_data()
    
    # Styled domains table
    domains_table = html.Div(children=[
        html.H4("🌐 Current Domains", className="text-lg font-semibold text-white mb-4"),
        html.Table(className='w-full text-white', children=[
            html.Thead(children=[
                html.Tr(className='border-b border-white/20', children=[
                    html.Th('ID', className='text-left py-3 px-4 font-semibold'),
                    html.Th('Domain', className='text-left py-3 px-4 font-semibold'),
                    html.Th('Category', className='text-left py-3 px-4 font-semibold'),
                    html.Th('Status', className='text-left py-3 px-4 font-semibold'),
                    html.Th('Added Date', className='text-left py-3 px-4 font-semibold')
                ])
            ]),
            html.Tbody(children=[
                html.Tr(className='border-b border-white/10 hover:bg-white/5', children=[
                    html.Td(domain['id'], className='py-3 px-4'),
                    html.Td([
                        html.A(domain['domain'], 
                              href=f"https://{domain['domain']}", 
                              target="_blank",
                              className='text-blue-300 hover:text-blue-200 font-medium')
                    ], className='py-3 px-4'),
                    html.Td([
                        html.Span(domain['category'], 
                                className=f'domain-badge category-{domain["category"].lower()}')
                    ], className='py-3 px-4'),
                    html.Td([
                        html.Span(domain['status'].title(), 
                                className=f'domain-badge status-{domain["status"]}')
                    ], className='py-3 px-4'),
                    html.Td(domain['added_date'], className='py-3 px-4 text-white/80')
                ])
                for domain in current_data['domains']
            ])
        ])
    ])
    
    return domains_table, message

# Enhanced metrics management
@app.callback([Output('metrics-table', 'children'),
               Output('metric-message', 'children')],
              [Input('add-metric-btn', 'n_clicks')],
              [dash.dependencies.State('metric-date', 'value'),
               dash.dependencies.State('metric-value', 'value'),
               dash.dependencies.State('metric-type', 'value')])
def manage_metrics(n_clicks, date, value, metric_type):
    message = ""
    
    if n_clicks and date and value and metric_type:
        data_store = load_data()
        new_metric = {'date': date, 'value': value, 'metric_type': metric_type}
        data_store['metrics'].append(new_metric)
        save_data(data_store)
        message = html.Div(f"✅ Metric for {date} added successfully!", 
                          className='bg-blue-500/20 border border-blue-400 text-blue-200 px-4 py-3 rounded-lg')
    
    # Load current data for table
    current_data = load_data()
    
    # Styled metrics table
    metrics_table = html.Div(children=[
        html.H4("📊 Current Metrics", className="text-lg font-semibold text-white mb-4"),
        html.Table(className='w-full text-white', children=[
            html.Thead(children=[
                html.Tr(className='border-b border-white/20', children=[
                    html.Th('Date', className='text-left py-3 px-4 font-semibold'),
                    html.Th('Type', className='text-left py-3 px-4 font-semibold'),
                    html.Th('Value', className='text-left py-3 px-4 font-semibold')
                ])
            ]),
            html.Tbody(children=[
                html.Tr(className='border-b border-white/10 hover:bg-white/5', children=[
                    html.Td(metric['date'], className='py-3 px-4'),
                    html.Td(metric.get('metric_type', 'page_views').replace('_', ' ').title(), 
                           className='py-3 px-4 text-white/80'),
                    html.Td(metric['value'], className='py-3 px-4 font-medium')
                ])
                for metric in current_data['metrics']
            ])
        ])
    ])
    
    return metrics_table, message

# Enhanced API testing callback
@app.callback(Output('api-response', 'children'),
              [Input('test-api-btn', 'n_clicks')],
              [dash.dependencies.State('api-endpoint', 'value')])
def test_api(n_clicks, endpoint):
    if not n_clicks:
        return "Click 'Test API' to see response 🚀"
    
    try:
        method, url = endpoint.split(' ', 1)
        full_url = f"http://localhost:8050{url}"
        
        if method == 'GET':
            response = requests.get(full_url)
        
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == '__main__':
    print("🚀 Starting Beautiful Domain Manager with Flask REST API...")
    print("🌐 Dashboard: http://localhost:8050")
    print("📁 Data stored in: domains.json")
    print("📡 API endpoints:")
    print("  🌐 GET /api/domains - Get all domains")
    print("  ➕ POST /api/domains - Create new domain")
    print("  🔍 GET /api/domains/<id> - Get specific domain")
    print("  ✏️ PUT /api/domains/<id> - Update domain")
    print("  🗑️ DELETE /api/domains/<id> - Delete domain")
    print("  📊 GET /api/metrics - Get all metrics")
    print("  📈 POST /api/metrics - Create new metric")
    print("  📈 GET /api/stats - Get statistics")
    print("  ⚡ Auto-refresh every 5 seconds")
    
    app.run(debug=True, port=8050)