from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import sys
import os
import requests
import httpx

# Add both agent directories to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraping_agent'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'email_agent'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'email_send'))

# Import functions from both agents
from scraping_agent.main import get_professors_data
from email_agent.main import get_email
from email_agent.data import get_data
from email_send.main import send_email, EmailRequest as SendEmailRequest

app = FastAPI(
    title="Professor Research & Email API",
    description="API for finding professors and generating personalized emails",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
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

@app.get("/")
async def root():
    return {
        "message": "Professor Research & Email API",
        "endpoints": {
            "scraping": "/api/scraping",
            "email": "/api/email",
            "send-email": "/api/send-email",
            "docs": "/docs"
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

@app.post("/auth/callback")
async def auth_callback(request: dict):
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "code": request["code"],
                "grant_type": "authorization_code",
                "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code")
            
        return token_response.json()

@app.post("/auth/refresh")
async def refresh_token(request: dict):
    async with httpx.AsyncClient() as client:
        refresh_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "refresh_token": request["refresh_token"],
                "grant_type": "refresh_token",
            }
        )
        
        if refresh_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to refresh token")
            
        return refresh_response.json()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}
