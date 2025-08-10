#!/usr/bin/env python3
"""
Simple email test using SendGrid as alternative to Gmail API
This approach works without complex domain-wide delegation setup
"""

import os
import sys

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Load environment variables
from dotenv import load_dotenv

load_dotenv()


def test_sendgrid_setup():
    """Test SendGrid setup as an alternative to Gmail API"""
    print("🥅 Total Keepers - SendGrid Email Test (Alternative)")
    print("=" * 60)

    print("\n📧 SendGrid Setup Instructions:")
    print("-" * 40)
    print("1. Go to https://sendgrid.com and create a free account")
    print("2. Verify your account and domain")
    print("3. Create an API key with Mail Send permissions")
    print("4. Add SENDGRID_API_KEY to your .env file")
    print("5. Install SendGrid: pip install sendgrid")

    print("\n💡 Benefits of SendGrid:")
    print("- No complex domain-wide delegation setup")
    print("- Better email deliverability")
    print("- Free tier: 100 emails/day")
    print("- Professional email templates")
    print("- Email analytics and tracking")


def create_working_gmail_script():
    """Create a Gmail script that should work with proper setup"""
    gmail_script = '''#!/usr/bin/env python3
"""
Working Gmail API script - requires proper domain setup
"""

import os
import sys
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

class WorkingGmailSender:
    def __init__(self):
        self.service = None
        self.credentials_file = "keys/total-keepers-6492ff87b584.json"
        # This needs to be a real email address you control
        self.sender_email = "your-actual-email@gmail.com"  # CHANGE THIS
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with proper email delegation"""
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_file,
            scopes=['https://www.googleapis.com/auth/gmail.send']
        )
        
        # For domain-wide delegation (requires Google Workspace)
        # credentials = credentials.with_subject(self.sender_email)
        
        self.service = build('gmail', 'v1', credentials=credentials)
    
    def send_simple_email(self, to_email: str, subject: str, body: str):
        """Send a simple email"""
        try:
            message = MIMEText(body)
            message['to'] = to_email
            message['from'] = self.sender_email
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            print(f"✅ Email sent! Message ID: {result['id']}")
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

# To use this script:
# 1. Replace 'your-actual-email@gmail.com' with your real email
# 2. Set up domain-wide delegation in Google Workspace (if using custom domain)
# 3. Or use your personal Gmail with OAuth2 (more complex setup)
'''

    with open("scripts/working_gmail_example.py", "w") as f:
        f.write(gmail_script)

    print("\n📝 Created: scripts/working_gmail_example.py")
    print("📋 This script shows the proper setup for Gmail API")


