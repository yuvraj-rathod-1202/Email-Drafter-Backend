import requests
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
load_dotenv()

class EmailContent(BaseModel):
    subject: str
    body: str

def get_email_content(name, email, data, userPrompt, userData):
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt = f"""Task:
        You are an AI assistant that generates email content for professors.
        Create a professional email to {name} at {email} based on the provided data.

        Data: {data}
        
        From users perspective, the email should be concise, respectful, and relevant to the professor's expertise. The email should include:
        1. A clear subject line that reflects the content of the email.
        2. A body that introduces the user, states the purpose of the email, and includes any relevant information or questions.
        3. A polite closing statement.

        Ensure that the email is well-structured and free of grammatical errors.
        User Prompt: {userPrompt}
        User Data: {userData}

        Generate the email subject and body in JSON format:
        {{
            "subject": "Your email subject here",
            "body": "Your email body here with \\n for line breaks"
        }}

        Return only the JSON object.
    """
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        content = result['candidates'][0]['content']['parts'][0]['text']
        
        # Try to parse JSON from the response
        try:
            data_dict = json.loads(content)
        except json.JSONDecodeError:
            # Fallback if not proper JSON
            data_dict = {"subject": "No Subject", "body": content}
        
        email_content = EmailContent(**data_dict)
        subject = email_content.subject if email_content.subject else "No Subject"
        body = email_content.body if email_content.body else "No Body"
        
        return [subject, body]
        
    except Exception as e:
        print(f"Error generating email content: {e}")
        return ["Error generating subject", "Error generating email content"]