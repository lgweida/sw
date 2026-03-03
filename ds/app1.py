"""
FIX OEMS - Order & Execution Management System
Professional Trading Dashboard (Tailwind CSS version)
"""

from datetime import datetime
import requests

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

# Custom HTML template with Tailwind and Font Awesome
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
                    border: 1px solid rgba(255,255,255,0.06);
                }
                .table-header-bg {
                    background-color: rgba(255,255,255,0.04);
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
    <body class="bg-dark-900 text-white font-sans min-h-screen">
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
# Helpers (unchanged)
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
# Tailwind-styled UI Components
# =============================================================================

def top_bar():
    return html.Div(
        className="sticky top-0 z-10 border-b border-dark-700 bg-dark-800 py-3 px-6 shadow-md",
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
                                html.Span("FIX OEMS", className="font-bold text-xl tracking-tight"),
                                html.Span("Trading Dashboard", className="text-gray-400 text-xs tracking-wide"),
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
                            className="text-gray-400 text-sm font-mono",
                        ),
                    ],
                ),
            ],
        ),
    )


def stat_card(title, value_id, color=None):
    """Enhanced stat card with better styling"""
    color_map = {
        "green": "text-success",
        "yellow": "text-warning",
        "blue": "text-primary",
        "gray": "text-gray-400",
        "red": "text-danger",
    }
    
    bg_colors = {
        "green": "bg-dark-800/80",
        "yellow": "bg-dark-800/80",
        "blue": "bg-dark-800/80",
        "gray": "bg-dark-800/80",
        "red": "bg-dark-800/80",
        None: "bg-dark-800/80"
    }
    
    return html.Div(
        className=f"{bg_colors[color]} border border-dark-700 rounded-lg p-4 shadow-sm card-hover",
        children=[
            html.Div(
                title,
                className="text-xs text-gray-400 uppercase font-semibold tracking-wider mb-1"
            ),
            html.Div(
                "0",
                id=value_id,
                className=f"text-2xl font-bold mt-1 {color_map.get(color, 'text-white')}"
            ),
        ],
    )


