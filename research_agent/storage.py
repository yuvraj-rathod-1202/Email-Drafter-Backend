import json
import os

def save_professor_data(data, path="C:\\projects\\Summer_Siege\\research_agent\\professors_data.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            existing = json.load(f)
    else:
        existing = []

    existing.append(data)
    with open(path, "w") as f:
        json.dump(existing, f, indent=2)
