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
homeLayout = html.Div([
    html.H2("🏠 Welcome to MeetEZ"),
    html.Hr(),
    dcc.Link("➕ Add Event", href="/dashboard/add-event", className="btn btn-primary", style={"marginLeft": "10px"}),
    dcc.Link("🔍 View Events", href="/dashboard/view-events", className="btn btn-primary", style={"marginLeft": "10px"}),
    dcc.Link("👥 View Subscribers", href="/dashboard/view-subscribers", className="btn btn-primary", style={"marginLeft": "10px"}),
    dcc.Link("📋 View User Subscriptions", href="/dashboard/view-user-events", className="btn btn-primary", style={"marginLeft": "10px"}),
    dcc.Link("✏️ Update Event", href="/dashboard/update-event", className="btn btn-warning", style={"marginLeft": "10px"}),

])

addEventLayout = html.Div([
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

updateEventLayout = html.Div([
    html.H2("✏️ Update or Delete an Event"),

    dbc.Input(id="updateEventId", type="number", placeholder="Enter Event ID", className="mb-2"),
    dbc.Input(id="updateEventTitle", type="text", placeholder="New Title", className="mb-2"),
    dbc.Textarea(id="updateEventDescription", placeholder="New Description", className="mb-2"),
    dbc.Input(id="updateEventDate", type="date", className="mb-2"),

    dbc.Button("Update Event", id="submitUpdateEvent", color="warning", className="mt-2"),
    html.Div(id="updateEventOutput", className="mt-3"),

    html.Hr(),

    dbc.Button("🗑️ Delete Event", id="deleteEventButton", color="danger", className="mt-2"),
    html.Div(id="deleteEventOutput", className="mt-3"),

    html.Hr(),
    dcc.Link("🏠 Home", href="/dashboard/", className="btn btn-secondary")
])


viewEventsLayout = html.Div([
    
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

viewSubscribersLayout = html.Div([
    html.H2("👥 View Subscribers for an Event"),
    dbc.Input(id="view-subs-event-id", type="number", placeholder="Enter Event ID"),
    dbc.Button("Fetch Subscribers", id="fetch-subs-btn", color="primary", className="mt-2"),
    html.Div(id="subs-output"),
    html.Hr(),
    dcc.Link("🏠 Home", href="/dashboard/", className="btn btn-secondary"),
])

viewUserEventsLayout = html.Div([
    html.H2("📋 View Events Subscribed by User"),
    dbc.Input(id="user-events-user-id", type="number", placeholder="Enter User ID"),
    dbc.Button("Fetch Events", id="fetch-user-events-btn", color="primary", className="mt-2"),
    html.Div(id="user-events-output"),
    html.Hr(),
    dcc.Link("🏠 Home", href="/dashboard/", className="btn btn-secondary"),
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
            return addEventLayout
        elif pathname == "/dashboard/view-events":
            return viewEventsLayout
        elif pathname == "/dashboard/view-subscribers":
            return viewSubscribersLayout
        elif pathname == "/dashboard/view-user-events":
            return viewUserEventsLayout
        elif pathname == "/dashboard/update-event":
            return updateEventLayout
        return homeLayout


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
                response = requests.get(f"{API_URL}/getEvents", timeout=5)
                
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

    @dash_app.callback(
        Output("user-events-output", "children"),
        [Input("fetch-user-events-btn", "n_clicks")],
        [State("user-events-user-id", "value")]
    )
    def get_user_events(n_clicks, user_id):
        if n_clicks and user_id:
            try:
                response = requests.get(f"{API_URL}/getUserEvents", params={"user_id": user_id})
                if response.status_code == 200:
                    events = response.json().get("events", [])
                    if not events:
                        return "This user is not subscribed to any events."
                    return html.Ul([
                        html.Li(f"ID: {e['event_id']} | Title: {e['title']} | Date: {e['event_date']}")
                        for e in events
                    ])
                else:
                    return f"Error: {response.json().get('error', 'Unknown error')}"
            except requests.exceptions.RequestException as e:
                return f"API Request Failed: {str(e)}"
        return ""

    @dash_app.callback(
        Output("updateEventOutput", "children"),
        [Input("submitUpdateEvent", "n_clicks")],
        [State("updateEventId", "value"),
         State("updateEventTitle", "value"),
         State("updateEventDescription", "value"),
         State("updateEventDate", "value")]
    )
    def update_event(n_clicks, eventId, title, description, eventDate):
        if n_clicks and eventId:
            data = {
                "event_id": eventId,
                "title": title,
                "description": description,
                "event_date": eventDate
            }
            try:
                response = requests.post(f"{API_URL}/updateEvent", json=data)
                if response.status_code == 200:
                    return "Event updated and notifications sent!"
                else:
                    return f"Error: {response.json().get('error', 'Unknown error')}"
            except requests.exceptions.RequestException as e:
                return f"API Request Failed: {str(e)}"
        return ""

    @dash_app.callback(
        Output("deleteEventOutput", "children"),
        [Input("deleteEventButton", "n_clicks")],
        [State("updateEventId", "value")]
    )
    def deleteEvent(n_clicks, event_id):
        if n_clicks and event_id:
            try:
                response = requests.post(f"{API_URL}/deleteEvent", json={"event_id": event_id})
                if response.status_code == 200:
                    return "Event deleted successfully!"
                else:
                    return f"Error: {response.json().get('error', 'Unknown error')}"
            except requests.exceptions.RequestException as e:
                return f"API Request Failed: {str(e)}"
        return ""

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
    
    @dash_app.callback(
        Output("subs-output", "children"),
        [Input("fetch-subs-btn", "n_clicks")],
        [State("view-subs-event-id", "value")]
    )
    def get_subscribers(n_clicks, event_id):
        if n_clicks and event_id:
            try:
                response = requests.get(f"{API_URL}/getSubscribers", params={"event_id": event_id})
                if response.status_code == 200:
                    subscribers = response.json().get("subscribers", [])
                    if not subscribers:
                        return "No subscribers found for this event."
                    return html.Ul([
                        html.Li(f"ID: {s['user_id']} | Name: {s['name']} | Email: {s['email']}")
                        for s in subscribers
                    ])
                else:
                    return f"Error: {response.json().get('error', 'Unknown error')}"
            except requests.exceptions.RequestException as e:
                return f"API Request Failed: {str(e)}"
        return ""
