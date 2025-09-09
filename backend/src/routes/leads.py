from flask import Blueprint, request, jsonify
from src.models.company import db, Company, Contact
from src.services.lead_discovery import LeadDiscoveryService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

leads_bp = Blueprint('leads', __name__)

# Initialize lead discovery service
lead_service = LeadDiscoveryService()

@leads_bp.route('/discover', methods=['POST'])
def discover_leads():
    """
    Discover new leads based on specified triggers.
    """
    try:
        data = request.get_json()
        trigger_types = data.get('trigger_types', ['hiring', 'funding', 'outdated_tech'])
        limit_per_type = data.get('limit_per_type', 20)
        
        all_companies = []
        
        # Discover companies based on different triggers
        if 'hiring' in trigger_types:
            logger.info("Discovering companies hiring marketers...")
            hiring_companies = lead_service.find_companies_hiring_marketers(limit_per_type)
            all_companies.extend(hiring_companies)
            
        if 'funding' in trigger_types:
            logger.info("Discovering recently funded companies...")
            funded_companies = lead_service.find_recently_funded_companies(limit=limit_per_type)
            all_companies.extend(funded_companies)
            
        if 'outdated_tech' in trigger_types:
            logger.info("Discovering companies with outdated tech...")
            outdated_companies = lead_service.find_companies_with_outdated_tech(limit_per_type)
            all_companies.extend(outdated_companies)
        
        # Save companies to database and find contacts
        saved_companies = []
        for company_data in all_companies:
            try:
                # Check if company already exists
                existing_company = Company.query.filter_by(domain=company_data['domain']).first()
                
                if not existing_company:
                    # Create new company
                    company = Company(
                        name=company_data['name'],
                        domain=company_data['domain'],
                        industry=company_data.get('industry'),
                        employee_count=company_data.get('employee_count'),
                        funding_stage=company_data.get('funding_stage'),
                        recent_funding_amount=company_data.get('recent_funding_amount'),
                        recent_funding_date=company_data.get('recent_funding_date'),
                        website_technologies=company_data.get('website_technologies'),
                        trigger_type=company_data['trigger_type'],
                        trigger_details=company_data['trigger_details']
                    )
                    
                    db.session.add(company)
                    db.session.flush()  # Get the ID
                    
                    # Find decision-makers for this company
                    contacts_data = lead_service.find_decision_makers(
                        company_data['domain'], 
                        company_data.get('employee_count', 50)
                    )
                    
                    # Save contacts
                    for contact_data in contacts_data:
                        decision_score = lead_service.calculate_decision_maker_score(
                            contact_data['job_title'],
                            company_data.get('employee_count', 50)
                        )
                        
                        contact = Contact(
                            company_id=company.id,
                            first_name=contact_data['first_name'],
                            last_name=contact_data['last_name'],
                            email=contact_data['email'],
                            job_title=contact_data['job_title'],
                            linkedin_url=contact_data.get('linkedin_url'),
                            decision_maker_score=decision_score
                        )
                        
                        db.session.add(contact)
                    
                    db.session.commit()
                    saved_companies.append(company.to_dict())
                    
                else:
                    logger.info(f"Company {company_data['domain']} already exists, skipping...")
                    
            except Exception as e:
                logger.error(f"Error saving company {company_data.get('name', 'Unknown')}: {str(e)}")
                db.session.rollback()
        
        return jsonify({
            'success': True,
            'message': f'Discovered {len(saved_companies)} new companies',
            'companies': saved_companies
        })
        
    except Exception as e:
        logger.error(f"Error in discover_leads: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@leads_bp.route('/companies', methods=['GET'])
def get_companies():
    """
    Get all discovered companies with optional filtering.
    """
    try:
        # Query parameters
        trigger_type = request.args.get('trigger_type')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = Company.query
        
        if trigger_type:
            query = query.filter(Company.trigger_type == trigger_type)
            
        companies = query.offset(offset).limit(limit).all()
        
        # Include contact count for each company
        companies_data = []
        for company in companies:
            company_dict = company.to_dict()
            company_dict['contact_count'] = len(company.contacts)
            company_dict['top_contacts'] = [contact.to_dict() for contact in 
                                         sorted(company.contacts, 
                                               key=lambda x: x.decision_maker_score, 
                                               reverse=True)[:3]]
            companies_data.append(company_dict)
        
        return jsonify({
            'success': True,
            'companies': companies_data,
            'total': Company.query.count()
        })
        
    except Exception as e:
        logger.error(f"Error in get_companies: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@leads_bp.route('/companies/<int:company_id>/contacts', methods=['GET'])
def get_company_contacts(company_id):
    """
    Get all contacts for a specific company.
    """
    try:
        company = Company.query.get_or_404(company_id)
        
        # Sort contacts by decision maker score
        contacts = sorted(company.contacts, 
                         key=lambda x: x.decision_maker_score, 
                         reverse=True)
        
        contacts_data = [contact.to_dict() for contact in contacts]
        
        return jsonify({
            'success': True,
            'company': company.to_dict(),
            'contacts': contacts_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_company_contacts: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@leads_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get statistics about discovered leads.
    """
    try:
        total_companies = Company.query.count()
        total_contacts = Contact.query.count()
        
        # Stats by trigger type
        trigger_stats = {}
        for trigger_type in ['hiring', 'funding', 'outdated_tech']:
            count = Company.query.filter(Company.trigger_type == trigger_type).count()
            trigger_stats[trigger_type] = count
        
        # Email validation stats
        validated_emails = Contact.query.filter(Contact.email_validated == True).count()
        contacted_count = Contact.query.filter(Contact.contacted == True).count()
        responses_count = Contact.query.filter(Contact.response_received == True).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_companies': total_companies,
                'total_contacts': total_contacts,
                'trigger_breakdown': trigger_stats,
                'email_stats': {
                    'validated_emails': validated_emails,
                    'contacted': contacted_count,
                    'responses': responses_count
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

