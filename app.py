from flask import Flask, jsonify, request
from dash import Dash
from adapter import connectDB, createSchema, sendEmail

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
        rows = cur.fetchall()
        conn.close()

        events = [
            {
                "event_id": row[0],
                "user_id": row[1],
                "title": row[2],
                "description": row[3],
                "event_date": row[4],
                "created_at": row[5]
            } 
            for row in rows
        ]

        return jsonify({"events": events})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/updateEvent", methods=["POST"])
def updateEvent():
    data = request.get_json()
    event_id = data.get("event_id")
    title = data.get("title")
    description = data.get("description")
    event_date = data.get("event_date")

    if not event_id:
        return jsonify({"error": "Missing event_id"}), 400

    conn = connectDB()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500

    try:
        cur = conn.cursor()

        # 1. Update the event
        cur.execute("""
            UPDATE events
            SET title = %s, description = %s, event_date = %s
            WHERE event_id = %s;
        """, (title, description, event_date, event_id))

        # 2. Get emails of subscribed users
        cur.execute("""
            SELECT u.email
            FROM notifications n
            JOIN users u ON n.user_id = u.user_id
            WHERE n.event_id = %s;
        """, (event_id,))
        email_rows = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()

        # 3. Send emails
        for (email,) in email_rows:
            subject = "Your Event Has Been Updated"
            body = f"""
                <p>Hello,</p>
                <p>The event you are subscribed to has been updated:</p>
                <ul>
                    <li><strong>Title:</strong> {title}</li>
                    <li><strong>Description:</strong> {description}</li>
                    <li><strong>Date:</strong> {event_date}</li>
                </ul>
                <p>Visit your dashboard for more details.</p>
            """
            sendEmail(email, subject, body)

        return jsonify({"message": "Event updated and notifications sent."})
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route("/deleteEvent", methods=["POST"])
def delete_event():
    data = request.get_json()
    event_id = data.get("event_id")

    if not event_id:
        return jsonify({"error": "Missing event_id"}), 400

    conn = connectDB()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM events WHERE event_id = %s;", (event_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Event deleted successfully."})
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
    
@app.route("/getSubscribers", methods=["GET"])
def getSubscribers():
    event_id = request.args.get("event_id")
    if not event_id:
        return jsonify({"error": "Missing event_id parameter"}), 400

    conn = connectDB()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT u.user_id, u.name, u.email
            FROM notifications n
            JOIN users u ON n.user_id = u.user_id
            WHERE n.event_id = %s;
        """, (event_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        subscribers = [{"user_id": r[0], "name": r[1], "email": r[2]} for r in rows]
        return jsonify({"subscribers": subscribers})
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route("/dbTestLocal", methods=["GET"])
def dbTestLocal():
    conn = connectDB()
    if conn:
        conn.close()
        return jsonify({"message": "✅ Flask is able to connect to the database locally!"})
    else:
        return jsonify({"error": "❌ Flask cannot connect to the database!"}), 500

@app.route("/addUser", methods=["POST"])
def addUser():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    conn = connectDB()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500

    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email) VALUES (%s, %s) RETURNING user_id;", (name, email))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "User added successfully", "user_id": user_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/getUserEvents", methods=["GET"])
def getUserEvents():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400

    conn = connectDB()
    if not conn:
        return jsonify({"error": "Failed to connect to database"}), 500

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT e.event_id, e.title, e.description, e.event_date, e.created_at
            FROM notifications n
            JOIN events e ON n.event_id = e.event_id
            WHERE n.user_id = %s;
        """, (user_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        events = [{
            "event_id": r[0],
            "title": r[1],
            "description": r[2],
            "event_date": str(r[3]),
            "created_at": str(r[4])
        } for r in rows]

        return jsonify({"events": events})
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
    app.run(debug=False,host="0.0.0.0", port=8000)