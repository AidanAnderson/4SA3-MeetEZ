from flask import Flask, jsonify
import psycopg2
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

app = Flask(__name__)

# Azure Key Vault Configuration
KEY_VAULT_NAME = "MeetEZKeyVault"
KV_URI = f"https://meetezkeyvault.vault.azure.net/"

# Secret names in Key Vault
DB_HOST_SECRET = "db-host"
DB_NAME_SECRET = "db-name"
DB_USER_SECRET = "db-user"
DB_PASSWORD_SECRET = "db-password"

def get_secret(secret_name):
    """Fetch a secret from Azure Key Vault."""
    try:
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=KV_URI, credential=credential)
        secret = client.get_secret(secret_name)
        return secret.value
    except Exception as e:
        print(f"Error fetching secret '{secret_name}': {e}")
        return None

def connect_db():
    """Connect to the PostgreSQL database using credentials from Key Vault."""
    try:
        db_host = get_secret(DB_HOST_SECRET)
        db_name = get_secret(DB_NAME_SECRET)
        db_user = get_secret(DB_USER_SECRET)
        db_password = get_secret(DB_PASSWORD_SECRET)

        if not all([db_host, db_name, db_user, db_password]):
            raise ValueError("Missing one or more database credentials.")

        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            sslmode="require"
        )
        return conn
    except Exception as e:
        return str(e)

@app.route("/")
def home():
    return "Flask app is running and connected to Azure Key Vault."

@app.route("/init-db")
def init_db():
    """Create a test table if it doesn't exist."""
    conn = connect_db()
    if isinstance(conn, str):
        return jsonify({"error": conn})
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_data (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Table created successfully"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/insert")
def insert_data():
    """Insert test data into the database."""
    conn = connect_db()
    if isinstance(conn, str):
        return jsonify({"error": conn})
    
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO test_data (name) VALUES ('Azure Key Vault Test') RETURNING id;")
        inserted_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Inserted successfully", "id": inserted_id})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/fetch")
def fetch_data():
    """Fetch all records from the database."""
    conn = connect_db()
    if isinstance(conn, str):
        return jsonify({"error": conn})

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test_data;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"data": rows})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
