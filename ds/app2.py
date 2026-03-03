"""
FIX OEMS - Order & Execution Management System
Professional Trading Dashboard (Tailwind CSS version)
"""

from datetime import datetime
import requests
import uuid  # Added for UUID generation (missing in original snippet)

from dash import Dash, dcc, html, Input, Output, State, callback, dash_table, ctx
from dash import _dash_renderer

_dash_renderer._set_react_version("18.2.0")

# =============================================================================
# Configuration
# =============================================================================

API_BASE_URL = "http://localhost:8081/api"
REFRESH_MS = 2000

app = Dash(
    __name__,
    external_stylesheets=[],
    title="FIX OEMS - Trading Dashboard",
    suppress_callback_exceptions=True,
)

# Custom HTML template with Tailwind and Font Awesome (Light Theme)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <!-- Tailwind CSS v3 -->
        <script src="https://cdn.tailwindcss.com"></script>
        <!-- Font Awesome -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <!-- Custom Tailwind config -->
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        colors: {
                            primary: '#165DFF',
                            success: '#00d4aa',
                            danger: '#ff6b6b',
                            warning: '#ffd93d',
                            dark: {
                                900: '#111827',
                                800: '#1f2937',
                                700: '#374151',
                                600: '#4b5563',
                            }
                        },
                        fontFamily: {
                            mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'monospace'],
                            sans: ['Inter', 'system-ui', 'sans-serif'],
                        }
                    }
                }
            }
        </script>
        <style type="text/tailwindcss">
            @layer utilities {
                .content-auto {
                    content-visibility: auto;
                }
                .table-border-custom {
                    border: 1px solid rgba(0,0,0,0.06); /* Light border */
                }
                .table-header-bg {
                    background-color: rgba(0,0,0,0.04); /* Light header bg */
                }
                .btn-active {
                    @apply bg-primary text-white;
                }
                .card-hover {
                    @apply hover:shadow-lg hover:shadow-primary/10 transition-all duration-200;
                }
            }
        </style>
    </head>
    <!-- Light Theme: White background + dark text -->
    <body class="bg-white text-gray-900 font-sans min-h-screen">
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# =============================================================================
# Helpers
# =============================================================================

def safe_get_json(url: str, timeout: int = 2):
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None


def format_time(ts):
    if not ts:
        return ""
    if isinstance(ts, str):
        return ts[11:19] if len(ts) >= 19 else ts
    return str(ts)


def format_price(v):
    if v is None:
        return "MKT"
    try:
        fv = float(v)
        if fv <= 0:
            return "MKT"
        return f"${fv:.2f}"
    except Exception:
        return "MKT"


def normalize_orders_for_table(orders):
    out = []
    for o in orders or []:
        row = dict(o)
        row["timestamp"] = format_time(row.get("timestamp"))
        row["price"] = format_price(row.get("price"))
        row["filledQuantity"] = row.get("filledQuantity") or 0
        row["leavesQuantity"] = row.get("leavesQuantity")
        if row["leavesQuantity"] is None:
            row["leavesQuantity"] = row.get("quantity", 0)
        out.append(row)
    return out


def normalize_execs_for_table(execs):
    out = []
    for e in execs or []:
        row = dict(e)
        row["timestamp"] = format_time(row.get("timestamp"))

        lp = row.get("lastPrice")
        ap = row.get("avgPrice")

        try:
            row["lastPrice"] = f"${float(lp):.2f}" if lp and float(lp) > 0 else "-"
        except Exception:
            row["lastPrice"] = "-"

        try:
            row["avgPrice"] = f"${float(ap):.2f}" if ap and float(ap) > 0 else "-"
        except Exception:
            row["avgPrice"] = "-"

        out.append(row)
    return out

# =============================================================================
# Tailwind-styled UI Components (Light Theme)
# =============================================================================

