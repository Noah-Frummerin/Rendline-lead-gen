import re
from typing import Dict, List, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailGeneratorService:
    """
    Service for generating personalized cold emails based on company triggers
    and contact information. Uses templates and dynamic content insertion.
    """
    
    def __init__(self):
        self.email_templates = self._load_email_templates()
        self.subject_templates = self._load_subject_templates()
    
    def generate_email(self, contact_data: Dict, company_data: Dict, template_type: Optional[str] = None) -> Dict:
        """
        Generate a personalized email for a specific contact and company.
        
        Args:
            contact_data: Contact information (name, title, etc.)
            company_data: Company information (name, trigger, etc.)
            template_type: Specific template to use (optional)
        
        Returns:
            Dict with subject, body, and metadata
        """
        try:
            # Determine template type based on company trigger if not specified
            if not template_type:
                template_type = company_data.get('trigger_type', 'general')
            
            # Get appropriate templates
            email_template = self.email_templates.get(template_type, self.email_templates['general'])
            subject_template = self.subject_templates.get(template_type, self.subject_templates['general'])
            
            # Prepare variables for template substitution
            template_vars = self._prepare_template_variables(contact_data, company_data)
            
            # Generate subject and body
            subject = self._substitute_template_variables(subject_template, template_vars)
            body = self._substitute_template_variables(email_template, template_vars)
            
            # Clean up the generated content
            subject = self._clean_text(subject)
            body = self._clean_text(body)
            
            return {
                'subject': subject,
                'body': body,
                'template_type': template_type,
                'personalization_score': self._calculate_personalization_score(template_vars),
                'generated_at': datetime.utcnow().isoformat(),
                'template_variables': template_vars
            }
            
        except Exception as e:
            logger.error(f"Error generating email: {str(e)}")
            return {
                'subject': f"Website Redesign Opportunity for {company_data.get('name', 'Your Company')}",
                'body': self._get_fallback_email(contact_data, company_data),
                'template_type': 'fallback',
                'error': str(e)
            }
    
    def generate_email_batch(self, contacts_companies: List[Dict]) -> List[Dict]:
        """
        Generate emails for multiple contact-company pairs.
        
        Args:
            contacts_companies: List of dicts with 'contact' and 'company' keys
        
        Returns:
            List of generated email data
        """
        results = []
        
        for item in contacts_companies:
            contact_data = item.get('contact', {})
            company_data = item.get('company', {})
            
            email_data = self.generate_email(contact_data, company_data)
            email_data['contact_id'] = contact_data.get('id')
            email_data['company_id'] = company_data.get('id')
            
            results.append(email_data)
        
        return results
    
    def _load_email_templates(self) -> Dict[str, str]:
        """
        Load email templates for different trigger types.
        """
        return {
            'hiring': """Hi {first_name},

I noticed {company_name} is currently hiring for a {hiring_role} - congratulations on the growth! 

As you bring on new {hiring_department} talent, having a high-converting website becomes even more critical for empowering your team to drive results. I took a quick look at {company_domain} and noticed {website_observation}.

I specialize in building websites for growing {industry} companies that need to convert their marketing investment into measurable results. My recent client in {industry} saw a 40% increase in qualified leads within 60 days of their new website launch.

Would a 10-minute conversation about how a strategic website redesign could support your {hiring_department} goals be valuable? I can share some quick wins that could be implemented even before your new hire starts.

Best regards,
[Your Name]
Website Design Specialist

P.S. I'd be happy to send over a free 5-minute audit video showing specific opportunities I spotted on {company_domain} - no strings attached.""",

            'funding': """Hi {first_name},

Congratulations on {company_name}'s recent {funding_stage} round! {funding_details}

As you scale with this new investment, your website becomes a critical asset for converting that funding into market leadership. I specialize in helping funded {industry} companies build websites that attract top talent, convert enterprise customers, and establish market authority.

I took a quick look at {company_domain} and see some immediate opportunities to better reflect {company_name}'s growth trajectory and funding success.

My recent client, a Series A {industry} startup, saw their enterprise demo requests increase by 65% after we redesigned their site to better communicate their funded status and growth potential.

Would a brief conversation about aligning your website with your post-funding growth goals be valuable? I can share some specific strategies that have worked well for other funded companies in {industry}.

Best regards,
[Your Name]
Website Design Specialist for Growing Companies

P.S. Happy to send a quick audit showing how to better leverage your funding announcement on your website.""",

            'outdated_tech': """Hi {first_name},

I was researching {industry} companies and came across {company_name}. Your {business_focus} looks impressive!

I noticed {company_domain} is using some older web technologies that might be limiting your site's performance and search visibility. {tech_observation}

In today's competitive {industry} landscape, website performance directly impacts lead generation and customer trust. I recently helped a similar {industry} company modernize their site, resulting in 50% faster load times and a 35% increase in contact form submissions.

Would a 15-minute conversation about modernizing {company_name}'s web presence be valuable? I can share some quick technical wins that could improve your site's performance immediately.

Best regards,
[Your Name]
Website Performance Specialist

P.S. I'd be happy to run a free technical audit of {company_domain} and send you a summary of the biggest opportunities - takes me 10 minutes, could save you hours of research.""",

            'general': """Hi {first_name},

I came across {company_name} while researching innovative {industry} companies and was impressed by {company_focus}.

I specialize in building high-converting websites for {industry} companies that are serious about growth. My clients typically see 40-60% increases in qualified leads within 90 days of launch.

I took a quick look at {company_domain} and noticed some opportunities to better showcase {company_name}'s expertise and convert more visitors into customers.

Would a brief conversation about how a strategic website redesign could support {company_name}'s growth goals be valuable?

Best regards,
[Your Name]
Website Design Specialist

P.S. Happy to send over a free audit of {company_domain} showing the biggest opportunities I spotted."""
        }
    
    def _load_subject_templates(self) -> Dict[str, str]:
        """
        Load subject line templates for different trigger types.
        """
        return {
            'hiring': "Website support for {company_name}'s new {hiring_role}?",
            'funding': "Congrats on the {funding_stage} - website alignment opportunity",
            'outdated_tech': "Quick website performance opportunity for {company_name}",
            'general': "Website optimization opportunity for {company_name}"
        }
    
    def _prepare_template_variables(self, contact_data: Dict, company_data: Dict) -> Dict:
        """
        Prepare variables for template substitution based on contact and company data.
        """
        variables = {
            # Contact variables
            'first_name': contact_data.get('first_name', 'there'),
            'last_name': contact_data.get('last_name', ''),
            'full_name': f"{contact_data.get('first_name', '')} {contact_data.get('last_name', '')}".strip(),
            'job_title': contact_data.get('job_title', 'team member'),
            
            # Company variables
            'company_name': company_data.get('name', 'your company'),
            'company_domain': company_data.get('domain', 'your website'),
            'industry': company_data.get('industry', 'your industry'),
            'employee_count': company_data.get('employee_count', 50),
            
            # Trigger-specific variables
            'trigger_type': company_data.get('trigger_type', 'general'),
            'trigger_details': company_data.get('trigger_details', ''),
        }
        
        # Add trigger-specific variables
        trigger_type = company_data.get('trigger_type', 'general')
        
        if trigger_type == 'hiring':
            variables.update(self._extract_hiring_variables(company_data))
        elif trigger_type == 'funding':
            variables.update(self._extract_funding_variables(company_data))
        elif trigger_type == 'outdated_tech':
            variables.update(self._extract_tech_variables(company_data))
        
        # Add personalization variables
        variables.update(self._generate_personalization_variables(variables))
        
        return variables
    
    def _extract_hiring_variables(self, company_data: Dict) -> Dict:
        """
        Extract hiring-specific variables from trigger details.
        """
        trigger_details = company_data.get('trigger_details', '')
        
        # Try to extract role from trigger details
        hiring_role = 'Marketing Manager'  # Default
        if 'hiring:' in trigger_details.lower():
            role_match = re.search(r'hiring:\s*(.+)', trigger_details, re.IGNORECASE)
            if role_match:
                hiring_role = role_match.group(1).strip()
        
        # Determine department based on role
        role_lower = hiring_role.lower()
        if any(word in role_lower for word in ['marketing', 'growth', 'digital']):
            department = 'marketing'
        elif any(word in role_lower for word in ['sales', 'business development', 'account']):
            department = 'sales'
        else:
            department = 'team'
        
        return {
            'hiring_role': hiring_role,
            'hiring_department': department
        }
    
    def _extract_funding_variables(self, company_data: Dict) -> Dict:
        """
        Extract funding-specific variables.
        """
        funding_stage = company_data.get('funding_stage', 'funding')
        funding_amount = company_data.get('recent_funding_amount')
        
        funding_details = ''
        if funding_amount:
            if funding_amount >= 1000000:
                amount_str = f"${funding_amount/1000000:.1f}M"
            else:
                amount_str = f"${funding_amount/1000:.0f}K"
            funding_details = f"Raising {amount_str} is a significant milestone!"
        
        return {
            'funding_stage': funding_stage,
            'funding_details': funding_details
        }
    
    def _extract_tech_variables(self, company_data: Dict) -> Dict:
        """
        Extract technology-specific variables.
        """
        trigger_details = company_data.get('trigger_details', '')
        
        # Extract specific technology mentioned
        tech_observation = "some outdated technologies that could be modernized"
        if 'technology:' in trigger_details.lower():
            tech_match = re.search(r'technology:\s*(.+)', trigger_details, re.IGNORECASE)
            if tech_match:
                tech = tech_match.group(1).strip()
                tech_observation = f"it's using {tech}, which could be limiting performance"
        
        return {
            'tech_observation': tech_observation
        }
    
    def _generate_personalization_variables(self, variables: Dict) -> Dict:
        """
        Generate additional personalization variables based on existing data.
        """
        company_name = variables.get('company_name', '')
        industry = variables.get('industry', '')
        
        # Generate business focus based on company name and industry
        business_focus = f"work in {industry}" if industry else "business"
        if any(word in company_name.lower() for word in ['tech', 'software', 'app']):
            business_focus = "technology solutions"
        elif any(word in company_name.lower() for word in ['consulting', 'services']):
            business_focus = "consulting services"
        
        # Generate website observation
        website_observation = "some opportunities to improve conversion rates"
        if variables.get('employee_count', 0) > 100:
            website_observation = "it could better reflect your company's scale and expertise"
        
        # Generate company focus
        company_focus = f"your approach to {industry}" if industry else "your business model"
        
        return {
            'business_focus': business_focus,
            'website_observation': website_observation,
            'company_focus': company_focus
        }
    
    def _substitute_template_variables(self, template: str, variables: Dict) -> str:
        """
        Substitute template variables in the given template string.
        """
        result = template
        
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """
        Clean up generated text by removing extra whitespace and formatting issues.
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([,.!?])', r'\1', text)
        
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()
    
    def _calculate_personalization_score(self, variables: Dict) -> float:
        """
        Calculate a score (0-1) indicating how personalized the email is.
        """
        score = 0.0
        
        # Base score for having basic info
        if variables.get('first_name') and variables.get('first_name') != 'there':
            score += 0.2
        
        if variables.get('company_name') and variables.get('company_name') != 'your company':
            score += 0.2
        
        # Bonus for specific trigger information
        if variables.get('trigger_type') != 'general':
            score += 0.3
        
        # Bonus for industry information
        if variables.get('industry') and variables.get('industry') != 'your industry':
            score += 0.2
        
        # Bonus for specific details
        if variables.get('hiring_role') or variables.get('funding_details') or variables.get('tech_observation'):
            score += 0.1
        
        return min(1.0, score)
    
    def _get_fallback_email(self, contact_data: Dict, company_data: Dict) -> str:
        """
        Generate a simple fallback email when template processing fails.
        """
        first_name = contact_data.get('first_name', 'there')
        company_name = company_data.get('name', 'your company')
        
        return f"""Hi {first_name},

I came across {company_name} and was impressed by your work.

I specialize in building high-converting websites for growing companies. My clients typically see significant increases in qualified leads within 90 days of launch.

Would a brief conversation about how a strategic website redesign could support {company_name}'s growth goals be valuable?

Best regards,
[Your Name]
Website Design Specialist"""

