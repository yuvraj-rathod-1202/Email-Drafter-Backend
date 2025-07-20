from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText

app = FastAPI()

# CORS for frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model
class EmailRequest(BaseModel):
    access_token: str
    to: str
    subject: str
    body: str

async def send_email(request: EmailRequest):
    try:
        # Use access token to send mail via Gmail API
        creds = Credentials(token=request.access_token)
        service = build('gmail', 'v1', credentials=creds)

        message = MIMEText(request.body)
        message['to'] = request.to
        message['subject'] = request.subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = service.users().messages().send(userId="me", body={'raw': raw}).execute()

        return {"status": "Email sent", "id": send_message['id']}

    except Exception as e:
        return {"error": str(e)}
