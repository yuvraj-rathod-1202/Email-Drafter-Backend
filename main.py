from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import sys
import os
import requests
import httpx
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import firebase_admin
from firebase_admin import credentials, firestore
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv

load_dotenv()

# Add both agent directories to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraping_agent'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'email_agent'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'email_send'))

# Import functions from both agents
from scraping_agent.main import get_professors_data
from email_agent.main import get_email
from email_agent.data import get_data
from email_send.main import send_email, EmailRequest as SendEmailRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        })
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Failed to initialize Firebase: {e}")
        raise

db = firestore.client()
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler.start()
    logger.info("Scheduler started")
    
    # Add the scheduled job to run every 5 minutes
    scheduler.add_job(
        send_scheduled_emails,
        IntervalTrigger(minutes=1),
        id='send_scheduled_emails',
        name='Send scheduled emails',
        replace_existing=True
    )
    
    yield
    
    # Shutdown
    scheduler.shutdown()
    logger.info("Scheduler stopped")

# Firebase database functions
def get_due_scheduled_emails(now: datetime) -> List[Dict]:
    """Get emails that are scheduled and due to be sent (within 5 minutes of scheduled time)"""
    try:
        # Calculate the time window (current time ± 5 minutes)
        time_window_start = now - timedelta(minutes=5)
        time_window_end = now + timedelta(minutes=5)
        
        query = db.collection('emails').where(
            'status', '==', 'scheduled'
        ).where(
            'scheduledAt', '>=', time_window_start
        ).where(
            'scheduledAt', '<=', time_window_end
        )
        
        emails = []
        for doc in query.stream():
            email_data = doc.to_dict()
            email_data['id'] = doc.id
            emails.append(email_data)
        
        return emails
    except Exception as e:
        logger.error(f"Error fetching scheduled emails: {e}")
        return []

def update_email_status(email_id: str, status: str, sent_at: Optional[datetime] = None) -> bool:
    """Update email status and sentAt timestamp"""
    try:
        update_data: Dict[str, Any] = {'status': status}
        if sent_at:
            # Firestore automatically handles datetime objects
            update_data['sentAt'] = sent_at
            
        db.collection('emails').document(email_id).update(update_data)
        return True
    except Exception as e:
        logger.error(f"Error updating email status: {e}")
        return False

async def get_user_tokens(userId: str) -> Optional[Dict]:
    """Get user's OAuth tokens from userTokens collection"""
    try:
        # Get userTokens document using userId as document ID
        doc_ref = db.collection('userTokens').document(userId)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
        
    except Exception as e:
        logger.error(f"Error fetching user tokens for userId {userId}: {e}")
        return None

async def refresh_user_token(userId: str, refresh_token: str) -> Optional[Dict]:
    """Refresh user's access token"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                }
            )
            
            if response.status_code == 200:
                tokens = response.json()
                
                # Calculate new expiry time
                expires_at = datetime.now(timezone.utc) + timedelta(seconds=tokens.get('expires_in', 3600))
                
                # Update tokens in database
                await update_user_tokens(userId, tokens['access_token'], expires_at)
                
                return {
                    'access_token': tokens['access_token'],
                    'expires_at': expires_at
                }
            else:
                logger.error(f"Token refresh failed for userId {userId}: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Error refreshing token for userId {userId}: {e}")
        return None

async def update_user_tokens(userId: str, access_token: str, expires_at: datetime) -> bool:
    """Update user's tokens in userTokens collection"""
    try:
        # Update the token document using userId as document ID
        doc_ref = db.collection('userTokens').document(userId)
        doc_ref.update({
            'access_token': access_token,
            'expires_at': expires_at,
            'updated_at': datetime.now(timezone.utc)
        })
        return True
            
    except Exception as e:
        logger.error(f"Error updating tokens for userId {userId}: {e}")
        return False

