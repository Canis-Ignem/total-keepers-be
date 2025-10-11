# Setting up No-Reply Emails with GCP

## Option 1: Gmail API with Google Workspace Custom Domain

### Prerequisites
- Google Workspace account (not free Gmail)
- Custom domain (e.g., `totalkeepers.com`)
- Domain verification in Google Workspace

### Step 1: Set up No-Reply Email Address in Google Workspace

1. **Go to Google Admin Console**: https://admin.google.com/
2. **Navigate to Directory > Users**
3. **Add a new user**:
   - First name: `No`
   - Last name: `Reply`
   - Primary email: `no-reply@totalkeepers.com`
   - Password: Generate a strong password
4. **Disable user login** (optional for security):
   - Go to **Security > Authentication**
   - Turn off **2-Step Verification** requirement
   - Set account to suspended if you don't want anyone logging in

### Step 2: Configure Service Account with Domain-Wide Delegation

1. **Create Service Account** (as per main guide)
2. **Enable Domain-Wide Delegation**:
   - In service account details, check "Enable Google Workspace Domain-wide Delegation"
   - Note the Client ID
3. **Authorize in Admin Console**:
   - Go to **Security > API Controls > Domain-wide Delegation**
   - Add Client ID with scope: `https://www.googleapis.com/auth/gmail.send`

### Step 3: Update Email Service Code

```python
# app/services/gmail_service.py
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings

class GmailService:
    def __init__(self):
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate using service account with domain-wide delegation"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_CREDENTIALS_FILE,
                scopes=['https://www.googleapis.com/auth/gmail.send']
            )
            
            # Impersonate the no-reply user
            delegated_credentials = credentials.with_subject(settings.NOREPLY_EMAIL)
            
            self.service = build('gmail', 'v1', credentials=delegated_credentials)
            
        except Exception as e:
            print(f"Authentication failed: {e}")
            raise
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   from_email: Optional[str] = None, 
                   reply_to: Optional[str] = None):
        """Send an email using Gmail API from no-reply address"""
        try:
            message = MIMEMultipart()
            message['To'] = to_email
            message['From'] = from_email or settings.NOREPLY_EMAIL
            message['Subject'] = subject
            
            # Add reply-to header if specified
            if reply_to:
                message['Reply-To'] = reply_to
            else:
                # Discourage replies
                message['Reply-To'] = settings.NOREPLY_EMAIL
            
            # Add HTML body
            message.attach(MIMEText(body, 'html'))
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send email
            send_message = self.service.users().messages().send(
                userId='me',  # Will use the delegated user (no-reply)
                body={'raw': raw_message}
            ).execute()
            
            print(f"Email sent successfully from {settings.NOREPLY_EMAIL}: {send_message['id']}")
            return True
            
        except HttpError as error:
            print(f"Gmail API error: {error}")
            return False
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
```

### Step 4: Update Environment Configuration

```env
# .env file
NOREPLY_EMAIL=no-reply@totalkeepers.com
ADMIN_EMAIL=admin@totalkeepers.com
GOOGLE_CREDENTIALS_FILE=path/to/service-account.json
```

```python
# app/core/config.py
class Settings:
    # ... existing settings ...
    
    NOREPLY_EMAIL: str = "no-reply@totalkeepers.com"
    ADMIN_EMAIL: str = "admin@totalkeepers.com"
    GOOGLE_CREDENTIALS_FILE: str = "gcp-service-account.json"
```

## Option 2: SendGrid with Custom No-Reply Address

### Step 1: Domain Authentication in SendGrid

1. **Go to SendGrid Dashboard** > **Settings** > **Sender Authentication**
2. **Authenticate Your Domain**:
   - Enter your domain: `totalkeepers.com`
   - Follow DNS setup instructions
   - Verify domain ownership

### Step 2: Create Sender Identity

1. **Go to Settings** > **Sender Authentication** > **Single Sender Verification**
2. **Create new sender**:
   - From Name: `Total Keepers`
   - From Email: `no-reply@totalkeepers.com`
   - Reply To: `admin@totalkeepers.com` (or same as from)
   - Company: `Total Keepers`

### Step 3: Update SendGrid Service

```python
# app/services/sendgrid_service.py
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, ReplyTo

class SendGridEmailService:
    def __init__(self):
        self.client = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    
    def send_email(self, to_email: str, subject: str, body: str):
        """Send email using SendGrid with no-reply address"""
        try:
            from_email = Email(settings.NOREPLY_EMAIL, "Total Keepers")
            to_email = To(to_email)
            content = Content("text/html", body)
            
            mail = Mail(from_email, to_email, subject, content)
            
            # Set reply-to to admin email (optional)
            mail.reply_to = ReplyTo(settings.ADMIN_EMAIL, "Total Keepers Support")
            
            response = self.client.send(mail)
            print(f"Email sent successfully from {settings.NOREPLY_EMAIL}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
```

## Option 3: SMTP with Custom Domain

### Step 1: Configure DNS Records

Add these DNS records to your domain:

```
Type: MX
Name: @
Value: 1 smtp.gmail.com

Type: TXT
Name: @
Value: v=spf1 include:_spf.google.com ~all
```