def top_bar():
    return html.Div(
        # Light theme: White bg + light border/shadow
        className="sticky top-0 z-10 border-b border-gray-200 bg-white py-3 px-6 shadow-md",
        children=html.Div(
            className="container mx-auto flex items-center justify-between",
            children=[
                # Left: Logo + Title
                html.Div(
                    className="flex items-center gap-3",
                    children=[
                        html.I(className="fa-solid fa-chart-line text-xl text-primary"),
                        html.Div(
                            className="flex flex-col",
                            children=[
                                html.Span("FIX OEMS", className="font-bold text-xl tracking-tight text-gray-900"),
                                html.Span("Trading Dashboard", className="text-gray-600 text-xs tracking-wide"),
                            ]
                        ),
                    ],
                ),
                # Right: Connection status + Time
                html.Div(
                    className="flex items-center gap-6",
                    children=[
                        html.Span(
                            "DISCONNECTED",
                            id="connection-badge",
                            className="bg-danger text-white text-xs font-semibold px-4 py-1.5 rounded-full shadow-sm",
                        ),
                        html.Span(
                            id="header-time",
                            className="text-gray-600 text-sm font-mono",
                        ),
                    ],
                ),
            ],
        ),
    )


def stat_card(title, value_id, color=None):
    """Enhanced stat card with light theme styling"""
    color_map = {
        "green": "text-success",
        "yellow": "text-warning",
        "blue": "text-primary",
        "gray": "text-gray-600",
        "red": "text-danger",
    }
    
    bg_colors = {
        "green": "bg-gray-50",
        "yellow": "bg-gray-50",
        "blue": "bg-gray-50",
        "gray": "bg-gray-50",
        "red": "bg-gray-50",
        None: "bg-gray-50"
    }
    
    return html.Div(
        className=f"{bg_colors[color]} border border-gray-200 rounded-lg p-4 shadow-sm card-hover",
        children=[
            html.Div(
                title,
                className="text-xs text-gray-600 uppercase font-semibold tracking-wider mb-1"
            ),
            html.Div(
                "0",
                id=value_id,
                className=f"text-2xl font-bold mt-1 {color_map.get(color, 'text-gray-900')}"
            ),
        ],
    )


def stats_row():
    """Improved stats grid with responsive layout (light theme)"""
    return html.Div(
        className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-6",
        children=[
            stat_card("Total Orders", "stat-orders"),
            stat_card("Filled", "stat-filled", color="green"),
            stat_card("Partial", "stat-partial", color="yellow"),
            stat_card("Working", "stat-open", color="blue"),
            stat_card("Cancelled", "stat-cancelled", color="gray"),
            stat_card("Rejected", "stat-rejected", color="red"),
        ],
    )


