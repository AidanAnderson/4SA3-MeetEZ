import logging
import requests
from dash import html, dcc, Input, Output, State, dash
import dash_bootstrap_components as dbc


# Setup logging, API not available still
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# API_URL is defined here so that it can be edited easier
API_URL = "https://meetez-czgpatgmh8c4cfcz.canadacentral-01.azurewebsites.net"

# Define the main layout
layout = html.Div([
    dcc.Location(id="url", refresh=False),  # Detects URL changes
    html.Div(id="page-content", children=html.H2("🏠 Loading..."))  # Default
])

# Define page layouts
home_layout = html.Div([
    html.H2("🏠 Welcome to MeetEZ"),
    html.Hr(),
    dcc.Link("➕ Add Event", href="/dashboard/add-event", className="btn btn-primary", style={"marginLeft": "10px"}),
    dcc.Link("🔍 View Events", href="/dashboard/view-events", className="btn btn-primary", style={"marginLeft": "10px"})

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
    
    logger.info("View Events page loaded"),
    
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

    # Page Navigation
    @dash_app.callback(
        Output("page-content", "children"),
        [Input("url", "pathname")]
    )
    def display_page(pathname):
        if pathname == "/dashboard/add-event":
            return add_event_layout
        elif pathname == "/dashboard/view-events":
            return view_events_layout
        return home_layout

    @dash_app.callback(
        Output("event-output", "children"),
        [Input("submit-event", "n_clicks")],
        [State("user-id", "value"), State("event-title", "value"),
         State("event-description", "value"), State("event-date", "value")]
    )
    def add_event(n_clicks, user_id, title, description, event_date):
        if n_clicks and user_id and title and event_date:
            data = {"user_id": user_id, "title": title, "description": description, "event_date": event_date}
            try:
                response = requests.post(f"{API_URL}/addEvent", json=data)
                if response.status_code == 200:
                    return f"Event added successfully! ID: {response.json().get('event_id')}"
                else:
                    return f"Error: {response.json().get('error', 'Unknown error')}"
            except requests.exceptions.RequestException as e:
                return f"API Request Failed: {str(e)}"
        return ""

    # Fetch Events on Page Load
    @dash_app.callback(
        Output("events-list", "children"),
        [Input("url", "pathname")]
    )
    def view_events(pathname):
        if pathname == "/dashboard/view-events":
            try:
                # Log request for debugging
                logger.info("Fetching events from API...")

                # Call API with a timeout to prevent hanging
                #Logging API path
                logger.info(f"{API_URL}/getEvents")
                response = requests.get(f"{API_URL}/getEvents", timeout=50)
                
                if response.status_code == 200:
                    events = response.json().get("events", [])
                    logger.info(f"Received {len(events)} events from the API")
                    
                    # Log event data
                    print(f"Received events: {events}")

                    if events:
                        return [html.Div(f"{event}") for event in events]
                    else:
                        return "No events available."
                else:
                    logger.error(f"Error fetching events: {response.status_code}")
                    return f"API Error: {response.status_code}"
            except requests.exceptions.Timeout:
                return "API request timed out!"
            except Exception as e:
                logger.error(f"API Error: {str(e)}")
                return f"API Error: {str(e)}"
                
        return "Loading..."



    # Subscribe to Event Button 
    @dash_app.callback(
        Output("subscribe-output", "children"),
        [Input("subscribe-btn", "n_clicks")],
        [State("subscribe-user-id", "value"), State("subscribe-event-id", "value")]
    )
    def subscribe_event(n_clicks, user_id, event_id):
        if n_clicks and user_id and event_id:
            data = {"user_id": user_id, "event_id": event_id}
            try:
                response = requests.post(f"{API_URL}/subscribeEvent", json=data)
                if response.status_code == 200:
                    return "Successfully subscribed to the event!"
                else:
                    return f"Error: {response.json().get('error', 'Unknown error')}"
            except requests.exceptions.RequestException as e:
                return f"API Request Failed: {str(e)}"
        return ""
