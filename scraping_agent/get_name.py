import os
import requests
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

def get_professors_info(prompt):
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt_text = f"""Task:
        You are given a free-form user prompt describing research interests. Your job is to:

        1. Identify EXACTLY 3-5 best-matching professors from Indian Institutes of Technology (IIT) based on the research interests described in the prompt.
        2. Focus primarily on professors from IIT Gandhinagar, but include professors from other IITs if they are highly relevant.
        3. Rank them by relevance to the user's research interests (most relevant first).
        4. Provide current working email addresses and department information.
        5. Include additional information like specific research projects, notable publications, or expertise areas.
        
        Return an array of exactly 3-5 professors in the following JSON format:
        [
            {{
                "id": "1",
                "name": "Prof. Name",
                "department": "Department Name",
                "research_areas": ["area1", "area2"],
                "email": "email@iitgn.ac.in",
                "additional_data": ["info1", "info2"]
            }}
        ]

        Make sure to return exactly 3-5 professors that best match the research interests, ranked by relevance.
        Fill the additional_data field with relevant information like specific research projects, recent publications, or specialized expertise areas.

        Prompt: {prompt}
    """
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt_text
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
        data_list = []
        try:
            data_list = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from text if it's wrapped in markdown
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_text = content[json_start:json_end].strip()
                data_list = json.loads(json_text)
            else:
                print("Failed to parse JSON response")
                return []
        
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
        print(f"Error generating professors info: {e}")
        return []


# get_professors_info(prompt="I am interestd to work with nipun batra")