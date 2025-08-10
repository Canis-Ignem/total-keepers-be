# Google Cloud Platform Email Setup Guide

This guide covers setting up email services for the Total Keepers campus booking system using Google Cloud Platform.

## Table of Contents
1. [Overview](#overview)
2. [Option 1: Gmail API (Recommended)](#option-1-gmail-api-recommended)
3. [Option 2: SendGrid with GCP](#option-2-sendgrid-with-gcp)
4. [Option 3: Google Cloud SMTP Relay](#option-3-google-cloud-smtp-relay)
5. [Environment Configuration](#environment-configuration)
6. [Testing the Setup](#testing-the-setup)

## Overview

The campus booking system sends email notifications for:
- Booking confirmations to participants
- Booking notifications to organizers
- Guardian notifications (for minors)

## Option 1: Gmail API (Recommended)

### Prerequisites
- Google Cloud Account
- Gmail account for sending emails
- GCP Project

### Step 1: Create or Select a GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project" or select existing project
4. Note your Project ID for later use

### Step 2: Enable Gmail API

1. In the GCP Console, navigate to **APIs & Services > Library**
2. Search for "Gmail API"
3. Click on "Gmail API" and click **Enable**

### Step 3: Create Service Account

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > Service Account**
3. Fill in the details:
   - **Service account name**: `campus-email-service`
   - **Service account ID**: `campus-email-service`
   - **Description**: `Service account for campus booking email notifications`
4. Click **Create and Continue**
5. Grant roles (optional for now): Skip this step
6. Click **Done**

### Step 4: Create Service Account Key

1. In **APIs & Services > Credentials**, find your service account
2. Click on the service account email
3. Go to the **Keys** tab
4. Click **Add Key > Create New Key**
5. Select **JSON** format
6. Download the JSON file
7. Rename it to `gcp-service-account.json`
8. Store it securely (DO NOT commit to version control)

### Step 5: Configure Domain-Wide Delegation (for G Suite/Workspace)

If using a Google Workspace domain:

1. In the service account details, note the **Client ID**
2. Go to [Google Admin Console](https://admin.google.com/)
3. Navigate to **Security > API Controls > Domain-wide Delegation**
4. Click **Add new** and enter:
   - **Client ID**: From your service account
   - **OAuth Scopes**: `https://www.googleapis.com/auth/gmail.send`
5. Click **Authorize**

### Step 6: Set up Application Default Credentials

```bash
# Set environment variable pointing to your service account key
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\gcp-service-account.json"
```

### Step 7: Install Required Python Packages

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 8: Update Email Service Code

Create or update `app/services/gmail_service.py`:

```python
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings

class GmailService:
    def __init__(self):
        self.credentials = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate using service account credentials"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_CREDENTIALS_FILE,
                scopes=['https://www.googleapis.com/auth/gmail.send']
            )
            
            # If using domain-wide delegation
            if settings.GMAIL_DELEGATED_USER:
                credentials = credentials.with_subject(settings.GMAIL_DELEGATED_USER)
            
            self.credentials = credentials
            self.service = build('gmail', 'v1', credentials=credentials)
            
        except Exception as e:
            print(f"Authentication failed: {e}")
            raise
    
    def send_email(self, to_email: str, subject: str, body: str, from_email: Optional[str] = None):
        """Send an email using Gmail API"""
        try:
            message = MIMEMultipart()
            message['to'] = to_email
            message['from'] = from_email or settings.DEFAULT_FROM_EMAIL
            message['subject'] = subject
            
            message.attach(MIMEText(body, 'html'))
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"Email sent successfully: {send_message['id']}")
            return True
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
```

## Option 2: SendGrid with GCP

### Step 1: Create SendGrid Account

1. Go to [SendGrid](https://sendgrid.com/) and sign up
2. Verify your account

### Step 2: Create API Key

1. In SendGrid dashboard, go to **Settings > API Keys**
2. Click **Create API Key**
3. Choose **Restricted Access**
4. Grant **Mail Send** permissions
5. Copy the API key (store securely)

### Step 3: Store API Key in GCP Secret Manager

1. In GCP Console, go to **Security > Secret Manager**
2. Click **Create Secret**
3. Name: `sendgrid-api-key`
4. Secret value: Your SendGrid API key
5. Click **Create**

### Step 4: Install SendGrid Python SDK

```bash
pip install sendgrid
```

### Step 5: Update Email Service for SendGrid

```python
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from google.cloud import secretmanager

from app.core.config import settings

class SendGridEmailService:
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _get_api_key_from_secret_manager(self):
        """Retrieve SendGrid API key from GCP Secret Manager"""
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{settings.GCP_PROJECT_ID}/secrets/sendgrid-api-key/versions/latest"
        
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    
    def _initialize_client(self):
        """Initialize SendGrid client"""
        api_key = self._get_api_key_from_secret_manager()
        self.client = sendgrid.SendGridAPIClient(api_key=api_key)
    
    def send_email(self, to_email: str, subject: str, body: str, from_email: str = None):
        """Send email using SendGrid"""
        try:
            from_email = Email(from_email or settings.DEFAULT_FROM_EMAIL)
            to_email = To(to_email)
            content = Content("text/html", body)
            
            mail = Mail(from_email, to_email, subject, content)
            
            response = self.client.send(mail)
            print(f"Email sent successfully: {response.status_code}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
```

## Option 3: Google Cloud SMTP Relay

### Step 1: Set up SMTP Relay in Google Workspace Admin

1. Go to [Google Admin Console](https://admin.google.com/)
2. Navigate to **Apps > Google Workspace > Gmail > Routing**
3. Click **Configure** next to SMTP relay service
4. Add your server's IP address
5. Configure authentication (if needed)

### Step 2: Use Python SMTP Library

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class SMTPEmailService:
    def __init__(self):
        self.smtp_server = "smtp-relay.gmail.com"
        self.smtp_port = 587
    
    def send_email(self, to_email: str, subject: str, body: str, from_email: str = None):
        """Send email using SMTP relay"""
        try:
            message = MIMEMultipart()
            message['From'] = from_email or settings.DEFAULT_FROM_EMAIL
            message['To'] = to_email
            message['Subject'] = subject
            
            message.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                # Authentication may not be required for IP-whitelisted servers
                server.send_message(message)
            
            print("Email sent successfully")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
```

## Environment Configuration

Add these variables to your `.env` file:

```env
# Gmail API Configuration
GOOGLE_CREDENTIALS_FILE=path/to/gcp-service-account.json
GMAIL_DELEGATED_USER=your-email@yourdomain.com  # For domain-wide delegation
DEFAULT_FROM_EMAIL=noreply@totalkeepers.com

# SendGrid Configuration (Alternative)
GCP_PROJECT_ID=your-gcp-project-id
SENDGRID_FROM_EMAIL=noreply@totalkeepers.com

# Email Settings
ORGANIZER_EMAIL=admin@totalkeepers.com
```

Update `app/core/config.py`:

```python
class Settings:
    # ... existing settings ...
    
    # Email configuration
    GOOGLE_CREDENTIALS_FILE: str = "gcp-service-account.json"
    GMAIL_DELEGATED_USER: Optional[str] = None
    DEFAULT_FROM_EMAIL: str = "noreply@totalkeepers.com"
    ORGANIZER_EMAIL: str = "admin@totalkeepers.com"
    GCP_PROJECT_ID: Optional[str] = None
```

## Testing the Setup

### Create a test script `test_email.py`:

```python
import asyncio
from app.services.email_service import EmailService

async def test_email():
    # Test booking confirmation email
    booking_summary = {
        'booking_reference': 'TEST-123',
        'participant_name': 'Test User',
        'participant_email': 'test@example.com',
        'session_title': 'Test Session',
        'session_date': '2025-08-10 16:00:00',
        'session_location': 'Test Location',
        'session_price': 35.00
    }
    
    try:
        EmailService.send_booking_confirmation_to_participant(booking_summary)
        print("✅ Participant email sent successfully")
        
        EmailService.send_booking_notification_to_organizer(booking_summary)
        print("✅ Organizer email sent successfully")
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_email())
```

Run the test:
```bash
python test_email.py
```

## Security Best Practices

1. **Never commit credentials to version control**
2. **Use environment variables or secret management**
3. **Restrict API permissions to minimum required**
4. **Regularly rotate API keys**
5. **Monitor email usage and quotas**

## Troubleshooting

### Common Issues:

1. **Authentication Errors**
   - Verify service account key file path
   - Check if Gmail API is enabled
   - Verify domain-wide delegation settings

2. **Permission Denied**
   - Ensure proper OAuth scopes
   - Check service account permissions
   - Verify domain-wide delegation configuration

3. **Rate Limiting**
   - Gmail API has daily quotas
   - Implement retry logic with exponential backoff
   - Consider using multiple service accounts for high volume

### Gmail API Quotas:
- **Daily quota**: 1 billion requests per day
- **Per-user rate limit**: 250 quota units per user per second

## Cost Considerations

- **Gmail API**: Free up to quotas
- **SendGrid**: Free tier includes 100 emails/day
- **SMTP Relay**: Free with Google Workspace

Choose the option that best fits your volume and technical requirements.