def order_entry_panel():
    """Redesigned order entry panel with light theme styling"""
    return html.Div(
        # Light theme: White bg + light border/shadow
        className="bg-white border border-gray-200 rounded-lg p-5 shadow-md card-hover",
        children=[
            # Header
            html.Div(
                className="flex items-center gap-2 mb-5 pb-3 border-b border-gray-200",
                children=[
                    html.I(className="fa-solid fa-paper-plane text-primary"),
                    html.Span("Order Entry", className="font-bold text-lg text-gray-900")
                ],
            ),
            
            # Symbol Input
            html.Div(className="mb-4", children=[
                html.Label("Symbol", className="block text-xs text-gray-600 mb-2 font-semibold"),
                dcc.Input(
                    id="symbol-input",
                    type="text",
                    placeholder="e.g. AAPL",
                    # Light theme input styling
                    className="w-full bg-gray-50 border border-gray-300 rounded-md px-3 py-2 text-gray-900 uppercase font-bold focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all",
                ),
            ]),
            
            # Quantity + Price (two columns)
            html.Div(className="grid grid-cols-2 gap-4 mb-4", children=[
                html.Div([
                    html.Label("Quantity", className="block text-xs text-gray-600 mb-2 font-semibold"),
                    dcc.Input(
                        id="quantity-input",
                        type="number",
                        min="1",
                        step="1",
                        placeholder="Shares",
                        className="w-full bg-gray-50 border border-gray-300 rounded-md px-3 py-2 text-gray-900 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all",
                    ),
                ]),
                html.Div([
                    html.Label("Price", className="block text-xs text-gray-600 mb-2 font-semibold"),
                    dcc.Input(
                        id="price-input",
                        type="number",
                        min="0",
                        step="0.01",
                        placeholder="Limit Price",
                        className="w-full bg-gray-50 border border-gray-300 rounded-md px-3 py-2 text-gray-900 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all",
                    ),
                ]),
            ]),
            
            # Order Type dropdown
            html.Div(className="mb-4", children=[
                html.Label("Order Type", className="block text-xs text-gray-600 mb-2 font-semibold"),
                dcc.Dropdown(
                    id="order-type-select",
                    options=[
                        {"label": "LIMIT", "value": "LIMIT"},
                        {"label": "MARKET", "value": "MARKET"},
                    ],
                    value="LIMIT",
                    className="w-full bg-gray-50 border border-gray-300 rounded-md text-gray-900 outline-none",
                    style={"backgroundColor": "#f9fafb", "color": "#111827"},
                ),
            ]),

            # Network dropdown
            html.Div(className="mb-4", children=[
                html.Label(
                    className="flex items-center gap-1.5 text-xs text-gray-600 mb-2 font-semibold",
                    children=[
                        html.I(className="fa-solid fa-network-wired text-primary/70"),
                        html.Span("Network"),
                    ],
                ),
                dcc.Dropdown(
                    id="network-select",
                    options=[
                        {"label": "🔷 Bloomberg",  "value": "BLOOMBERG"},
                        {"label": "⬛ NYFIX",      "value": "NYFIX"},
                        {"label": "🟦 Sungard",    "value": "SUNGARD"},
                        {"label": "🟩 Fidessa",    "value": "FIDESSA"},
                        {"label": "🟧 TradeWare",  "value": "TRADEWARE"},
                        {"label": "🟪 TradeWeb",   "value": "TRADEWEB"},
                        {"label": "⬜ CRD",        "value": "CRD"},
                    ],
                    placeholder="Select network…",
                    clearable=True,
                    className="w-full",
                    style={"backgroundColor": "#f9fafb", "color": "#111827"},
                ),
            ]),

            # Broker Code dropdown (Bloomberg only)
            html.Div(
                id="broker-code-wrapper",
                style={"display": "none"},
                className="mb-4",
                children=[
                    html.Label(
                        className="flex items-center gap-1.5 text-xs text-gray-600 mb-2 font-semibold",
                        children=[
                            html.I(className="fa-solid fa-building-columns text-primary/70"),
                            html.Span("Broker Code"),
                            html.Span("*", className="text-danger ml-0.5"),
                        ],
                    ),
                    dcc.Dropdown(
                        id="broker-code-select",
                        options=[
                            {"label": "MZUL — UBS Lux",            "value": "MZUL"},
                            {"label": "MZOP — OpCo",                "value": "MZOP"},
                            {"label": "MZPT — Portugal",            "value": "MZPT"},
                            {"label": "IMET — iMeta Technologies",  "value": "IMET"},
                        ],
                        placeholder="Select broker code…",
                        clearable=True,
                        className="w-full",
                        style={"backgroundColor": "#f9fafb", "color": "#111827"},
                    ),
                ],
            ),

            # Bloomberg UUID field
            html.Div(
                id="uuid-wrapper",
                style={"display": "none"},
                className="mb-5",
                children=[
                    html.Label(
                        className="flex items-center gap-1.5 text-xs text-gray-600 mb-2 font-semibold",
                        children=[
                            html.I(className="fa-solid fa-fingerprint text-primary/70"),
                            html.Span("Bloomberg UUID"),
                            html.Span("*", className="text-danger ml-0.5"),
                        ],
                    ),
                    html.Div(
                        className="relative flex items-center gap-2",
                        children=[
                            dcc.Input(
                                id="uuid-input",
                                type="text",
                                placeholder="e.g. 123e4567-e89b-12d3-a456-426614174000",
                                className="w-full bg-gray-50 border border-gray-300 rounded-md px-3 py-2 text-gray-900 font-mono text-xs focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all",
                            ),
                            html.Button(
                                html.I(className="fa-solid fa-rotate text-xs"),
                                id="uuid-generate-btn",
                                title="Generate new UUID",
                                className="shrink-0 bg-gray-200 hover:bg-primary text-gray-700 hover:text-white px-2.5 py-2 rounded-md transition-all",
                            ),
                        ],
                    ),
                    html.Div(
                        "Auto-populated — edit or regenerate as needed",
                        className="text-xs text-gray-500 mt-1",
                    ),
                ],
            ),

            # OnBehalfOfCompID — tag 116 (NYFIX / TradeWare / TradeWeb)
            html.Div(
                id="onbehalf-wrapper",
                style={"display": "none"},
                className="mb-5",
                children=[
                    html.Label(
                        className="flex items-center gap-1.5 text-xs text-gray-600 mb-2 font-semibold",
                        children=[
                            html.I(className="fa-solid fa-id-badge text-warning/70"),
                            html.Span("OnBehalfOfCompID"),
                            html.Span(" (tag 116)", className="text-gray-500 font-normal ml-1"),
                            html.Span("*", className="text-danger ml-0.5"),
                        ],
                    ),
                    dcc.Input(
                        id="onbehalf-input",
                        type="text",
                        placeholder="e.g. CLIENTFIRM1",
                        className="w-full bg-gray-50 border border-warning/30 rounded-md px-3 py-2 text-gray-900 font-mono text-xs focus:ring-2 focus:ring-warning/40 focus:border-warning/60 outline-none transition-all",
                    ),
                    html.Div(
                        "Required for routing via this network",
                        className="text-xs text-gray-500 mt-1",
                    ),
                ],
            ),
            
            # Buy/Sell buttons
            html.Div(className="grid grid-cols-2 gap-4 mb-3", children=[
                html.Button(
                    "BUY",
                    id="buy-btn",
                    className="bg-success hover:bg-success/90 text-white font-bold py-2.5 px-4 rounded-md shadow-sm hover:shadow-md transition-all active:scale-95",
                ),
                html.Button(
                    "SELL",
                    id="sell-btn",
                    className="bg-danger hover:bg-danger/90 text-white font-bold py-2.5 px-4 rounded-md shadow-sm hover:shadow-md transition-all active:scale-95",
                ),
            ]),
            
            # Status message
            html.Div(id="order-status-msg", className="mt-2 text-sm rounded-md p-2"),
        ],
    )


