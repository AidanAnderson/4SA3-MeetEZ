from flask import Flask, jsonify
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
    app.run(debug=True, port=8000)
