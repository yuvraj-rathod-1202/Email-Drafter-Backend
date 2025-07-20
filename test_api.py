import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"

def test_scraping_endpoint():
    """Test the scraping endpoint"""
    print("Testing /scraping endpoint...")
    
    payload = {
        "prompt": "I am interested in application of AI which puts impact in society, My department is AI and I am looking for professors who are working in this area."
    }
    
    response = requests.post(f"{BASE_URL}/scraping", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Scraping successful!")
        print(f"Professor: {result['name']}")
        print(f"Email: {result['email']}")
        print(f"Data entries: {len(result['data'])}")
        return result
    else:
        print(f"❌ Scraping failed: {response.status_code} - {response.text}")
        return None

def test_email_endpoint():
    """Test the email endpoint"""
    print("\nTesting /email endpoint...")
    
    payload = {
        "name": "Krishna Prasad Miyapuram",
        "email": "krishnakm@iitgn.ac.in",
        "user_prompt": "I am interested in application of AI which puts impact in society",
        "user_data": "Name: Yuvraj Rathod, Department: AI, Institute: IIT Gandhinagar, Year: second, Interest: use of AI in real world applications"
    }
    
    response = requests.post(f"{BASE_URL}/email", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Email generation successful!")
        print(f"To: {result['to']}")
        print(f"Subject: {result['subject']}")
        print(f"Body preview: {result['body'][:100]}...")
        return result
    else:
        print(f"❌ Email generation failed: {response.status_code} - {response.text}")
        return None

def test_combined_endpoint():
    """Test the combined scrape-and-email endpoint"""
    print("\nTesting /scrape-and-email endpoint...")
    
    payload = {
        "scraping_prompt": "I am interested in application of AI which puts impact in society, My department is AI and I am looking for professors who are working in this area.",
        "user_data": "Name: Yuvraj Rathod, Department: AI, Institute: IIT Gandhinagar, Year: second, Interest: use of AI in real world applications"
    }
    
    response = requests.post(f"{BASE_URL}/scrape-and-email", params=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Combined operation successful!")
        print(f"Professor: {result['professor_data']['name']}")
        print(f"Email Subject: {result['email']['subject']}")
        return result
    else:
        print(f"❌ Combined operation failed: {response.status_code} - {response.text}")
        return None

def test_health_endpoint():
    """Test the health check endpoint"""
    print("\nTesting /health endpoint...")
    
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Health check: {result['status']}")
        return result
    else:
        print(f"❌ Health check failed: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    print("🚀 Testing FastAPI Professor Research & Email API")
    print("=" * 50)
    
    # Test health first
    test_health_endpoint()
    
    # Test individual endpoints
    professor_data = test_scraping_endpoint()
    email_data = test_email_endpoint()
    
    # Test combined endpoint
    combined_data = test_combined_endpoint()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
