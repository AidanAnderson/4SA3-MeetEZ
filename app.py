from flask import Flask, jsonify
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
import psycopg2

app = Flask(__name__)

# Azure Key Vault Configuration
KV_URI = "https://meetezkeyvault.vault.azure.net"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=KV_URI, credential=credential)

def get_secret(secret_name):
    """ Fetch a secret from Azure Key Vault """
    try:
        return client.get_secret(secret_name).value
    except Exception as e:
        print(f"Error fetching {secret_name}: {e}")
        return None

# Retrieve database credentials dynamically
DB_HOST = get_secret("db-host")  # Ensure this matches the Key Vault secret name
DB_NAME = get_secret("db-name")
DB_USER = get_secret("db-user")
DB_PASSWORD = get_secret("azure-postgresql-password-bf846")  # Using existing password secret

# Validate that all secrets are retrieved
if None in [DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]:
    raise ValueError("ERROR: One or more database secrets are missing!")

# Set environment variable for database connection
os.environ["DATABASE_URL"] = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Function to connect to the PostgreSQL database
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=5432  # Default PostgreSQL port
        )
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None

@app.route("/")
def home():
    return jsonify({"message": "Flask App is Running!"})

@app.route("/db-test")
def db_test():
    """ Test database connection """
    conn = connect_db()
    if conn:
        return jsonify({"message": "Database Connection Successful!"})
    else:
        return jsonify({"error": "Failed to connect to the database!"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
