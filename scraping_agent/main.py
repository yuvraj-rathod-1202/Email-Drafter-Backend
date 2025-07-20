from get_name import get_professors_info
from get_data import get_data

def get_professors_data(prompt):
    professors_info = get_professors_info(prompt)
    
    # Process each professor and get their additional data
    professors_with_data = []
    for prof in professors_info:
        # Convert the new format to old format for get_data compatibility
        prof_data_legacy = {
            'name': prof.get('name', ''),
            'curent_institute': prof.get('department', '')  # Use department as institute
        }
        
        try:
            additional_data = get_data(prof_data_legacy)
        except Exception as e:
            print(f"Error getting data for {prof.get('name', '')}: {e}")
            additional_data = []
        
        # Create the final professor object with merged additional data
        # Combine AI-generated additional data with scraped additional data
        ai_additional_data = prof.get("additional_data", [])
        scraped_additional_data = additional_data if isinstance(additional_data, list) else []
        
        professor_result = {
            "id": prof.get("id"),
            "name": prof.get("name"),
            "department": prof.get("department"),
            "research_areas": prof.get("research_areas"),
            "email": prof.get("email"),
            "additional_data": ai_additional_data + scraped_additional_data
        }
        professors_with_data.append(professor_result)
    
    return professors_with_data


if __name__ == "__main__":
    user_prompt = "I am interested in application of AI which put impact in society, My department is AI and I am looking for professors who are working in this area. Please help me to find the best matching professors"
    professors_data = get_professors_data(user_prompt)

    print(f"Found {len(professors_data)} professors:")
    for prof in professors_data:
        print(f"- {prof['name']} ({prof['department']})")
        print(f"  Research Areas: {prof['research_areas']}")
        print(f"  Email: {prof['email']}")
        print()