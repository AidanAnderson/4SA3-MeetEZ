# dashboardUI.py
from dash import html# or "from dash import html" if using Dash 2.x

# Only define layout and/or callbacks here—no import from app.py!
layout = html.Div([
    html.H1("Minimal Dash App"),
    html.P("Hello from Dash!")
])
