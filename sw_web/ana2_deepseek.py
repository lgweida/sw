import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Header component
header = html.Header(
    className="elementor elementor-location-header",
    style={
        "position": "fixed",
        "top": "0",
        "width": "100%",
        "zIndex": "1000",
        "backgroundColor": "white",
        "boxShadow": "0 2px 10px rgba(0,0,0,0.1)",
        "padding": "10px 0"
    },
    children=[
        dbc.Container(
            fluid=True,
            children=[
                dbc.Row(
                    align="center",
                    children=[
                        dbc.Col(
                            html.A(
                                html.Img(
                                    src="https://www.anaconda.com/wp-content/uploads/2024/11/2020_Anaconda_Logo_RGB_Corporate.png",
                                    style={"height": "50px"}
                                ),
                                href="https://www.anaconda.com"
                            ),
                            width=3
                        ),
                        dbc.Col(
                            dbc.Nav(
                                [
                                    # Products dropdown
                                    dbc.DropdownMenu(
                                        [
                                            dbc.DropdownMenuItem("AI PLATFORM", header=True),
                                            dbc.DropdownMenuItem("Platform Overview", href="https://www.anaconda.com/ai-platform"),
                                            dbc.DropdownMenuItem("Trusted Distribution", href="https://www.anaconda.com/ai-platform/trusted-distribution"),
                                            dbc.DropdownMenuItem("Secure Governance", href="https://www.anaconda.com/ai-platform/secure-governance"),
                                            dbc.DropdownMenuItem("Actionable Insights", href="https://www.anaconda.com/ai-platform/actionable-insights"),
                                            dbc.DropdownMenuItem(divider=True),
                                            dbc.DropdownMenuItem("ANACONDA AI PLATFORM", header=True),
                                            dbc.DropdownMenuItem("Get Started", href="https://auth.anaconda.com/ui/login", style={"color": "#0072ff"}),
                                            dbc.DropdownMenuItem("Get a Demo", href="https://www.anaconda.com/request-a-demo", style={"color": "#0072ff"}),
                                            dbc.DropdownMenuItem(divider=True),
                                            dbc.DropdownMenuItem("PRICING", header=True),
                                            dbc.DropdownMenuItem("Anaconda Pricing", href="https://www.anaconda.com/pricing"),
                                        ],
                                        label="Products",
                                        nav=True,
                                        in_navbar=True,
                                        style={"margin": "0 10px"}
                                    ),
                                    
                                    # Solutions dropdown
                                    dbc.DropdownMenu(
                                        [
                                            dbc.DropdownMenuItem("BY INDUSTRY", header=True),
                                            dbc.DropdownMenuItem("All Industries", href="https://www.anaconda.com/industries"),
                                            dbc.DropdownMenuItem("Academia", href="https://www.anaconda.com/industries/education"),
                                            dbc.DropdownMenuItem("Financial", href="https://www.anaconda.com/industries/financial-services"),
                                            dbc.DropdownMenuItem("Government", href="https://www.anaconda.com/industries/government"),
                                            dbc.DropdownMenuItem("Healthcare", href="https://www.anaconda.com/industries/healthcare"),
                                            dbc.DropdownMenuItem("Manufacturing", href="https://www.anaconda.com/industries/manufacturing"),
                                            dbc.DropdownMenuItem("Technology", href="https://www.anaconda.com/industries/technology"),
                                            dbc.DropdownMenuItem(divider=True),
                                            dbc.DropdownMenuItem("PROFESSIONAL SERVICES", header=True),
                                            dbc.DropdownMenuItem("Anaconda Professional Services", href="https://www.anaconda.com/professional-services"),
                                        ],
                                        label="Solutions",
                                        nav=True,
                                        in_navbar=True,
                                        style={"margin": "0 10px"}
                                    ),
                                    
                                    # Resources dropdown
                                    dbc.DropdownMenu(
                                        [
                                            dbc.DropdownMenuItem("RESOURCE CENTER", header=True),
                                            dbc.DropdownMenuItem("All Resources", href="https://www.anaconda.com/resources"),
                                            dbc.DropdownMenuItem("Topics", href="https://www.anaconda.com/topics"),
                                            dbc.DropdownMenuItem("Blog", href="https://www.anaconda.com/blog"),
                                            dbc.DropdownMenuItem("Guides", href="https://www.anaconda.com/guides"),
                                            dbc.DropdownMenuItem("Webinars", href="https://www.anaconda.com/recources/webinar"),
                                            dbc.DropdownMenuItem("Podcast", href="https://www.anaconda.com/resources/podcast"),
                                            dbc.DropdownMenuItem("Whitepapers", href="https://www.anaconda.com/resources/whitepaper"),
                                            dbc.DropdownMenuItem(divider=True),
                                            dbc.DropdownMenuItem("FOR USERS", header=True),
                                            dbc.DropdownMenuItem("Download Distribution", href="https://www.anaconda.com/download"),
                                            dbc.DropdownMenuItem("Docs", href="/docs/main"),
                                            dbc.DropdownMenuItem("Support Center", href="https://anaconda.com/app/support-center"),
                                            dbc.DropdownMenuItem("Community", href="https://forum.anaconda.com/"),
                                            dbc.DropdownMenuItem("Anaconda Learning", href="https://www.anaconda.com/learning"),
                                        ],
                                        label="Resources",
                                        nav=True,
                                        in_navbar=True,
                                        style={"margin": "0 10px"}
                                    ),
                                    
                                    # Company dropdown
                                    dbc.DropdownMenu(
                                        [
                                            dbc.DropdownMenuItem("COMPANY", header=True),
                                            dbc.DropdownMenuItem("About Anaconda", href="https://www.anaconda.com/about-us"),
                                            dbc.DropdownMenuItem("Leadership", href="https://www.anaconda.com/about-us/leadership"),
                                            dbc.DropdownMenuItem("Our Open-Source Commitment", href="https://www.anaconda.com/our-open-source-commitment"),
                                            dbc.DropdownMenuItem("Newsroom", href="https://www.anaconda.com/newsroom"),
                                            dbc.DropdownMenuItem("Press Releases", href="https://www.anaconda.com/press"),
                                            dbc.DropdownMenuItem("Careers", href="https://www.anaconda.com/about-us/careers"),
                                            dbc.DropdownMenuItem(divider=True),
                                            dbc.DropdownMenuItem("PARTNER NETWORK", header=True),
                                            dbc.DropdownMenuItem("Partners", href="https://www.anaconda.com/partners"),
                                            dbc.DropdownMenuItem("Technology Partners", href="https://www.anaconda.com/partners/technology"),
                                            dbc.DropdownMenuItem("Channels and Services Partners", href="https://www.anaconda.com/partners/channel-and-services"),
                                            dbc.DropdownMenuItem("Become a Partner", href="https://www.anaconda.com/partners/become-a-partner"),
                                            dbc.DropdownMenuItem(divider=True),
                                            dbc.DropdownMenuItem("CONTACT", header=True),
                                            dbc.DropdownMenuItem("Contact Us", href="https://www.anaconda.com/contact"),
                                        ],
                                        label="Company",
                                        nav=True,
                                        in_navbar=True,
                                        style={"margin": "0 10px"}
                                    ),
                                    
                                    # Buttons
                                    dbc.NavItem(
                                        dbc.NavLink(
                                            "Free Download",
                                            href="https://www.anaconda.com/download",
                                            style={
                                                "color": "white",
                                                "backgroundColor": "#0072ff",
                                                "borderRadius": "4px",
                                                "padding": "8px 16px",
                                                "margin": "0 5px"
                                            }
                                        )
                                    ),
                                    dbc.NavItem(
                                        dbc.NavLink(
                                            "Sign In",
                                            href="https://auth.anaconda.com/ui/login",
                                            style={
                                                "color": "#0072ff",
                                                "border": "1px solid #0072ff",
                                                "borderRadius": "4px",
                                                "padding": "8px 16px",
                                                "margin": "0 5px"
                                            }
                                        )
                                    ),
                                    dbc.NavItem(
                                        dbc.NavLink(
                                            "Get Demo",
                                            href="https://www.anaconda.com/request-a-demo",
                                            style={
                                                "color": "white",
                                                "backgroundColor": "#0072ff",
                                                "borderRadius": "4px",
                                                "padding": "8px 16px",
                                                "margin": "0 5px"
                                            }
                                        )
                                    ),
                                ],
                                navbar=True,
                                style={
                                    "display": "flex",
                                    "justifyContent": "flex-end",
                                    "alignItems": "center",
                                    "width": "100%"
                                }
                            ),
                            width=9
                        )
                    ]
                )
            ]
        )
    ]
)