def order_actions_panel():
    """Redesigned order actions panel (light theme)"""
    return html.Div(
        className="bg-white border border-gray-200 rounded-lg p-5 shadow-md card-hover",
        children=[
            # Header
            html.Div(
                className="flex items-center gap-2 mb-5 pb-3 border-b border-gray-200",
                children=[
                    html.I(className="fa-solid fa-pen-to-square text-primary"),
                    html.Span("Order Actions", className="font-bold text-lg text-gray-900")
                ],
            ),
            
            # Selected order info (two columns)
            html.Div(className="grid grid-cols-2 gap-4 mb-4", children=[
                html.Div([
                    html.Label("ClOrdId", className="block text-xs text-gray-600 mb-2 font-semibold"),
                    dcc.Input(
                        id="action-clordid", 
                        disabled=True, 
                        className="w-full bg-gray-50/70 border border-gray-300 rounded-md px-3 py-2 text-gray-900 opacity-80 cursor-not-allowed"
                    ),
                ]),
                html.Div([
                    html.Label("Symbol", className="block text-xs text-gray-600 mb-2 font-semibold"),
                    dcc.Input(
                        id="action-symbol", 
                        disabled=True, 
                        className="w-full bg-gray-50/70 border border-gray-300 rounded-md px-3 py-2 text-gray-900 opacity-80 cursor-not-allowed"
                    ),
                ]),
            ]),
            
            # Side + New Qty + New Price (three columns)
            html.Div(className="grid grid-cols-3 gap-4 mb-4", children=[
                html.Div([
                    html.Label("Side", className="block text-xs text-gray-600 mb-2 font-semibold"),
                    dcc.Dropdown(
                        id="action-side",
                        options=[{"label": "BUY", "value": "BUY"}, {"label": "SELL", "value": "SELL"}],
                        disabled=True,
                        className="w-full bg-gray-50 border border-gray-300 rounded-md text-gray-900 outline-none",
                        style={"backgroundColor": "#f9fafb", "color": "#111827"},
                    ),
                ]),
                html.Div([
                    html.Label("New Qty", className="block text-xs text-gray-600 mb-2 font-semibold"),
                    dcc.Input(
                        id="action-qty",
                        type="number",
                        min="1",
                        step="1",
                        placeholder="Update Qty",
                        className="w-full bg-gray-50 border border-gray-300 rounded-md px-3 py-2 text-gray-900 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all",
                    ),
                ]),
                html.Div([
                    html.Label("New Price", className="block text-xs text-gray-600 mb-2 font-semibold"),
                    dcc.Input(
                        id="action-price",
                        type="number",
                        min="0",
                        step="0.01",
                        placeholder="Update Price",
                        className="w-full bg-gray-50 border border-gray-300 rounded-md px-3 py-2 text-gray-900 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all",
                    ),
                ]),
            ]),
            
            # Action buttons (Amend/Cancel/Clear)
            html.Div(className="grid grid-cols-3 gap-4 mb-3", children=[
                html.Button(
                    "AMEND ORDER",
                    id="amend-btn",
                    className="bg-primary hover:bg-primary/90 text-white font-bold py-2 px-4 rounded-md shadow-sm hover:shadow-md transition-all active:scale-95 text-sm",
                ),
                html.Button(
                    "CANCEL ORDER",
                    id="cancel-btn",
                    className="bg-danger hover:bg-danger/90 text-white font-bold py-2 px-4 rounded-md shadow-sm hover:shadow-md transition-all active:scale-95 text-sm",
                ),
                html.Button(
                    "CLEAR",
                    id="clear-action-btn",
                    className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded-md shadow-sm hover:shadow-md transition-all active:scale-95 text-sm",
                ),
            ]),
            
            # Action status message
            html.Div(id="action-status-msg", className="mt-2 text-sm rounded-md p-2"),
        ],
    )


