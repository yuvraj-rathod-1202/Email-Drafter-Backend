from get_name import get_professors_info
from get_data import get_data

def get_professors_data(prompt):
    
    professor_info = get_professors_info(prompt)

    data = get_data(professor_info)

    return {"name": professor_info.get("name"), "email": professor_info.get("email"), "data": data}


if __name__ == "__main__":
    user_prompt = "I am interested in apllication of AI which put impact in society, My department is AI and I am looking for professors who are working in this area. Please help me to find the best matching professors"
    professors_data = get_professors_data(user_prompt)

    print(professors_data.get("data"))