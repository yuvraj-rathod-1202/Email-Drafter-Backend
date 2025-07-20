from sentence_transformers import SentenceTransformer, util
import json

model = SentenceTransformer('all-MiniLM-L6-v2')

with open('C:\\projects\\Summer_Siege\\research_agent\\professors_data.json', 'r') as f:
    professors = json.load(f)

user_prompt = input("Describe your interests, department, or preferred research area:\n> ")
user_embedding = model.encode(user_prompt, convert_to_tensor=True)

WEIGHTS = {
    "Name": 0.3,
    "Research Interests": 0.3,
    "Publications": 0.3,
    "Department": 0.1
}

best_matches_score = 0
best_matches_prof = {}

for prof in professors:
    score = 0

    for field, weight in WEIGHTS.items():
        text = prof.get(field, "")
        if text:
            field_embedding = model.encode(text, convert_to_tensor=True)
            similarity = util.cos_sim(user_embedding, field_embedding)[0][0].item()
            score += weight * similarity

    if score > best_matches_score:
        best_matches_score = score
        best_matches_prof = prof


print("\nTop Matching Professors:")

print(f"\nName: {best_matches_prof['Name']}")
print(f"Department: {best_matches_prof['Department']}")
print(f"Interests: {best_matches_prof['Research Interests']}")
print(f"Publications: {best_matches_prof['Publications']}")
print(f"Match Score: {best_matches_score:.2f}")