# Email Scheduling System

This FastAPI application includes an email scheduling system that works with your existing `emails` collection in Firestore. The scheduler automatically sends emails with status 'scheduled' when their `scheduledAt` time is within ±5 minutes of the current time.

## Features

- **Automatic email sending** based on existing Firestore collection
- **Status-based scheduling** - only processes emails with status 'scheduled'
- **Time window flexibility** - sends emails within ±5 minutes of scheduled time
- **Status updates** - automatically updates status to 'sent' or 'failed'
- **Background processing** with APScheduler every 5 minutes
- **RESTful API** for monitoring scheduled emails

## How It Works

### Scheduler Process
1. **Every 5 minutes**, the scheduler queries the `emails` collection
2. **Finds emails** where:
   - `status` = 'scheduled'
   - `scheduledAt` is within ±5 minutes of current time
3. **Sends each email** from the user's email (`userEmail`) to the professor (`professorEmail`)
4. **Updates status** to:
   - `'sent'` if successful (also sets `sentAt` timestamp)
   - `'failed'` if unsuccessful

### Email Collection Structure
Your existing `emails` collection should match this interface:

```typescript
interface EmailRecord {
  id: string;
  professorName: string;
  professorEmail: string;
  userEmail: string;
  subject: string;
  body: string;
  status: 'sent' | 'scheduled' | 'delivered' | 'failed';
  sentAt: Date;
  scheduledAt?: Date;
  researchInterest: string;
  userId: string;
}
```

## API Endpoints

### 1. Get Scheduled/Sent Emails
```http
GET /api/scheduled-emails?sent=false
```

Get emails from the collection, filtered by status:
- `sent=false` - Returns emails with status 'scheduled'
- `sent=true` - Returns emails with status 'sent' 
- No parameter - Returns all emails

### 2. Get Specific Email
```http
GET /api/emails/{email_id}
```

Retrieve a specific email by its document ID.

### 3. Manual Trigger (Testing)
```http
POST /api/trigger-scheduled-emails
```

Manually trigger the scheduled email sending process for testing purposes.

### 4. Health Check
```http
GET /health
```

Check if the API and scheduler are running.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Firebase Setup
Follow the instructions in `FIREBASE_SETUP.md`:

1. Create a Firebase project
2. Generate service account credentials
3. Save the JSON file as `firebase-service-account.json`
4. Or set up environment variables for Firebase

### 3. Environment Variables
Update your `.env` file:

```env
# Google OAuth (needed for future email sending implementation)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# Firebase (choose one method)
# Method 1: Service account file
GOOGLE_APPLICATION_CREDENTIALS=firebase-service-account.json

# Method 2: Environment variables
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----..."
FIREBASE_CLIENT_EMAIL=your_service_account_email
```

### 4. Run the Server
```bash
uvicorn main:app --reload --port 8000
```

## Testing

### Run the Test Script
```bash
python test_scheduler.py
```

This will:
1. Check API health and information
2. Fetch scheduled emails from your collection
3. Fetch sent emails from your collection  
4. Manually trigger the scheduler
5. Show sample email record structure

### Manual Testing
1. **Add test emails** to your Firestore `emails` collection with:
   ```json
   {
     "professorName": "Dr. John Smith",
     "professorEmail": "john.smith@university.edu", 
     "userEmail": "student@example.com",
     "subject": "Research Collaboration Inquiry",
     "body": "Dear Dr. Smith, I am interested in your research...",
     "status": "scheduled",
     "scheduledAt": "2024-01-15T10:00:00Z",
     "researchInterest": "Machine Learning",
     "userId": "user123"
   }
   ```

2. **Set `scheduledAt`** to within ±5 minutes of current time

3. **Wait for scheduler** or use manual trigger endpoint

4. **Check status** - should change to 'sent' or 'failed'

## Email Sending Implementation

**Note**: The current implementation includes a placeholder function `send_email_from_user()`. To complete the integration, you need to:

1. **Store user OAuth tokens** in your database (user collection)
2. **Implement token retrieval** based on `userEmail` or `userId`
3. **Add token refresh logic** for expired tokens
4. **Integrate Gmail API** to send emails from the user's account

Example implementation structure:
```python
async def send_email_from_user(user_email: str, to_email: str, subject: str, body: str) -> bool:
    # 1. Get user's stored OAuth tokens from database
    user_tokens = get_user_tokens(user_email)
    
    # 2. Check if tokens are expired and refresh if needed
    if tokens_expired(user_tokens):
        user_tokens = refresh_user_tokens(user_tokens)
    
    # 3. Use Gmail API to send email
    return await send_via_gmail_api(user_tokens, to_email, subject, body)
```

## Monitoring

The system includes comprehensive logging:
- Scheduler startup/shutdown
- Email processing attempts and results  
- Status updates
- Error handling and failures

Check the server logs to monitor operations:
```bash
# View logs in real-time
uvicorn main:app --reload --log-level info
```

## Configuration

### Scheduler Interval
The scheduler runs every 5 minutes by default. To change this, modify the `IntervalTrigger` in `main.py`:

```python
scheduler.add_job(
    send_scheduled_emails,
    IntervalTrigger(minutes=10),  # Change to 10 minutes
    # ...
)
```

### Time Window
The ±5 minute window can be adjusted in the `get_due_scheduled_emails()` function:

```python
# Change ±5 minutes to ±10 minutes
time_window_start = now - timedelta(minutes=10) 
time_window_end = now + timedelta(minutes=10)
```

## Production Considerations

1. **Complete email integration** with Gmail API and user token management
2. **Proper error handling** and retry logic for failed emails
3. **Rate limiting** to respect Gmail API limits
4. **Monitoring and alerting** for failed email sends
5. **Database indexing** on `status` and `scheduledAt` fields for performance
6. **Security** - ensure proper Firebase security rules
