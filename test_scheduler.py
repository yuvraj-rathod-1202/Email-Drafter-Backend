#!/usr/bin/env python3
"""
Test script for the updated email scheduling functionality
Works with existing emails collection in Firestore
"""

import httpx
import asyncio
from datetime import datetime, timezone, timedelta
import json

BASE_URL = "http://localhost:8000"

async def test_get_scheduled_emails():
    """Test getting scheduled emails from the emails collection"""
    
    async with httpx.AsyncClient() as client:
        # Get all scheduled emails
        print("Fetching scheduled emails...")
        response = await client.get(f"{BASE_URL}/api/scheduled-emails?sent=false")
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            emails = result['emails']
            print(f"Found {len(emails)} scheduled emails")
            
            for email in emails:
                print(f"- ID: {email['id']}")
                print(f"  From: {email.get('userEmail', 'N/A')}")
                print(f"  To: {email.get('professorEmail', 'N/A')} ({email.get('professorName', 'N/A')})")
                print(f"  Subject: {email.get('subject', 'N/A')}")
                print(f"  Status: {email.get('status', 'N/A')}")
                print(f"  Scheduled At: {email.get('scheduledAt', 'N/A')}")
                print()
        else:
            print(f"Error: {response.text}")

async def test_get_sent_emails():
    """Test getting sent emails from the emails collection"""
    
    async with httpx.AsyncClient() as client:
        # Get all sent emails
        print("Fetching sent emails...")
        response = await client.get(f"{BASE_URL}/api/scheduled-emails?sent=true")
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            emails = result['emails']
            print(f"Found {len(emails)} sent emails")
            
            for email in emails:
                print(f"- ID: {email['id']}")
                print(f"  From: {email.get('userEmail', 'N/A')}")
                print(f"  To: {email.get('professorEmail', 'N/A')} ({email.get('professorName', 'N/A')})")
                print(f"  Subject: {email.get('subject', 'N/A')}")
                print(f"  Status: {email.get('status', 'N/A')}")
                print(f"  Sent At: {email.get('sentAt', 'N/A')}")
                print()
        else:
            print(f"Error: {response.text}")

async def test_trigger_scheduler():
    """Test manually triggering the scheduler"""
    
    async with httpx.AsyncClient() as client:
        print("Manually triggering the email scheduler...")
        response = await client.post(f"{BASE_URL}/api/trigger-scheduled-emails")
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Scheduler result: {result['message']}")
        else:
            print(f"Error: {response.text}")

async def test_health_check():
    """Test the health check endpoint"""
    
    async with httpx.AsyncClient() as client:
        print("Checking API health...")
        response = await client.get(f"{BASE_URL}/health")
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Health status: {result['status']} - {result['message']}")
        else:
            print(f"Error: {response.text}")

async def test_api_info():
    """Test the root endpoint to see API information"""
    
    async with httpx.AsyncClient() as client:
        print("Getting API information...")
        response = await client.get(f"{BASE_URL}/")
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("API Information:")
            print(f"- Message: {result['message']}")
            print("- Available endpoints:")
            for endpoint, path in result['endpoints'].items():
                print(f"  {endpoint}: {path}")
            
            if 'scheduler' in result:
                scheduler_info = result['scheduler']
                print("- Scheduler information:")
                print(f"  Status: {scheduler_info['status']}")
                print(f"  Interval: {scheduler_info['interval']}")
                print(f"  Description: {scheduler_info['description']}")
        else:
            print(f"Error: {response.text}")

async def test_user_tokens(user_email: str = "test@example.com"):
    """Test getting user token information"""
    
    async with httpx.AsyncClient() as client:
        print(f"Checking user tokens for: {user_email}")
        response = await client.get(f"{BASE_URL}/api/user-tokens/{user_email}")
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Token Information:")
            print(f"- User Email: {result.get('userEmail')}")
            print(f"- Has Tokens: {result.get('hasTokens')}")
            print(f"- Expires At: {result.get('expiresAt')}")
            print(f"- Updated At: {result.get('updatedAt')}")
            print(f"- Is Expired: {result.get('isExpired')}")
        elif response.status_code == 404:
            print("No tokens found for this user")
        else:
            print(f"Error: {response.text}")