### Step 2: Set up SMTP Service

```python
# app/services/smtp_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

class SMTPEmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.username = settings.NOREPLY_EMAIL
        self.password = settings.NOREPLY_EMAIL_PASSWORD  # App password
    
    def send_email(self, to_email: str, subject: str, body: str):
        """Send email using SMTP with no-reply address"""
        try:
            message = MIMEMultipart()
            message['From'] = formataddr(("Total Keepers", settings.NOREPLY_EMAIL))
            message['To'] = to_email
            message['Subject'] = subject
            message['Reply-To'] = settings.ADMIN_EMAIL
            
            message.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(message)
            
            print(f"Email sent successfully from {settings.NOREPLY_EMAIL}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
```

## Update Your Email Service

```python
# app/services/email_service.py
from typing import Dict, Any
from app.services.gmail_service import GmailService  # or your chosen service

class EmailService:
    email_client = GmailService()
    
    @classmethod
    def send_booking_confirmation_to_participant(cls, booking_summary: Dict[str, Any]):
        """Send booking confirmation email to participant"""
        subject = f"Booking Confirmation - {booking_summary['session_title']}"
        
        body = f"""
        <html>
        <body>
            <h2>Booking Confirmed!</h2>
            <p>Dear {booking_summary['participant_name']},</p>
            
            <p>Your booking has been confirmed for:</p>
            <ul>
                <li><strong>Session:</strong> {booking_summary['session_title']}</li>
                <li><strong>Date:</strong> {booking_summary['session_date']}</li>
                <li><strong>Location:</strong> {booking_summary['session_location']}</li>
                <li><strong>Reference:</strong> {booking_summary['booking_reference']}</li>
                <li><strong>Price:</strong> €{booking_summary['session_price']}</li>
            </ul>
            
            <p>Please arrive 15 minutes before the session starts.</p>
            
            <p>Best regards,<br>
            Total Keepers Team</p>
            
            <hr>
            <small>This is an automated message. Please do not reply to this email. 
            For questions, contact us at admin@totalkeepers.com</small>
        </body>
        </html>
        """
        
        return cls.email_client.send_email(
            to_email=booking_summary['participant_email'],
            subject=subject,
            body=body
        )
    
    @classmethod
    def send_booking_notification_to_organizer(cls, booking_summary: Dict[str, Any]):
        """Send booking notification to organizer"""
        subject = f"New Booking - {booking_summary['session_title']}"
        
        body = f"""
        <html>
        <body>
            <h2>New Booking Received</h2>
            
            <p>A new booking has been made:</p>
            <ul>
                <li><strong>Participant:</strong> {booking_summary['participant_name']}</li>
                <li><strong>Email:</strong> {booking_summary['participant_email']}</li>
                <li><strong>Session:</strong> {booking_summary['session_title']}</li>
                <li><strong>Date:</strong> {booking_summary['session_date']}</li>
                <li><strong>Reference:</strong> {booking_summary['booking_reference']}</li>
                <li><strong>Price:</strong> €{booking_summary['session_price']}</li>
            </ul>
            
            <p>Please ensure all preparations are made for this session.</p>
            
            <p>Best regards,<br>
            Campus Booking System</p>
        </body>
        </html>
        """
        
        return cls.email_client.send_email(
            to_email=settings.ADMIN_EMAIL,
            subject=subject,
            body=body
        )
```

## Testing the No-Reply Setup

```python
# test_noreply_email.py
from app.services.email_service import EmailService

def test_noreply_email():
    booking_summary = {
        'booking_reference': 'TEST-NOREPLY-123',
        'participant_name': 'Test User',
        'participant_email': 'your-test-email@gmail.com',  # Use your email for testing
        'session_title': 'Test Session',
        'session_date': '2025-08-10 16:00:00',
        'session_location': 'Test Location',
        'session_price': 35.00
    }
    
    # Test sending from no-reply address
    result = EmailService.send_booking_confirmation_to_participant(booking_summary)
    if result:
        print("✅ No-reply email sent successfully")
        print("📧 Check your inbox and verify it came from no-reply@totalkeepers.com")
    else:
        print("❌ Failed to send no-reply email")

if __name__ == "__main__":
    test_noreply_email()
```

## Best Practices for No-Reply Emails

1. **Clear "Do Not Reply" Message**: Include clear text that this is an automated message
2. **Provide Alternative Contact**: Always include a way for users to reach support
3. **Professional Sender Name**: Use "Total Keepers" or similar instead of just the email
4. **Reply-To Header**: Set reply-to to your support email
5. **Consistent Branding**: Use your brand colors and logo in email templates

## Important Notes

- **Google Workspace Required**: For Gmail API with custom domain, you need a paid Google Workspace account
- **Domain Verification**: Your domain must be verified and properly configured
- **SPF/DKIM Records**: Set up proper email authentication to avoid spam filters
- **Monitor Delivery**: Keep an eye on email delivery rates and spam reports

Choose Option 1 (Gmail API) if you already have Google Workspace, or Option 2 (SendGrid) for the most reliable delivery without requiring Google Workspace.
