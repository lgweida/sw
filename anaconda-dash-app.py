import dash
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc

# Initialize the Dash app with Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the navigation structure
nav_items = {
    "Products": {
        "AI PLATFORM": [
            {"title": "Platform Overview", "desc": "The Anaconda AI Platform is the only unified AI platform for open source saving users time, money, and risk.", "link": "/ai-platform"},
            {"title": "Trusted Distribution", "desc": "More than 12,000 vetted Python packages. Free Download", "link": "/ai-platform/trusted-distribution"},
            {"title": "Secure Governance", "desc": "Enterprise-grade governance with role-based access control", "link": "/ai-platform/secure-governance"},
            {"title": "Actionable Insights", "desc": "Comprehensive analytics on package usage, team collaboration, and resource utilization", "link": "/ai-platform/actionable-insights"},
        ],
        "ANACONDA AI PLATFORM": [
            {"title": "Get Started", "link": "https://auth.anaconda.com/ui/login", "button": True},
            {"title": "Get a Demo", "link": "/request-a-demo", "button": True},
        ],
        "PRICING": [
            {"title": "Anaconda Pricing", "link": "/pricing"},
        ]
    },
    "Solutions": {
        "BY INDUSTRY": [
            {"title": "All Industries", "link": "/industries"},
            {"title": "Academia", "link": "/industries/education"},
            {"title": "Financial", "link": "/industries/financial-services"},
            {"title": "Government", "link": "/industries/government"},
            {"title": "Healthcare", "link": "/industries/healthcare"},
            {"title": "Manufacturing", "link": "/industries/manufacturing"},
            {"title": "Technology", "link": "/industries/technology"},
        ],
        "PROFESSIONAL SERVICES": [
            {"title": "Anaconda Professional Services", "link": "/professional-services"},
        ]
    },
    "Resources": {
        "RESOURCE CENTER": [
            {"title": "All Resources", "link": "/resources"},
            {"title": "Topics", "link": "/topics"},
            {"title": "Blog", "link": "/blog"},
            {"title": "Guides", "link": "/guides"},
            {"title": "Webinars", "link": "/resources/webinar"},
            {"title": "Podcast", "link": "/resources/podcast"},
            {"title": "Whitepapers", "link": "/resources/whitepaper"},
        ],
        "FOR USERS": [
            {"title": "Download Distribution", "link": "/download"},
            {"title": "Docs", "link": "/docs/main"},
            {"title": "Support Center", "link": "/app/support-center"},
            {"title": "Community", "link": "https://forum.anaconda.com/"},
            {"title": "Anaconda Learning", "link": "/learning"},
        ]
    },
    "Company": {
        "COMPANY": [
            {"title": "About Anaconda", "link": "/about-us"},
            {"title": "Leadership", "link": "/about-us/leadership"},
            {"title": "Our Open-Source Commitment", "link": "/our-open-source-commitment"},
            {"title": "Newsroom", "link": "/newsroom"},
            {"title": "Press Releases", "link": "/press"},
            {"title": "Careers", "link": "/about-us/careers"},
        ],
        "PARTNER NETWORK": [
            {"title": "Partners", "link": "/partners"},
            {"title": "Technology Partners", "link": "/partners/technology"},
            {"title": "Channels and Services Partners", "link": "/partners/channel-and-services"},
            {"title": "Become a Partner", "link": "/partners/become-a-partner"},
        ],
        "CONTACT": [
            {"title": "Contact Us", "link": "/contact"},
        ]
    }
}

# Function to create dropdown menu items
def create_dropdown_items(section_items):
    items = []
    for item in section_items:
        if item.get("desc"):
            items.append(
                dbc.DropdownMenuItem(
                    [
                        html.Div(item["title"], className="fw-bold"),
                        html.Div(item["desc"], className="text-muted small")
                    ],
                    href=item["link"],
                    className="py-2"
                )
            )
        elif item.get("button"):
            items.append(
                dbc.DropdownMenuItem(
                    item["title"],
                    href=item["link"],
                    className="btn btn-primary btn-sm text-white my-1 mx-2"
                )
            )
        else:
            items.append(
                dbc.DropdownMenuItem(item["title"], href=item["link"])
            )
    return items

# Create navigation dropdowns
nav_dropdowns = []
for main_item, sections in nav_items.items():
    dropdown_content = []
    
    for section_title, section_items in sections.items():
        # Add section header
        dropdown_content.append(
            dbc.DropdownMenuItem(
                section_title,
                header=True,
                className="text-uppercase small fw-bold"
            )
        )
        # Add section items
        dropdown_content.extend(create_dropdown_items(section_items))
        # Add divider if not last section
        if section_title != list(sections.keys())[-1]:
            dropdown_content.append(dbc.DropdownMenuItem(divider=True))
    
    nav_dropdowns.append(
        dbc.NavItem(
            dbc.DropdownMenu(
                dropdown_content,
                label=main_item,
                nav=True,
                in_navbar=True,
                className="mx-2"
            )
        )
    )

