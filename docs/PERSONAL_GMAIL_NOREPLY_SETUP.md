# No-Reply Email Setup with Personal Gmail Account

## Overview
When using a **personal Gmail account** (not Google Workspace), you have several options for sending no-reply emails through GCP.

## Option 1: 🥇 Gmail SMTP with App Password (Recommended for Personal Accounts)

### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification if not already enabled

### Step 2: Create App Password
1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Select "Mail" and "Other (custom name)"
3. Name it "Total Keepers Backend"
4. Copy the generated 16-character password

### Step 3: Configure Environment Variables
Add to your `.env` file:
```env
# Gmail SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-gmail@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=your-gmail@gmail.com
SMTP_FROM_NAME=Total Keepers
```

### Step 4: Install Required Packages
```bash
pip install smtplib email-validator
```

## Option 2: 🥈 SendGrid (Most Professional)

### Why SendGrid for No-Reply?
- Professional appearance
- Better deliverability 
- No Gmail branding
- Free tier: 100 emails/day
- Custom from addresses

### Setup Steps
1. Sign up at [sendgrid.com](https://sendgrid.com)
2. Verify your email
3. Create API key with "Mail Send" permissions
4. Add to `.env`:
```env
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=no-reply@your-temp-domain.com
SENDGRID_FROM_NAME=Total Keepers
```

## Option 3: 🥉 Gmail API with OAuth2 (Complex)

### Requirements
- OAuth2 consent screen setup
- User consent flow
- Token refresh handling

### When to Use
- Need Gmail integration features
- Want to send from Gmail directly
- Have time for complex setup

## Implementation Examples

### 1. Gmail SMTP Implementation
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

class GmailSMTPSender:
    def __init__(self):
        load_dotenv()
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.username = os.getenv('SMTP_USERNAME')
        self.password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('SMTP_FROM_EMAIL')
        self.from_name = os.getenv('SMTP_FROM_NAME', 'Total Keepers')
    
    def send_booking_confirmation(self, to_email, booking_data):
        """Send booking confirmation via Gmail SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Booking Confirmed - {booking_data['session_title']}"
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Reply-To'] = "no-reply@totalkeepers.com"  # Set reply-to as no-reply
            
            # HTML content
            html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px;">
                <h2>🥅 Booking Confirmation</h2>
                <p>Dear <strong>{booking_data['participant_name']}</strong>,</p>
                <p>Your booking has been confirmed!</p>
                
                <div style="background: #f8f9fa; padding: 20px; margin: 20px 0;">
                    <h3>Session Details:</h3>
                    <ul>
                        <li><strong>Session:</strong> {booking_data['session_title']}</li>
                        <li><strong>Date:</strong> {booking_data.get('date', 'TBD')}</li>
                        <li><strong>Price:</strong> €{booking_data.get('price', '0.00')}</li>
                    </ul>
                </div>
                
                <p><small>This is an automated message. Please do not reply to this email.</small></p>
            </div>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            print(f"✅ Email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
```

### 2. SendGrid Implementation
```python
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

class SendGridSender:
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.client = sendgrid.SendGridAPIClient(api_key=self.api_key)
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL')
        self.from_name = os.getenv('SENDGRID_FROM_NAME', 'Total Keepers')
    
    def send_booking_confirmation(self, to_email, booking_data):
        """Send booking confirmation via SendGrid"""
        try:
            from_email = Email(self.from_email, self.from_name)
            to_email = To(to_email)
            subject = f"Booking Confirmed - {booking_data['session_title']}"
            
            html_content = f"""
            <h2>🥅 Booking Confirmation</h2>
            <p>Your booking for <strong>{booking_data['session_title']}</strong> is confirmed!</p>
            <p>Date: {booking_data.get('date', 'TBD')}</p>
            <p>Price: €{booking_data.get('price', '0.00')}</p>
            """
            
            content = Content("text/html", html_content)
            mail = Mail(from_email, to_email, subject, content)
            
            response = self.client.send(mail)
            print(f"✅ SendGrid email sent (Status: {response.status_code})")
            return True
            
        except Exception as e:
            print(f"❌ SendGrid error: {e}")
            return False
```

## Comparison Table

| Method | Setup Time | Cost | Reliability | Professional Look | Daily Limit |
|--------|------------|------|-------------|-------------------|-------------|
| Gmail SMTP | 5 min | Free | Good | Basic | 500 emails |
| SendGrid | 10 min | Free tier | Excellent | Professional | 100 emails |
| Gmail API | 2+ hours | Free | Good | Basic | Varies |

## Recommendations

### For Quick Testing
Use **Gmail SMTP** with app password:
- Fastest setup
- Uses your existing Gmail
- Good for development

### For Production
Use **SendGrid**:
- More professional appearance
- Better deliverability rates
- No Gmail branding
- Detailed analytics

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate app passwords** regularly
4. **Monitor email sending** for abuse
5. **Implement rate limiting** in your application

## Testing Scripts

I'll create test scripts for both approaches so you can try them immediately.