def orders_table():
    """Orders table with light theme styling"""
    return html.Div(
        className="bg-white border border-gray-200 rounded-lg shadow-md card-hover",
        children=[
            html.Div(
                className="flex items-center justify-between p-5 border-b border-gray-200",
                children=[
                    html.Div(
                        className="flex items-center gap-2",
                        children=[
                            html.I(className="fa-solid fa-list-ol text-primary"),
                            html.Span("Active Orders", className="font-bold text-lg text-gray-900"),
                        ]
                    ),
                    dcc.Interval(
                        id="orders-refresh-interval",
                        interval=REFRESH_MS,
                        n_intervals=0,
                    ),
                ]
            ),
            html.Div(
                className="p-4 overflow-x-auto",
                children=dash_table.DataTable(
                    id="orders-table",
                    columns=[
                        {"name": "ClOrdId", "id": "clOrdId"},
                        {"name": "Symbol", "id": "symbol"},
                        {"name": "Side", "id": "side"},
                        {"name": "Qty", "id": "quantity"},
                        {"name": "Price", "id": "price"},
                        {"name": "Filled", "id": "filledQuantity"},
                        {"name": "Leaves", "id": "leavesQuantity"},
                        {"name": "Status", "id": "orderStatus"},
                        {"name": "Time", "id": "timestamp"},
                        {"name": "Network", "id": "network"},
                    ],
                    data=[],
                    page_size=10,
                    style_header={
                        "backgroundColor": "rgba(0,0,0,0.04)",
                        "color": "#111827",
                        "fontWeight": "bold",
                        "fontSize": "0.75rem",
                        "textTransform": "uppercase",
                        "borderBottom": "1px solid rgba(0,0,0,0.06)",
                        "padding": "12px 8px",
                    },
                    style_cell={
                        "backgroundColor": "white",
                        "color": "#111827",
                        "fontSize": "0.75rem",
                        "padding": "10px 8px",
                        "border": "1px solid rgba(0,0,0,0.06)",
                        "whiteSpace": "nowrap",
                    },
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "rgba(0,0,0,0.02)",
                        }
                    ],
                    style_table={"overflowX": "auto"},
                    row_selectable="single",
                    selected_rows=[],
                ),
            ),
        ],
    )


