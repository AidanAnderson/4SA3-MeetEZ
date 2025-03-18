from dash import html, dcc, Input, Output, dash
import dash_bootstrap_components as dbc
from adapter import connectDB, sendEmail

# Define the main layout
layout = html.Div([
    dcc.Location(id="url", refresh=False),  # Detects URL changes
    html.Div(id="page-content", children=html.H2("🏠 Loading..."))  # Default
])

# Define page layouts
home_layout = html.Div([
    html.H2("🏠 Welcome to MeetEZ"),
    dcc.Link("➕ Add Event", href="/dashboard/add-event", className="btn btn-primary"),
    dcc.Link("🔍 View Events", href="/dashboard/view-events", className="btn btn-secondary", style={"marginLeft": "10px"})
])

add_event_layout = html.Div([
    html.H2("➕ Add an Event"),
    dbc.Input(id="user-id", type="number", placeholder="Enter UserID"),
    dbc.Input(id="event-title", type="text", placeholder="Enter Event Title"),
    dbc.Textarea(id="event-description", placeholder="Enter Event Description"),
    dbc.Input(id="event-date", type="date"),
    dbc.Button("Submit", id="submit-event", color="primary", className="mt-2"),
    html.Div(id="event-output"),
    html.Hr(),
    dcc.Link("🏠 Home", href="/dashboard/", className="btn btn-secondary"),
    dcc.Link("🔍 View Events", href="/dashboard/view-events", className="btn btn-primary", style={"marginLeft": "10px"})
])

view_events_layout = html.Div([
    html.H2("🔍 View and Subscribe to Events"),
    dbc.Input(id="subscribe-user-id", type="number", placeholder="Enter UserID to subscribe"),
    dbc.Input(id="subscribe-event-id", type="number", placeholder="Enter EventID to subscribe"),
    dbc.Button("Subscribe", id="subscribe-btn", color="success", className="mt-2"),
    html.Div(id="subscribe-output"),
    html.H3("📅 Available Events"),
    html.Div(id="events-list"),
    html.Hr(),
    dcc.Link("🏠 Home", href="/dashboard/", className="btn btn-secondary"),
    dcc.Link("➕ Add Event", href="/dashboard/add-event", className="btn btn-primary", style={"marginLeft": "10px"})
])

# Callback to update page-content based on the URL
def register_callbacks(dash_app):
    @dash_app.callback(
        Output("page-content", "children"),
        [Input("url", "pathname")]
    )
    def display_page(pathname):
        print(f"Navigating to: {pathname}")  # Debugging log
        
        if pathname == "/dashboard/add-event":
            return add_event_layout
        elif pathname == "/dashboard/view-events":
            return view_events_layout
        else:
            return home_layout  # Default to home
