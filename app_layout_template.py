import dash
import dash_bootstrap_components as dbc
from dash import html

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Header/Navigation Bar
# Using dbc.NavbarSimple for a clean and simple header.
# `fixed="top"` makes it stick to the top of the screen.
header = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="App Name",
    brand_href="#",
    color="primary",
    dark=True,
    fixed="top",
)

# Left Sidebar
# The sidebar is styled with `position: "fixed"` to keep it in place while scrolling.
# The `top` style property is set to account for the height of the fixed navbar.
sidebar = html.Div(
    style={
        "position": "fixed",
        "top": "56px",  # Standard height for the dbc.NavbarSimple
        "left": 0,
        "bottom": 0,
        "width": "16rem",
        "padding": "2rem 1rem",
        "backgroundColor": "#f8f9fa",
        "borderRight": "1px solid #dee2e6",
    },
    children=[
        html.H4("Sidebar", className="display-6"),
        html.Hr(),
        html.P(
            "Navigation links for the app", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Analytics", href="/analytics", active="exact"),
                dbc.NavLink("Settings", href="/settings", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
)

# Main Content Area
# The main content area has `marginLeft` and `marginTop` to prevent it
# from being obscured by the sidebar and header.
main_content = html.Div(
    style={
        "marginTop": "56px",
        "marginLeft": "16rem",
        "padding": "2rem 1rem",
    },
    children=[
        dbc.Container(
            fluid=True,
            children=[
                html.H1("Main Content Area"),
                html.P("This area holds the main content, split into two columns below."),
                html.Hr(),
                # The two-column layout is created using dbc.Row and dbc.Col
                dbc.Row(
                    [
                        # Left Column
                        dbc.Col(
                            md=6,
                            children=[
                                dbc.Card([
                                    dbc.CardHeader("Left Column"),
                                    dbc.CardBody([
                                        html.H5("Content for the left side", className="card-title"),
                                        html.P("This is the left part of the main content.", className="card-text"),
                                    ]),
                                ])
                            ],
                        ),
                        # Right Column
                        dbc.Col(
                            md=6,
                            children=[
                                dbc.Card([
                                    dbc.CardHeader("Right Column"),
                                    dbc.CardBody([
                                        html.H5("Content for the right side", className="card-title"),
                                        html.P("This is the right part of the main content.", className="card-text"),
                                    ]),
                                ])
                            ],
                        ),
                    ]
                ),
            ],
        )
    ],
)

# App Layout
app.layout = html.Div([header, sidebar, main_content])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8090)
