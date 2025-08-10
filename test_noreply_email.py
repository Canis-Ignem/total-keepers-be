#!/usr/bin/env python3
"""
Test script for no-reply email functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email_service import EmailService
from app.core.config import settings

def test_noreply_email():
    """Test the no-reply email functionality"""
    
    print("🧪 Testing No-Reply Email Functionality")
    print("=" * 50)
    
    # Test email details
    test_email = "test@example.com"  # Replace with your test email
    subject = "Test No-Reply Email"
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            .container { max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; }
            .header { background-color: #1e40af; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; }
            .notice { background-color: #fef3c7; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f59e0b; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🥅 Total Keepers</h1>
                <h2>No-Reply Email Test</h2>
            </div>
            <div class="content">
                <h3>This is a test no-reply email</h3>
                <p>Hello! This email is sent from our no-reply system.</p>
                
                <div class="notice">
                    <strong>⚠️ Please Do Not Reply</strong><br>
                    This is an automated message sent from a no-reply address. 
                    Please do not reply to this email as it is not monitored.
                </div>
                
                <p>If you need assistance, please contact us through our official channels:</p>
                <ul>
                    <li>📧 Email: contact@totalkeepers.com</li>
                    <li>🌐 Website: www.totalkeepers.com</li>
                    <li>📱 Phone: +34 XXX XXX XXX</li>
                </ul>
                
                <p>Thank you!</p>
                <p><strong>The Total Keepers Team</strong></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = """
    TOTAL KEEPERS - No-Reply Email Test
    
    This is a test no-reply email.
    
    ⚠️ Please Do Not Reply
    This is an automated message sent from a no-reply address. 
    Please do not reply to this email as it is not monitored.
    
    If you need assistance, please contact us:
    - Email: contact@totalkeepers.com
    - Website: www.totalkeepers.com
    - Phone: +34 XXX XXX XXX
    
    Thank you!
    The Total Keepers Team
    """
    
    print(f"📧 Sending no-reply email to: {test_email}")
    print(f"📝 Subject: {subject}")
    print(f"🔧 SMTP Server: {settings.SMTP_SERVER}")
    print(f"👤 From Name: {settings.SMTP_FROM_NAME}")
    print(f"📬 No-Reply Address: {settings.NOREPLY_EMAIL}")
    print(f"🔐 SMTP Username: {settings.SMTP_USERNAME}")
    print()
    
    # Test regular email method
    print("Testing regular send_email method...")
    result1 = EmailService.send_email(test_email, subject + " (Regular)", html_content, text_content)
    print(f"✅ Regular email result: {result1}")
    print()
    
    # Test dedicated no-reply method
    print("Testing dedicated send_noreply_email method...")
    result2 = EmailService.send_noreply_email(test_email, subject + " (No-Reply)", html_content, text_content)
    print(f"✅ No-reply email result: {result2}")
    print()
    
    if result1 and result2:
        print("🎉 Both email methods working successfully!")
        print("📬 Check your inbox to see the difference in headers")
    else:
        print("❌ Some emails failed to send")
        print("🔍 Check your SMTP configuration in .env file")

if __name__ == "__main__":
    test_noreply_email()
