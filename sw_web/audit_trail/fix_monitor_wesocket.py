import dash
from dash import dcc, html, dash_table, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
import json
import threading
import time
from datetime import datetime, timedelta
import logging
import socket
import asyncio
import websockets
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "ULLink FIX Hub Monitor"

# Global variables for data storage
connections_data = deque(maxlen=1000)
orders_data = deque(maxlen=10000)
exec_reports_data = deque(maxlen=10000)

# Database setup
def init_db():
    conn = sqlite3.connect('fix_hub_monitor.db')
    cursor = conn.cursor()
    
    # Create connections table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS connections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        connection_type TEXT,
        status TEXT,
        ip_address TEXT,
        port INTEGER,
        connected_at TIMESTAMP,
        disconnected_at TIMESTAMP,
        last_heartbeat TIMESTAMP
    )
    ''')
    
    # Create orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        cl_ord_id TEXT,
        symbol TEXT,
        side TEXT,
        order_qty REAL,
        price REAL,
        ord_type TEXT,
        session_id TEXT,
        timestamp TIMESTAMP,
        status TEXT
    )
    ''')
    
    # Create execution reports table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS execution_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exec_id TEXT,
        order_id TEXT,
        exec_type TEXT,
        ord_status TEXT,
        last_qty REAL,
        last_px REAL,
        leaves_qty REAL,
        cum_qty REAL,
        avg_px REAL,
        session_id TEXT,
        timestamp TIMESTAMP
    )
    ''')
    
    # Create message log table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS message_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        message_type TEXT,
        message_text TEXT,
        direction TEXT,
        timestamp TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Layout components
def create_connection_status_card():
    return dbc.Card([
        dbc.CardHeader("Connection Status", className="bg-primary text-white"),
        dbc.CardBody([
            html.Div(id="connection-stats"),
            dash_table.DataTable(
                id='connections-table',
                columns=[
                    {"name": "Session ID", "id": "session_id"},
                    {"name": "Type", "id": "connection_type"},
                    {"name": "Status", "id": "status"},
                    {"name": "IP Address", "id": "ip_address"},
                    {"name": "Port", "id": "port"},
                    {"name": "Connected", "id": "connected_at"},
                    {"name": "Last HB", "id": "last_heartbeat"}
                ],
                style_table={'overflowX': 'auto'},
                page_size=10,
                filter_action="native",
                sort_action="native"
            )
        ])
    ])

def create_orders_card():
    return dbc.Card([
        dbc.CardHeader("Orders Overview", className="bg-success text-white"),
        dbc.CardBody([
            html.Div(id="order-stats"),
            dash_table.DataTable(
                id='orders-table',
                columns=[
                    {"name": "Order ID", "id": "order_id"},
                    {"name": "ClOrdID", "id": "cl_ord_id"},
                    {"name": "Symbol", "id": "symbol"},
                    {"name": "Side", "id": "side"},
                    {"name": "Qty", "id": "order_qty"},
                    {"name": "Price", "id": "price"},
                    {"name": "Type", "id": "ord_type"},
                    {"name": "Session", "id": "session_id"},
                    {"name": "Status", "id": "status"},
                    {"name": "Timestamp", "id": "timestamp"}
                ],
                style_table={'overflowX': 'auto'},
                page_size=10,
                filter_action="native",
                sort_action="native"
            )
        ])
    ])

def create_exec_reports_card():
    return dbc.Card([
        dbc.CardHeader("Execution Reports", className="bg-info text-white"),
        dbc.CardBody([
            html.Div(id="execution-stats"),
            dash_table.DataTable(
                id='executions-table',
                columns=[
                    {"name": "Exec ID", "id": "exec_id"},
                    {"name": "Order ID", "id": "order_id"},
                    {"name": "Type", "id": "exec_type"},
                    {"name": "Status", "id": "ord_status"},
                    {"name": "Last Qty", "id": "last_qty"},
                    {"name": "Last Px", "id": "last_px"},
                    {"name": "Leaves Qty", "id": "leaves_qty"},
                    {"name": "Cum Qty", "id": "cum_qty"},
                    {"name": "Avg Px", "id": "avg_px"},
                    {"name": "Session", "id": "session_id"},
                    {"name": "Timestamp", "id": "timestamp"}
                ],
                style_table={'overflowX': 'auto'},
                page_size=10,
                filter_action="native",
                sort_action="native"
            )
        ])
    ])

# App layout
app.layout = dbc.Container([
    html.H1("ULLink FIX Hub Monitor", className="text-center my-4"),
    
    # Refresh controls
    dbc.Row([
        dbc.Col([
            dbc.Button("Refresh Data", id="refresh-btn", color="primary", className="me-2"),
            dcc.Interval(id='refresh-interval', interval=5000, n_intervals=0),
            html.Div(id="last-update")
        ], width=12)
    ]),
    
    # Stats row
    dbc.Row([
        dbc.Col(create_connection_status_card(), width=12, className="my-3"),
    ]),
    
    dbc.Row([
        dbc.Col(create_orders_card(), width=6, className="my-3"),
        dbc.Col(create_exec_reports_card(), width=6, className="my-3"),
    ]),
    
    # Message log
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Message Log", className="bg-secondary text-white"),
                dbc.CardBody([
                    html.Div(id="message-log", style={
                        'height': '300px', 
                        'overflowY': 'scroll', 
                        'fontFamily': 'monospace',
                        'fontSize': '12px'
                    })
                ])
            ])
        ], width=12)
    ]),
    
    # Hidden div for storing data
    dcc.Store(id='connections-store'),
    dcc.Store(id='orders-store'),
    dcc.Store(id='executions-store')
], fluid=True)

# Callbacks
@app.callback(
    [Output('connections-table', 'data'),
     Output('orders-table', 'data'),
     Output('executions-table', 'data'),
     Output('connection-stats', 'children'),
     Output('order-stats', 'children'),
     Output('execution-stats', 'children'),
     Output('last-update', 'children'),
     Output('message-log', 'children')],
    [Input('refresh-btn', 'n_clicks'),
     Input('refresh-interval', 'n_intervals')]
)
def update_dashboard(n_clicks, n_intervals):
    # Get data from database
    conn = sqlite3.connect('fix_hub_monitor.db')
    
    # Connection stats
    connections_df = pd.read_sql('SELECT * FROM connections ORDER BY connected_at DESC', conn)
    active_connections = len(connections_df[connections_df['status'] == 'Connected'])
    
    # Order stats
    orders_df = pd.read_sql('SELECT * FROM orders ORDER BY timestamp DESC', conn)
    total_orders = len(orders_df)
    
    # Execution stats
    exec_df = pd.read_sql('SELECT * FROM execution_reports ORDER BY timestamp DESC', conn)
    total_executions = len(exec_df)
    
    # Message log
    messages_df = pd.read_sql('SELECT * FROM message_log ORDER BY timestamp DESC LIMIT 50', conn)
    message_log = []
    for _, row in messages_df.iterrows():
        message_log.append(html.Div([
            html.Span(f"[{row['timestamp']}] ", style={'color': 'gray'}),
            html.Span(f"{row['session_id']} ", style={'color': 'blue'}),
            html.Span(f"{row['direction']} ", 
                     style={'color': 'green' if row['direction'] == 'OUT' else 'red'}),
            html.Span(f"{row['message_type']}: {row['message_text']}")
        ]))
    
    conn.close()
    
    # Create stats displays
    conn_stats = html.Div([
        html.Span(f"Active: {active_connections}", className="badge bg-success me-2"),
        html.Span(f"Total: {len(connections_df)}", className="badge bg-info")
    ])
    
    order_stats = html.Div([
        html.Span(f"Total: {total_orders}", className="badge bg-success me-2"),
        html.Span(f"Today: {len(orders_df[orders_df['timestamp'] >= datetime.now().strftime('%Y-%m-%d')])}", 
                 className="badge bg-info")
    ])
    
    exec_stats = html.Div([
        html.Span(f"Total: {total_executions}", className="badge bg-success me-2"),
        html.Span(f"Today: {len(exec_df[exec_df['timestamp'] >= datetime.now().strftime('%Y-%m-%d')])}", 
                 className="badge bg-info")
    ])
    
    last_update = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return (
        connections_df.to_dict('records'),
        orders_df.to_dict('records'),
        exec_df.to_dict('records'),
        conn_stats,
        order_stats,
        exec_stats,
        last_update,
        message_log
    )

# FIX Message Processor (Mock implementation)
class FIXMessageProcessor:
    def __init__(self):
        self.running = True
        
    def process_message(self, session_id, message, direction):
        """Process FIX message and update database"""
        try:
            conn = sqlite3.connect('fix_hub_monitor.db')
            cursor = conn.cursor()
            
            # Parse basic FIX message (simplified)
            msg_type = self.get_message_type(message)
            
            # Log message
            cursor.execute('''
                INSERT INTO message_log (session_id, message_type, message_text, direction, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, msg_type, message, direction, datetime.now()))
            
            # Process different message types
            if msg_type == 'D':  # New Order Single
                self.process_new_order(session_id, message, cursor)
            elif msg_type == '8':  # Execution Report
                self.process_execution_report(session_id, message, cursor)
            elif msg_type == '0':  # Heartbeat
                self.update_heartbeat(session_id, cursor)
            elif msg_type == '1':  # Test Request
                pass  # Handle test request
            elif msg_type == '5':  # Logout
                self.update_connection_status(session_id, 'Disconnected', cursor)
            elif msg_type == 'A':  # Logon
                self.update_connection_status(session_id, 'Connected', cursor)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def get_message_type(self, message):
        """Extract message type from FIX message"""
        try:
            # Simple parsing - in real implementation, use proper FIX parser
            tags = message.split('|')
            for tag in tags:
                if tag.startswith('35='):
                    return tag.split('=')[1]
        except:
            return 'UNKNOWN'
        return 'UNKNOWN'
    
    def process_new_order(self, session_id, message, cursor):
        """Process New Order Single"""
        # Extract order details (simplified)
        order_details = self.parse_order_message(message)
        cursor.execute('''
            INSERT INTO orders (order_id, cl_ord_id, symbol, side, order_qty, price, ord_type, session_id, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_details.get('order_id', 'N/A'),
            order_details.get('cl_ord_id', 'N/A'),
            order_details.get('symbol', 'N/A'),
            order_details.get('side', 'N/A'),
            order_details.get('order_qty', 0),
            order_details.get('price', 0),
            order_details.get('ord_type', 'N/A'),
            session_id,
            datetime.now(),
            'NEW'
        ))
    
    def process_execution_report(self, session_id, message, cursor):
        """Process Execution Report"""
        # Extract execution details (simplified)
        exec_details = self.parse_execution_message(message)
        cursor.execute('''
            INSERT INTO execution_reports (exec_id, order_id, exec_type, ord_status, last_qty, last_px, leaves_qty, cum_qty, avg_px, session_id, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            exec_details.get('exec_id', 'N/A'),
            exec_details.get('order_id', 'N/A'),
            exec_details.get('exec_type', 'N/A'),
            exec_details.get('ord_status', 'N/A'),
            exec_details.get('last_qty', 0),
            exec_details.get('last_px', 0),
            exec_details.get('leaves_qty', 0),
            exec_details.get('cum_qty', 0),
            exec_details.get('avg_px', 0),
            session_id,
            datetime.now()
        ))
    
    def update_heartbeat(self, session_id, cursor):
        """Update heartbeat timestamp"""
        cursor.execute('''
            UPDATE connections SET last_heartbeat = ? WHERE session_id = ?
        ''', (datetime.now(), session_id))
    
    def update_connection_status(self, session_id, status, cursor):
        """Update connection status"""
        if status == 'Connected':
            cursor.execute('''
                INSERT OR REPLACE INTO connections (session_id, status, connected_at, last_heartbeat)
                VALUES (?, ?, ?, ?)
            ''', (session_id, status, datetime.now(), datetime.now()))
        else:
            cursor.execute('''
                UPDATE connections SET status = ?, disconnected_at = ? WHERE session_id = ?
            ''', (status, datetime.now(), session_id))
    
    def parse_order_message(self, message):
        """Parse New Order Single message (simplified)"""
        # Implement proper FIX message parsing
        return {'order_id': '123', 'cl_ord_id': 'CL123', 'symbol': 'AAPL', 'side': '1', 'order_qty': 100, 'price': 150.0, 'ord_type': '2'}
    
    def parse_execution_message(self, message):
        """Parse Execution Report message (simplified)"""
        # Implement proper FIX message parsing
        return {'exec_id': 'EX123', 'order_id': '123', 'exec_type': '0', 'ord_status': '2', 'last_qty': 100, 'last_px': 150.0, 'leaves_qty': 0, 'cum_qty': 100, 'avg_px': 150.0}

