import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[
    # Tailwind CSS via CDN
    "https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css",
    dbc.themes.BOOTSTRAP
])

# Top navigation bar
top_nav = html.Nav(
    className="bg-white shadow-sm",
    children=[
        html.Div(
            className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
            children=[
                html.Div(
                    className="flex justify-between h-16",
                    children=[
                        # Logo
                        html.Div(
                            className="flex-shrink-0 flex items-center",
                            children=[
                                html.Img(
                                    className="h-8 w-auto",
                                    src="https://www.anaconda.com/wp-content/uploads/2024/11/2020_Anaconda_Logo_RGB_Corporate.png",
                                    alt="Anaconda Logo"
                                )
                            ]
                        ),
                        # Main navigation
                        html.Div(
                            className="hidden sm:ml-6 sm:flex sm:space-x-8",
                            children=[
                                dcc.Link("Products", href="#", className="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"),
                                dcc.Link("Solutions", href="#", className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"),
                                dcc.Link("Resources", href="#", className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"),
                                dcc.Link("Company", href="#", className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"),
                            ]
                        ),
                        # Right side buttons
                        html.Div(
                            className="hidden sm:ml-6 sm:flex sm:items-center space-x-4",
                            children=[
                                dcc.Link(
                                    "Free Download",
                                    href="https://www.anaconda.com/download",
                                    className="bg-white text-indigo-600 px-4 py-2 rounded-md text-sm font-medium border border-indigo-600 hover:bg-indigo-50"
                                ),
                                dcc.Link(
                                    "Sign In",
                                    href="https://auth.anaconda.com/ui/login",
                                    className="bg-white text-gray-500 px-4 py-2 rounded-md text-sm font-medium hover:text-gray-700"
                                ),
                                dcc.Link(
                                    "Get Demo",
                                    href="https://www.anaconda.com/request-a-demo",
                                    className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# Left sidebar navigation
sidebar = html.Div(
    className="hidden md:flex md:flex-shrink-0",
    children=[
        html.Div(
            className="flex flex-col w-64 border-r border-gray-200 bg-white",
            children=[
                html.Div(
                    className="h-0 flex-1 flex flex-col pt-5 pb-4 overflow-y-auto",
                    children=[
                        # Sidebar navigation
                        html.Nav(
                            className="mt-5 flex-1 px-2 space-y-1",
                            children=[
                                # AI Platform section
                                html.Div(
                                    children=[
                                        html.H3(
                                            "AI PLATFORM",
                                            className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider"
                                        ),
                                        dcc.Link(
                                            "Platform Overview",
                                            href="https://www.anaconda.com/ai-platform",
                                            className="group flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md"
                                        ),
                                        dcc.Link(
                                            "Trusted Distribution",
                                            href="https://www.anaconda.com/ai-platform/trusted-distribution",
                                            className="group flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md"
                                        ),
                                        dcc.Link(
                                            "Secure Governance",
                                            href="https://www.anaconda.com/ai-platform/secure-governance",
                                            className="group flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md"
                                        ),
                                        dcc.Link(
                                            "Actionable Insights",
                                            href="https://www.anaconda.com/ai-platform/actionable-insights",
                                            className="group flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md"
                                        ),
                                    ]
                                ),
                                # Divider
                                html.Div(className="border-t border-gray-200 my-4"),
                                # Resources section
                                html.Div(
                                    children=[
                                        html.H3(
                                            "RESOURCES",
                                            className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider"
                                        ),
                                        dcc.Link(
                                            "All Resources",
                                            href="https://www.anaconda.com/resources",
                                            className="group flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md"
                                        ),
                                        dcc.Link(
                                            "Blog",
                                            href="https://www.anaconda.com/blog",
                                            className="group flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md"
                                        ),
                                        dcc.Link(
                                            "Guides",
                                            href="https://www.anaconda.com/guides",
                                            className="group flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md"
                                        ),
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# Main content
main_content = html.Div(
    className="flex-1 overflow-auto focus:outline-none",
    children=[
        html.Div(
            className="pt-8 pb-12",
            children=[
                html.Div(
                    className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8",
                    children=[
                        html.H1(
                            "Advance AI with Clarity and Confidence",
                            className="text-3xl font-bold text-gray-900 text-center"
                        ),
                        html.P(
                            "Simplify, safeguard, and accelerate AI value with open source.",
                            className="mt-4 text-lg text-gray-500 text-center"
                        ),
                        # Buttons
                        html.Div(
                            className="mt-8 flex justify-center space-x-4",
                            children=[
                                dcc.Link(
                                    "Sign Up for Free",
                                    href="https://auth.anaconda.com/ui/registration",
                                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
                                ),
                                dcc.Link(
                                    "Get a Demo",
                                    href="/request-a-demo",
                                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-indigo-700 bg-indigo-100 hover:bg-indigo-200"
                                )
                            ]
                        ),
                        # Platform section
                        html.Div(
                            className="mt-16",
                            children=[
                                html.H2(
                                    "The Only Unified AI Platform for Open Source",
                                    className="text-2xl font-bold text-gray-900"
                                ),
                                html.P(
                                    "Trusted distribution, simplified workflows, real-time insights, and governance controls you need to elevate practitioner productivity to save your organization time, money, and risk.",
                                    className="mt-4 text-gray-500"
                                ),
                                # Feature cards
                                html.Div(
                                    className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3",
                                    children=[
                                        # Feature card 1
                                        html.Div(
                                            className="bg-white overflow-hidden shadow rounded-lg",
                                            children=[
                                                html.Div(
                                                    className="px-4 py-5 sm:p-6",
                                                    children=[
                                                        html.Div(
                                                            className="flex items-center",
                                                            children=[
                                                                html.Img(
                                                                    src="https://www.anaconda.com/wp-content/uploads/2025/07/Decoration-icon-calm.svg",
                                                                    className="h-10 w-10"
                                                                ),
                                                                html.H3(
                                                                    "Calm the Chaos",
                                                                    className="ml-3 text-lg font-medium text-gray-900"
                                                                )
                                                            ]
                                                        ),
                                                        html.P(
                                                            "Anaconda's unified approach frees you from silos, dependency blindspots, hyperscaler lock-in, debilitating vulnerabilities, lengthy development cycles, and failed pilots.",
                                                            className="mt-4 text-gray-500"
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        # Feature card 2
                                        html.Div(
                                            className="bg-white overflow-hidden shadow rounded-lg",
                                            children=[
                                                html.Div(
                                                    className="px-4 py-5 sm:p-6",
                                                    children=[
                                                        html.Div(
                                                            className="flex items-center",
                                                            children=[
                                                                html.Img(
                                                                    src="https://www.anaconda.com/wp-content/uploads/2025/01/Decoration-Icon-Generative-AI.svg",
                                                                    className="h-10 w-10"
                                                                ),
                                                                html.H3(
                                                                    "Deliver Value with the Anaconda AI Platform",
                                                                    className="ml-3 text-lg font-medium text-gray-900"
                                                                )
                                                            ]
                                                        ),
                                                        html.P(
                                                            "Organizations achieve 119% ROI by centralizing their approach to sourcing, securing, building, and deploying AI with the Anaconda AI Platform.",
                                                            className="mt-4 text-gray-500"
                                                        )
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# App layout
app.layout = html.Div(
    className="h-screen flex flex-col",
    children=[
        top_nav,
        html.Div(
            className="flex flex-1 overflow-hidden",
            children=[
                sidebar,
                main_content
            ]
        )
    ]
)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=9090)