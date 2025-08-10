# Standard library imports
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Local application imports
from app.core.config import settings
from app.schemas.campus import BookingSummary

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def send_email(
        to_email: str, subject: str, html_content: str, text_content: str = None
    ) -> bool:
        """Send an email using Gmail SMTP"""
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            
            # Use SMTP_FROM_EMAIL if available, otherwise fallback to EMAIL_FROM
            actual_from_email = settings.SMTP_FROM_EMAIL or settings.EMAIL_FROM
            from_name = settings.SMTP_FROM_NAME
            noreply_email = settings.NOREPLY_EMAIL
            
            # Set up no-reply functionality
            msg["From"] = f"{from_name} <{noreply_email}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg["Reply-To"] = noreply_email  # Set no-reply address
            msg["Sender"] = actual_from_email  # Actual sending email
            
            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, "plain")
                msg.attach(text_part)

            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Send email using Gmail SMTP
            smtp_server = settings.SMTP_SERVER or settings.SMTP_HOST
            smtp_username = settings.SMTP_USERNAME or settings.SMTP_USER
            smtp_password = settings.SMTP_PASSWORD
            
            if not smtp_username or not smtp_password:
                logger.error("SMTP credentials not configured. Check SMTP_USERNAME and SMTP_PASSWORD in .env")
                return False
            
            logger.info(f"Connecting to {smtp_server}:{settings.SMTP_PORT}")
            with smtplib.SMTP(smtp_server, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                    logger.info("TLS encryption started")
                
                server.login(smtp_username, smtp_password)
                logger.info("SMTP authentication successful")
                
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {str(e)}")
            logger.error("Check your Gmail app password and 2FA settings")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending to {to_email}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    @staticmethod
    def send_booking_confirmation_to_participant(
        booking_summary: BookingSummary,
    ) -> bool:
        """Send booking confirmation email to participant"""
        subject = f"Campus Booking Confirmation - {booking_summary.booking_reference}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                .container {{ max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; }}
                .header {{ background-color: #1e40af; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .booking-details {{ background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ background-color: #f9fafb; padding: 15px; text-align: center; font-size: 12px; color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🥅 Total Keepers Campus</h1>
                    <h2>Booking Confirmation</h2>
                </div>
                
                <div class="content">
                    <h3>Hello {booking_summary.participant_name}!</h3>
                    
                    <p>Thank you for registering for our goalkeeper training campus! Your booking has been confirmed.</p>
                    
                    <div class="booking-details">
                        <h4>📋 Booking Details</h4>
                        <p><strong>Booking Reference:</strong> {booking_summary.booking_reference}</p>
                        <p><strong>Session:</strong> {booking_summary.session_title}</p>
                        <p><strong>Date & Time:</strong> {booking_summary.session_date.strftime("%A, %B %d, %Y at %I:%M %p")}</p>
                        <p><strong>Location:</strong> {booking_summary.session_location}</p>
                        <p><strong>Coach:</strong> {booking_summary.coach_name}</p>
                    </div>
                    
                    <h4>📝 What to Bring:</h4>
                    <ul>
                        <li>Goalkeeper gloves</li>
                        <li>Comfortable training clothes</li>
                        <li>Water bottle</li>
                        <li>Positive attitude!</li>
                    </ul>
                    
                    <h4>📍 Important Information:</h4>
                    <ul>
                        <li>Please arrive 15 minutes before the session starts</li>
                        <li>If you need to cancel, please contact us at least 24 hours in advance</li>
                        <li>In case of weather concerns, we'll notify you via email</li>
                    </ul>
                    
                    <p>We're excited to see you on the field! If you have any questions, feel free to contact us.</p>
                    
                    <p>Best regards,<br>
                    <strong>Total Keepers Team</strong><br>
                    aitorpeetxe@gmail.com</p>
                </div>
                
                <div class="footer">
                    <p>Total Keepers - Elite Goalkeeper Training Campus</p>
                    <p>This email was sent regarding your booking reference: {booking_summary.booking_reference}</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Total Keepers Campus - Booking Confirmation
        
        Hello {booking_summary.participant_name}!
        
        Thank you for registering for our goalkeeper training campus! Your booking has been confirmed.
        
        BOOKING DETAILS:
        - Reference: {booking_summary.booking_reference}
        - Session: {booking_summary.session_title}
        - Date: {booking_summary.session_date.strftime("%A, %B %d, %Y at %I:%M %p")}
        - Location: {booking_summary.session_location}
        - Coach: {booking_summary.coach_name}
        
        What to bring:
        - Goalkeeper gloves
        - Comfortable training clothes
        - Water bottle
        - Positive attitude!
        
        Important:
        - Arrive 15 minutes early
        - Cancel 24 hours in advance if needed
        - Check email for weather updates
        
        Questions? Contact us at aitorpeetxe@gmail.com
        
        Best regards,
        Total Keepers Team
        """

        return EmailService.send_email(
            booking_summary.participant_email, subject, html_content, text_content
        )

    @staticmethod
    def send_booking_notification_to_organizer(booking_summary: BookingSummary) -> bool:
        """Send booking notification email to organizer"""
        subject = f"New Campus Booking - {booking_summary.booking_reference}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                .container {{ max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; }}
                .header {{ background-color: #059669; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .booking-details {{ background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🆕 New Campus Booking</h1>
                </div>
                
                <div class="content">
                    <h3>New participant registration!</h3>
                    
                    <div class="booking-details">
                        <h4>📋 Booking Details</h4>
                        <p><strong>Reference:</strong> {booking_summary.booking_reference}</p>
                        <p><strong>Participant:</strong> {booking_summary.participant_name}</p>
                        <p><strong>Email:</strong> {booking_summary.participant_email}</p>
                        <p><strong>Session:</strong> {booking_summary.session_title}</p>
                        <p><strong>Date:</strong> {booking_summary.session_date.strftime("%A, %B %d, %Y at %I:%M %p")}</p>
                        <p><strong>Location:</strong> {booking_summary.session_location}</p>
                        <p><strong>Coach:</strong> {booking_summary.coach_name}</p>
                    </div>
                    
                    <p>The participant has been automatically sent a confirmation email with all the details.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email("aitorpeetxe@gmail.com", subject, html_content)

    @staticmethod
    def send_welcome_email(user_email: str, user_name: str) -> bool:
        """Send welcome email to new user"""
        subject = "Welcome to Total Keepers! 🥅"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to Total Keepers</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 30px; text-align: center;">
                <h1 style="margin: 0;">🥅 Welcome to Total Keepers!</h1>
                <p style="margin: 10px 0 0 0; font-size: 18px;">Elite Goalkeeper Training Academy</p>
            </div>
            
            <div style="padding: 30px 20px;">
                <h2 style="color: #2c3e50;">Hello {user_name}! 👋</h2>
                
                <p>Welcome to the Total Keepers family! We're excited to have you join our 
                elite goalkeeper training community.</p>
                
                <div style="background: #f8f9fa; border-left: 4px solid #3498db; 
                            padding: 20px; margin: 25px 0;">
                    <h3 style="margin-top: 0; color: #2c3e50;">🎯 What's Next?</h3>
                    <ul style="margin-bottom: 0;">
                        <li>Browse our training sessions and camps</li>
                        <li>Book your first goalkeeper training session</li>
                        <li>Join our community of dedicated goalkeepers</li>
                        <li>Access exclusive training resources</li>
                    </ul>
                </div>
                
                <div style="background: #e8f5e8; border: 1px solid #4caf50; 
                            padding: 20px; margin: 25px 0; border-radius: 5px;">
                    <h4 style="margin-top: 0; color: #2e7d32;">🎁 Special Welcome Offer</h4>
                    <p style="margin-bottom: 0;">Use code <strong>WELCOME2025</strong> 
                    for 10% off your first training session!</p>
                </div>
                
                <p>If you have any questions or need assistance, feel free to reach out to our team.</p>
                
                <p>Best regards,<br>
                <strong>The Total Keepers Team</strong><br>
                Elite Goalkeeper Training Academy</p>
            </div>
            
            <div style="background: #34495e; color: white; padding: 20px; 
                        text-align: center; font-size: 12px;">
                <p style="margin: 0;">Thank you for choosing Total Keepers!</p>
                <p style="margin: 5px 0 0 0;">For support, contact: info@totalkeepers.com</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to Total Keepers! 🥅
        
        Hello {user_name}!
        
        Welcome to the Total Keepers family! We're excited to have you join our 
        elite goalkeeper training community.
        
        What's Next:
        - Browse our training sessions and camps
        - Book your first goalkeeper training session
        - Join our community of dedicated goalkeepers
        - Access exclusive training resources
        
        Special Welcome Offer:
        Use code WELCOME2025 for 10% off your first training session!
        
        If you have any questions, contact us at info@totalkeepers.com
        
        Best regards,
        The Total Keepers Team
        Elite Goalkeeper Training Academy
        """
        
        try:
            return EmailService.send_email(user_email, subject, html_content, text_content)
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user_email}: {str(e)}")
            return False

    @staticmethod
    def send_noreply_email(
        to_email: str, subject: str, html_content: str, text_content: str = None
    ) -> bool:
        """Send a no-reply email with explicit no-reply headers"""
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            
            # Use the actual sending email for SMTP auth
            actual_from_email = settings.SMTP_FROM_EMAIL or settings.EMAIL_FROM
            from_name = settings.SMTP_FROM_NAME
            noreply_email = settings.NOREPLY_EMAIL
            
            # Set up clear no-reply headers
            msg["From"] = f"{from_name} <{noreply_email}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg["Reply-To"] = noreply_email
            msg["Sender"] = actual_from_email
            msg["X-Auto-Response-Suppress"] = "All"  # Suppress auto-replies
            msg["Auto-Submitted"] = "auto-generated"  # Mark as automated
            
            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, "plain")
                msg.attach(text_part)

            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Send email using Gmail SMTP
            smtp_server = settings.SMTP_SERVER or settings.SMTP_HOST
            smtp_username = settings.SMTP_USERNAME or settings.SMTP_USER
            smtp_password = settings.SMTP_PASSWORD
            
            if not smtp_username or not smtp_password:
                logger.error("SMTP credentials not configured. Check SMTP_USERNAME and SMTP_PASSWORD in .env")
                return False
            
            logger.info(f"Sending no-reply email to {to_email}")
            with smtplib.SMTP(smtp_server, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                
                server.login(smtp_username, smtp_password)
                server.send_message(msg)

            logger.info(f"No-reply email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send no-reply email to {to_email}: {str(e)}")
            return False