# ULLink Integration (Mock implementation)
class ULLinkMonitor:
    def __init__(self):
        self.processor = FIXMessageProcessor()
        
    def start_monitoring(self):
        """Start monitoring ULLink hub"""
        # This would connect to ULLink API or log files in real implementation
        logger.info("Starting ULLink monitoring...")
        
        # Simulate message processing
        import random
        sessions = [f"SESSION_{i}" for i in range(1, 31)]
        message_types = ['D', '8', '0', '1', '5', 'A']
        
        while self.processor.running:
            # Simulate receiving messages
            session = random.choice(sessions)
            msg_type = random.choice(message_types)
            direction = random.choice(['IN', 'OUT'])
            
            # Simulate message content
            message = f"35={msg_type}|49={session}|56=HUB|34=123|52={datetime.now().strftime('%Y%m%d-%H:%M:%S')}"
            
            self.processor.process_message(session, message, direction)
            time.sleep(0.1)  # Simulate message rate

# Start monitoring in background thread
def start_background_monitoring():
    monitor = ULLinkMonitor()
    monitor_thread = threading.Thread(target=monitor.start_monitoring, daemon=True)
    monitor_thread.start()

if __name__ == '__main__':
    # Start background monitoring
    start_background_monitoring()
    
    # Start Dash app
    app.run(debug=True, host='0.0.0.0', port=8050)
