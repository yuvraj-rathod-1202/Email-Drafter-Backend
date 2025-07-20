import os
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
import json

load_dotenv()

class Professor(BaseModel):
    name: str
    email: str
    curent_institute: str

client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))

def get_professors_info(prompt):
    

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"""Task:
            You are given a free-form user prompt. Your job is to:

            1. Check if the name of a professor is mentioned in the prompt.
            - If a professor's name is explicitly written, return their details in the given schema.
            - If the name is not mentioned, identify the best-matching IIT Gnadhinagar professor based on research interests described in the prompt.

            2. Use your knowledge of faculty members at the Indian Institutes of Technology Gandhinagar (IITGN) and their research areas.

            3. Give the current working email of current institute of the professor where they are teaching now.

            4. Return the output strictly in the following format:

            class Professor(BaseModel):
                name: str
                email: str
                curent_institute: str

            Prompt: {prompt}
        """,
        config={
            "response_mime_type": "application/json",
            "response_schema": Professor.model_json_schema(),
        }
    )

    data_dict = json.loads(response.text) if response.text else {"name": "", "email": "", "curent_institute": ""}
    professor = Professor(**data_dict)
    print(f"Extracted Professor Info: {professor.dict()}")
    return professor.dict() if professor else {"name": "", "email": "", "curent_institute": ""}


# get_professors_info(prompt="I am interestd to work with nipun batra")