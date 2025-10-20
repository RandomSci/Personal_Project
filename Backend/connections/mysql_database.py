import pymysql
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "automate_ai")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))

connection = None

def init_mysql():
    global connection
    try:
        connection = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            port=MYSQL_PORT,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print(f"✅ Connected to MySQL: {MYSQL_DB}")
        create_tables()
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("⚠️  Running without MySQL")

def close_mysql():
    global connection
    if connection:
        connection.close()
        print("✅ MySQL connection closed")

def get_mysql():
    return connection

def create_tables():
    """Create necessary tables if they don't exist"""
    cursor = connection.cursor()
    
    # Leads table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            niche VARCHAR(100),
            problem TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    
    # Analytics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            event_name VARCHAR(100),
            event_data JSON,
            url VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    connection.commit()
    print("✅ Tables created/verified")

def insert_lead(name: str, email: str, niche: str, problem: str):
    """Insert a new lead"""
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO leads (name, email, niche, problem) VALUES (%s, %s, %s, %s)",
            (name, email, niche, problem)
        )
        connection.commit()
        return cursor.lastrowid
    except pymysql.IntegrityError:
        return None
    except Exception as e:
        print(f"Error inserting lead: {e}")
        return None

def insert_analytics(event_name: str, event_data: dict, url: str):
    """Insert analytics event"""
    try:
        import json
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO analytics (event_name, event_data, url) VALUES (%s, %s, %s)",
            (event_name, json.dumps(event_data), url)
        )
        connection.commit()
    except Exception as e:
        print(f"Error inserting analytics: {e}")

def get_leads(limit: int = 100):
    """Get all leads"""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM leads ORDER BY created_at DESC LIMIT %s", (limit,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching leads: {e}")
        return []