# Create the navigation bar
navbar = dbc.Navbar(
    dbc.Container(
        [
            # Logo
            html.A(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(
                                src="https://www.anaconda.com/wp-content/uploads/2024/11/2020_Anaconda_Logo_RGB_Corporate.png",
                                height="40"
                            )
                        ),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="/",
                style={"textDecoration": "none"},
            ),
            
            # Navigation items
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav(
                    [
                        *nav_dropdowns,
                        # Action buttons
                        dbc.NavItem(
                            dbc.Button(
                                "Free Download",
                                color="success",
                                outline=True,
                                size="sm",
                                href="/download",
                                className="mx-1"
                            )
                        ),
                        dbc.NavItem(
                            dbc.Button(
                                "Sign In",
                                color="primary",
                                outline=True,
                                size="sm",
                                href="https://auth.anaconda.com/ui/login",
                                className="mx-1"
                            )
                        ),
                        dbc.NavItem(
                            dbc.Button(
                                "Get Demo",
                                color="primary",
                                size="sm",
                                href="/request-a-demo",
                                className="mx-1"
                            )
                        ),
                    ],
                    className="ms-auto",
                    navbar=True,
                ),
                id="navbar-collapse",
                navbar=True,
            ),
        ],
        fluid=True,
    ),
    color="white",
    className="shadow-sm sticky-top",
    style={"backgroundColor": "white"}
)

# Main content area
main_content = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Welcome to Anaconda", className="text-center mt-5 mb-4"),
                        html.P(
                            "The World's Most Popular Data Science Platform",
                            className="text-center lead text-muted mb-5"
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.H4("AI Platform", className="card-title"),
                                                    html.P(
                                                        "The only unified AI platform for open source, saving users time, money, and risk.",
                                                        className="card-text"
                                                    ),
                                                    dbc.Button("Learn More", color="primary", href="/ai-platform")
                                                ]
                                            )
                                        ],
                                        className="h-100 shadow-sm"
                                    ),
                                    md=4,
                                    className="mb-4"
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.H4("Trusted Distribution", className="card-title"),
                                                    html.P(
                                                        "More than 12,000 vetted Python packages ready for enterprise use.",
                                                        className="card-text"
                                                    ),
                                                    dbc.Button("Download Now", color="success", href="/download")
                                                ]
                                            )
                                        ],
                                        className="h-100 shadow-sm"
                                    ),
                                    md=4,
                                    className="mb-4"
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.H4("Professional Services", className="card-title"),
                                                    html.P(
                                                        "Expert guidance to accelerate your data science and AI initiatives.",
                                                        className="card-text"
                                                    ),
                                                    dbc.Button("Get Started", color="info", href="/professional-services")
                                                ]
                                            )
                                        ],
                                        className="h-100 shadow-sm"
                                    ),
                                    md=4,
                                    className="mb-4"
                                ),
                            ]
                        )
                    ]
                )
            ]
        )
    ],
    className="py-5"
)

# Footer
footer = html.Footer(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H5("Products", className="text-uppercase mb-3"),
                            html.Ul(
                                [
                                    html.Li(html.A("AI Platform", href="/ai-platform", className="text-decoration-none text-muted")),
                                    html.Li(html.A("Trusted Distribution", href="/ai-platform/trusted-distribution", className="text-decoration-none text-muted")),
                                    html.Li(html.A("Pricing", href="/pricing", className="text-decoration-none text-muted")),
                                ],
                                className="list-unstyled"
                            )
                        ],
                        md=3
                    ),
                    dbc.Col(
                        [
                            html.H5("Resources", className="text-uppercase mb-3"),
                            html.Ul(
                                [
                                    html.Li(html.A("Documentation", href="/docs", className="text-decoration-none text-muted")),
                                    html.Li(html.A("Blog", href="/blog", className="text-decoration-none text-muted")),
                                    html.Li(html.A("Community", href="https://forum.anaconda.com/", className="text-decoration-none text-muted")),
                                ],
                                className="list-unstyled"
                            )
                        ],
                        md=3
                    ),
                    dbc.Col(
                        [
                            html.H5("Company", className="text-uppercase mb-3"),
                            html.Ul(
                                [
                                    html.Li(html.A("About Us", href="/about-us", className="text-decoration-none text-muted")),
                                    html.Li(html.A("Careers", href="/about-us/careers", className="text-decoration-none text-muted")),
                                    html.Li(html.A("Contact", href="/contact", className="text-decoration-none text-muted")),
                                ],
                                className="list-unstyled"
                            )
                        ],
                        md=3
                    ),
                    dbc.Col(
                        [
                            html.H5("Connect", className="text-uppercase mb-3"),
                            html.P("Stay updated with Anaconda", className="text-muted"),
                            dbc.Button("Subscribe to Newsletter", color="primary", size="sm")
                        ],
                        md=3
                    ),
                ]
            ),
            html.Hr(className="my-4"),
            html.P(
                "© 2025 Anaconda Inc. All Rights Reserved.",
                className="text-center text-muted mb-0"
            )
        ],
        className="py-5"
    ),
    className="bg-light mt-5"
)

# App layout
app.layout = html.Div([
    navbar,
    main_content,
    footer
])

# Callback for responsive navbar
@callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# Run the app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
