from email_content import get_email_content
from data import get_data

def get_email(name, email, data, userPrompt, userData):

    subject, body = get_email_content(name, email, data, userPrompt, userData)

    return {
        "subject": subject,
        "body": body,
        "to": email,
    }

if __name__ == "__main__":
    name = "Krishna Prasad Miyapuram"
    email = "krishnakm@iitgn.ac.in"
    userPrompt = "I am interested in application of AI which puts impact in society, My department is AI and I am looking for professors who are working in this area. Please help me to find the best matching professors"
    userData = "Name: Yuvraj Rathod, Department: AI, Institute: IIT Gandhinagar, Year: second, Interest: use of AI in real world applications"
    data = get_data()
    
    data = get_email(name, email, data, userPrompt, userData)
    print(f"Subject:\n {data['subject']}")
    print(f"Body:\n {data['body']}")