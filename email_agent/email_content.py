from google.generativeai import genai
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
load_dotenv()

class EmailContent(BaseModel):
    subject: str
    body: str

client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))

def get_email_content(name, email, data, userPrompt, userData):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""Task:
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

            Generate the email subject and body in the following format:
            class EmailContent(BaseModel):
                subject: str
                body: str

            The `body` string should contain `\\n` where a new line should occur. Return the output strictly in the format above as a JSON object.
        """,
        config={
            "response_mime_type": "application/json",
            "response_schema": EmailContent.model_json_schema(),
        }
    )

    data_dict = json.loads(response.text) if response.text else {"subject": "", "body": ""}
    email_content = EmailContent(**data_dict)
    subject = email_content.subject if email_content.subject else "No Subject"
    body = email_content.body if email_content.body else "No Body"
    
    return [subject, body]