async def send_email_from_user(user_email: str, to_email: str, subject: str, body: str, userId: str) -> bool:
    """Send email from user's email to recipient using Gmail API"""
    try:
        logger.info(f"Attempting to send email from {user_email} to {to_email}")
        logger.info(f"Subject: {subject}")
        
        # 1. Get user's stored OAuth tokens
        user_tokens = await get_user_tokens(userId)
        if not user_tokens:
            logger.error(f"No tokens found for user: {user_email}")
            return False
        
        access_token = user_tokens.get('access_token')
        expires_at = user_tokens.get('expires_at')
        refresh_token = user_tokens.get('refresh_token')
        
        if not access_token or not refresh_token:
            logger.error(f"Invalid tokens for user: {user_email}")
            return False
        
        # 2. Check if token needs refresh
        now = datetime.now(timezone.utc)
        if expires_at:
            expires_at_dt = datetime.fromtimestamp(expires_at / 1000, tz=timezone.utc)

            if expires_at_dt < now:
                logger.info(f"Token expired for userId {userId}, refreshing...")
                refreshed_tokens = await refresh_user_token(userId, refresh_token)

                if not refreshed_tokens:
                    logger.error(f"Failed to refresh token for userId {userId}")
                    return False

                access_token = refreshed_tokens['access_token']
        
        # 3. Send email using Gmail API
        email_request = SendEmailRequest(
            access_token=access_token,
            to=to_email,
            subject=subject,
            body=body
        )
        
        result = await send_email(email_request)
        
        if "id" in result:
            logger.info(f"Email sent successfully from {user_email} to {to_email}")
            return True
        else:
            logger.error(f"Failed to send email from {user_email} to {to_email}: {result}")
            return False
        
    except Exception as e:
        logger.error(f"Error sending email from {user_email} to {to_email}: {e}")
        return False

async def send_scheduled_emails():
    """Send emails that are scheduled and due to be sent"""
    try:
        now = datetime.now(timezone.utc)
        scheduled_emails = get_due_scheduled_emails(now)
        print("Found scheduled emails:")
        logger.info(f"Found {len(scheduled_emails)} emails scheduled for sending")
        
        for email in scheduled_emails:
            try:
                email_id = email['id']
                user_email = email['userEmail']
                to_email = email['to']
                subject = email['subject']
                body = email['body']
                
                logger.info(f"Processing scheduled email {email_id} from {user_email} to {to_email}")
                
                # Send the email
                success = await send_email_from_user(user_email, to_email, subject, body, email['userId'])
                
                if success:
                    # Update status to 'sent' and set sentAt timestamp
                    update_email_status(email_id, 'sent', datetime.now(timezone.utc))
                    logger.info(f"Successfully sent email {email_id}")
                else:
                    # Update status to 'failed'
                    update_email_status(email_id, 'failed')
                    logger.error(f"Failed to send email {email_id}")
                    
            except Exception as e:
                logger.error(f"Error processing email {email.get('id', 'unknown')}: {e}")
                # Update status to 'failed' on error
                if 'id' in email:
                    update_email_status(email['id'], 'failed')
                
    except Exception as e:
        logger.error(f"Error in send_scheduled_emails: {e}")

