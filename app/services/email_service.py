# Standard library imports
import logging
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

# Third-party imports
try:
    from azure.communication.email import EmailClient
    AZURE_EMAIL_AVAILABLE = True
except ImportError:
    AZURE_EMAIL_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Azure Communication Email SDK not installed. Install with: pip install azure-communication-email")

# Local application imports
from app.core.config import settings
from app.schemas.campus import BookingSummary

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def send_email_azure(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Send an email using Azure Communication Services"""
        if not AZURE_EMAIL_AVAILABLE:
            logger.warning("Azure Communication Email SDK not available")
            return False
            
        if not settings.AZURE_COMMUNICATION_CONNECTION_STRING or not settings.AZURE_EMAIL_SENDER:
            logger.warning("Azure Communication Services not configured. Set AZURE_COMMUNICATION_CONNECTION_STRING and AZURE_EMAIL_SENDER")
            return False

        try:
            # Create Azure Email client
            email_client = EmailClient.from_connection_string(
                settings.AZURE_COMMUNICATION_CONNECTION_STRING
            )

            # Prepare email message
            message = {
                "senderAddress": settings.AZURE_EMAIL_SENDER,
                "recipients": {
                    "to": [{"address": to_email}]
                },
                "content": {
                    "subject": subject,
                    "plainText": text_content or "Please view this email in HTML format.",
                    "html": html_content
                }
            }

            # Send email
            logger.info(f"Sending email via Azure Communication Services to {to_email}")
            poller = email_client.begin_send(message)
            result = poller.result()
            
            logger.info(f"Azure email sent successfully to {to_email}. Message ID: {result['id']}, Status: {result['status']}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email via Azure Communication Services to {to_email}: {str(e)}")
            return False

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
            return False

    @staticmethod
    def send_email_dual(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> dict:
        """
        Send email via both Gmail SMTP and Azure Communication Services for redundancy.
        Returns dict with status of each service.
        """
        results = {
            "gmail": False,
            "azure": False,
            "success": False
        }

        # Try Gmail SMTP
        try:
            gmail_result = EmailService.send_email(to_email, subject, html_content, text_content)
            results["gmail"] = gmail_result
            if gmail_result:
                logger.info(f"Gmail SMTP delivery successful to {to_email}")
        except Exception as e:
            logger.error(f"Gmail SMTP delivery failed to {to_email}: {str(e)}")
            results["gmail"] = False

        # Try Azure Communication Services
        try:
            azure_result = EmailService.send_email_azure(to_email, subject, html_content, text_content)
            results["azure"] = azure_result
            if azure_result:
                logger.info(f"Azure Communication Services delivery successful to {to_email}")
        except Exception as e:
            logger.error(f"Azure Communication Services delivery failed to {to_email}: {str(e)}")
            results["azure"] = False

        # Mark as success if at least one method succeeded
        results["success"] = results["gmail"] or results["azure"]
        
        if results["success"]:
            logger.info(f"Email delivered successfully to {to_email} (Gmail: {results['gmail']}, Azure: {results['azure']})")
        else:
            logger.error(f"All email delivery methods failed for {to_email}")
        
        return results

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
            # Send via both Gmail and Azure for redundancy
            results = EmailService.send_email_dual(
                admin_email, subject, html_content, text_content
            )
            
            if results["success"]:
                logger.info(
                    f"Spanish invoice email sent successfully for order {order_id} "
                    f"(Gmail: {results['gmail']}, Azure: {results['azure']})"
                )
            else:
                logger.error(
                    f"Failed to send Spanish invoice email for order {order_id} via all methods"
                )
            
            return results["success"]
        except Exception as e:
            logger.error(
                f"Exception sending Spanish invoice email for order {order_id}: {str(e)}"
            )
            return False

    @staticmethod
    def send_customer_order_confirmation(
        customer_email: str,
        customer_name: str,
        order_id: str,
        order_items: list = None,
    ) -> bool:
        """Send Spanish order confirmation email to customer"""
        subject = f"Confirmación de Pedido - Total Keepers #{order_id}"

        # Build product list
        product_list_html = ""
        product_list_text = ""
        
        if order_items:
            for item in order_items:
                product_name = item.get("product_name", "Producto")
                size = item.get("size", "N/A")
                quantity = item.get("quantity", 1)
                
                product_list_html += f"<li><strong>{product_name}</strong> - Talla: {size} - Cantidad: {quantity}</li>\n"
                product_list_text += f"- {product_name} - Talla: {size} - Cantidad: {quantity}\n"
        else:
            product_list_html = "<li>Tu pedido</li>"
            product_list_text = "- Tu pedido\n"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .email-container {{ max-width: 600px; margin: 0 auto; background-color: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                .header {{ background-color: #1e40af; color: white; padding: 30px; text-align: center; }}
                .logo {{ font-size: 32px; font-weight: bold; margin-bottom: 10px; }}
                .content {{ padding: 30px; line-height: 1.8; }}
                .greeting {{ font-size: 18px; margin-bottom: 20px; }}
                .order-section {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .order-list {{ list-style: none; padding-left: 0; }}
                .order-list li {{ padding: 10px 0; border-bottom: 1px solid #dee2e6; }}
                .order-list li:last-child {{ border-bottom: none; }}
                .message {{ color: #374151; font-size: 15px; }}
                .footer {{ background-color: #1e40af; color: white; padding: 25px; text-align: center; }}
                .footer-links {{ margin-top: 15px; }}
                .footer-links a {{ color: white; text-decoration: none; margin: 0 10px; }}
                .social {{ margin-top: 10px; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <!-- Header -->
                <div class="header">
                    <div class="logo">🥅 TOTAL KEEPERS</div>
                    <div>Confirmación de Pedido</div>
                </div>

                <!-- Content -->
                <div class="content">
                    <div class="greeting">
                        <strong>Hola {customer_name},</strong>
                    </div>

                    <p class="message">
                        Gracias por tu compra.
                    </p>

                    <p class="message">
                        Te confirmamos que hemos recibido correctamente tu pedido de:
                    </p>

                    <!-- Order Items -->
                    <div class="order-section">
                        <ul class="order-list">
                            {product_list_html}
                        </ul>
                    </div>

                    <p class="message">
                        Nuestro equipo de <strong>TOTAL KEEPERS</strong> preparará tu pedido con el mayor cuidado y la mayor 
                        rapidez para que lo recibas lo antes posible.
                    </p>

                    <p class="message">
                        Agradecemos tu confianza en <strong>TOTAL KEEPERS GLOVES</strong>.
                    </p>

                    <p class="message">
                        Seguimos trabajando para ofrecerte los mejores guantes y la mejor protección bajo los palos.
                    </p>

                    <p class="message" style="margin-top: 30px;">
                        Atentamente,<br>
                        <strong>TOTAL KEEPERS</strong>
                    </p>
                </div>

                <!-- Footer -->
                <div class="footer">
                    <p style="margin: 0;"><strong>TOTAL KEEPERS</strong></p>
                    <div class="footer-links">
                        <a href="mailto:totalkeepersbilbao@gmail.com">totalkeepersbilbao@gmail.com</a><br>
                        <a href="https://totalkeepers.net/" target="_blank">https://totalkeepers.net/</a>
                    </div>
                    <div class="social">
                        Redes sociales: @totalkeepers
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
Hola {customer_name},

Gracias por tu compra.

Te confirmamos que hemos recibido correctamente tu pedido de:

{product_list_text}

Nuestro equipo de TOTAL KEEPERS preparará tu pedido con el mayor cuidado y la mayor
rapidez para que lo recibas lo antes posible.

Agradecemos tu confianza en TOTAL KEEPERS GLOVES.

Seguimos trabajando para ofrecerte los mejores guantes y la mejor protección bajo los
palos.

Atentamente,
TOTAL KEEPERS

totalkeepersbilbao@gmail.com
https://totalkeepers.net/
Redes sociales: @totalkeepers
        """

        try:
            logger.info(
                f"Attempting to send customer confirmation email for order {order_id} to {customer_email}"
            )
            # Send ONLY via Azure Communication Services (not Gmail)
            azure_result = EmailService.send_email_azure(
                customer_email, subject, html_content, text_content
            )
            
            if azure_result:
                logger.info(
                    f"✅ Customer confirmation email sent successfully via Azure for order {order_id} to {customer_email}"
                )
            else:
                logger.error(
                    f"❌ Failed to send customer confirmation email via Azure for order {order_id}"
                )
            
            return azure_result
        except Exception as e:
            logger.error(
                f"Exception sending customer confirmation email for order {order_id}: {str(e)}"
            )
            return False
