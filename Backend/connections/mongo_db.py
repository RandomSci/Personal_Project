from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGO_DB", "automate_ai")

client = None
db = None

def init_mongo():
    global client, db
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DATABASE_NAME]
        # Verify connection
        client.admin.command('ping')
        print(f"✅ Connected to MongoDB: {DATABASE_NAME}")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("⚠️  Running without MongoDB")

def close_mongo():
    global client
    if client:
        client.close()
        print("✅ MongoDB connection closed")

def get_mongo_db():
    return db

# Collections
def get_leads_collection():
    if db:
        return db["leads"]
    return None

def get_analytics_collection():
    if db:
        return db["analytics"]
    return None

def get_chats_collection():
    if db:
        return db["chats"]
    return None

# Insert operations
def insert_lead_mongo(name: str, email: str, niche: str, problem: str):
    """Insert lead to MongoDB"""
    try:
        if db:
            leads = db["leads"]
            result = leads.insert_one({
                "name": name,
                "email": email,
                "niche": niche,
                "problem": problem,
                "created_at": __import__('datetime').datetime.utcnow()
            })
            return str(result.inserted_id)
    except Exception as e:
        print(f"MongoDB insert error: {e}")
    return None

def get_all_leads_mongo():
    """Get all leads from MongoDB"""
    try:
        if db:
            leads = db["leads"]
            return list(leads.find({}).limit(100))
    except Exception as e:
        print(f"MongoDB fetch error: {e}")
    return []