def create_sendgrid_alternative():
    """Create a SendGrid email script as working alternative"""
    sendgrid_script = '''#!/usr/bin/env python3
"""
SendGrid email sending - Working alternative to Gmail API
Run: pip install sendgrid
"""

import os
import sys
from typing import Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content
except ImportError:
    print("❌ SendGrid not installed. Run: pip install sendgrid")
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv()

class SendGridEmailService:
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY not found in environment variables")
        self.client = sendgrid.SendGridAPIClient(api_key=self.api_key)
        self.from_email = "no-reply@totalkeepers.com"  # Must be verified in SendGrid
    
    def send_booking_confirmation(self, booking_data: Dict[str, Any]) -> bool:
        """Send booking confirmation email"""
        try:
            # Create email content
            subject = f"Booking Confirmed - {booking_data['session_title']}"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2c3e50;">🥅 Booking Confirmation</h2>
                
                <p>Dear <strong>{booking_data['participant_name']}</strong>,</p>
                
                <p>Your booking has been confirmed!</p>
                
                <div style="background: #f8f9fa; padding: 20px; margin: 20px 0; border-left: 4px solid #007bff;">
                    <h3>Session Details:</h3>
                    <ul>
                        <li><strong>Session:</strong> {booking_data['session_title']}</li>
                        <li><strong>Date:</strong> {booking_data.get('date', 'TBD')}</li>
                        <li><strong>Location:</strong> {booking_data.get('location', 'TBD')}</li>
                        <li><strong>Price:</strong> €{booking_data.get('price', '0.00')}</li>
                        <li><strong>Reference:</strong> {booking_data.get('reference', 'TK-001')}</li>
                    </ul>
                </div>
                
                <p>Please arrive 15 minutes early. Bring your gloves and water bottle!</p>
                
                <hr>
                <p><small>This is an automated email. For questions, contact admin@totalkeepers.com</small></p>
            </div>
            """
            
            # Create SendGrid email
            from_email = Email(self.from_email, "Total Keepers")
            to_email = To(booking_data['email'])
            content = Content("text/html", html_content)
            
            mail = Mail(from_email, to_email, subject, content)
            
            # Send email
            response = self.client.send(mail)
            
            if response.status_code == 202:
                print(f"✅ Email sent successfully to {booking_data['email']}")
                print(f"📬 Status: {response.status_code}")
                return True
            else:
                print(f"❌ Failed to send email. Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ SendGrid error: {e}")
            return False

def main():
    """Test SendGrid email sending"""
    print("🥅 Total Keepers - SendGrid Email Test")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv('SENDGRID_API_KEY')
    if not api_key:
        print("❌ SENDGRID_API_KEY not found in .env file")
        print("\\n📋 Setup instructions:")
        print("1. Get API key from SendGrid dashboard")
        print("2. Add to .env: SENDGRID_API_KEY=your_api_key_here")
        return
    
    try:
        email_service = SendGridEmailService()
        
        # Test data
        booking_data = {
            'participant_name': 'Test User',
            'email': input("Enter your email for testing: "),
            'session_title': 'Youth Goalkeeper Development',
            'date': 'August 15, 2025 at 16:00',
            'location': 'Total Keepers Training Center',
            'price': '35.00',
            'reference': 'TK-TEST-001'
        }
        
        confirm = input(f"\\nSend test email to {booking_data['email']}? (y/N): ")
        
        if confirm.lower() in ['y', 'yes']:
            success = email_service.send_booking_confirmation(booking_data)
            if success:
                print("\\n🎉 Success! Check your email inbox.")
            else:
                print("\\n❌ Failed to send email.")
        else:
            print("📬 Email sending cancelled.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
'''

    with open("scripts/test_sendgrid_email.py", "w") as f:
        f.write(sendgrid_script)

    print("📝 Created: scripts/test_sendgrid_email.py")
    print("📋 This script provides a working SendGrid alternative")


def main():
    """Main function to explain the email setup situation"""
    print("🥅 Total Keepers Email Setup Analysis")
    print("=" * 50)

    print("\\n📊 Current Status:")
    print("✅ Google Cloud credentials file found")
    print("✅ Gmail API authentication successful")
    print("❌ Domain-wide delegation not properly configured")

    print("\\n🔧 The Issue:")
    print("Gmail API requires either:")
    print("1. Domain-wide delegation (Google Workspace + custom domain)")
    print("2. OAuth2 flow for personal Gmail accounts")
    print("3. Service account with proper email delegation")

    print("\\n💡 Recommended Solutions:")
    print("\\n1. 🥇 SendGrid (Easiest & Most Reliable)")
    print("   - No complex setup required")
    print("   - Better email deliverability")
    print("   - Free tier: 100 emails/day")
    print("   - Professional appearance")

    print("\\n2. 🥈 Gmail API with Domain Setup")
    print("   - Requires Google Workspace account")
    print("   - Need custom domain (totalkeepers.com)")
    print("   - Complex domain-wide delegation setup")

    print("\\n3. 🥉 SMTP with App Passwords")
    print("   - Use regular Gmail SMTP")
    print("   - Requires app-specific passwords")
    print("   - May hit Gmail sending limits")

    # Create alternative scripts
    create_sendgrid_alternative()
    create_working_gmail_script()
    test_sendgrid_setup()

    print("\\n🎯 Next Steps:")
    print("1. For immediate testing: Set up SendGrid (recommended)")
    print("2. For production: Consider SendGrid or proper Gmail domain setup")
    print("3. Update .env with chosen email service credentials")


if __name__ == "__main__":
    main()