def executions_table():
    """Executions table with light theme styling"""
    return html.Div(
        className="bg-white border border-gray-200 rounded-lg shadow-md card-hover",
        children=[
            html.Div(
                className="flex items-center justify-between p-5 border-b border-gray-200",
                children=[
                    html.Div(
                        className="flex items-center gap-2",
                        children=[
                            html.I(className="fa-solid fa-check-double text-primary"),
                            html.Span("Executions", className="font-bold text-lg text-gray-900"),
                        ]
                    ),
                    dcc.Interval(
                        id="execs-refresh-interval",
                        interval=REFRESH_MS,
                        n_intervals=0,
                    ),
                ]
            ),
            html.Div(
                className="p-4 overflow-x-auto",
                children=dash_table.DataTable(
                    id="execs-table",
                    columns=[
                        {"name": "ExecID", "id": "execId"},
                        {"name": "ClOrdId", "id": "clOrdId"},
                        {"name": "Symbol", "id": "symbol"},
                        {"name": "Side", "id": "side"},
                        {"name": "Last Qty", "id": "lastQty"},
                        {"name": "Last Price", "id": "lastPrice"},
                        {"name": "Avg Price", "id": "avgPrice"},
                        {"name": "Cum Qty", "id": "cumQty"},
                        {"name": "Time", "id": "timestamp"},
                        {"name": "Network", "id": "network"},
                    ],
                    data=[],
                    page_size=10,
                    style_header={
                        "backgroundColor": "rgba(0,0,0,0.04)",
                        "color": "#111827",
                        "fontWeight": "bold",
                        "fontSize": "0.75rem",
                        "textTransform": "uppercase",
                        "borderBottom": "1px solid rgba(0,0,0,0.06)",
                        "padding": "12px 8px",
                    },
                    style_cell={
                        "backgroundColor": "white",
                        "color": "#111827",
                        "fontSize": "0.75rem",
                        "padding": "10px 8px",
                        "border": "1px solid rgba(0,0,0,0.06)",
                        "whiteSpace": "nowrap",
                    },
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "rgba(0,0,0,0.02)",
                        }
                    ],
                    style_table={"overflowX": "auto"},
                ),
            ),
        ],
    )


# =============================================================================
# Main Layout
# =============================================================================

app.layout = html.Div(
    className="min-h-screen",
    children=[
        top_bar(),
        html.Div(
            className="container mx-auto px-4 py-6",
            children=[
                # Stats Row
                stats_row(),
                
                # Main Grid (Order Entry + Actions | Tables)
                html.Div(
                    className="grid grid-cols-1 lg:grid-cols-3 gap-6",
                    children=[
                        # Left Column (Order Entry + Actions)
                        html.Div(
                            className="grid grid-cols-1 gap-6",
                            children=[
                                order_entry_panel(),
                                order_actions_panel(),
                            ]
                        ),
                        
                        # Right Column (Tables)
                        html.Div(
                            className="lg:col-span-2 grid grid-cols-1 gap-6",
                            children=[
                                orders_table(),
                                executions_table(),
                            ]
                        ),
                    ],
                ),
            ],
        ),
    ],
)

# =============================================================================
# Callbacks (Core Functionality)
# =============================================================================

# Update header time
@callback(
    Output("header-time", "children"),
    Input("orders-refresh-interval", "n_intervals")
)
def update_header_time(n):
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

# Generate UUID
@callback(
    Output("uuid-input", "value"),
    Input("uuid-generate-btn", "n_clicks"),
    prevent_initial_call=True
)
def generate_uuid(n_clicks):
    return str(uuid.uuid4())

# Show/hide Bloomberg-specific fields
@callback(
    Output("broker-code-wrapper", "style"),
    Output("uuid-wrapper", "style"),
    Input("network-select", "value")
)
def toggle_bloomberg_fields(selected_network):
    if selected_network == "BLOOMBERG":
        return {"display": "block"}, {"display": "block"}
    return {"display": "none"}, {"display": "none"}

# Show/hide OnBehalfOfCompID (NYFIX/TradeWare/TradeWeb)
@callback(
    Output("onbehalf-wrapper", "style"),
    Input("network-select", "value")
)
def toggle_onbehalf_field(selected_network):
    if selected_network in ["NYFIX", "TRADEWARE", "TRADEWEB"]:
        return {"display": "block"}
    return {"display": "none"}

