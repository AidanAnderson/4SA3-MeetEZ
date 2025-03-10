# dashboardUI.py
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from datetime import datetime
from adapter import connectDB  # Import from adapter.py
from app import app  # Import the Flask app

# Initialize Dash with Flask as the server.
dash_app = dash.Dash(
    __name__,
    server=app,
    routes_pathname_prefix='/dashboard/',
    requests_pathname_prefix='/dashboard/'
)

dash_app.layout = html.Div([
    html.H1("MeetEZ Dashboard UI"),
    
    html.Div([
        html.Button("Insert Timestamp", id="insert-button", n_clicks=0),
        html.Div(id="insert-output", style={'marginTop': 20})
    ]),
    
    html.H2("Records List"),
    html.Button("Refresh Records", id="refresh-button", n_clicks=0),
    html.Ul(id="records-list", style={'marginTop': 20})
])

# Callback to insert a new timestamp record into test_table.
@dash_app.callback(
    Output("insert-output", "children"),
    Input("insert-button", "n_clicks")
)
def insertTimestamp(n_clicks):
    if n_clicks > 0:
        conn = connectDB()
        if not conn:
            return "Failed to connect to the database."
        try:
            cur = conn.cursor()
            # Ensure the table exists.
            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id SERIAL PRIMARY KEY,
                    recorded_at TIMESTAMP NOT NULL
                )
            """)
            now = datetime.utcnow()
            cur.execute("INSERT INTO test_table (recorded_at) VALUES (%s) RETURNING id;", (now,))
            inserted_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            return f"Inserted timestamp with id {inserted_id} at {now}."
        except Exception as e:
            return f"Error inserting record: {e}"
    return ""

# Callback to refresh and display the list of records from test_table.
@dash_app.callback(
    Output("records-list", "children"),
    Input("refresh-button", "n_clicks")
)
def refreshRecords(n_clicks):
    conn = connectDB()
    if not conn:
        return [html.Li("Failed to connect to the database.")]
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, recorded_at FROM test_table ORDER BY recorded_at DESC;")
        records = cur.fetchall()
        cur.close()
        conn.close()
        return [html.Li(f"ID: {record[0]}, Time: {record[1]}") for record in records]
    except Exception as e:
        return [html.Li(f"Error fetching records: {e}")]