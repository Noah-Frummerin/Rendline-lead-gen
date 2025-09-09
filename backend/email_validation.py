import requests
import re
import dns.resolver
import smtplib
import socket
from typing import Dict, List, Optional
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailValidationService:
    """
    Service for validating email addresses using multiple methods:
    1. Format validation (regex)
    2. Domain validation (DNS lookup)
    3. SMTP validation (basic connection test)
    4. Third-party API validation (when API keys available)
    """
    
    def __init__(self, zerobounce_api_key: Optional[str] = None, hunter_api_key: Optional[str] = None):
        self.zerobounce_api_key = zerobounce_api_key
        self.hunter_api_key = hunter_api_key
        self.zerobounce_url = "https://api.zerobounce.net/v2/validate"
        self.hunter_url = "https://api.hunter.io/v2/email-verifier"
        
    def validate_email(self, email: str) -> Dict:
        """
        Comprehensive email validation using multiple methods.
        Returns validation result with confidence score.
        """
        result = {
            'email': email,
            'is_valid': False,
            'confidence_score': 0.0,
            'validation_method': 'comprehensive',
            'details': {}
        }
        
        try:
            # Step 1: Format validation
            format_valid = self._validate_format(email)
            result['details']['format_valid'] = format_valid
            
            if not format_valid:
                result['validation_result'] = 'invalid_format'
                return result
            
            # Step 2: Domain validation
            domain_valid = self._validate_domain(email)
            result['details']['domain_valid'] = domain_valid
            
            if not domain_valid:
                result['validation_result'] = 'invalid_domain'
                return result
            
            # Step 3: SMTP validation (basic)
            smtp_result = self._validate_smtp(email)
            result['details']['smtp_result'] = smtp_result
            
            # Step 4: Third-party API validation (if available)
            api_result = None
            if self.zerobounce_api_key:
                api_result = self._validate_with_zerobounce(email)
            elif self.hunter_api_key:
                api_result = self._validate_with_hunter(email)
            
            if api_result:
                result['details']['api_result'] = api_result
                result['is_valid'] = api_result.get('is_valid', False)
                result['confidence_score'] = api_result.get('confidence_score', 0.0)
                result['validation_result'] = api_result.get('result', 'unknown')
            else:
                # Calculate confidence based on our own validation
                confidence = 0.0
                if format_valid:
                    confidence += 0.3
                if domain_valid:
                    confidence += 0.4
                if smtp_result.get('deliverable', False):
                    confidence += 0.3
                
                result['confidence_score'] = confidence
                result['is_valid'] = confidence >= 0.7
                result['validation_result'] = 'valid' if result['is_valid'] else 'risky'
            
        except Exception as e:
            logger.error(f"Error validating email {email}: {str(e)}")
            result['validation_result'] = 'error'
            result['details']['error'] = str(e)
        
        return result
    
    def validate_email_batch(self, emails: List[str]) -> List[Dict]:
        """
        Validate multiple emails in batch.
        """
        results = []
        for email in emails:
            result = self.validate_email(email)
            results.append(result)
        
        return results
    
    def _validate_format(self, email: str) -> bool:
        """
        Validate email format using regex.
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_domain(self, email: str) -> bool:
        """
        Validate email domain using DNS lookup.
        """
        try:
            domain = email.split('@')[1]
            
            # Check for MX record
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                return len(mx_records) > 0
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                # If no MX record, check for A record
                try:
                    a_records = dns.resolver.resolve(domain, 'A')
                    return len(a_records) > 0
                except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                    return False
                    
        except Exception as e:
            logger.error(f"Error validating domain for {email}: {str(e)}")
            return False
    
    def _validate_smtp(self, email: str) -> Dict:
        """
        Basic SMTP validation - check if server accepts the email.
        Note: This is a basic check and may not work with all servers.
        """
        result = {
            'deliverable': False,
            'smtp_response': None
        }
        
        try:
            domain = email.split('@')[1]
            
            # Get MX record
            mx_records = dns.resolver.resolve(domain, 'MX')
            mx_record = str(mx_records[0].exchange)
            
            # Connect to SMTP server
            server = smtplib.SMTP(timeout=10)
            server.connect(mx_record, 25)
            server.helo('example.com')
            server.mail('test@example.com')
            
            # Test the recipient
            code, message = server.rcpt(email)
            server.quit()
            
            result['smtp_response'] = f"{code}: {message.decode()}"
            result['deliverable'] = code == 250
            
        except Exception as e:
            logger.debug(f"SMTP validation failed for {email}: {str(e)}")
            result['smtp_response'] = str(e)
            # Don't mark as invalid just because SMTP test failed
            # Many servers block SMTP testing
            result['deliverable'] = None
        
        return result
    
    def _validate_with_zerobounce(self, email: str) -> Optional[Dict]:
        """
        Validate email using ZeroBounce API.
        """
        if not self.zerobounce_api_key:
            return None
            
        try:
            params = {
                'api_key': self.zerobounce_api_key,
                'email': email
            }
            
            response = requests.get(self.zerobounce_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'is_valid': data.get('status') == 'valid',
                    'confidence_score': 0.9 if data.get('status') == 'valid' else 0.1,
                    'result': data.get('status', 'unknown'),
                    'sub_result': data.get('sub_result'),
                    'provider': 'zerobounce'
                }
            else:
                logger.error(f"ZeroBounce API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling ZeroBounce API: {str(e)}")
            return None
    
    def _validate_with_hunter(self, email: str) -> Optional[Dict]:
        """
        Validate email using Hunter.io API.
        """
        if not self.hunter_api_key:
            return None
            
        try:
            params = {
                'email': email,
                'api_key': self.hunter_api_key
            }
            
            response = requests.get(self.hunter_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                email_data = data.get('data', {})
                
                result_mapping = {
                    'deliverable': 'valid',
                    'undeliverable': 'invalid',
                    'risky': 'risky',
                    'unknown': 'unknown'
                }
                
                hunter_result = email_data.get('result', 'unknown')
                confidence = email_data.get('score', 0) / 100.0  # Hunter uses 0-100 scale
                
                return {
                    'is_valid': hunter_result == 'deliverable',
                    'confidence_score': confidence,
                    'result': result_mapping.get(hunter_result, 'unknown'),
                    'provider': 'hunter'
                }
            else:
                logger.error(f"Hunter API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling Hunter API: {str(e)}")
            return None
    
    def get_email_reputation_score(self, email: str) -> float:
        """
        Calculate a reputation score for an email address based on various factors.
        """
        score = 0.5  # Base score
        
        try:
            domain = email.split('@')[1].lower()
            
            # Boost score for business domains
            business_domains = [
                'gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com',
                'company.com', 'corp.com', 'inc.com'
            ]
            
            # Penalize free email providers for B2B
            free_providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
            if domain in free_providers:
                score -= 0.2
            
            # Boost for corporate-looking domains
            if any(keyword in domain for keyword in ['corp', 'inc', 'llc', 'ltd', 'company']):
                score += 0.2
            
            # Penalize suspicious patterns
            if any(char in email for char in ['..', '++', '--']):
                score -= 0.3
            
            # Boost for professional-looking email patterns
            local_part = email.split('@')[0].lower()
            if '.' in local_part or '_' in local_part:  # firstname.lastname pattern
                score += 0.1
            
        except Exception as e:
            logger.error(f"Error calculating reputation score for {email}: {str(e)}")
        
        return max(0.0, min(1.0, score))  # Clamp between 0 and 1