app = FastAPI(
    title="Professor Research & Email API",
    description="API for finding professors and generating personalized emails",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://academic-email-agent.vercel.app",
        "http://localhost:8081",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# Pydantic models for request/response
class ScrapingRequest(BaseModel):
    prompt: str

class ProfessorResponse(BaseModel):
    id: str
    name: str
    department: str
    research_areas: List[str]
    email: str
    additional_data: Optional[List] = []

class EmailRequest(BaseModel):
    name: str
    email: str
    user_prompt: str
    user_data: str
    data: Optional[List] = None

class EmailResponse(BaseModel):
    subject: str
    body: str
    to: str
    
class CodeModel(BaseModel):
    code: str

# Updated model to match your EmailRecord interface
class EmailRecord(BaseModel):
    id: Optional[str] = None
    professorName: str
    professorEmail: str
    userEmail: str
    subject: str
    body: str
    status: str  # 'sent' | 'scheduled' | 'delivered' | 'failed'
    sentAt: Optional[datetime] = None
    scheduledAt: Optional[datetime] = None
    researchInterest: str
    userId: str

class UserTokens(BaseModel):
    id: Optional[str] = None
    userEmail: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    updated_at: datetime

@app.get("/")
async def root():
    return {
        "message": "Professor Research & Email API",
        "endpoints": {
            "scraping": "/api/scraping",
            "email": "/api/email", 
            "send-email": "/api/send-email",
            "scheduled-emails": "/api/scheduled-emails",
            "trigger-scheduler": "/api/trigger-scheduled-emails",
            "user-tokens": "/api/user-tokens/{user_email}",
            "test-email": "/api/test-email-send",
            "health": "/health",
            "docs": "/docs"
        },
        "scheduler": {
            "status": "running",
            "interval": "5 minutes",
            "description": "Automatically sends emails with status 'scheduled' when scheduledAt is within ±5 minutes of current time"
        },
        "token_management": {
            "description": "Automatically retrieves and refreshes user tokens from userTokens collection",
            "collection": "userTokens",
            "required_fields": ["userEmail", "access_token", "refresh_token", "expires_at"]
        }
    }

@app.post("/api/scraping", response_model=List[ProfessorResponse])
async def scrape_professor_data(request: ScrapingRequest):
    """
    Scrape professor data based on research interests and requirements.
    
    Args:
        request: Contains the user prompt describing research interests
        
    Returns:
        Array of professor information including id, name, department, research_areas, and email
    """
    try:
        result = get_professors_data(request.prompt)
        
        # Convert the result to ProfessorResponse format
        professors = []
        for prof_data in result:
            professor = ProfessorResponse(
                id=prof_data.get("id", ""),
                name=prof_data.get("name", ""),
                department=prof_data.get("department", ""),
                research_areas=prof_data.get("research_areas", []),
                email=prof_data.get("email", ""),
                additional_data=prof_data.get("additional_data", [])
            )
            professors.append(professor)
        
        return professors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping professor data: {str(e)}")

@app.post("/api/email", response_model=EmailResponse)
async def generate_email(request: EmailRequest):
    """
    Generate a personalized email to a professor based on their research data.
    
    Args:
        request: Contains professor info, user data, and research context
        
    Returns:
        Generated email with subject, body, and recipient
    """
    try:
        # Use provided data or get default data
        professor_data = request.data if request.data else get_data()
        
        result = get_email(
            name=request.name,
            email=request.email,
            data=professor_data,
            userPrompt=request.user_prompt,
            userData=request.user_data
        )
        
        return EmailResponse(
            subject=result.get("subject", ""),
            body=result.get("body", ""),
            to=result.get("to", request.email)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating email: {str(e)}")


@app.post("/api/send-email")
async def send_email_endpoint(request: SendEmailRequest):
    """
    Send an email using Gmail API with the provided access token.
    
    Args:
        request: Contains access_token, to, subject, and body
        
    Returns:
        Status of email sending operation
    """
    try:
        result = await send_email(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

from fastapi import Request

@app.post("/auth/callback")
async def auth_callback(request: Request):
    body = await request.json()  # If frontend sends JSON
    # Or use: body = await request.form() if sent as form-data

    print("Received auth callback request", body)

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "code": body["code"],
                "grant_type": "authorization_code",
                "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
                "access_type": "offline",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if token_response.status_code != 200:
            print("Google Token Error:", token_response.text)
            raise HTTPException(status_code=400, detail="Failed to exchange code")

        return token_response.json()


@app.post("/auth/refresh")
async def refresh_token(request: Request):
    body = await request.json()
    
    async with httpx.AsyncClient() as client:
        refresh_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "refresh_token": body["refresh_token"],
                "grant_type": "refresh_token",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if refresh_response.status_code != 200:
            print("Refresh Token Error:", refresh_response.text)
            raise HTTPException(status_code=400, detail="Failed to refresh token")

        return refresh_response.json()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}