# Main content with two cards
main_content = dbc.Container(
    fluid=True,
    style={"marginTop": "80px", "padding": "20px"},
    children=[
        dbc.Row(
            [
                # Left card
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Anaconda Distribution", className="bg-primary text-white"),
                            dbc.CardBody(
                                [
                                    html.H4("Python Data Science Platform", className="card-title"),
                                    html.P(
                                        "Anaconda Distribution is the easiest way to perform Python/R data science "
                                        "and machine learning on Linux, Windows, and Mac OS X.",
                                        className="card-text",
                                    ),
                                    dbc.Button(
                                        "Download Now",
                                        href="https://www.anaconda.com/download",
                                        color="primary"
                                    ),
                                ]
                            ),
                            dbc.CardFooter("Over 20 million users worldwide"),
                        ],
                        style={"height": "100%", "boxShadow": "0 4px 8px 0 rgba(0,0,0,0.2)"}
                    ),
                    md=6,
                    style={"padding": "10px"}
                ),
                
                # Right card
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Anaconda Professional", className="bg-success text-white"),
                            dbc.CardBody(
                                [
                                    html.H4("Enterprise-Grade Python", className="card-title"),
                                    html.P(
                                        "Anaconda Professional provides additional features for enterprise users "
                                        "including commercial licenses, prioritized packages, and enhanced security.",
                                        className="card-text",
                                    ),
                                    dbc.Button(
                                        "Learn More",
                                        href="https://www.anaconda.com/products/individual",
                                        color="success"
                                    ),
                                ]
                            ),
                            dbc.CardFooter("Trusted by Fortune 500 companies"),
                        ],
                        style={"height": "100%", "boxShadow": "0 4px 8px 0 rgba(0,0,0,0.2)"}
                    ),
                    md=6,
                    style={"padding": "10px"}
                ),
            ],
            className="mb-4",
        ),
        
        # Additional row with some sample content
        dbc.Row(
            [
                dbc.Col(
                    dcc.Markdown("""
                    ### About Anaconda
                    Anaconda is the birthplace of Python data science. We are a movement of data scientists, 
                    data-driven enterprises, and open source communities.
                    """),
                    md=12
                )
            ]
        )
    ]
)

# App layout
app.layout = html.Div(
    children=[
        header,
        main_content
    ]
)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8070)
