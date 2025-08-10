#!/usr/bin/env python3
"""
SendGrid email sending - Working alternative to Gmail API
Run: pip install sendgrid
"""

import os
import sys
from typing import Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content
except ImportError:
    print("SendGrid not installed. Run: pip install sendgrid")
    sys.exit(1)

from dotenv import load_dotenv

load_dotenv()


class SendGridEmailService:
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
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
                <h2 style="color: #2c3e50;">Booking Confirmation</h2>
                
                <p>Dear <strong>{booking_data["participant_name"]}</strong>,</p>
                
                <p>Your booking has been confirmed!</p>
                
                <div style="background: #f8f9fa; padding: 20px; margin: 20px 0; border-left: 4px solid #007bff;">
                    <h3>Session Details:</h3>
                    <ul>
                        <li><strong>Session:</strong> {booking_data["session_title"]}</li>
                        <li><strong>Date:</strong> {booking_data.get("date", "TBD")}</li>
                        <li><strong>Location:</strong> {booking_data.get("location", "TBD")}</li>
                        <li><strong>Price:</strong> €{booking_data.get("price", "0.00")}</li>
                        <li><strong>Reference:</strong> {booking_data.get("reference", "TK-001")}</li>
                    </ul>
                </div>
                
                <p>Please arrive 15 minutes early. Bring your gloves and water bottle!</p>
                
                <hr>
                <p><small>This is an automated email. For questions, contact admin@totalkeepers.com</small></p>
            </div>
            """

            # Create SendGrid email
            from_email = Email(self.from_email, "Total Keepers")
            to_email = To(booking_data["email"])
            content = Content("text/html", html_content)

            mail = Mail(from_email, to_email, subject, content)

            # Send email
            response = self.client.send(mail)

            if response.status_code == 202:
                print(f"Email sent successfully to {booking_data['email']}")
                print(f"Status: {response.status_code}")
                return True
            else:
                print(f"Failed to send email. Status: {response.status_code}")
                return False

        except Exception as e:
            print(f"SendGrid error: {e}")
            return False


def main():
    """Test SendGrid email sending"""
    print("Total Keepers - SendGrid Email Test")
    print("=" * 50)

    # Check if API key is set
    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key:
        print("SENDGRID_API_KEY not found in .env file")
        print("\nSetup instructions:")
        print("1. Get API key from SendGrid dashboard")
        print("2. Add to .env: SENDGRID_API_KEY=your_api_key_here")
        return

    try:
        email_service = SendGridEmailService()

        # Test data
        booking_data = {
            "participant_name": "Test User",
            "email": input("Enter your email for testing: "),
            "session_title": "Youth Goalkeeper Development",
            "date": "August 15, 2025 at 16:00",
            "location": "Total Keepers Training Center",
            "price": "35.00",
            "reference": "TK-TEST-001",
        }

        confirm = input(f"\nSend test email to {booking_data['email']}? (y/N): ")

        if confirm.lower() in ["y", "yes"]:
            success = email_service.send_booking_confirmation(booking_data)
            if success:
                print("\nSuccess! Check your email inbox.")
            else:
                print("\nFailed to send email.")
        else:
            print("Email sending cancelled.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
