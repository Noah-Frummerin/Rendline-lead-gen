import requests
import json
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LeadDiscoveryService:
    """
    Service for discovering potential leads based on various triggers:
    1. Companies hiring for marketing/sales roles
    2. Recently funded startups
    3. Companies with outdated websites/tech stacks
    """
    
    def __init__(self, apollo_api_key: Optional[str] = None, builtwith_api_key: Optional[str] = None):
        self.apollo_api_key = apollo_api_key
        self.builtwith_api_key = builtwith_api_key
        self.apollo_base_url = "https://api.apollo.io/v1"
        self.builtwith_base_url = "https://api.builtwith.com"
        
    def find_companies_hiring_marketers(self, limit: int = 50) -> List[Dict]:
        """
        Find companies that are currently hiring marketing/sales professionals.
        This indicates they're investing in growth and may need a new website.
        """
        companies = []
        
        # Marketing job titles that indicate growth investment
        marketing_titles = [
            "Marketing Manager",
            "Head of Marketing", 
            "VP Marketing",
            "Growth Manager",
            "Digital Marketing Manager",
            "Marketing Director",
            "Head of Growth",
            "VP Growth"
        ]
        
        for title in marketing_titles[:3]:  # Limit to avoid rate limits
            try:
                # Simulate Apollo API call (replace with actual API when keys are available)
                companies_batch = self._mock_apollo_hiring_search(title, limit // len(marketing_titles))
                companies.extend(companies_batch)
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Error searching for {title}: {str(e)}")
                
        return companies[:limit]
    
    def find_recently_funded_companies(self, days_back: int = 30, limit: int = 50) -> List[Dict]:
        """
        Find companies that received funding in the last N days.
        These companies have budget and need to upgrade their online presence.
        """
        companies = []
        
        try:
            # Simulate funding data search (replace with actual Crunchbase API)
            companies = self._mock_funding_search(days_back, limit)
        except Exception as e:
            logger.error(f"Error searching for funded companies: {str(e)}")
            
        return companies
    
    def find_companies_with_outdated_tech(self, limit: int = 50) -> List[Dict]:
        """
        Find companies using outdated web technologies that indicate
        they need a website refresh.
        """
        companies = []
        
        # Technologies that indicate an outdated website
        outdated_techs = [
            "jQuery 1.x",  # Very old jQuery versions
            "Flash",       # Deprecated technology
            "Internet Explorer",  # IE-specific code
            "Bootstrap 2", # Very old Bootstrap
        ]
        
        try:
            # Simulate BuiltWith API search
            for tech in outdated_techs[:2]:  # Limit searches
                companies_batch = self._mock_builtwith_search(tech, limit // len(outdated_techs))
                companies.extend(companies_batch)
                time.sleep(1)
        except Exception as e:
            logger.error(f"Error searching for outdated tech: {str(e)}")
            
        return companies[:limit]
    
    def find_decision_makers(self, company_domain: str, company_size: int) -> List[Dict]:
        """
        Find decision-makers at a company based on company size and domain.
        """
        contacts = []
        
        # Determine target titles based on company size
        if company_size <= 50:
            target_titles = ["Founder", "CEO", "Co-Founder", "Owner"]
        elif company_size <= 200:
            target_titles = ["Head of Marketing", "Marketing Director", "VP Marketing", "Founder", "CEO"]
        else:
            target_titles = ["Head of Marketing", "Marketing Director", "VP Marketing", "Chief Marketing Officer"]
            
        try:
            # Simulate Apollo contact search
            contacts = self._mock_apollo_contact_search(company_domain, target_titles)
        except Exception as e:
            logger.error(f"Error finding contacts for {company_domain}: {str(e)}")
            
        return contacts
    
    def _mock_apollo_hiring_search(self, job_title: str, limit: int) -> List[Dict]:
        """
        Mock Apollo API search for companies hiring specific roles.
        Replace with actual Apollo API calls when API key is available.
        """
        # Simulate realistic company data
        mock_companies = [
            {
                "name": f"TechCorp Solutions",
                "domain": "techcorp-solutions.com",
                "industry": "Software",
                "employee_count": 75,
                "trigger_type": "hiring",
                "trigger_details": f"Currently hiring: {job_title}",
                "website_url": "https://techcorp-solutions.com"
            },
            {
                "name": f"GrowthStart Inc",
                "domain": "growthstart.io",
                "industry": "SaaS",
                "employee_count": 25,
                "trigger_type": "hiring", 
                "trigger_details": f"Currently hiring: {job_title}",
                "website_url": "https://growthstart.io"
            },
            {
                "name": f"ScaleUp Ventures",
                "domain": "scaleup-ventures.com",
                "industry": "E-commerce",
                "employee_count": 150,
                "trigger_type": "hiring",
                "trigger_details": f"Currently hiring: {job_title}",
                "website_url": "https://scaleup-ventures.com"
            }
        ]
        
        return mock_companies[:limit]
    
    def _mock_funding_search(self, days_back: int, limit: int) -> List[Dict]:
        """
        Mock funding data search. Replace with actual Crunchbase API.
        """
        mock_companies = [
            {
                "name": "FundedStartup AI",
                "domain": "fundedstartup.ai",
                "industry": "Artificial Intelligence",
                "employee_count": 35,
                "funding_stage": "Series A",
                "recent_funding_amount": 5000000,
                "recent_funding_date": (datetime.now() - timedelta(days=15)).date(),
                "trigger_type": "funding",
                "trigger_details": "Raised $5M Series A 15 days ago"
            },
            {
                "name": "NextGen Robotics",
                "domain": "nextgen-robotics.com", 
                "industry": "Robotics",
                "employee_count": 60,
                "funding_stage": "Seed",
                "recent_funding_amount": 2000000,
                "recent_funding_date": (datetime.now() - timedelta(days=8)).date(),
                "trigger_type": "funding",
                "trigger_details": "Raised $2M Seed round 8 days ago"
            }
        ]
        
        return mock_companies[:limit]
    
    def _mock_builtwith_search(self, technology: str, limit: int) -> List[Dict]:
        """
        Mock BuiltWith API search. Replace with actual BuiltWith API.
        """
        mock_companies = [
            {
                "name": "LegacyTech Corp",
                "domain": "legacytech.com",
                "industry": "Manufacturing",
                "employee_count": 200,
                "website_technologies": json.dumps([technology, "Apache", "PHP"]),
                "trigger_type": "outdated_tech",
                "trigger_details": f"Website uses outdated technology: {technology}"
            },
            {
                "name": "OldSchool Industries",
                "domain": "oldschool-industries.net",
                "industry": "Consulting", 
                "employee_count": 80,
                "website_technologies": json.dumps([technology, "IIS", "ASP.NET"]),
                "trigger_type": "outdated_tech",
                "trigger_details": f"Website uses outdated technology: {technology}"
            }
        ]
        
        return mock_companies[:limit]
    
    def _mock_apollo_contact_search(self, domain: str, titles: List[str]) -> List[Dict]:
        """
        Mock Apollo contact search. Replace with actual Apollo API.
        """
        mock_contacts = [
            {
                "first_name": "Sarah",
                "last_name": "Johnson",
                "email": f"sarah.johnson@{domain}",
                "job_title": titles[0] if titles else "Marketing Director",
                "linkedin_url": f"https://linkedin.com/in/sarah-johnson-{domain.split('.')[0]}"
            },
            {
                "first_name": "Mike",
                "last_name": "Chen", 
                "email": f"mike.chen@{domain}",
                "job_title": titles[1] if len(titles) > 1 else "Head of Growth",
                "linkedin_url": f"https://linkedin.com/in/mike-chen-{domain.split('.')[0]}"
            }
        ]
        
        return mock_contacts[:2]  # Limit to avoid overwhelming
    
    def calculate_decision_maker_score(self, job_title: str, company_size: int) -> float:
        """
        Calculate a score (0-1) for how likely someone is to be a decision-maker
        for website redesign projects based on their title and company size.
        """
        title_lower = job_title.lower()
        
        # High-priority titles
        if any(keyword in title_lower for keyword in ['ceo', 'founder', 'owner', 'president']):
            if company_size <= 50:
                return 0.95
            elif company_size <= 200:
                return 0.75
            else:
                return 0.4  # CEOs of large companies rarely make website decisions
                
        # Marketing leadership titles
        if any(keyword in title_lower for keyword in ['head of marketing', 'marketing director', 'vp marketing', 'cmo']):
            return 0.9
            
        # Growth/digital titles
        if any(keyword in title_lower for keyword in ['head of growth', 'growth director', 'digital marketing']):
            return 0.85
            
        # General marketing titles
        if 'marketing manager' in title_lower:
            if company_size <= 100:
                return 0.7
            else:
                return 0.5
                
        # Sales leadership (sometimes involved in website decisions)
        if any(keyword in title_lower for keyword in ['head of sales', 'sales director', 'vp sales']):
            return 0.6
            
        # Default for other titles
        return 0.2