# Populate order actions form when row is selected
@callback(
    Output("action-clordid", "value"),
    Output("action-symbol", "value"),
    Output("action-side", "value"),
    Output("action-qty", "value"),
    Output("action-price", "value"),
    Input("orders-table", "selected_rows"),
    State("orders-table", "data")
)
def populate_order_actions(selected_rows, orders_data):
    if not selected_rows or not orders_data:
        return "", "", "", "", ""
    
    selected_row = orders_data[selected_rows[0]]
    return (
        selected_row.get("clOrdId", ""),
        selected_row.get("symbol", ""),
        selected_row.get("side", ""),
        selected_row.get("quantity", ""),
        selected_row.get("price", "").replace("$", "") if selected_row.get("price") != "MKT" else "",
    )

# Refresh orders table
@callback(
    Output("orders-table", "data"),
    Input("orders-refresh-interval", "n_intervals")
)
def refresh_orders(n):
    orders = safe_get_json(f"{API_BASE_URL}/orders")
    return normalize_orders_for_table(orders)

# Refresh executions table
@callback(
    Output("execs-table", "data"),
    Input("execs-refresh-interval", "n_intervals")
)
def refresh_executions(n):
    execs = safe_get_json(f"{API_BASE_URL}/executions")
    return normalize_execs_for_table(execs)

# Update order stats
@callback(
    Output("stat-orders", "children"),
    Output("stat-filled", "children"),
    Output("stat-partial", "children"),
    Output("stat-open", "children"),
    Output("stat-cancelled", "children"),
    Output("stat-rejected", "children"),
    Input("orders-refresh-interval", "n_intervals"),
    State("orders-table", "data")
)
def update_order_stats(n, orders_data):
    total = len(orders_data)
    filled = 0
    partial = 0
    open_ = 0
    cancelled = 0
    rejected = 0
    
    for order in orders_data:
        status = order.get("orderStatus", "").upper()
        if status == "FILLED":
            filled += 1
        elif status == "PARTIALLY_FILLED":
            partial += 1
        elif status in ["NEW", "PARTIALLY_FILLED", "WORKING"]:
            open_ += 1
        elif status == "CANCELLED":
            cancelled += 1
        elif status == "REJECTED":
            rejected += 1
    
    return total, filled, partial, open_, cancelled, rejected

# Submit new order (Buy/Sell)
@callback(
    Output("order-status-msg", "children"),
    Output("order-status-msg", "className"),
    Input("buy-btn", "n_clicks"),
    Input("sell-btn", "n_clicks"),
    State("symbol-input", "value"),
    State("quantity-input", "value"),
    State("price-input", "value"),
    State("order-type-select", "value"),
    State("network-select", "value"),
    State("broker-code-select", "value"),
    State("uuid-input", "value"),
    State("onbehalf-input", "value"),
    prevent_initial_call=True
)
def submit_order(buy_clicks, sell_clicks, symbol, qty, price, ord_type, network, broker_code, uuid_val, onbehalf):
    # Determine side (Buy/Sell)
    trigger = ctx.triggered_id
    if not trigger:
        return "No action selected", "mt-2 text-sm text-danger bg-red-50 rounded-md p-2"
    
    side = "BUY" if trigger == "buy-btn" else "SELL"
    
    # Validate required fields
    errors = []
    if not symbol:
        errors.append("Symbol is required")
    if not qty or int(qty) <= 0:
        errors.append("Valid quantity (≥1) is required")
    if ord_type == "LIMIT" and (not price or float(price) <= 0):
        errors.append("Valid limit price (≥0.01) is required")
    if not network:
        errors.append("Network is required")
    
    # Network-specific validation
    if network == "BLOOMBERG":
        if not broker_code:
            errors.append("Broker Code is required for Bloomberg")
        if not uuid_val:
            errors.append("Bloomberg UUID is required")
    if network in ["NYFIX", "TRADEWARE", "TRADEWEB"] and not onbehalf:
        errors.append("OnBehalfOfCompID is required for this network")
    
    if errors:
        return (
            f"❌ Error: {', '.join(errors)}",
            "mt-2 text-sm text-danger bg-red-50 rounded-md p-2"
        )
    
    # Prepare order payload
    order_payload = {
        "clOrdId": str(uuid.uuid4()),  # Generate unique ClOrdId
        "symbol": symbol.upper(),
        "side": side,
        "quantity": int(qty),
        "orderType": ord_type,
        "price": float(price) if ord_type == "LIMIT" else 0,
        "network": network,
        "brokerCode": broker_code,
        "bloombergUUID": uuid_val,
        "onBehalfOfCompID": onbehalf,
        "timestamp": datetime.now().isoformat()
    }
    
    # Submit order to API (mock for demo)
    try:
        # Replace with actual API call: requests.post(f"{API_BASE_URL}/orders", json=order_payload)
        return (
            f"✅ {side} order for {qty} {symbol} submitted successfully (ClOrdId: {order_payload['clOrdId'][:8]}...)",
            "mt-2 text-sm text-success bg-green-50 rounded-md p-2"
        )
    except Exception as e:
        return (
            f"❌ Failed to submit order: {str(e)}",
            "mt-2 text-sm text-danger bg-red-50 rounded-md p-2"
        )

