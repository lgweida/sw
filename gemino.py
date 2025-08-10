import dash
from dash import html, dcc

from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# Header component (already sticky)
header = html.Header(
    className="fixed top-0 w-full z-50 bg-white shadow-md py-2",
    children=[
        html.Div(
            className="container mx-auto flex items-center justify-between",
            children=[
                html.A(
                    html.Img(
                        src="https://www.anaconda.com/wp-content/uploads/2024/11/2020_Anaconda_Logo_RGB_Corporate.png",
                        className="h-12"
                    ),
                    href="https://www.anaconda.com"
                ),
                html.Nav(
                    className="flex items-center space-x-4",
                    children=[
                        # Products dropdown
                        html.Details(
                            className="relative",
                            children=[
                                html.Summary(
                                    "Products",
                                    className="cursor-pointer"
                                ),
                                html.Div(
                                    className="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10",
                                    children=[
                                        html.A("AI PLATFORM", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("Platform Overview", href="https://www.anaconda.com/ai-platform", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Trusted Distribution", href="https://www.anaconda.com/ai-platform/trusted-distribution", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Secure Governance", href="https://www.anaconda.com/ai-platform/secure-governance", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Actionable Insights", href="https://www.anaconda.com/ai-platform/actionable-insights", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.Hr(className="my-1"),
                                        html.A("ANACONDA AI PLATFORM", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("Get Started", href="https://auth.anaconda.com/ui/login", className="block px-4 py-2 text-sm text-blue-500 hover:bg-gray-100"),
                                        html.A("Get a Demo", href="https://www.anaconda.com/request-a-demo", className="block px-4 py-2 text-sm text-blue-500 hover:bg-gray-100"),
                                        html.Hr(className="my-1"),
                                        html.A("PRICING", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("Anaconda Pricing", href="https://www.anaconda.com/pricing", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                    ]
                                )
                            ]
                        ),
                        # Solutions dropdown
                        html.Details(
                            className="relative",
                            children=[
                                html.Summary(
                                    "Solutions",
                                    className="cursor-pointer"
                                ),
                                html.Div(
                                    className="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10",
                                    children=[
                                        html.A("BY INDUSTRY", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("All Industries", href="https://www.anaconda.com/industries", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Academia", href="https://www.anaconda.com/industries/education", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Financial", href="https://www.anaconda.com/industries/financial-services", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Government", href="https://www.anaconda.com/industries/government", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Healthcare", href="https://www.anaconda.com/industries/healthcare", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Manufacturing", href="https://www.anaconda.com/industries/manufacturing", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Technology", href="https://www.anaconda.com/industries/technology", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.Hr(className="my-1"),
                                        html.A("PROFESSIONAL SERVICES", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("Anaconda Professional Services", href="https://www.anaconda.com/professional-services", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                    ]
                                )
                            ]
                        ),
                        # Resources dropdown
                        html.Details(
                            className="relative",
                            children=[
                                html.Summary(
                                    "Resources",
                                    className="cursor-pointer"
                                ),
                                html.Div(
                                    className="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10",
                                    children=[
                                        html.A("RESOURCE CENTER", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("All Resources", href="https://www.anaconda.com/resources", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Topics", href="https://www.anaconda.com/topics", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Blog", href="https://www.anaconda.com/blog", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Guides", href="https://www.anaconda.com/guides", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Webinars", href="https://www.anaconda.com/recources/webinar", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Podcast", href="https://www.anaconda.com/resources/podcast", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Whitepapers", href="https://www.anaconda.com/resources/whitepaper", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.Hr(className="my-1"),
                                        html.A("FOR USERS", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("Download Distribution", href="https://www.anaconda.com/download", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Docs", href="/docs/main", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Support Center", href="https://anaconda.com/app/support-center", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Community", href="https://forum.anaconda.com/", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Anaconda Learning", href="https://www.anaconda.com/learning", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                    ]
                                )
                            ]
                        ),
                        # Company dropdown
                        html.Details(
                            className="relative",
                            children=[
                                html.Summary(
                                    "Company",
                                    className="cursor-pointer"
                                ),
                                html.Div(
                                    className="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10",
                                    children=[
                                        html.A("COMPANY", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("About Anaconda", href="https://www.anaconda.com/about-us", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Leadership", href="https://www.anaconda.com/about-us/leadership", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Our Open-Source Commitment", href="https://www.anaconda.com/our-open-source-commitment", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Newsroom", href="https://www.anaconda.com/newsroom", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Press Releases", href="https://www.anaconda.com/press", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Careers", href="https://www.anaconda.com/about-us/careers", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.Hr(className="my-1"),
                                        html.A("PARTNER NETWORK", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("Partners", href="https://www.anaconda.com/partners", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Technology Partners", href="https://www.anaconda.com/partners/technology", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Channels and Services Partners", href="https://www.anaconda.com/partners/channel-and-services", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.A("Become a Partner", href="https://www.anaconda.com/partners/become-a-partner", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                        html.Hr(className="my-1"),
                                        html.A("CONTACT", href="#", className="block px-4 py-2 text-sm text-gray-700 font-bold"),
                                        html.A("Contact Us", href="https://www.anaconda.com/contact", className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"),
                                    ]
                                )
                            ]
                        ),
                        # Buttons
                        html.A(
                            "Free Download",
                            href="https://www.anaconda.com/download",
                            className="bg-blue-500 text-white rounded px-4 py-2 mx-1"
                        ),
                        html.A(
                            "Sign In",
                            href="https://auth.anaconda.com/ui/login",
                            className="text-blue-500 border border-blue-500 rounded px-4 py-2 mx-1"
                        ),
                        html.A(
                            "Get Demo",
                            href="https://www.anaconda.com/request-a-demo",
                            className="bg-blue-500 text-white rounded px-4 py-2 mx-1"
                        ),
                    ]
                )
            ]
        )
    ]
)

# Left sidebar component (sticky)
left_sidebar = html.Div(
    className="h-screen bg-gray-100 p-5 overflow-y-auto shadow-lg flex-shrink-0 w-64",
    children=[
        html.H4("Navigation", className="text-lg font-bold mb-4"),
        html.Nav(
            className="flex flex-col space-y-2",
            children=[
                html.A("Dashboard", href="#", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded"),
                html.A("Projects", href="#", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded"),
                html.A("Environments", href="#", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded"),
                html.A("Packages", href="#", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded"),
                html.A("Channels", href="#", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded"),
                html.A("Settings", href="#", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded"),
            ]
        ),
        html.Hr(className="my-4"),
        html.H5("Quick Links", className="text-md font-bold mt-4 mb-3"),
        html.Nav(
            className="flex flex-col space-y-2",
            children=[
                html.A("Documentation", href="https://docs.anaconda.com/", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded"),
                html.A("Community", href="https://forum.anaconda.com/", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded"),
                html.A("Support", href="https://anaconda.com/app/support-center", className="text-gray-700 hover:bg-gray-200 px-4 py-2 rounded"),
            ]
        )
    ]
)

# Main content with two cards (adjusted for left sidebar)
main_content = html.Div(
    className="p-5 flex-grow pt-20",
    children=[
        html.Div(
            className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4",
            children=[
                # Left card
                html.Div(
                    className="bg-white rounded-lg shadow-md flex flex-col",
                    children=[
                        html.Div(
                            "Anaconda Distribution",
                            className="bg-blue-500 text-white p-4 rounded-t-lg font-bold"
                        ),
                        html.Div(
                            className="p-4 flex-grow",
                            children=[
                                html.H4("Python Data Science Platform", className="text-xl font-bold mb-2"),
                                html.P(
                                    "Anaconda Distribution is the easiest way to perform Python/R data science "
                                    "and machine learning on Linux, Windows, and Mac OS X.",
                                    className="text-gray-700 mb-4"
                                ),
                                html.A(
                                    "Download Now",
                                    href="https://www.anaconda.com/download",
                                    className="bg-blue-500 text-white px-4 py-2 rounded"
                                ),
                            ]
                        ),
                        html.Div(
                            "Over 20 million users worldwide",
                            className="bg-gray-100 p-4 rounded-b-lg text-sm text-gray-600"
                        ),
                    ]
                ),
                # Right card
                html.Div(
                    className="bg-white rounded-lg shadow-md flex flex-col",
                    children=[
                        html.Div(
                            "Anaconda Professional",
                            className="bg-green-500 text-white p-4 rounded-t-lg font-bold"
                        ),
                        html.Div(
                            className="p-4 flex-grow",
                            children=[
                                html.H4("Enterprise-Grade Python", className="text-xl font-bold mb-2"),
                                html.P(
                                    "Anaconda Professional provides additional features for enterprise users "
                                    "including commercial licenses, prioritized packages, and enhanced security.",
                                    className="text-gray-700 mb-4"
                                ),
                                html.A(
                                    "Learn More",
                                    href="https://www.anaconda.com/products/individual",
                                    className="bg-green-500 text-white px-4 py-2 rounded"
                                ),
                            ]
                        ),
                        html.Div(
                            "Trusted by Fortune 500 companies",
                            className="bg-gray-100 p-4 rounded-b-lg text-sm text-gray-600"
                        ),
                    ]
                ),
            ]
        ),
        # Additional row with some sample content
        html.Div(
            className="prose max-w-none",
            children=[
                dcc.Markdown("""
                ### About Anaconda
                Anaconda is the birthplace of Python data science. We are a movement of data scientists, 
                data-driven enterprises, and open source communities.
                """)
            ]
        )
    ]
)

# App layout
app.layout = html.Div(
    children=[
        html.Script(src="https://cdn.tailwindcss.com"),
        header,
        html.Div(className="flex", children=[
            left_sidebar,
            main_content
        ])
    ]
)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=9070)