async def test_manual_email_send():
    """Test manually sending an email"""
    
    async with httpx.AsyncClient() as client:
        # Test email data
        email_data = {
            "userEmail": "test@example.com",  # Replace with actual user email
            "toEmail": "recipient@example.com",  # Replace with test recipient
            "subject": "Test Email from Scheduler",
            "body": "This is a test email sent through the API scheduler system."
        }
        
        print("Testing manual email send...")
        response = await client.post(f"{BASE_URL}/api/test-email-send", json=email_data)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Email Send Result:")
            print(f"- Success: {result.get('success')}")
            print(f"- Message: {result.get('message')}")
            print(f"- From: {result.get('from')}")
            print(f"- To: {result.get('to')}")
            print(f"- Subject: {result.get('subject')}")
        else:
            print(f"Error: {response.text}")

async def create_sample_scheduled_email():
    """
    Note: This function shows how to create a sample email record.
    In practice, you would create this from your frontend application.
    """
    
    print("\nNote: To test the scheduler, you need to:")
    print("1. Add email records to your Firestore 'emails' collection with:")
    print("   - status: 'scheduled'")
    print("   - scheduledAt: within ±5 minutes of current time")
    print("   - All required fields as per EmailRecord interface")
    print()
    print("2. Add user tokens to your Firestore 'userTokens' collection with:")
    print("   - userEmail: matching the userEmail in the email record")
    print("   - access_token: valid Google OAuth access token")
    print("   - refresh_token: valid Google OAuth refresh token")
    print("   - expires_at: token expiration timestamp")
    print("   - updated_at: last update timestamp")
    print()
    print("Sample email record structure:")
    
    sample_email = {
        "professorName": "Dr. John Smith",
        "professorEmail": "john.smith@university.edu",
        "userEmail": "student@example.com",
        "subject": "Research Collaboration Inquiry",
        "body": "Dear Dr. Smith, I am interested in your research on...",
        "status": "scheduled",
        "scheduledAt": datetime.now(timezone.utc).isoformat(),
        "researchInterest": "Machine Learning",
        "userId": "user123"
    }
    
    print(json.dumps(sample_email, indent=2, default=str))
    
    print("\nSample userTokens record structure:")
    sample_tokens = {
        "userEmail": "student@example.com",
        "access_token": "ya29.a0AfH6SMC...",  # Your actual access token
        "refresh_token": "1//0GWZ9...",        # Your actual refresh token
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    print(json.dumps(sample_tokens, indent=2, default=str))

if __name__ == "__main__":
    print("Testing updated email scheduling functionality...")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("="*60)
    
    # Test API info
    asyncio.run(test_api_info())
    print("\n" + "="*60 + "\n")
    
    # Test health check
    asyncio.run(test_health_check())
    print("\n" + "="*60 + "\n")
    
    # Test user tokens
    asyncio.run(test_user_tokens("test@example.com"))  # Replace with actual user email
    print("\n" + "="*60 + "\n")
    
    # Test manual email send
    asyncio.run(test_manual_email_send())
    print("\n" + "="*60 + "\n")
    
    # Test getting scheduled emails
    asyncio.run(test_get_scheduled_emails())
    print("\n" + "="*60 + "\n")
    
    # Test getting sent emails
    asyncio.run(test_get_sent_emails())
    print("\n" + "="*60 + "\n")
    
    # Test manual trigger
    asyncio.run(test_trigger_scheduler())
    print("\n" + "="*60 + "\n")
    
    # Show sample email structure
    asyncio.run(create_sample_scheduled_email())
