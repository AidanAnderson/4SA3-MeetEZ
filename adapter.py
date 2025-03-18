"""
Created on Mon Mar 10 14:58:16 2025

@author: Aidan

Focusing on Singleton and Adapter Design Patterns 
Single connection here as well as an adapter to our database so that
all other connections are made as children to this DBAdapter function
"""

# adapter.py
import os
import psycopg2
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# Singleton metaclass to ensure only one instance is created.
class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Adapter(metaclass=SingletonMeta):
    def __init__(self):
        # Azure Key Vault Configuration
        self.keyVault = "https://meetezkeyvault.vault.azure.net"
        self.credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=self.keyVault, credential=self.credential)
        
        # Retrieve and validate database credentials
        self.DB_HOST = self.getSecret("db-host")
        self.DB_NAME = self.getSecret("db-name")
        self.DB_USER = self.getSecret("db-user")
        self.DB_PASSWORD = self.getSecret("azure-postgresql-password-bf846")
        
        if None in [self.DB_HOST, self.DB_NAME, self.DB_USER, self.DB_PASSWORD]:
            raise ValueError("ERROR: One or more database secrets are missing!")
        
        # Initialize email provider API connection details
        self.email_api_key = self.getSecret("email-api-key")
        self.email_address = self.getSecret("email-sender")
            
    def getSecret(self, secretName):
        """Fetch a secret from Azure Key Vault"""
        try:
            return self.client.get_secret(secretName).value
        except Exception as e:
            print(f"Error fetching {secretName}: {e}")
            return None

    def connectDB(self):
        """Connect to the PostgreSQL database and return a connection object."""
        try:
            conn = psycopg2.connect(
                dbname=self.DB_NAME,
                user=self.DB_USER,
                password=self.DB_PASSWORD,
                host=self.DB_HOST,
                port=5432  # Default PostgreSQL port
            )
            return conn
        except Exception as e:
            print("Database connection failed:", e)
            return None
    
    # Example method for sending an email via your provider.
    def sendEmail(self, recipient, subject, body):
        
        message = Mail(
            from_email= self.email_address,
            to_emails = recipient,
            subject = subject,
            html_content = body)
        
        try:
            sg = SendGridAPIClient(self.email_api_key)
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(f'adapter error: {str(e)}')
            
        print(f"Sending email to {recipient} with subject '{subject}'")
        return {"status": "Email sent"}

# Helper functions to expose a simple interface.
def connectDB():
    adapter = Adapter()  # Singleton instance
    return adapter.connectDB()

def sendEmail(recipient, subject, body):
    adapter = Adapter()
    return adapter.sendEmail(recipient, subject, body)

# Function to setup DB schema
def createSchema():
    conn = connectDB()
    if not conn:
        print("Failed to connect to the database.")
        return False
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS events (
                event_id SERIAL PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                event_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id SERIAL PRIMARY KEY,
                user_id INT NOT NULL,
                event_id INT NOT NULL,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Database schema created successfully.")
        return True
    except Exception as e:
        print(f"Error creating database schema: {e}")
        return False