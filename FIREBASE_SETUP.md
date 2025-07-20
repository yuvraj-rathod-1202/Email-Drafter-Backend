# Firebase Configuration Guide

## Setup Instructions:

1. Go to the Firebase Console: https://console.firebase.google.com/
2. Create a new project or select an existing one
3. Go to Project Settings > Service Accounts
4. Click "Generate new private key" to download the service account JSON file
5. Save the JSON file as `firebase-service-account.json` in your project root
6. Add the following to your `.env` file:

```env
GOOGLE_APPLICATION_CREDENTIALS=firebase-service-account.json
```

## Alternative Setup (Using Environment Variables):

Instead of using the service account JSON file, you can set up Firebase using environment variables:

```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account-email@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
```

## Database Structure:

The scheduled emails collection (`scheduled_emails`) will have the following structure:

```json
{
  "recipient": "user@example.com",
  "subject": "Email Subject",
  "body": "Email body content",
  "scheduled_time": "2024-01-01T10:00:00Z",
  "access_token": "access_token_here",
  "refresh_token": "refresh_token_here", 
  "token_expiry": "2024-01-01T11:00:00Z",
  "sent": false,
  "created_at": "2024-01-01T09:00:00Z",
  "sent_at": "2024-01-01T10:00:00Z" // Only added when sent
}
```

## Security Notes:

- Never commit the service account JSON file to version control
- Add `firebase-service-account.json` to your `.gitignore`
- Use environment variables in production
- Ensure your Firebase security rules are properly configured
