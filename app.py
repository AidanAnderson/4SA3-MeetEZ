from flask import Flask, jsonify
from datetime import datetime
from adapter import connectDB, sendEmail

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Flask App is Running!"})

@app.route("/dbConn")
def dbConn():
    """ Test database connection """
    conn = connectDB()
    if conn:
        return jsonify({"message": "Database Connection Successful!"})
    else:
        return jsonify({"error": "Failed to connect to the database!"}), 500

@app.route("/dbTest")
def dbTest():
    """ Test database: Drop old table, Insert and Read Timestamp """
    conn = connectDB()
    if not conn:
        return jsonify({"error": "Failed to connect to the database"}), 500

    try:
        cur = conn.cursor()

        # Step 1: Drop the old test_table if it exists
        cur.execute("DROP TABLE IF EXISTS test_table;")

        # Step 2: Create new test_table
        cur.execute("""
            CREATE TABLE test_table (
                id SERIAL PRIMARY KEY,
                recorded_at TIMESTAMP NOT NULL
            )
        """)

        # Step 3: Insert current timestamp
        now = datetime.utcnow()
        cur.execute("INSERT INTO test_table (recorded_at) VALUES (%s) RETURNING id;", (now,))
        inserted_id = cur.fetchone()[0]
        conn.commit()
        write_message = "Write Successful"

        # Step 4: Retrieve the last inserted timestamp
        cur.execute("SELECT recorded_at FROM test_table WHERE id = %s;", (inserted_id,))
        last_timestamp = cur.fetchone()[0]
        read_message = "Read Successful"

        cur.close()
        conn.close()

        return jsonify({
            "write_status": write_message,
            "read_status": read_message,
            "timestamp": last_timestamp
        })

    except Exception as e:
        return jsonify({"error": f"Database query failed: {str(e)}"}), 500
        
# Import the UI after the application is fully defined
#import dashboardUI
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
