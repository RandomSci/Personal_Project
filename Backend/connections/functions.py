import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
YOUR_EMAIL = os.getenv("YOUR_EMAIL", "")

def send_email(recipient_email: str, name: str, niche: str, problem: str) -> bool:
    """Send email notification to you and auto-reply to user"""
    try:
        if not SENDER_EMAIL or not SENDER_PASSWORD:
            print("⚠️ Email not configured in .env")
            return False
        # Email to you (notification)
        subject_to_you = f"🚀 New Lead: {name} from {niche}"
        body_to_you = f"""
        <h2>New Lead Submission</h2>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {recipient_email}</p>
        <p><strong>Niche:</strong> {niche}</p>
        <p><strong>Problem:</strong> {problem}</p>
        <p><em>Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
        """
        
        send_smtp_email(YOUR_EMAIL, subject_to_you, body_to_you)
        
        # Auto-reply to user
        subject_to_user = "Your Automation Plan is Coming! 🤖"
        body_to_user = f"""
        <h2>Hi {name},</h2>
        <p>Thanks for reaching out! I got your message about your {niche} business.</p>
        <p><strong>Here's what happens next:</strong></p>
        <ul>
            <li>I'll review your bottleneck within 24 hours</li>
            <li>You'll get a personalized automation plan</li>
            <li>We'll schedule a quick call to discuss setup</li>
        </ul>
        <p>In the meantime, check out some quick automation wins in my case studies.</p>
        <p>Talk soon!<br><strong>AutoMate AI</strong></p>
        """
        
        send_smtp_email(recipient_email, subject_to_user, body_to_user)
        
        print(f"✅ Emails sent successfully for {recipient_email}")
        return True
    
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

def send_smtp_email(recipient: str, subject: str, body: str):
    """Generic SMTP email sender"""
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL
        message["To"] = recipient
        
        part = MIMEText(body, "html")
        message.attach(part)
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient, message.as_string())
        
        return True
    except Exception as e:
        print(f"SMTP error: {e}")
        return False

async def log_event(event_name: str, event_data: dict):
    """Log events for debugging/analytics"""
    try:
        from Backend.connections.mongo_db import get_analytics_collection
        analytics_col = await get_analytics_collection()
        await analytics_col.insert_one({
            "event": event_name,
            "data": event_data,
            "timestamp": datetime.utcnow()
        })
    except Exception as e:
        print(f"Logging error: {e}")

def generate_automation_plan(niche: str, problem: str) -> str:
    """Generate a basic automation plan based on niche and problem"""
    plans = {
        "saas": "Implement AI chatbot for customer support + automated onboarding emails",
        "ecommerce": "Set up automated abandoned cart recovery + inventory notifications",
        "agency": "Build client reporting dashboard + automated weekly status emails",
        "creator": "Automate social media posting + email list growth sequences",
        "service": "Create booking automation + automated invoice reminders"
    }
    
    return plans.get(niche.lower(), "Custom automation workflow based on your needs")