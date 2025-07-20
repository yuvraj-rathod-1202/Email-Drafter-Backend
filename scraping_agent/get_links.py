import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_links(prof_name, prof_institute):
    params = {
        "q": f"{prof_name} {prof_institute} current research projects",
        "api_key": os.getenv("SERP_API_KEY"),
        "engine": "google"
    }

    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()

    links = []

    for result in data.get("organic_results", []):
        links.append([result.get("link"), result.get("title", "")])

    return links


# print(get_links("Nipun Batra", "IIT Gandhinagar"))