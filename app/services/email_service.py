# Standard library imports
import logging
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

# Local application imports
from app.core.config import settings
from app.schemas.campus import BookingSummary

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
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
                logger.error(
                    "SMTP credentials not configured. Check SMTP_USERNAME and SMTP_PASSWORD in .env"
                )
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
            return EmailService.send_email(
                user_email, subject, html_content, text_content
            )
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user_email}: {str(e)}")
            return False

    @staticmethod
    def send_noreply_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
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
                logger.error(
                    "SMTP credentials not configured. Check SMTP_USERNAME and SMTP_PASSWORD in .env"
                )
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

    @staticmethod
    def send_payment_success_notification(
        order_id: str,
        payment_id: str,
        amount: float,
        customer_email: str = None,
        transaction_id: str = None,
        shipping_address: dict = None,
        order_items: list = None,  # Add order items parameter
    ) -> bool:
        """Send Spanish invoice email for successful payment"""
        admin_email = settings.FINANCE_EMAIL
        subject = f"Factura Total Keepers - Pedido #{order_id}"

        # Calculate VAT details (VAT is already included in the price)
        vat_rate = 0.21  # 21% VAT in Spain
        net_amount = amount / (1 + vat_rate)
        vat_amount = amount - net_amount

        # Generate invoice number based on order and timestamp
        invoice_date = datetime.utcnow()
        invoice_number = f"TK-{invoice_date.strftime('%Y%m%d')}-{order_id}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .invoice-container {{ max-width: 800px; margin: 0 auto; background-color: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                .header {{ background-color: #1e40af; color: white; padding: 30px; }}
                .company-info {{ display: flex; justify-content: space-between; align-items: center; }}
                .logo {{ font-size: 28px; font-weight: bold; }}
                .invoice-title {{ font-size: 24px; margin-top: 10px; }}
                .invoice-details {{ padding: 30px; }}
                .invoice-meta {{ display: flex; justify-content: space-between; margin-bottom: 30px; }}
                .billing-info {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
                .items-table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
                .items-table th, .items-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
                .items-table th {{ background-color: #f8f9fa; font-weight: bold; }}
                .total-section {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; }}
                .total-row {{ display: flex; justify-content: space-between; margin-bottom: 10px; }}
                .total-final {{ font-size: 18px; font-weight: bold; border-top: 2px solid #1e40af; padding-top: 10px; }}
                .footer {{ background-color: #1e40af; color: white; padding: 20px; text-align: center; }}
                .payment-info {{ background-color: #e8f4f8; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
                .vat-notice {{ background-color: #fff3cd; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #ffc107; }}
            </style>
        </head>
        <body>
            <div class="invoice-container">
                <!-- Header -->
                <div class="header">
                    <div class="company-info">
                        <div>
                            <div class="logo">🥅 TOTAL KEEPERS</div>
                            <div>Tienda de Equipamiento Deportivo</div>
                        </div>
                        <div style="text-align: right;">
                            <div class="invoice-title">FACTURA</div>
                            <div>Nº {invoice_number}</div>
                        </div>
                    </div>
                </div>

                <!-- Invoice Details -->
                <div class="invoice-details">
                    <!-- Invoice Meta -->
                    <div class="invoice-meta">
                        <div>
                            <h3 style="margin-top: 0;">Datos de la Empresa</h3>
                            <strong>UNAI GOTI EZQUERRA Y OTRO SC</strong><br>
                            CIF: J75949271<br>
                            Dirección: MÚGICA Y BUTRÓN 7-1C 48007 BILBAO, VIZCAYA<br>
                            España<br>
                            Email: totalkeepersbilbao@gmail.com
                        </div>
                        <div style="text-align: right;">
                            <h3 style="margin-top: 0;">Detalles de la Factura</h3>
                            <strong>Fecha:</strong> {
            invoice_date.strftime("%d/%m/%Y")
        }<br>
                            <strong>Pedido:</strong> #{order_id}<br>
                            <strong>Pago ID:</strong> {payment_id}<br>
                            <strong>Transacción:</strong> {transaction_id or "N/A"}
                        </div>
                    </div>

                    <!-- Payment Info -->
                    <div class="payment-info">
                        <h4 style="margin-top: 0; color: #0c5460;">✅ Pago Procesado Correctamente</h4>
                        <p style="margin-bottom: 0;">
                            El pago ha sido procesado exitosamente a través de Redsys.
                            {
            f"Email del cliente: {customer_email}"
            if customer_email
            else "Cliente: Invitado"
        }
                        </p>
                    </div>

                    <!-- VAT Notice -->
                    <div class="vat-notice">
                        <h4 style="margin-top: 0; color: #856404;">📋 Información Fiscal</h4>
                        <p style="margin-bottom: 0;">
                            <strong>IVA incluido:</strong> Todos los precios mostrados incluyen el 21% de IVA según la normativa española vigente.
                        </p>
                    </div>

                    <!-- Billing Information -->
                    <div class="billing-info">
                        <h3 style="margin-top: 0;">Datos de Facturación y Envío</h3>
                        <div style="display: flex; gap: 30px;">
                            <div style="flex: 1;">
                                <h4 style="margin-bottom: 10px; color: #1e40af;">Cliente</h4>
                                <strong>Email:</strong> {
            customer_email or "Cliente Invitado"
        }<br>
                                <strong>Método de Pago:</strong> Tarjeta de Crédito/Débito (Redsys)<br>
                                <strong>Estado del Pago:</strong> ✅ Completado
                            </div>
                            {
            f'''
                            <div style="flex: 1;">
                                <h4 style="margin-bottom: 10px; color: #1e40af;">Dirección de Envío</h4>
                                <strong>{shipping_address.get("first_name", "")} {shipping_address.get("last_name", "")}</strong><br>
                                {shipping_address.get("address_line_1", "")}<br>
                                {f"{shipping_address.get('address_line_2')}<br>" if shipping_address.get("address_line_2") else ""}
                                {shipping_address.get("city", "")}, {shipping_address.get("state", "")}<br>
                                {shipping_address.get("postal_code", "")} {shipping_address.get("country", "")}<br>
                                {f"Tel: {shipping_address.get('phone', '')}" if shipping_address.get("phone") else ""}
                            </div>
                            '''
            if shipping_address
            else ""
        }
                        </div>
                    </div>

                    <!-- Items Table -->
                    <table class="items-table">
                        <thead>
                            <tr>
                                <th>Descripción</th>
                                <th style="text-align: center;">Talla</th>
                                <th style="text-align: center;">Cantidad</th>
                                <th style="text-align: right;">Precio Unitario</th>
                                <th style="text-align: right;">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {
            "".join(
                [
                    f'''
                            <tr>
                                <td>{item.get("product_name", "Producto")}</td>
                                <td style="text-align: center;">{item.get("size", "N/A")}</td>
                                <td style="text-align: center;">{item.get("quantity", 1)}</td>
                                <td style="text-align: right;">€{item.get("unit_price", 0):.2f}</td>
                                <td style="text-align: right;">€{item.get("total_price", 0):.2f}</td>
                            </tr>
                            '''
                    for item in order_items
                ]
            )
            if order_items
            else f'''
                            <tr>
                                <td>Pedido Total Keepers #{order_id}</td>
                                <td style="text-align: center;">-</td>
                                <td style="text-align: center;">1</td>
                                <td style="text-align: right;">€{net_amount:.2f}</td>
                                <td style="text-align: right;"><strong>€{amount:.2f}</strong></td>
                            </tr>
                            '''
        }
                        </tbody>
                    </table>

                    <!-- Totals -->
                    <div class="total-section">
                        <div class="total-row">
                            <span>Subtotal (Base Imponible):</span>
                            <span>€{net_amount:.2f}</span>
                        </div>
                        <div class="total-row">
                            <span>IVA (21%):</span>
                            <span>€{vat_amount:.2f}</span>
                        </div>
                        <div class="total-row total-final">
                            <span>TOTAL FACTURA:</span>
                            <span>€{amount:.2f}</span>
                        </div>
                    </div>

                    <!-- Additional Information -->
                    <div style="margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 8px;">
                        <h4 style="margin-top: 0;">Información Adicional</h4>
                        <ul style="margin-bottom: 0;">
                            <li>Esta factura se genera automáticamente tras el pago exitoso</li>
                            <li>Conserve este documento para sus registros contables</li>
                            <li>Para cualquier consulta, contacte con: totalkeepersbilbao@gmail.com</li>
                            <li>Fecha y hora de procesamiento: {
            datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
        } UTC</li>
                        </ul>
                    </div>
                </div>

                <!-- Footer -->
                <div class="footer">
                    <p style="margin: 0;"><strong>Total Keepers - Equipamiento Deportivo Profesional</strong></p>
                    <p style="margin: 5px 0 0 0;">Factura generada automáticamente • Sistema de Pagos Seguro Redsys</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        FACTURA TOTAL KEEPERS
        Nº {invoice_number}
        
        DATOS DE LA EMPRESA:
        Total Keepers S.L.
        CIF: B12345678
        Dirección: Calle Principal, 123
        48001 Bilbao, Vizcaya, España
        Email: totalkeepersbilbao@gmail.com
        
        DETALLES DE LA FACTURA:
        Fecha: {invoice_date.strftime("%d/%m/%Y")}
        Pedido: #{order_id}
        Pago ID: {payment_id}
        Transacción: {transaction_id or "N/A"}
        
        PAGO PROCESADO CORRECTAMENTE
        El pago ha sido procesado exitosamente a través de Redsys.
        {
            f"Email del cliente: {customer_email}"
            if customer_email
            else "Cliente: Invitado"
        }
        
        INFORMACIÓN FISCAL:
        IVA incluido: Todos los precios mostrados incluyen el 21% de IVA según la normativa española vigente.
        
        DATOS DE FACTURACIÓN Y ENVÍO:
        Cliente: {customer_email or "Cliente Invitado"}
        Método de Pago: Tarjeta de Crédito/Débito (Redsys)
        Estado del Pago: Completado
        
        {
            f'''DIRECCIÓN DE ENVÍO:
        {shipping_address.get("first_name", "")} {shipping_address.get("last_name", "")}
        {shipping_address.get("address_line_1", "")}
        {f"{shipping_address.get('address_line_2')}" if shipping_address.get("address_line_2") else ""}
        {shipping_address.get("city", "")}, {shipping_address.get("state", "")}
        {shipping_address.get("postal_code", "")} {shipping_address.get("country", "")}
        {f"Tel: {shipping_address.get('phone', '')}" if shipping_address.get("phone") else ""}
        '''
            if shipping_address
            else ""
        }
        
        DETALLE DEL PEDIDO:
        Descripción: Pedido Total Keepers #{order_id}
        Cantidad: 1
        Precio Base: €{net_amount:.2f}
        IVA (21%): €{vat_amount:.2f}
        Total: €{amount:.2f}
        
        TOTALES:
        Subtotal (Base Imponible): €{net_amount:.2f}
        IVA (21%): €{vat_amount:.2f}
        TOTAL FACTURA: €{amount:.2f}
        
        INFORMACIÓN ADICIONAL:
        - Esta factura se genera automáticamente tras el pago exitoso
        - Conserve este documento para sus registros contables
        - Para cualquier consulta, contacte con: totalkeepersbilbao@gmail.com
        - Fecha y hora de procesamiento: {
            datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
        } UTC
        
        Total Keepers - Equipamiento Deportivo Profesional
        Factura generada automáticamente • Sistema de Pagos Seguro Redsys
        """

        try:
            logger.info(
                f"Attempting to send Spanish invoice email for order {order_id} to {admin_email}"
            )
            result = EmailService.send_email(
                admin_email, subject, html_content, text_content
            )
            if result:
                logger.info(
                    f"Spanish invoice email sent successfully for order {order_id}"
                )
            else:
                logger.error(
                    f"Failed to send Spanish invoice email for order {order_id}"
                )
            return result
        except Exception as e:
            logger.error(
                f"Exception sending Spanish invoice email for order {order_id}: {str(e)}"
            )
            return False
