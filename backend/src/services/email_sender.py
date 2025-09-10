import smtplib
import time
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import logging
from datetime import datetime

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
            result['subject'] = subject
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'to_email': to_email,
                'subject': subject,
                'sent_at': datetime.utcnow().isoformat()
            }
    
    def send_email_batch(self, email_data_list: List[Dict], delay_between_emails: Optional[float] = None) -> List[Dict]:
        """Send multiple emails with rate limiting."""
        results = []
        delay = delay_between_emails or self.rate_limit_delay
        
        for i, email_data in enumerate(email_data_list):
            try:
                # Extract email parameters
                to_email = email_data['to_email']
                subject = email_data['subject']
                body = email_data['body']
                from_email = email_data.get('from_email')
                from_name = email_data.get('from_name')
                
                # Send email
                result = self.send_email(to_email, subject, body, from_email, from_name)
                
                # Add batch metadata
                result['batch_index'] = i
                result['contact_id'] = email_data.get('contact_id')
                result['company_id'] = email_data.get('company_id')
                
                results.append(result)
                
                # Rate limiting delay (except for last email)
                if i < len(email_data_list) - 1:
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error in batch email {i}: {str(e)}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'batch_index': i,
                    'contact_id': email_data.get('contact_id'),
                    'company_id': email_data.get('company_id')
                })
        
        return results
    
    def _send_via_smtp(self, to_email: str, subject: str, body: str, from_email: Optional[str] = None, from_name: Optional[str] = None) -> Dict:
        """Send email using SMTP."""
        from_email = from_email or self.smtp_config['from_email']
        from_name = from_name or self.smtp_config.get('from_name', '')
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name} <{from_email}>" if from_name else from_email
        msg['To'] = to_email
        
        # Add body (assume HTML if contains HTML tags, otherwise plain text)
        if '<' in body and '>' in body:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        # Send email
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
    
    def _send_via_sendgrid(self, to_email: str, subject: str, body: