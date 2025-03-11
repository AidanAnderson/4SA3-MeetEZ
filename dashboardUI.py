# dashboardUI.py
from dash import html, dcc, Input, Output, State
from adapter import connectDB, sendEmail

# A single layout that includes both a DB read button and email-sending fields
layout = html.Div([
    html.H2("Database Read and Email Sending"),

    # Section 1: Read from DB
    html.Button("Read from DB", id="read-db-button", n_clicks=0),
    html.Div(id="db-output", style={"marginTop": "20px"}),

    html.Hr(),

    # Section 2: Send an Email
    html.H3("Send an Email"),
    html.Div([
        html.Label("Recipient:"),
        dcc.Input(id="email-recipient", type="text", placeholder="Enter recipient email"),
    ], style={"marginTop": "10px"}),

    html.Div([
        html.Label("Subject:"),
        dcc.Input(id="email-subject", type="text", placeholder="Enter email subject"),
    ], style={"marginTop": "10px"}),

    html.Div([
        html.Label("Body:"),
        dcc.Textarea(id="email-body", placeholder="Enter email body", style={"width": "100%", "height": "100px"}),
    ], style={"marginTop": "10px"}),

    html.Button("Send Email", id="send-email-button", n_clicks=0, style={"marginTop": "10px"}),
    html.Div(id="email-output", style={"marginTop": "20px"})
])

def register_callbacks(dash_app):
    """
    Attach all Dash callbacks here. This prevents circular imports
    by avoiding direct imports of app.py in this file.
    """

    # 1. Callback to read from the database
    @dash_app.callback(
        Output("db-output", "children"),
        Input("read-db-button", "n_clicks")
    )
    def read_db(n_clicks):
        if n_clicks == 0:
            return "Click the button to read from the database."
        conn = connectDB()
        if not conn:
            return "Failed to connect to the database."
        try:
            cur = conn.cursor()
            # Example query: get the current timestamp from the database.
            cur.execute("SELECT now();")
            result = cur.fetchone()[0]
            conn.close()
            return f"Database current time: {result}"
        except Exception as e:
            return f"Database query error: {e}"

    # 2. Callback to send an email
    @dash_app.callback(
        Output("email-output", "children"),
        Input("send-email-button", "n_clicks"),
        State("email-recipient", "value"),
        State("email-subject", "value"),
        State("email-body", "value")
    )
    def send_email_callback(n_clicks, recipient, subject, body):
        if n_clicks == 0:
            return "Enter email details and click 'Send Email'."
        if not recipient or not subject or not body:
            return "Please fill out all fields."
        try:
            response = sendEmail(recipient, subject, body)
            # You can parse `response` if your adapter returns something meaningful
            return f"Email sent successfully to {recipient}!"
        except Exception as e:
            return f"Error sending email: {str(e)}"
