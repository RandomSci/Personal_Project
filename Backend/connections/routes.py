from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()

from Backend.connections.mongo_db import get_leads_collection, get_analytics_collection, get_chats_collection
from Backend.connections.mysql_database import insert_lead, insert_analytics, get_leads
from Backend.connections.redis_database import cache_get, cache_set
from Backend.connections.functions import send_email, log_event

# Admin credentials from .env
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

router = APIRouter()

# Pydantic models
class AdminLogin(BaseModel):
    username: str
    password: str

class LeadSubmission(BaseModel):
    name: str
    email: EmailStr
    niche: str
    problem: str
    timestamp: str = None

class AnalyticsEvent(BaseModel):
    name: str
    timestamp: str
    url: str
    buttonText: str = None

class ChatMessage(BaseModel):
    message: str
    user_email: str = None

# POST /api/auth/login
@router.post("/auth/login")
async def admin_login(credentials: AdminLogin):
    """Simple admin login with hardcoded credentials"""
    if credentials.username == ADMIN_USERNAME and credentials.password == ADMIN_PASSWORD:
        return {
            "authenticated": True,
            "token": "admin_session_" + str(datetime.utcnow().timestamp()),
            "message": "Login successful"
        }
    else:
        return {
            "authenticated": False,
            "message": "Invalid credentials"
        }

# POST /api/leads
@router.post("/leads")
async def submit_lead(lead: LeadSubmission, background_tasks: BackgroundTasks):
    """Submit a new lead from the form"""
    try:
        # Check if email already exists in cache
        cached = await cache_get(f"lead:{lead.email}")
        if cached:
            raise HTTPException(status_code=400, detail="Email already submitted")
        
        # Insert into MongoDB
        leads_col = await get_leads_collection()
        mongo_result = await leads_col.insert_one({
            "name": lead.name,
            "email": lead.email,
            "niche": lead.niche,
            "problem": lead.problem,
            "created_at": datetime.utcnow(),
            "source": "web_form"
        })
        
        # Also insert into MySQL for backup
        insert_lead(lead.name, lead.email, lead.niche, lead.problem)
        
        # Cache the email for 24 hours
        await cache_set(f"lead:{lead.email}", "submitted", ex=86400)
        
        # Send email notification in background
        background_tasks.add_task(send_email, lead.email, lead.name, lead.niche, lead.problem)
        
        # Log event
        await log_event("lead_submitted", {
            "email": lead.email,
            "niche": lead.niche
        })
        
        return {
            "status": "success",
            "message": "Lead submitted successfully",
            "lead_id": str(mongo_result.inserted_id)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error submitting lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# POST /api/analytics
@router.post("/analytics")
async def track_analytics(event: AnalyticsEvent):
    """Track user interactions and events"""
    try:
        analytics_col = await get_analytics_collection()
        
        await analytics_col.insert_one({
            "name": event.name,
            "timestamp": event.timestamp,
            "url": event.url,
            "buttonText": event.buttonText,
            "created_at": datetime.utcnow()
        })
        
        # Also to MySQL
        insert_analytics(event.name, {
            "button": event.buttonText,
            "url": event.url
        }, event.url)
        
        return {"status": "tracked"}
    
    except Exception as e:
        print(f"Analytics error: {e}")
        return {"status": "error", "detail": str(e)}

# POST /api/chat
@router.post("/chat")
async def chat_message(message: ChatMessage):
    """Store chat messages"""
    try:
        chats_col = await get_chats_collection()
        
        result = await chats_col.insert_one({
            "message": message.message,
            "user_email": message.user_email,
            "created_at": datetime.utcnow()
        })
        
        return {
            "status": "success",
            "message_id": str(result.inserted_id)
        }
    
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# GET /api/leads (get all leads)
@router.get("/leads")
async def get_all_leads():
    """Get all leads"""
    try:
        from Backend.connections.mongo_db import db
        
        if db is not None:
            leads_col = db["leads"]
            leads = list(leads_col.find({}))
            
            # Convert ObjectId to string for JSON serialization
            for lead in leads:
                lead["_id"] = str(lead["_id"])
            
            return {
                "count": len(leads),
                "leads": leads
            }
        else:
            return {
                "count": 0,
                "leads": []
            }
    
    except Exception as e:
        print(f"Error fetching leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# GET /api/analytics (get all analytics events)
@router.get("/analytics")
async def get_analytics():
    """Get all analytics events"""
    try:
        from Backend.connections.mongo_db import db
        
        if db is not None:
            analytics_col = db["analytics"]
            events = list(analytics_col.find({}))
            
            for event in events:
                event["_id"] = str(event["_id"])
            
            return {
                "count": len(events),
                "events": events
            }
        else:
            return {
                "count": 0,
                "events": []
            }
    
    except Exception as e:
        print(f"Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def api_health():
    return {"status": "ok", "api": "v1"}