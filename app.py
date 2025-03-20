from flask import Flask, jsonify, request
from dash import Dash
from adapter import *

# Create Flask app
app = Flask(__name__)
app.url_map.strict_slashes = False

@app.route("/")
def home():
    return jsonify({"message": "Flask App is Running!"})

@app.route("/showRoutes")
def showRoutes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({"rule": rule.rule, "endpoint": rule.endpoint, "methods": list(rule.methods)})
    return jsonify(routes)

@app.route("/createSchema")
def initSchema():
    success = createSchema()
    if success:
        return jsonify({"message": "Database schema initialized successfully!"})
    else:
        return jsonify({"error": "Failed to initialize database schema!"}), 500


@app.route("/addEvent", methods=["POST"])
def addEvent():
    data = request.get_json()  # Read JSON from the request
    user_id = data.get("user_id")
    title = data.get("title")
    description = data.get("description")
    event_date = data.get("event_date")
    
    conn = connectDB()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO events (user_id, title, description, event_date)
            VALUES (%s, %s, %s, %s) RETURNING event_id;
        """, (user_id, title, description, event_date))
        event_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Event added successfully!", "event_id": event_id})
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route("/getEvents", methods=["GET"])
def getEvents():
    conn = connectDB()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM events;")
        events = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"events": events})
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route("/subscribeEvent", methods=["POST"])
def subscribeEvent():
    data = request.get_json()
    user_id = data.get("user_id")
    event_id = data.get("event_id")
    
    conn = connectDB()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO notifications (user_id, event_id)
            VALUES (%s, %s);
        """, (user_id, event_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Subscribed to event successfully!"})
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route("/addUser", methods=["POST"])
def addUser():
    data = request.get_json()
    user_id = data.get("user_id")
    email = data.get("email")
    name = data.get("name")

    conn = connectDB()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500

    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (user_id, email, name)
            VALUES (%s, %s, %s);
        """, (user_id, email, name))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "User added successfully!"})
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Import updated layout & callback function
from dashboardUI import layout, register_callbacks

dash_app = Dash(
    __name__,
    server=app,
    url_base_pathname="/dashboard/",
    suppress_callback_exceptions=True
)

# Set layout & register callbacks
dash_app.layout = layout
register_callbacks(dash_app)

if __name__ == "__main__":
    app.run(debug=False, port=8000)
