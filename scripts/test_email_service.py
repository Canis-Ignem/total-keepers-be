#!/usr/bin/env python3
"""
Test the updated email service with Gmail SMTP
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.email_service import EmailService
from app.schemas.campus import BookingSummary
from app.core.config import settings


def test_email_service_configuration():
    """Test email service configuration"""
    print("🔍 Testing Email Service Configuration")
    print("=" * 50)
    
    print("📧 SMTP Settings:")
    print(f"   Server: {settings.SMTP_SERVER or settings.SMTP_HOST}")
    print(f"   Port: {settings.SMTP_PORT}")
    print(f"   TLS: {settings.SMTP_TLS}")
    print(f"   Username: {settings.SMTP_USERNAME or settings.SMTP_USER}")
    print(f"   Password: {'*' * len(settings.SMTP_PASSWORD) if settings.SMTP_PASSWORD else 'Not set'}")
    print(f"   From Email: {settings.SMTP_FROM_EMAIL or settings.EMAIL_FROM}")
    print(f"   From Name: {settings.SMTP_FROM_NAME}")
    
    # Check if required settings are present
    missing_settings = []
    if not (settings.SMTP_USERNAME or settings.SMTP_USER):
        missing_settings.append("SMTP_USERNAME")
    if not settings.SMTP_PASSWORD:
        missing_settings.append("SMTP_PASSWORD")
    
    if missing_settings:
        print(f"\n❌ Missing required settings: {', '.join(missing_settings)}")
        return False
    else:
        print("\n✅ All required email settings are configured")
        return True


def test_simple_email():
    """Test sending a simple email"""
    print("\n📧 Testing Simple Email")
    print("-" * 30)
    
    to_email = input("Enter your email for testing: ")
    if not to_email:
        print("❌ Email address is required")
        return False
    
    subject = "Test Email - Total Keepers Email Service"
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Test Email</title>
    </head>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1e40af; color: white; padding: 20px; text-align: center;">
            <h1>🥅 Total Keepers</h1>
            <h2>Email Service Test</h2>
        </div>
        
        <div style="padding: 20px;">
            <h3>Email Service Working! ✅</h3>
            <p>This is a test email from the Total Keepers email service.</p>
            <p>If you're reading this, the Gmail SMTP integration is working correctly.</p>
            
            <div style="background: #f0f9ff; border: 1px solid #0284c7; padding: 15px; margin: 20px 0;">
                <h4>📋 Service Details:</h4>
                <ul>
                    <li><strong>Email Service:</strong> Gmail SMTP</li>
                    <li><strong>Test Time:</strong> {}</li>
                    <li><strong>Status:</strong> ✅ Working</li>
                </ul>
            </div>
            
            <p>Best regards,<br><strong>Total Keepers Team</strong></p>
        </div>
        
        <div style="background: #f9fafb; padding: 15px; text-align: center; font-size: 12px;">
            <p>This is an automated test email. Please do not reply.</p>
        </div>
    </body>
    </html>
    """.format(datetime.now().strftime("%B %d, %Y at %I:%M %p"))
    
    text_content = f"""
    Total Keepers - Email Service Test
    
    Email Service Working! ✅
    
    This is a test email from the Total Keepers email service.
    If you're reading this, the Gmail SMTP integration is working correctly.
    
    Service Details:
    - Email Service: Gmail SMTP
    - Test Time: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
    - Status: ✅ Working
    
    Best regards,
    Total Keepers Team
    
    ---
    This is an automated test email. Please do not reply.
    """
    
    print(f"📤 Sending test email to {to_email}...")
    success = EmailService.send_email(to_email, subject, html_content, text_content)
    
    if success:
        print("✅ Test email sent successfully!")
        return True
    else:
        print("❌ Failed to send test email")
        return False


def test_booking_confirmation_email():
    """Test sending a booking confirmation email"""
    print("\n📧 Testing Booking Confirmation Email")
    print("-" * 40)
    
    to_email = input("Enter your email for testing: ")
    if not to_email:
        print("❌ Email address is required")
        return False
    
    # Create a mock booking summary
    booking_summary = BookingSummary(
        booking_reference="TK-TEST-001",
        participant_name="Test Participant",
        participant_email=to_email,
        session_title="Youth Goalkeeper Development",
        session_date=datetime(2025, 8, 16, 10, 0),
        session_location="Total Keepers Training Center, Madrid",
        coach_name="Aitor Peetxe"
    )
    
    print(f"📤 Sending booking confirmation to {to_email}...")
    success = EmailService.send_booking_confirmation_to_participant(booking_summary)
    
    if success:
        print("✅ Booking confirmation email sent successfully!")
        return True
    else:
        print("❌ Failed to send booking confirmation email")
        return False


def test_organizer_notification():
    """Test sending organizer notification email"""
    print("\n📧 Testing Organizer Notification Email")
    print("-" * 40)
    
    participant_email = input("Enter participant email for test booking: ")
    if not participant_email:
        print("❌ Participant email is required")
        return False
    
    # Create a mock booking summary
    booking_summary = BookingSummary(
        booking_reference="TK-TEST-002",
        participant_name="Test Participant",
        participant_email=participant_email,
        session_title="Advanced Goalkeeper Techniques",
        session_date=datetime(2025, 8, 17, 15, 0),
        session_location="Total Keepers Training Center, Madrid",
        coach_name="Aitor Peetxe"
    )
    
    print("📤 Sending organizer notification...")
    success = EmailService.send_booking_notification_to_organizer(booking_summary)
    
    if success:
        print("✅ Organizer notification email sent successfully!")
        return True
    else:
        print("❌ Failed to send organizer notification email")
        return False


def main():
    """Main test function"""
    print("🥅 Total Keepers Email Service Test")
    print("=" * 50)
    
    # Test configuration
    if not test_email_service_configuration():
        print("\n❌ Email service configuration is incomplete")
        print("Please check your .env file and ensure SMTP settings are correct")
        return
    
    print("\n🧪 Email Tests Available:")
    print("1. Simple test email")
    print("2. Booking confirmation email")
    print("3. Organizer notification email")
    print("4. All tests")
    
    choice = input("\nSelect test (1-4): ").strip()
    
    try:
        if choice == "1":
            test_simple_email()
        elif choice == "2":
            test_booking_confirmation_email()
        elif choice == "3":
            test_organizer_notification()
        elif choice == "4":
            print("\n🚀 Running all email tests...")
            test_simple_email()
            test_booking_confirmation_email()
            test_organizer_notification()
            print("\n🎉 All tests completed!")
        else:
            print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\n👋 Tests cancelled")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")


if __name__ == "__main__":
    main()
