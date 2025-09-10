import smtplib
import time
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import logging
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailSenderService:
    """
    Service for sending emails using SMTP or SendGrid API.
    """
    
    def __init__(self, smtp_config: Optional[Dict] = None, sendgrid_api_key: Optional[str] = None):
        self.smtp_config = smtp_config or self._get_default_smtp_config()
        self.sendgrid_api_key = sendgrid_api_key or os.getenv('SENDGRID_API_KEY')
        self.rate_limit_delay = 2  # seconds between emails
        self.max_retries = 3
        
    def _get_default_smtp_config(self) -> Dict:
        """Load SMTP configuration from environment variables."""
        return {
            'smtp_server': os.getenv('SMTP_SERVER'),
            'smtp_port': int(os.getenv('SMTP_PORT', 587)),
            'username': os.getenv('SMTP_USERNAME'),
            'password': os.getenv('SMTP_PASSWORD'),
            'use_tls': True,
        }

    def send_email(self, to_email: str, subject: str, body: str, from_email: Optional[str] = None, from_name: Optional[str] = None) -> Dict:
        """Send a single email."""
        try:
            # Use SendGrid API if available, otherwise SMTP
            if self.sendgrid_api_key:
                result = self._send_via_sendgrid(to_email, subject, body, from_email, from_name)
            else:
                result = self._send_via_smtp(to_email, subject, body, from_email, from_name)
            
            # Add metadata
            result['sent_at'] = datetime.utcnow().isoformat()
            result['to_email'] = to_email
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def _send_via_smtp(self, to_email: str, subject: str, body: str, from_email: Optional[str] = None, from_name: Optional[str] = None) -> Dict:
        """Send email using SMTP."""
        from_email = from_email or self.smtp_config.get('from_email')
        from_name = from_name or self.smtp_config.get('from_name', 'Rendline')
        
        if not from_email:
            return {'success': False, 'method': 'smtp', 'error': 'FROM_EMAIL not configured'}
            
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = to_email
        
        msg.attach(MIMEText(body, 'html'))
        
        try:
            with smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['smtp_port']) as server:
                if self.smtp_config.get('use_tls', True):
                    server.starttls()
                
                if self.smtp_config.get('username') and self.smtp_config.get('password'):
                    server.login(self.smtp_config['username'], self.smtp_config['password'])
                
                server.send_message(msg)
                
            logger.info(f"Email sent successfully to {to_email}")
            return {
                'success': True,
                'method': 'smtp',
                'message': 'Email sent successfully via SMTP'
            }
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication error: {str(e)}")
            return {
                'success': False,
                'method': 'smtp',
                'error': 'SMTP Authentication failed - check username/password'
            }
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"SMTP Recipients refused: {str(e)}")
            return {
                'success': False,
                'method': 'smtp',
                'error': f'Recipient {to_email} was refused by server'
            }
        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            return {
                'success': False,
                'method': 'smtp',
                'error': str(e)
            }
    
    def _send_via_sendgrid(self, to_email: str, subject: str, body: str, from_email: Optional[str] = None, from_name: Optional[str] = None) -> Dict:
        """Send email using SendGrid API."""
        try:
            if not self.sendgrid_api_key:
                return {'success': False, 'method': 'sendgrid', 'error': 'SendGrid API key not configured'}

            from_email = from_email or os.getenv('FROM_EMAIL')
            from_name = from_name or os.getenv('FROM_NAME', 'Rendline')

            message = Mail(
                from_email=Email(from_email, from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=body
            )
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)

            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Email sent successfully to {to_email} via SendGrid")
                return {
                    'success': True,
                    'method': 'sendgrid',
                    'message': 'Email sent successfully via SendGrid'
                }
            else:
                error_details = response.body.decode('utf-8') if response.body else 'Unknown error'
                logger.error(f"SendGrid error ({response.status_code}): {error_details}")
                return {
                    'success': False,
                    'method': 'sendgrid',
                    'error': f'SendGrid API failed with status code {response.status_code}',
                    'details': error_details
                }
        except Exception as e:
            logger.error(f"SendGrid error: {str(e)}")
            return {
                'success': False,
                'method': 'sendgrid',
                'error': str(e)
            }