def stats_row():
    """Improved stats grid with responsive layout"""
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
    """Redesigned order entry panel with better spacing and styling"""
    return html.Div(
        className="bg-dark-800 border border-dark-700 rounded-lg p-5 shadow-md card-hover",
        children=[
            # Header
            html.Div(
                className="flex items-center gap-2 mb-5 pb-3 border-b border-dark-700",
                children=[
                    html.I(className="fa-solid fa-paper-plane text-primary"),
                    html.Span("Order Entry", className="font-bold text-lg")
                ],
            ),
            
            # Symbol Input
            html.Div(className="mb-4", children=[
                html.Label("Symbol", className="block text-xs text-red-400 mb-2 font-semibold"),
                dcc.Input(
                    id="symbol-input",
                    type="text",
                    placeholder="e.g. AAPL",
                    className="w-full bg-dark-700 border border-dark-600 rounded-md px-3 py-2 text-white uppercase font-bold focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all",
                ),
            ]),
            
            # Quantity + Price (two columns)
            html.Div(className="grid grid-cols-2 gap-4 mb-4", children=[
                html.Div([
                    html.Label("Quantity", className="block text-xs text-gray-400 mb-2 font-semibold"),
                    dcc.Input(
                        id="quantity-input",
                        type="number",
                        min="1",
                        step="1",
                        placeholder="Shares",
                        className="w-full bg-dark-700 border border-dark-600 rounded-md px-3 py-2 text-white focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all",
                    ),
                ]),
                html.Div([
                    html.Label("Price", className="block text-xs text-gray-400 mb-2 font-semibold"),
                    dcc.Input(
                        id="price-input",
                        type="number",
                        min="0",
                        step="0.01",
                        placeholder="Limit Price",
                        className="w-full bg-dark-700 border border-dark-600 rounded-md px-3 py-2 text-white focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all",
                    ),
                ]),
            ]),
            
            # Order Type dropdown
            html.Div(className="mb-4", children=[
                html.Label("Order Type", className="block text-xs text-gray-400 mb-2 font-semibold"),
                dcc.Dropdown(
                    id="order-type-select",
                    options=[
                        {"label": "LIMIT", "value": "LIMIT"},
                        {"label": "MARKET", "value": "MARKET"},
                    ],
                    value="LIMIT",
                    className="w-full bg-dark-700 border border-dark-600 rounded-md text-white outline-none",
                    style={"backgroundColor": "#374151", "color": "white"},
                ),
            ]),

            # Network dropdown
            html.Div(className="mb-4", children=[
                html.Label(
                    className="flex items-center gap-1.5 text-xs text-gray-400 mb-2 font-semibold",
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
                    style={"backgroundColor": "#374151", "color": "white"},
                ),
            ]),

            # Broker Code dropdown (Bloomberg only)
            html.Div(
                id="broker-code-wrapper",
                style={"display": "none"},
                className="mb-4",
                children=[
                    html.Label(
                        className="flex items-center gap-1.5 text-xs text-primary mb-2 font-semibold",
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
                        style={"backgroundColor": "#374151", "color": "white"},
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
                        className="flex items-center gap-1.5 text-xs text-primary mb-2 font-semibold",
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
                                className="w-full bg-dark-700 border border-dark-600 rounded-md px-3 py-2 text-white font-mono text-xs focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all",
                            ),
                            html.Button(
                                html.I(className="fa-solid fa-rotate text-xs"),
                                id="uuid-generate-btn",
                                title="Generate new UUID",
                                className="shrink-0 bg-dark-600 hover:bg-primary text-gray-300 hover:text-white px-2.5 py-2 rounded-md transition-all",
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
                        className="flex items-center gap-1.5 text-xs text-warning mb-2 font-semibold",
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
                        className="w-full bg-dark-700 border border-warning/30 rounded-md px-3 py-2 text-white font-mono text-xs focus:ring-2 focus:ring-warning/40 focus:border-warning/60 outline-none transition-all",
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
    """Redesigned order actions panel"""
    return html.Div(
        className="bg-dark-800 border border-dark-700 rounded-lg p-5 shadow-md card-hover",
        children=[
            # Header
            html.Div(
                className="flex items-center gap-2 mb-5 pb-3 border-b border-dark-700",
                children=[
                    html.I(className="fa-solid fa-pen-to-square text-primary"),
                    html.Span("Order Actions", className="font-bold text-lg")
                ],
            ),
            
            # Selected order info (two columns)
            html.Div(className="grid grid-cols-2 gap-4 mb-4", children=[
                html.Div([
                    html.Label("ClOrdId", className="block text-xs text-gray-400 mb-2 font-semibold"),
                    dcc.Input(
                        id="action-clordid", 
                        disabled=True, 
                        className="w-full bg-dark-700/70 border border-dark-600 rounded-md px-3 py-2 text-white opacity-80 cursor-not-allowed"
                    ),
                ]),
                html.Div([
                    html.Label("Symbol", className="block text-xs text-gray-400 mb-2 font-semibold"),
                    dcc.Input(
                        id="action-symbol", 
                        disabled=True, 
                        className="w-full bg-dark-700/70 border border-dark-600 rounded-md px-3 py-2 text-white opacity-80 cursor-not-allowed"
                    ),
                ]),
            ]),
            
            # Side + New Qty + New Price (three columns)
            html.Div(className="grid grid-cols-3 gap-4 mb-4", children=[
                html.Div([
                    html.Label("Side", className="block text-xs text-gray-400 mb-2 font-semibold"),
                    dcc.Input(
                        id="action-side", 
                        disabled=True, 
                        className="w-full bg-dark-700/70 border border-dark-600 rounded-md px-3 py-2 text-white opacity-80 cursor-not-allowed"
                    ),
                ]),
                html.Div([
                    html.Label("New Qty", className="block text-xs text-gray-400 mb-2 font-semibold"),
                    dcc.Input(
                        id="amend-qty",
                        type="number",
                        min="1",
                        step="1",
                        placeholder="New Qty",
                        className="w-full bg-dark-700 border border-dark-600 rounded-md px-3 py-2 text-white focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all",
                    ),
                ]),
                html.Div([
                    html.Label("New Price", className="block text-xs text-gray-400 mb-2 font-semibold"),
                    dcc.Input(
                        id="amend-price",
                        type="number",
                        min="0",
                        step="0.01",
                        placeholder="New Price",
                        className="w-full bg-dark-700 border border-dark-600 rounded-md px-3 py-2 text-white focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all",
                    ),
                ]),
            ]),
            
            # Amend/Cancel buttons
            html.Div(className="grid grid-cols-2 gap-4 mb-3", children=[
                html.Button(
                    "Amend",
                    id="amend-btn",
                    className="bg-warning hover:bg-warning/90 text-dark-900 font-bold py-2.5 px-4 rounded-md shadow-sm hover:shadow-md transition-all active:scale-95",
                ),
                html.Button(
                    "Cancel",
                    id="cancel-btn",
                    className="bg-danger hover:bg-danger/90 text-white font-bold py-2.5 px-4 rounded-md shadow-sm hover:shadow-md transition-all active:scale-95",
                ),
            ]),
            
            # Status message
            html.Div(id="action-status-msg", className="mt-2 text-sm rounded-md p-2"),
        ],
    )


def orders_blotter():
    """Redesigned orders blotter with improved table styling"""
    return html.Div(
        className="bg-dark-800 border border-dark-700 rounded-lg p-5 shadow-md card-hover",
        children=[
            # Header with filter
            html.Div(
                className="flex flex-wrap items-center justify-between mb-5 pb-3 border-b border-dark-700 gap-3",
                children=[
                    html.Div(
                        className="flex items-center gap-2",
                        children=[
                            html.I(className="fa-solid fa-list text-primary"),
                            html.Span("Orders Blotter", className="font-bold text-lg")
                        ],
                    ),
                    
                    # Filter buttons
                    html.Div(
                        className="flex bg-dark-700 rounded-md p-1 shadow-sm",
                        children=[
                            html.Button(
                                "All",
                                id="orders-filter-all",
                                className="px-4 py-1.5 text-sm rounded-md transition-all hover:bg-primary/20 data-[active=true]:bg-primary data-[active=true]:text-white",
                                **{"data-active": "true"},
                            ),
                            html.Button(
                                "Working",
                                id="orders-filter-working",
                                className="px-4 py-1.5 text-sm rounded-md transition-all hover:bg-primary/20 data-[active=true]:bg-primary data-[active=true]:text-white",
                            ),
                            html.Button(
                                "Filled",
                                id="orders-filter-filled",
                                className="px-4 py-1.5 text-sm rounded-md transition-all hover:bg-primary/20 data-[active=true]:bg-primary data-[active=true]:text-white",
                            ),
                        ],
                    ),
                ],
            ),
            
            # DataTable
            dash_table.DataTable(
                id="orders-blotter",
                columns=[
                    {"name": "Time", "id": "timestamp"},
                    {"name": "ClOrdId", "id": "clOrdId"},
                    {"name": "Symbol", "id": "symbol"},
                    {"name": "Side", "id": "side"},
                    {"name": "Type", "id": "orderType"},
                    {"name": "Qty", "id": "quantity"},
                    {"name": "Price", "id": "price"},
                    {"name": "Filled", "id": "filledQuantity"},
                    {"name": "Remaining", "id": "leavesQuantity"},
                    {"name": "Status", "id": "status"},
                ],
                data=[],
                row_selectable="single",
                page_size=10,
                sort_action="native",
                sort_by=[{"column_id": "timestamp", "direction": "desc"}],
                style_table={
                    "overflowX": "auto",
                    "borderRadius": "0.375rem",
                    "border": "none",
                },
                style_cell={
                    "padding": "12px 14px",
                    "fontFamily": "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace",
                    "fontSize": "12px",
                    "borderBottom": "1px solid rgba(255,255,255,0.06)",
                    "borderRight": "1px solid rgba(255,255,255,0.03)",
                    "backgroundColor": "transparent",
                    "color": "white",
                    "textAlign": "left",
                    "whiteSpace": "nowrap",
                },
                style_header={
                    "fontWeight": "800",
                    "textTransform": "uppercase",
                    "fontSize": "10px",
                    "letterSpacing": "0.6px",
                    "borderBottom": "1px solid rgba(255,255,255,0.08)",
                    "borderRight": "1px solid rgba(255,255,255,0.08)",
                    "backgroundColor": "rgba(255,255,255,0.04)",
                    "color": "rgba(255,255,255,0.85)",
                    "padding": "14px",
                },
                style_data_conditional=[
                    {"if": {"filter_query": "{side} = BUY"}, "color": "#00d4aa", "fontWeight": "700"},
                    {"if": {"filter_query": "{side} = SELL"}, "color": "#ff6b6b", "fontWeight": "700"},
                    {"if": {"filter_query": "{status} = FILLED"}, "backgroundColor": "rgba(0, 212, 170, 0.08)"},
                    {"if": {"filter_query": "{status} = PARTIALLY_FILLED"}, "backgroundColor": "rgba(255, 217, 61, 0.08)"},
                    {"if": {"filter_query": "{status} = CANCELLED"}, "backgroundColor": "rgba(180, 180, 180, 0.05)"},
                    {"if": {"filter_query": "{status} = REPLACED"}, "backgroundColor": "rgba(77, 171, 247, 0.08)"},
                    {"if": {"filter_query": "{status} = REJECTED"}, "backgroundColor": "rgba(255, 107, 107, 0.08)"},
                    {"if": {"state": "selected"}, "backgroundColor": "rgba(77, 171, 247, 0.15)", "border": "1px solid rgba(77,171,247,0.5)"},
                    {"if": {"row_index": "odd"}, "backgroundColor": "rgba(255,255,255,0.02)"},
                ],
                style_data={
                    "height": "auto",
                    "lineHeight": "1.4",
                },
            ),
        ],
    )


def executions_blotter():
    """Redesigned executions blotter"""
    return html.Div(
        className="bg-dark-800 border border-dark-700 rounded-lg p-5 shadow-md card-hover",
        children=[
            # Header with clear button
            html.Div(
                className="flex flex-wrap items-center justify-between mb-5 pb-3 border-b border-dark-700 gap-3",
                children=[
                    html.Div(
                        className="flex items-center gap-2",
                        children=[
                            html.I(className="fa-solid fa-right-left text-primary"),
                            html.Span("Execution Reports", className="font-bold text-lg")
                        ],
                    ),
                    html.Button(
                        "Clear",
                        id="clear-executions-btn",
                        className="bg-dark-700 hover:bg-dark-600 text-gray-300 font-semibold py-1.5 px-4 rounded-md text-sm shadow-sm hover:shadow-md transition-all active:scale-95",
                    ),
                ],
            ),
            
            dash_table.DataTable(
                id="executions-blotter",
                columns=[
                    {"name": "Time", "id": "timestamp"},
                    {"name": "ExecId", "id": "execId"},
                    {"name": "ClOrdId", "id": "clOrdId"},
                    {"name": "OrigClOrdId", "id": "origClOrdId"},
                    {"name": "Symbol", "id": "symbol"},
                    {"name": "Side", "id": "side"},
                    {"name": "ExecType", "id": "execType"},
                    {"name": "LastQty", "id": "lastQuantity"},
                    {"name": "LastPx", "id": "lastPrice"},
                    {"name": "CumQty", "id": "cumQuantity"},
                    {"name": "AvgPx", "id": "avgPrice"},
                    {"name": "Status", "id": "orderStatus"},
                ],
                data=[],
                page_size=8,
                sort_action="native",
                sort_by=[{"column_id": "timestamp", "direction": "desc"}],
                style_table={
                    "overflowX": "auto",
                    "borderRadius": "0.375rem",
                    "border": "none",
                },
                style_cell={
                    "padding": "10px 12px",
                    "fontFamily": "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace",
                    "fontSize": "11px",
                    "borderBottom": "1px solid rgba(255,255,255,0.06)",
                    "borderRight": "1px solid rgba(255,255,255,0.03)",
                    "backgroundColor": "transparent",
                    "color": "white",
                    "textAlign": "left",
                    "whiteSpace": "nowrap",
                },
                style_header={
                    "fontWeight": "800",
                    "textTransform": "uppercase",
                    "fontSize": "10px",
                    "letterSpacing": "0.6px",
                    "borderBottom": "1px solid rgba(255,255,255,0.08)",
                    "borderRight": "1px solid rgba(255,255,255,0.08)",
                    "backgroundColor": "rgba(255,255,255,0.04)",
                    "color": "rgba(255,255,255,0.85)",
                    "padding": "12px",
                },
                style_data_conditional=[
                    {"if": {"filter_query": "{side} = BUY"}, "color": "#00d4aa", "fontWeight": "700"},
                    {"if": {"filter_query": "{side} = SELL"}, "color": "#ff6b6b", "fontWeight": "700"},
                    {"if": {"filter_query": "{execType} = FILL"}, "backgroundColor": "rgba(0, 212, 170, 0.08)"},
                    {"if": {"filter_query": "{execType} = PARTIAL_FILL"}, "backgroundColor": "rgba(255, 217, 61, 0.08)"},
                    {"if": {"filter_query": "{execType} = CANCELLED"}, "backgroundColor": "rgba(180, 180, 180, 0.05)"},
                    {"if": {"filter_query": "{execType} = REPLACED"}, "backgroundColor": "rgba(77, 171, 247, 0.08)"},
                    {"if": {"filter_query": "{execType} = REJECTED"}, "backgroundColor": "rgba(255, 107, 107, 0.08)"},
                    {"if": {"row_index": "odd"}, "backgroundColor": "rgba(255,255,255,0.02)"},
                ],
                style_data={
                    "height": "auto",
                    "lineHeight": "1.4",
                },
            ),
        ],
    )


def footer_bar():
    """Enhanced footer with better styling"""
    return html.Div(
        className="border-t border-dark-700 bg-dark-800 py-3 px-6 mt-auto",
        children=html.Div(
            className="container mx-auto flex flex-wrap items-center justify-between text-xs text-gray-500 gap-2",
            children=[
                html.Span("FIX OEMS v1.0 | Connected to localhost:8081"),
                html.Span(id="footer-session-info", className="font-mono"),
            ],
        ),
    )

# =============================================================================
# Main Layout
# =============================================================================

app.layout = html.Div(
    className="bg-dark-900 text-white min-h-screen flex flex-col",
    children=[
        dcc.Interval(id="refresh-interval", interval=REFRESH_MS, n_intervals=0),
        
        # Top bar
        top_bar(),
        
        # Main content area
        html.Div(
            className="container mx-auto flex-1 p-6",
            children=[
                # Stats row
                stats_row(),
                
                # Responsive grid layout
                html.Div(
                    className="grid grid-cols-1 lg:grid-cols-12 gap-6",
                    children=[
                        # Left column (responsive)
                        html.Div(
                            className="lg:col-span-3 space-y-6",
                            children=[
                                order_entry_panel(),
                                order_actions_panel(),
                            ],
                        ),
                        
                        # Right column (responsive)
                        html.Div(
                            className="lg:col-span-9 space-y-6",
                            children=[
                                orders_blotter(),
                                executions_blotter(),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        
        # Footer
        footer_bar(),
    ],
)

# =============================================================================
# Callbacks (unchanged from original)
# =============================================================================

@callback(Output("header-time", "children"), Input("refresh-interval", "n_intervals"))
def update_time(_n):
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@callback(
    Output("connection-badge", "children"),
    Output("connection-badge", "className"),
    Output("footer-session-info", "children"),
    Input("refresh-interval", "n_intervals"),
)
def update_connection_status(_n):
    sessions = safe_get_json(f"{API_BASE_URL}/sessions", timeout=2)
    if sessions and any(s.get("loggedOn") for s in sessions):
        logged_sessions = [s for s in sessions if s.get("loggedOn")]
        s = logged_sessions[0]
        footer = f"Session: {s.get('senderCompId')} → {s.get('targetCompId')}"
        badge_text = f"CONNECTED ({len(logged_sessions)} session{'s' if len(logged_sessions) > 1 else ''})"
        return badge_text, "bg-success text-white text-xs font-semibold px-4 py-1.5 rounded-full shadow-sm", footer
    return "DISCONNECTED", "bg-danger text-white text-xs font-semibold px-4 py-1.5 rounded-full shadow-sm", "No active session"


@callback(
    Output("stat-orders", "children"),
    Output("stat-filled", "children"),
    Output("stat-partial", "children"),
    Output("stat-open", "children"),
    Output("stat-cancelled", "children"),
    Output("stat-rejected", "children"),
    Input("refresh-interval", "n_intervals"),
)
def update_stats(_n):
    orders = safe_get_json(f"{API_BASE_URL}/orders", timeout=2) or []
    total = len(orders)
    filled = sum(1 for o in orders if (o.get("status") or "").upper() == "FILLED")
    partial = sum(1 for o in orders if (o.get("status") or "").upper() == "PARTIALLY_FILLED")
    working = sum(
        1 for o in orders
        if (o.get("status") or "").upper() in (
            "NEW", "PENDING", "PENDING_REPLACE", "PENDING_NEW", "PENDING_CANCEL", "PARTIALLY_FILLED"
        )
    )
    cancelled = sum(1 for o in orders if (o.get("status") or "").upper() in ("CANCELLED", "REPLACED"))
    rejected = sum(1 for o in orders if (o.get("status") or "").upper() == "REJECTED")
    return str(total), str(filled), str(partial), str(working), str(cancelled), str(rejected)


# Networks that require OnBehalfOfCompID (tag 116)
ONBEHALF_NETWORKS = {"NYFIX", "TRADEWARE", "TRADEWEB"}

import uuid as _uuid_lib

@callback(
    Output("broker-code-wrapper", "style"),
    Output("uuid-wrapper",        "style"),
    Output("onbehalf-wrapper",    "style"),
    Output("broker-code-select",  "value"),
    Output("onbehalf-input",      "value"),
    Input("network-select", "value"),
)
def toggle_network_fields(network):
    """Show/hide conditional fields based on selected network."""
    hidden  = {"display": "none"}
    visible = {"display": "block"}

    if network == "BLOOMBERG":
        return visible, visible, hidden, None, ""
    elif network in ONBEHALF_NETWORKS:
        return hidden, hidden, visible, None, ""
    else:
        # Sungard, Fidessa, CRD — no extra fields
        return hidden, hidden, hidden, None, ""


@callback(
    Output("uuid-input", "value"),
    Input("uuid-generate-btn", "n_clicks"),
    State("uuid-input", "value"),
    prevent_initial_call=False,
)
def generate_uuid(n_clicks, current_value):
    """Auto-populate UUID on load; regenerate when button is clicked."""
    # Always generate a fresh UUID if empty or button clicked
    if not current_value or n_clicks:
        return str(_uuid_lib.uuid4())
    return current_value


@callback(
    Output("order-status-msg", "children"),
    Input("buy-btn", "n_clicks"),
    Input("sell-btn", "n_clicks"),
    State("symbol-input",       "value"),
    State("quantity-input",     "value"),
    State("price-input",        "value"),
    State("order-type-select",  "value"),
    State("network-select",     "value"),
    State("broker-code-select", "value"),
    State("uuid-input",         "value"),
    State("onbehalf-input",     "value"),
    prevent_initial_call=True,
)
def submit_order(_buy, _sell, symbol, quantity, price, order_type,
                 network, broker_code, uuid_val, onbehalf_val):
    if not ctx.triggered:
        return ""

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    side = "BUY" if triggered_id == "buy-btn" else "SELL"

    if not symbol or not quantity:
        return html.Div("⚠ Enter symbol and quantity", className="bg-warning/20 text-warning p-2 rounded-md text-sm")

    order_type = (order_type or "LIMIT").upper()
    if order_type == "LIMIT" and (price is None or price == ""):
        return html.Div("⚠ Enter price for limit order", className="bg-warning/20 text-warning p-2 rounded-md text-sm")

    # Bloomberg-specific validation
    if network == "BLOOMBERG":
        if not broker_code:
            return html.Div("⚠ Broker Code is required for Bloomberg", className="bg-warning/20 text-warning p-2 rounded-md text-sm")
        if not uuid_val or not uuid_val.strip():
            return html.Div("⚠ Bloomberg UUID is required", className="bg-warning/20 text-warning p-2 rounded-md text-sm")

    # OnBehalfOfCompID-required networks validation
    if network in ONBEHALF_NETWORKS and (not onbehalf_val or not onbehalf_val.strip()):
        return html.Div(f"⚠ OnBehalfOfCompID (tag 116) is required for {network}", className="bg-warning/20 text-warning p-2 rounded-md text-sm")

    payload = {
        "symbol":    str(symbol).upper(),
        "side":      side,
        "orderType": order_type,
        "quantity":  int(quantity),
    }
    if order_type == "LIMIT":
        payload["price"] = float(price)
    if network:
        payload["network"] = network
    if broker_code:
        payload["brokerCode"] = broker_code
    if uuid_val and uuid_val.strip():
        payload["uuid"] = uuid_val.strip()
    if onbehalf_val and onbehalf_val.strip():
        payload["onBehalfOfCompId"] = onbehalf_val.strip()

    try:
        r = requests.post(f"{API_BASE_URL}/orders", json=payload, timeout=5)
        if r.status_code == 200:
            cid = r.json().get("clOrdId")
            bg_color   = "bg-success/20" if side == "BUY" else "bg-danger/20"
            text_color = "text-success"  if side == "BUY" else "text-danger"
            parts = [f"✓ {side} order sent: {cid}"]
            if network:
                parts.append(f"via {network}")
            if broker_code:
                parts.append(broker_code)
            if onbehalf_val and onbehalf_val.strip():
                parts.append(f"[116: {onbehalf_val.strip()}]")
            return html.Div(" ".join(parts), className=f"{bg_color} {text_color} p-2 rounded-md text-sm font-mono")
        err = r.json().get("message", "Order failed")
        return html.Div(f"✗ {err}", className="bg-danger/20 text-danger p-2 rounded-md text-sm")
    except Exception as e:
        return html.Div(f"Error: {str(e)}", className="bg-danger/20 text-danger p-2 rounded-md text-sm")


@callback(
    Output("orders-blotter", "data"),
    Input("refresh-interval", "n_intervals"),
    Input("orders-filter-all", "n_clicks"),
    Input("orders-filter-working", "n_clicks"),
    Input("orders-filter-filled", "n_clicks"),
)
def refresh_orders(_n, *args):
    triggered = ctx.triggered_id
    if triggered == "orders-filter-working":
        filter_value = "working"
    elif triggered == "orders-filter-filled":
        filter_value = "filled"
    else:
        filter_value = "all"

    orders = safe_get_json(f"{API_BASE_URL}/orders", timeout=2) or []
    fv = filter_value.lower()

    if fv == "working":
        orders = [
            o for o in orders
            if (o.get("status") or "").upper() in ("NEW", "PENDING", "PARTIALLY_FILLED", "PENDING_REPLACE", "PENDING_NEW", "PENDING_CANCEL")
        ]
    elif fv == "filled":
        orders = [o for o in orders if (o.get("status") or "").upper() == "FILLED"]

    return normalize_orders_for_table(orders)


@callback(Output("executions-blotter", "data"), Input("refresh-interval", "n_intervals"))
def refresh_executions(_n):
    execs = safe_get_json(f"{API_BASE_URL}/executions?limit=50", timeout=2) or []
    return normalize_execs_for_table(execs)


@callback(
    Output("action-clordid", "value"),
    Output("action-symbol", "value"),
    Output("action-side", "value"),
    Output("amend-qty", "value"),
    Output("amend-price", "value"),
    Input("orders-blotter", "selected_rows"),
    State("orders-blotter", "data"),
    prevent_initial_call=True,
)
def select_order(selected_rows, data):
    if selected_rows and data:
        row = data[selected_rows[0]]
        price = None
        if row.get("price") and row["price"] != "MKT":
            try:
                price = float(str(row["price"]).replace("$", ""))
            except Exception:
                price = None
        return row.get("clOrdId", ""), row.get("symbol", ""), row.get("side", ""), row.get("quantity", ""), price
    return "", "", "", "", ""


@callback(
    Output("action-status-msg", "children"),
    Input("cancel-btn", "n_clicks"),
    Input("amend-btn", "n_clicks"),
    State("action-clordid", "value"),
    State("action-symbol", "value"),
    State("action-side", "value"),
    State("amend-qty", "value"),
    State("amend-price", "value"),
    prevent_initial_call=True,
)
def handle_order_action(_cancel, _amend, clordid, symbol, side, new_qty, new_price):
    if not ctx.triggered or not clordid:
        return html.Div("Select an order first", className="bg-warning/20 text-warning p-2 rounded-md text-sm")

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    try:
        if triggered_id == "cancel-btn":
            r = requests.delete(
                f"{API_BASE_URL}/orders/{clordid}",
                params={"symbol": symbol, "side": side},
                timeout=5,
            )
            if r.status_code == 200:
                return html.Div("✓ Cancel sent", className="bg-primary/20 text-primary p-2 rounded-md text-sm")
            return html.Div("Cancel failed", className="bg-danger/20 text-danger p-2 rounded-md text-sm")

        if triggered_id == "amend-btn":
            if not new_qty and not new_price:
                return html.Div("Enter new qty or price", className="bg-warning/20 text-warning p-2 rounded-md text-sm")

            payload = {"symbol": symbol, "side": side}
            if new_qty:
                payload["newQuantity"] = int(new_qty)
            if new_price:
                payload["newPrice"] = float(new_price)

            r = requests.put(f"{API_BASE_URL}/orders/{clordid}", json=payload, timeout=5)
            if r.status_code == 200:
                return html.Div("✓ Amend sent", className="bg-primary/20 text-primary p-2 rounded-md text-sm")
            return html.Div("Amend failed", className="bg-danger/20 text-danger p-2 rounded-md text-sm")

        return html.Div("Request failed", className="bg-danger/20 text-danger p-2 rounded-md text-sm")
    except Exception as e:
        return html.Div(f"Error: {str(e)}", className="bg-danger/20 text-danger p-2 rounded-md text-sm")


@callback(
    Output("executions-blotter", "data", allow_duplicate=True),
    Input("clear-executions-btn", "n_clicks"),
    prevent_initial_call=True,
)
def clear_executions(_n):
    try:
        requests.delete(f"{API_BASE_URL}/executions", timeout=2)
    except Exception:
        pass
    return []


if __name__ == "__main__":
    print("=" * 60)
    print("  FIX OEMS - Order & Execution Management System (Tailwind)")
    print("=" * 60)
    print(f"  API: {API_BASE_URL}")
    print("  UI:  http://localhost:8050")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=8050)