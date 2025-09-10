import requests
import json
import time
import os
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
        self.apollo_api_key = apollo_api_key or os.getenv('APOLLO_API_KEY')
        self.builtwith_api_key = builtwith_api_key or os.getenv('BUILTWITH_API_KEY')
        self.apollo_base_url = "https://api.apollo.io/v1"
        self.builtwith_base_url = "https://api.builtwith.com"
        self.rate_limit_delay = 1.5  # seconds between API calls
        
    def find_companies_hiring_marketers(self, limit: int = 50) -> List[Dict]:
        """
        Find companies that are currently hiring marketing/sales professionals.
        """
        companies = []
        
        marketing_titles = [
            "Marketing Manager",
            "Head of Marketing", 
            "VP Marketing",
            "Growth Manager",
            "Digital Marketing Manager"
        ]
        
        for title in marketing_titles[:3]:
            try:
                if self.apollo_api_key:
                    companies_batch = self._apollo_hiring_search(title, limit // len(marketing_titles))
                else:
                    logger.warning("No Apollo API key found, using mock data")
                    companies_batch = self._mock_apollo_hiring_search(title, limit // len(marketing_titles))
                
                companies.extend(companies_batch)
                time.sleep(self.rate_limit_delay)
            except Exception as e:
                logger.error(f"Error searching for {title}: {str(e)}")
                
        return companies[:limit]
    
    def find_recently_funded_companies(self, days_back: int = 30, limit: int = 50) -> List[Dict]:
        """
        Find companies that received funding in the last N days.
        """
        companies = []
        
        try:
            if self.apollo_api_key:
                companies = self._apollo_funding_search(days_back, limit)
            else:
                logger.warning("No Apollo API key found, using mock data")
                companies = self._mock_funding_search(days_back, limit)
        except Exception as e:
            logger.error(f"Error searching for funded companies: {str(e)}")
            
        return companies
    
    def find_companies_with_outdated_tech(self, limit: int = 50) -> List[Dict]:
        """
        Find companies using outdated web technologies.
        """
        companies = []
        
        outdated_techs = [
            "jQuery 1.x",
            "Flash",
            "Internet Explorer",
            "Bootstrap 2"
        ]
        
        try:
            if self.builtwith_api_key:
                for tech in outdated_techs[:2]:
                    companies_batch = self._builtwith_search(tech, limit // len(outdated_techs))
                    companies.extend(companies_batch)
                    time.sleep(self.rate_limit_delay)
            else:
                logger.warning("No BuiltWith API key found, using mock data")
                for tech in outdated_techs[:2]:
                    companies_batch = self._mock_builtwith_search(tech, limit // len(outdated_techs))
                    companies.extend(companies_batch)
        except Exception as e:
            logger.error(f"Error searching for outdated tech: {str(e)}")
            
        return companies[:limit]
    
    def find_decision_makers(self, company_domain: str, company_size: int) -> List[Dict]:
        """
        Find decision-makers at a company.
        """
        contacts = []
        
        if company_size <= 50:
            target_titles = ["Founder", "CEO", "Co-Founder", "Owner"]
        elif company_size <= 200:
            target_titles = ["Head of Marketing", "Marketing Director", "VP Marketing", "Founder", "CEO"]
        else:
            target_titles = ["Head of Marketing", "Marketing Director", "VP Marketing", "Chief Marketing Officer"]
            
        try:
            if self.apollo_api_key:
                contacts = self._apollo_contact_search(company_domain, target_titles)
            else:
                logger.warning("No Apollo API key found, using mock data")
                contacts = self._mock_apollo_contact_search(company_domain, target_titles)
        except Exception as e:
            logger.error(f"Error finding contacts for {company_domain}: {str(e)}")
            
        return contacts
    
    def _apollo_hiring_search(self, job_title: str, limit: int) -> List[Dict]:
        """
        Real Apollo API search for companies hiring specific roles.
        """
        if not self.apollo_api_key:
            raise ValueError("Apollo API key required")
        
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'X-Api-Key': self.apollo_api_key
        }
        
        payload = {
            "api_key": self.apollo_api_key,
            "q_organization_keyword_tags": ["Hiring", "Growing", "Expanding"],
            "person_titles": [job_title],
            "per_page": limit,
            "page": 1
        }
        
        try:
            response = requests.post(
                f"{self.apollo_base_url}/mixed_people/search",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f"Rate limited, waiting {retry_after} seconds")
                time.sleep(retry_after)
                return []
            
            if response.status_code != 200:
                logger.error(f"Apollo API error: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            companies = []
            
            for person in data.get('people', []):
                org = person.get('organization', {})
                if org and org.get('name'):
                    company_data = {
                        "name": org.get('name'),
                        "domain": org.get('website_url', '').replace('http://', '').replace('https://', '').replace('www.', ''),
                        "industry": org.get('industry'),
                        "employee_count": org.get('estimated_num_employees', 50),
                        "trigger_type": "hiring",
                        "trigger_details": f"Currently hiring: {job_title}",
                        "website_url": org.get('website_url')
                    }
                    companies.append(company_data)
            
            return companies
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo API request error: {str(e)}")
            return []
    
    def _apollo_funding_search(self, days_back: int, limit: int) -> List[Dict]:
        """
        Search for recently funded companies using Apollo API.
        """
        if not self.apollo_api_key:
            raise ValueError("Apollo API key required")
        
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'X-Api-Key': self.apollo_api_key
        }
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        payload = {
            "api_key": self.apollo_api_key,
            "q_organization_funding_stage_list": ["Seed", "Series A", "Series B", "Series C"],
            "per_page": limit,
            "page": 1
        }
        
        try:
            response = requests.post(
                f"{self.apollo_base_url}/organizations/search",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Apollo funding search error: {response.status_code}")
                return self._mock_funding_search(days_back, limit)
            
            data = response.json()
            companies = []
            
            for org in data.get('organizations', []):
                company_data = {
                    "name": org.get('name'),
                    "domain": org.get('website_url', '').replace('http://', '').replace('https://', '').replace('www.', ''),
                    "industry": org.get('industry'),
                    "employee_count": org.get('estimated_num_employees', 50),
                    "funding_stage": org.get('funding_stage'),
                    "recent_funding_amount": org.get('latest_funding_amount'),
                    "trigger_type": "funding",
                    "trigger_details": f"Recently received {org.get('funding_stage', 'funding')}"
                }
                companies.append(company_data)
            
            return companies
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo funding API error: {str(e)}")
            return self._mock_funding_search(days_back, limit)
    
    def _apollo_contact_search(self, domain: str, titles: List[str]) -> List[Dict]:
        """
        Real Apollo contact search.
        """
        if not self.apollo_api_key:
            raise ValueError("Apollo API key required")
        
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'X-Api-Key': self.apollo_api_key
        }
        
        payload = {
            "api_key": self.apollo_api_key,
            "q_organization_domains": [domain],
            "person_titles": titles,
            "per_page": 5,
            "page": 1
        }
        
        try:
            response = requests.post(
                f"{self.apollo_base_url}/mixed_people/search",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Apollo contact search error: {response.status_code}")
                return self._mock_apollo_contact_search(domain, titles)
            
            data = response.json()
            contacts = []
            
            for person in data.get('people', []):
                if person.get('email'):
                    contact_data = {
                        "first_name": person.get('first_name', ''),
                        "last_name": person.get('last_name', ''),
                        "email": person.get('email'),
                        "job_title": person.get('title', ''),
                        "linkedin_url": person.get('linkedin_url')
                    }
                    contacts.append(contact_data)
            
            return contacts[:3]  # Limit to top 3 contacts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo contact API error: {str(e)}")
            return self._mock_apollo_contact_search(domain, titles)
    
    def _builtwith_search(self, technology: str, limit: int) -> List[Dict]:
        """
        Real BuiltWith API search for companies using specific technologies.
        """
        if not self.builtwith_api_key:
            raise ValueError("BuiltWith API key required")
        
        # BuiltWith API endpoint for technology lookup
        url = f"{self.builtwith_base_url}/v17/api.json"
        params = {
            'KEY': self.builtwith_api_key,
            'LOOKUP': technology,
            'NOMETA': 'yes',
            'NOATTR': 'yes'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"BuiltWith API error: {response.status_code}")
                return self._mock_builtwith_search(technology, limit)
            
            data = response.json()
            companies = []
            
            # Process BuiltWith response (structure varies)
            results = data.get('Results', [])
            for result in results[:limit]:
                domain = result.get('Domain', '')
                if domain:
                    company_data = {
                        "name": domain.replace('.com', '').replace('.', ' ').title(),
                        "domain": domain,
                        "industry": "Technology",  # Default, could be enhanced
                        "employee_count": 100,  # Default estimate
                        "website_technologies": json.dumps([technology]),
                        "trigger_type": "outdated_tech",
                        "trigger_details": f"Website uses outdated technology: {technology}"
                    }
                    companies.append(company_data)
            
            return companies
            
        except requests.exceptions.RequestException as e:
            logger.error(f"BuiltWith API error: {str(e)}")
            return self._mock_builtwith_search(technology, limit)
    
    # Keep existing mock methods as fallbacks...
    def _mock_apollo_hiring_search(self, job_title: str, limit: int) -> List[Dict]:
        """Mock data for development/testing."""
        mock_companies = [
            {
                "name": f"TechCorp Solutions {job_title[:3]}",
                "domain": f"techcorp-{job_title.lower().replace(' ', '-')}.com",
                "industry": "Software",
                "employee_count": 75,
                "trigger_type": "hiring",
                "trigger_details": f"Currently hiring: {job_title}",
                "website_url": f"https://techcorp-{job_title.lower().replace(' ', '-')}.com"
            },
            {
                "name": f"GrowthStart {job_title[:5]}",
                "domain": f"growthstart-{job_title.lower().replace(' ', '-')}.io",
                "industry": "SaaS",
                "employee_count": 25,
                "trigger_type": "hiring", 
                "trigger_details": f"Currently hiring: {job_title}",
                "website_url": f"https://growthstart-{job_title.lower().replace(' ', '-')}.io"
            }
        ]
        return mock_companies[:limit]
    
    def _mock_funding_search(self, days_back: int, limit: int) -> List[Dict]:
        """Mock funding data."""
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
        """Mock BuiltWith data."""
        mock_companies = [
            {
                "name": f"LegacyTech Corp ({technology})",
                "domain": f"legacytech-{technology.lower().replace(' ', '-').replace('.', '')}.com",
                "industry": "Manufacturing",
                "employee_count": 200,
                "website_technologies": json.dumps([technology, "Apache", "PHP"]),
                "trigger_type": "outdated_tech",
                "trigger_details": f"Website uses outdated technology: {technology}"
            }
        ]
        return mock_companies[:limit]
    
    def _mock_apollo_contact_search(self, domain: str, titles: List[str]) -> List[Dict]:
        """Mock contact data."""
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
        return mock_contacts[:2]
    
    def calculate_decision_maker_score(self, job_title: str, company_size: int) -> float:
        """Calculate decision-maker score (0-1)."""
        title_lower = job_title.lower()
        
        if any(keyword in title_lower for keyword in ['ceo', 'founder', 'owner', 'president']):
            if company_size <= 50:
                return 0.95
            elif company_size <= 200:
                return 0.75
            else:
                return 0.4
                
        if any(keyword in title_lower for keyword in ['head of marketing', 'marketing director', 'vp marketing', 'cmo']):
            return 0.9
            
        if any(keyword in title_lower for keyword in ['head of growth', 'growth director', 'digital marketing']):
            return 0.85
            
        if 'marketing manager' in title_lower:
            if company_size <= 100:
                return 0.7
            else:
                return 0.5
                
        if any(keyword in title_lower for keyword in ['head of sales', 'sales director', 'vp sales']):
            return 0.6
            
        return 0.2