import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailSenderService:
    """
    Service for sending emails using SMTP or email service APIs.
    Includes rate limiting, queue management, and delivery tracking.
    """
    
    def __init__(self, smtp_config: Optional[Dict] = None, sendgrid_api_key: Optional[str] = None):
        self.smtp_config = smtp_config or self._get_default_smtp_config()
        self.sendgrid_api_key = sendgrid_api_key
        self.rate_limit_delay = 2  # seconds between emails
        self.max_retries = 3
        
    def send_email(self, to_email: str, subject: str, body: str, from_email: Optional[str] = None, from_name: Optional[str] = None) -> Dict:
        """
        Send a single email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (can be HTML or plain text)
            from_email: Sender email (optional, uses config default)
            from_name: Sender name (optional)
        
        Returns:
            Dict with success status and details
        """
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
        """
        Send multiple emails with rate limiting.
        
        Args:
            email_data_list: List of dicts with email data (to_email, subject, body, etc.)
            delay_between_emails: Seconds to wait between emails (optional)
        
        Returns:
            List of send results
        """
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
        """
        Send email using SMTP.
        """
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
                
            return {
                'success': True,
                'method': 'smtp',
                'message': 'Email sent successfully via SMTP'
            }
            
        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            return {
                'success': False,
                'method': 'smtp',
                'error': str(e)
            }
    
    def _send_via_sendgrid(self, to_email: str, subject: str, body: str, from_email: Optional[str] = None, from_name: Optional[str] = None) -> Dict:
        """
        Send email using SendGrid API.
        """
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail
            
            from_email = from_email or self.smtp_config['from_email']
            from_name = from_name or self.smtp_config.get('from_name', '')
            
            # Create SendGrid client
            sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
            
            # Create message
            message = Mail(
                from_email=(from_email, from_name) if from_name else from_email,
                to_emails=to_email,
                subject=subject,
                html_content=body if '<' in body and '>' in body else None,
                plain_text_content=body if not ('<' in body and '>' in body) else None
            )
            
            # Send email
            response = sg.send(message)
            
            return {
                'success': True,
                'method': 'sendgrid',
                'message': 'Email sent successfully via SendGrid',
                'status_code': response.status_code
            }
            
        except ImportError:
            logger.warning("SendGrid library not installed, falling back to SMTP")
            return self._send_via_smtp(to_email, subject, body, from_email, from_name)
        except Exception as e:
            logger.error(f"SendGrid error: {str(e)}")
            return {
                'success': False,
                'method': 'sendgrid',
                'error': str(e)
            }
    
    def _get_default_smtp_config(self) -> Dict:
        """
        Get default SMTP configuration.
        In production, these should come from environment variables.
        """
        return {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'use_tls': True,
            'username': '',  # Set via environment variable
            'password': '',  # Set via environment variable or app password
            'from_email': 'your-email@gmail.com',  # Set via environment variable
            'from_name': 'Website Design Specialist'
        }
    
    def test_connection(self) -> Dict:
        """
        Test email service connection.
        """
        try:
            if self.sendgrid_api_key:
                # Test SendGrid connection
                import sendgrid
                sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
                # SendGrid doesn't have a simple connection test, so we'll just validate the key format
                if len(self.sendgrid_api_key) > 20:
                    return {'success': True, 'method': 'sendgrid', 'message': 'SendGrid API key appears valid'}
                else:
                    return {'success': False, 'method': 'sendgrid', 'error': 'Invalid SendGrid API key format'}
            else:
                # Test SMTP connection
                with smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['smtp_port']) as server:
                    if self.smtp_config.get('use_tls', True):
                        server.starttls()
                    
                    if self.smtp_config.get('username') and self.smtp_config.get('password'):
                        server.login(self.smtp_config['username'], self.smtp_config['password'])
                    
                    return {'success': True, 'method': 'smtp', 'message': 'SMTP connection successful'}
                    
        except ImportError as e:
            return {'success': False, 'error': f'Missing dependency: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_email_queue(self, contacts_data: List[Dict], email_template_data: List[Dict]) -> List[Dict]:
        """
        Create a queue of emails ready to be sent.
        
        Args:
            contacts_data: List of contact information
            email_template_data: List of generated email content
        
        Returns:
            List of email queue items
        """
        email_queue = []
        
        for i, (contact, email_data) in enumerate(zip(contacts_data, email_template_data)):
            queue_item = {
                'queue_id': f"email_{i}_{int(time.time())}",
                'contact_id': contact.get('id'),
                'company_id': contact.get('company_id'),
                'to_email': contact['email'],
                'subject': email_data['subject'],
                'body': email_data['body'],
                'from_email': self.smtp_config['from_email'],
                'from_name': self.smtp_config.get('from_name'),
                'template_type': email_data.get('template_type'),
                'personalization_score': email_data.get('personalization_score', 0.0),
                'created_at': datetime.utcnow().isoformat(),
                'status': 'queued'
            }
            
            email_queue.append(queue_item)
        
        return email_queue
    
    def send_queued_emails(self, email_queue: List[Dict], max_emails: Optional[int] = None) -> Dict:
        """
        Send emails from a queue with proper rate limiting and error handling.
        
        Args:
            email_queue: List of queued email items
            max_emails: Maximum number of emails to send (optional)
        
        Returns:
            Summary of sending results
        """
        if max_emails:
            email_queue = email_queue[:max_emails]
        
        results = self.send_email_batch(email_queue)
        
        # Calculate summary statistics
        successful = len([r for r in results if r.get('success', False)])
        failed = len(results) - successful
        
        return {
            'total_queued': len(email_queue),
            'successful_sends': successful,
            'failed_sends': failed,
            'success_rate': successful / len(results) if results else 0,
            'results': results
        }

