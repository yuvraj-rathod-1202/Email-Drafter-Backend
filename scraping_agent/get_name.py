import os
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
import json
from typing import List

load_dotenv()

class Professor(BaseModel):
    id: str
    name: str
    department: str
    research_areas: List[str]
    email: str
    additional_data: List[str]

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_professors_info(prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"""Task:
            You are given a free-form user prompt describing research interests. Your job is to:

            1. Identify EXACTLY 3-5 best-matching professors from Indian Institutes of Technology (IIT) based on the research interests described in the prompt.
            2. Focus primarily on professors from IIT Gandhinagar, but include professors from other IITs if they are highly relevant.
            3. Rank them by relevance to the user's research interests (most relevant first).
            4. Provide current working email addresses and department information.
            5. Include additional information like specific research projects, notable publications, or expertise areas.
            
            Return an array of exactly 3-5 professors in the following format:

            class Professor(BaseModel):
                id: str  # unique identifier (1, 2, 3, etc.)
                name: str  # full name with title (Dr./Prof.)
                department: str  # academic department
                research_areas: List[str]  # array of research areas
                email: str  # current email address
                additional_data: List[str]  # additional information like research interests, publications, etc.

            Make sure to return exactly 3-5 professors that best match the research interests, ranked by relevance.
            Fill the additional_data field with relevant information like specific research projects, recent publications, or specialized expertise areas.

            Prompt: {prompt}
        """,
        config={
            "response_mime_type": "application/json",
            "response_schema": {"type": "array", "items": Professor.model_json_schema()},
        }
    )

    try:
        data_list = json.loads(response.text) if response.text else []
        professors = []
        for i, data_dict in enumerate(data_list):
            # Ensure all required fields are present
            professor_data = {
                "id": data_dict.get("id", str(i + 1)),
                "name": data_dict.get("name", ""),
                "department": data_dict.get("department", ""),
                "research_areas": data_dict.get("research_areas", []),
                "email": data_dict.get("email", ""),
                "additional_data": data_dict.get("additional_data", [])
            }
            professors.append(Professor(**professor_data))
        
        print(f"Extracted {len(professors)} Professors")
        return [prof.dict() for prof in professors]
    except Exception as e:
        print(f"Error parsing professors: {e}")
        return []


# get_professors_info(prompt="I am interestd to work with nipun batra")