# Professor Research & Email API

A FastAPI-based web service that combines professor research data scraping with personalized email generation capabilities.

**Frontend Repository**: [academic-agent-outreach](https://github.com/yuvraj-rathod-1202/academic-agent-outreach)

## Features

- **Professor Data Scraping**: Find professors based on research interests and requirements
- **Email Generation**: Create personalized emails to professors using their research data
- **Combined Operations**: Scrape professor data and generate emails in one request
- **Interactive Documentation**: Automatic API documentation via FastAPI

## Setup

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**
```bash
cd Email-Drafter-Backend
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file in the root directory with:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### Running the Server

#### Option 1: Using the startup scripts

**Windows Command Prompt:**
```bash
start_server.bat
```

**Windows PowerShell:**
```powershell
.\start_server.ps1
```

#### Option 2: Direct Python execution
```bash
python main.py
```

#### Option 3: Using uvicorn directly
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start on `http://localhost:8000`

## API Endpoints

### 1. Root Endpoint
- **GET** `/`
- Returns API information and available endpoints

### 2. Professor Data Scraping
- **POST** `/scraping`
- Scrapes professor data based on research interests

**Request Body:**
```json
{
  "prompt": "I am interested in application of AI which puts impact in society, My department is AI and I am looking for professors who are working in this area."
}
```

**Response:**
```json
{
  "name": "Professor Name",
  "email": "professor@university.edu",
  "data": [
    {
      "title": "Research Paper Title",
      "data": "Research details..."
    }
  ]
}
```

### 3. Email Generation
- **POST** `/email`
- Generates personalized emails to professors

**Request Body:**
```json
{
  "name": "Krishna Prasad Miyapuram",
  "email": "krishnakm@iitgn.ac.in",
  "user_prompt": "I am interested in application of AI which puts impact in society",
  "user_data": "Name: Yuvraj Rathod, Department: AI, Institute: IIT Gandhinagar, Year: second, Interest: use of AI in real world applications",
  "data": null
}
```

**Response:**
```json
{
  "subject": "Email Subject",
  "body": "Email body content...",
  "to": "professor@university.edu"
}
```

### 4. Combined Scrape and Email
- **POST** `/scrape-and-email`
- Combines scraping and email generation in one request

**Query Parameters:**
- `scraping_prompt`: Prompt for finding professors
- `user_data`: Information about the user
- `user_prompt`: Optional custom prompt for email generation

**Response:**
```json
{
  "professor_data": {
    "name": "Professor Name",
    "email": "professor@university.edu",
    "data": [...]
  },
  "email": {
    "subject": "Email Subject",
    "body": "Email body...",
    "to": "professor@university.edu"
  }
}
```

### 5. Health Check
- **GET** `/health`
- Returns server health status

## Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Testing

Run the test script to verify all endpoints:
```bash
python test_api.py
```

## Example Usage

### Using curl

**Scrape professor data:**
```bash
curl -X POST "http://localhost:8000/scraping" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "I am interested in AI applications in healthcare"
     }'
```

**Generate email:**
```bash
curl -X POST "http://localhost:8000/email" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Dr. Smith",
       "email": "smith@university.edu",
       "user_prompt": "Research collaboration",
       "user_data": "PhD student in AI"
     }'
```

### Using Python requests

```python
import requests

# Scrape professor data
response = requests.post("http://localhost:8000/scraping", json={
    "prompt": "Machine learning research opportunities"
})
professor_data = response.json()

# Generate email
response = requests.post("http://localhost:8000/email", json={
    "name": professor_data["name"],
    "email": professor_data["email"],
    "user_prompt": "Research collaboration opportunity",
    "user_data": "Graduate student in Computer Science"
})
email_data = response.json()
```

## Project Structure

```
Email-Drafter-Backend/
├── main.py                # Main FastAPI application
├── requirements.txt       # Python dependencies
├── start_server.bat      # Windows batch startup script
├── start_server.ps1      # PowerShell startup script
├── test_scheduler.py      # Scheduling queue test script
├── README.md              # This file
├── scraping_agent/        # Professor data scraping module
│   ├── main.py
│   ├── get_name.py
│   ├── get_data.py
│   └── ...
└── email_agent/           # Email generation module
    ├── main.py
    ├── email_content.py
    ├── data.py
    └── ...
```

## Error Handling

The API includes comprehensive error handling:
- **400**: Bad Request - Invalid input data
- **500**: Internal Server Error - Processing errors
- Detailed error messages in response body

## Environment Variables

Required environment variables:
- `GENAI_API_KEY`: Your Gemini API key for AI processing

## Logging

The application uses FastAPI's built-in logging. For production deployments, consider adding structured logging.

## Deployment

For production deployment:

1. Use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. Set up reverse proxy (nginx, Apache)
3. Configure SSL certificates
4. Set up environment-specific configurations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request


