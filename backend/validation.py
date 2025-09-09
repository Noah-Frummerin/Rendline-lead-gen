from flask import Blueprint, request, jsonify
from src.models.company import db, Contact
from src.services.email_validation import EmailValidationService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

validation_bp = Blueprint('validation', __name__)

# Initialize email validation service
validation_service = EmailValidationService()

@validation_bp.route('/validate-email', methods=['POST'])
def validate_single_email():
    """
    Validate a single email address.
    """
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        result = validation_service.validate_email(email)
        
        return jsonify({
            'success': True,
            'validation_result': result
        })
        
    except Exception as e:
        logger.error(f"Error validating email: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@validation_bp.route('/validate-batch', methods=['POST'])
def validate_email_batch():
    """
    Validate multiple email addresses in batch.
    """
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        
        if not emails:
            return jsonify({'success': False, 'error': 'Emails list is required'}), 400
        
        results = validation_service.validate_email_batch(emails)
        
        return jsonify({
            'success': True,
            'validation_results': results,
            'summary': {
                'total': len(results),
                'valid': len([r for r in results if r['is_valid']]),
                'invalid': len([r for r in results if not r['is_valid']])
            }
        })
        
    except Exception as e:
        logger.error(f"Error validating email batch: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@validation_bp.route('/validate-contacts', methods=['POST'])
def validate_contacts():
    """
    Validate emails for all contacts or specific company contacts.
    """
    try:
        data = request.get_json()
        company_id = data.get('company_id')
        contact_ids = data.get('contact_ids', [])
        
        # Build query
        query = Contact.query
        
        if company_id:
            query = query.filter(Contact.company_id == company_id)
        elif contact_ids:
            query = query.filter(Contact.id.in_(contact_ids))
        else:
            # Validate all unvalidated contacts
            query = query.filter(Contact.email_validated == False)
        
        contacts = query.all()
        
        if not contacts:
            return jsonify({
                'success': True,
                'message': 'No contacts found to validate',
                'results': []
            })
        
        # Validate emails
        validation_results = []
        for contact in contacts:
            try:
                result = validation_service.validate_email(contact.email)
                
                # Update contact with validation result
                contact.email_validated = True
                contact.email_validation_result = result['validation_result']
                
                # Update decision maker score based on email reputation
                email_reputation = validation_service.get_email_reputation_score(contact.email)
                contact.decision_maker_score = (contact.decision_maker_score + email_reputation) / 2
                
                validation_results.append({
                    'contact_id': contact.id,
                    'email': contact.email,
                    'validation_result': result
                })
                
            except Exception as e:
                logger.error(f"Error validating contact {contact.id}: {str(e)}")
                validation_results.append({
                    'contact_id': contact.id,
                    'email': contact.email,
                    'validation_result': {'error': str(e)}
                })
        
        db.session.commit()
        
        # Summary statistics
        valid_count = len([r for r in validation_results 
                          if r['validation_result'].get('is_valid', False)])
        
        return jsonify({
            'success': True,
            'message': f'Validated {len(validation_results)} contacts',
            'results': validation_results,
            'summary': {
                'total_validated': len(validation_results),
                'valid_emails': valid_count,
                'invalid_emails': len(validation_results) - valid_count
            }
        })
        
    except Exception as e:
        logger.error(f"Error validating contacts: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@validation_bp.route('/update-decision-scores', methods=['POST'])
def update_decision_scores():
    """
    Recalculate decision maker scores for all contacts.
    """
    try:
        data = request.get_json()
        company_id = data.get('company_id')
        
        # Build query
        query = Contact.query
        if company_id:
            query = query.filter(Contact.company_id == company_id)
        
        contacts = query.all()
        
        updated_count = 0
        for contact in contacts:
            try:
                # Get company info for scoring
                company = contact.company
                
                # Recalculate decision maker score
                from src.services.lead_discovery import LeadDiscoveryService
                lead_service = LeadDiscoveryService()
                
                new_score = lead_service.calculate_decision_maker_score(
                    contact.job_title,
                    company.employee_count or 50
                )
                
                # Factor in email reputation if validated
                if contact.email_validated:
                    email_reputation = validation_service.get_email_reputation_score(contact.email)
                    new_score = (new_score + email_reputation) / 2
                
                contact.decision_maker_score = new_score
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Error updating score for contact {contact.id}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Updated decision maker scores for {updated_count} contacts'
        })
        
    except Exception as e:
        logger.error(f"Error updating decision scores: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@validation_bp.route('/filter-contacts', methods=['POST'])
def filter_contacts():
    """
    Filter contacts based on validation results and decision maker scores.
    """
    try:
        data = request.get_json()
        min_decision_score = data.get('min_decision_score', 0.5)
        email_validation_results = data.get('email_validation_results', ['valid', 'risky'])
        company_id = data.get('company_id')
        
        # Build query
        query = Contact.query
        
        if company_id:
            query = query.filter(Contact.company_id == company_id)
        
        # Filter by decision maker score
        query = query.filter(Contact.decision_maker_score >= min_decision_score)
        
        # Filter by email validation result
        if email_validation_results:
            query = query.filter(Contact.email_validation_result.in_(email_validation_results))
        
        # Order by decision maker score
        contacts = query.order_by(Contact.decision_maker_score.desc()).all()
        
        contacts_data = []
        for contact in contacts:
            contact_dict = contact.to_dict()
            contact_dict['company_name'] = contact.company.name
            contact_dict['company_domain'] = contact.company.domain
            contact_dict['trigger_type'] = contact.company.trigger_type
            contacts_data.append(contact_dict)
        
        return jsonify({
            'success': True,
            'contacts': contacts_data,
            'total_filtered': len(contacts_data),
            'filter_criteria': {
                'min_decision_score': min_decision_score,
                'email_validation_results': email_validation_results
            }
        })
        
    except Exception as e:
        logger.error(f"Error filtering contacts: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