# Amend/Cancel order
@callback(
    Output("action-status-msg", "children"),
    Output("action-status-msg", "className"),
    Input("amend-btn", "n_clicks"),
    Input("cancel-btn", "n_clicks"),
    Input("clear-action-btn", "n_clicks"),
    State("action-clordid", "value"),
    State("action-symbol", "value"),
    State("action-qty", "value"),
    State("action-price", "value"),
    prevent_initial_call=True
)
def process_order_action(amend_clicks, cancel_clicks, clear_clicks, clordid, symbol, new_qty, new_price):
    trigger = ctx.triggered_id
    
    # Clear action form
    if trigger == "clear-action-btn":
        return "", "mt-2 text-sm rounded-md p-2"
    
    # Validate ClOrdId is present
    if not clordid:
        return (
            "❌ Error: Select an order from the table first",
            "mt-2 text-sm text-danger bg-red-50 rounded-md p-2"
        )
    
    # Amend order
    if trigger == "amend-btn":
        if not new_qty or int(new_qty) <= 0:
            return (
                "❌ Error: Valid new quantity (≥1) is required",
                "mt-2 text-sm text-danger bg-red-50 rounded-md p-2"
            )
        
        # Mock API call for amend
        try:
            # requests.put(f"{API_BASE_URL}/orders/{clordid}", json={"quantity": int(new_qty), "price": float(new_price) if new_price else 0})
            return (
                f"✅ Order {clordid[:8]}... amended: {new_qty} shares (new price: {new_price or 'MKT'})",
                "mt-2 text-sm text-success bg-green-50 rounded-md p-2"
            )
        except Exception as e:
            return (
                f"❌ Failed to amend order: {str(e)}",
                "mt-2 text-sm text-danger bg-red-50 rounded-md p-2"
            )
    
    # Cancel order
    if trigger == "cancel-btn":
        # Mock API call for cancel
        try:
            # requests.delete(f"{API_BASE_URL}/orders/{clordid}")
            return (
                f"✅ Order {clordid[:8]}... cancelled successfully",
                "mt-2 text-sm text-success bg-green-50 rounded-md p-2"
            )
        except Exception as e:
            return (
                f"❌ Failed to cancel order: {str(e)}",
                "mt-2 text-sm text-danger bg-red-50 rounded-md p-2"
            )
    
    return "Unknown action", "mt-2 text-sm text-warning bg-yellow-50 rounded-md p-2"

# Update connection status (mock)
@callback(
    Output("connection-badge", "children"),
    Output("connection-badge", "className"),
    Input("orders-refresh-interval", "n_intervals")
)
def update_connection_status(n):
    # Mock connection check (replace with real API health check)
    is_connected = safe_get_json(f"{API_BASE_URL}/health") is not None
    
    if is_connected:
        return (
            "CONNECTED",
            "bg-success text-white text-xs font-semibold px-4 py-1.5 rounded-full shadow-sm"
        )
    return (
        "DISCONNECTED",
        "bg-danger text-white text-xs font-semibold px-4 py-1.5 rounded-full shadow-sm"
    )

# =============================================================================
# Run App
# =============================================================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)