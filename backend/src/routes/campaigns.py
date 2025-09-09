from flask import Blueprint, request, jsonify
from src.models.company import db, Company, Contact, EmailCampaign
from src.services.email_generator import EmailGeneratorService
from src.services.email_sender import EmailSenderService
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

campaigns_bp = Blueprint('campaigns', __name__)

# Initialize services
email_generator = EmailGeneratorService()
email_sender = EmailSenderService()

@campaigns_bp.route('/generate-emails', methods=['POST'])
def generate_emails():
    """
    Generate personalized emails for selected contacts.
    """
    try:
        data = request.get_json()
        contact_ids = data.get('contact_ids', [])
        template_type = data.get('template_type')  # Optional override
        
        if not contact_ids:
            return jsonify({'success': False, 'error': 'Contact IDs are required'}), 400
        
        # Get contacts with company information
        contacts = Contact.query.filter(Contact.id.in_(contact_ids)).all()
        
        if not contacts:
            return jsonify({'success': False, 'error': 'No contacts found'}), 404
        
        # Generate emails
        generated_emails = []
        for contact in contacts:
            try:
                contact_data = contact.to_dict()
                company_data = contact.company.to_dict()
                
                email_data = email_generator.generate_email(
                    contact_data, 
                    company_data, 
                    template_type
                )
                
                email_data['contact_id'] = contact.id
                email_data['company_id'] = contact.company_id
                email_data['contact_name'] = f"{contact.first_name} {contact.last_name}"
                email_data['company_name'] = contact.company.name
                
                generated_emails.append(email_data)
                
            except Exception as e:
                logger.error(f"Error generating email for contact {contact.id}: {str(e)}")
                generated_emails.append({
                    'contact_id': contact.id,
                    'error': str(e),
                    'subject': f"Website opportunity for {contact.company.name}",
                    'body': f"Hi {contact.first_name},\n\nI'd love to discuss a website opportunity for {contact.company.name}.\n\nBest regards,\n[Your Name]"
                })
        
        return jsonify({
            'success': True,
            'generated_emails': generated_emails,
            'total_generated': len(generated_emails)
        })
        
    except Exception as e:
        logger.error(f"Error generating emails: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@campaigns_bp.route('/preview-email', methods=['POST'])
def preview_email():
    """
    Generate a preview of an email for a specific contact without saving.
    """
    try:
        data = request.get_json()
        contact_id = data.get('contact_id')
        template_type = data.get('template_type')
        
        if not contact_id:
            return jsonify({'success': False, 'error': 'Contact ID is required'}), 400
        
        contact = Contact.query.get_or_404(contact_id)
        
        contact_data = contact.to_dict()
        company_data = contact.company.to_dict()
        
        email_data = email_generator.generate_email(
            contact_data, 
            company_data, 
            template_type
        )
        
        return jsonify({
            'success': True,
            'preview': email_data,
            'contact_info': {
                'name': f"{contact.first_name} {contact.last_name}",
                'email': contact.email,
                'company': contact.company.name,
                'title': contact.job_title
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating email preview: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@campaigns_bp.route('/send-emails', methods=['POST'])
def send_emails():
    """
    Send emails to selected contacts.
    """
    try:
        data = request.get_json()
        email_data_list = data.get('emails', [])
        test_mode = data.get('test_mode', False)
        
        if not email_data_list:
            return jsonify({'success': False, 'error': 'Email data is required'}), 400
        
        # Validate email data
        for email_data in email_data_list:
            required_fields = ['contact_id', 'to_email', 'subject', 'body']
            for field in required_fields:
                if field not in email_data:
                    return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        if test_mode:
            # In test mode, just return success without actually sending
            return jsonify({
                'success': True,
                'message': 'Test mode - emails not actually sent',
                'test_results': [
                    {
                        'contact_id': email['contact_id'],
                        'to_email': email['to_email'],
                        'subject': email['subject'],
                        'status': 'test_success'
                    }
                    for email in email_data_list
                ]
            })
        
        # Send emails
        send_results = email_sender.send_email_batch(email_data_list)
        
        # Update contact records
        successful_sends = []
        for result in send_results:
            if result.get('success') and result.get('contact_id'):
                try:
                    contact = Contact.query.get(result['contact_id'])
                    if contact:
                        contact.contacted = True
                        contact.contact_date = datetime.utcnow()
                        successful_sends.append(result['contact_id'])
                except Exception as e:
                    logger.error(f"Error updating contact {result.get('contact_id')}: {str(e)}")
        
        db.session.commit()
        
        # Calculate summary
        total_sent = len(send_results)
        successful = len([r for r in send_results if r.get('success')])
        
        return jsonify({
            'success': True,
            'message': f'Sent {successful}/{total_sent} emails successfully',
            'send_results': send_results,
            'summary': {
                'total_attempted': total_sent,
                'successful_sends': successful,
                'failed_sends': total_sent - successful,
                'success_rate': successful / total_sent if total_sent > 0 else 0
            }
        })
        
    except Exception as e:
        logger.error(f"Error sending emails: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@campaigns_bp.route('/create-campaign', methods=['POST'])
def create_campaign():
    """
    Create a new email campaign.
    """
    try:
        data = request.get_json()
        
        campaign = EmailCampaign(
            name=data['name'],
            trigger_type=data['trigger_type'],
            email_template=data['email_template'],
            subject_template=data['subject_template'],
            status='draft'
        )
        
        db.session.add(campaign)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'campaign': campaign.to_dict(),
            'message': 'Campaign created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@campaigns_bp.route('/campaigns', methods=['GET'])
def get_campaigns():
    """
    Get all email campaigns.
    """
    try:
        campaigns = EmailCampaign.query.all()
        
        return jsonify({
            'success': True,
            'campaigns': [campaign.to_dict() for campaign in campaigns]
        })
        
    except Exception as e:
        logger.error(f"Error getting campaigns: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@campaigns_bp.route('/campaigns/<int:campaign_id>', methods=['PUT'])
def update_campaign(campaign_id):
    """
    Update an existing campaign.
    """
    try:
        campaign = EmailCampaign.query.get_or_404(campaign_id)
        data = request.get_json()
        
        # Update fields
        for field in ['name', 'trigger_type', 'email_template', 'subject_template', 'status']:
            if field in data:
                setattr(campaign, field, data[field])
        
        campaign.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'campaign': campaign.to_dict(),
            'message': 'Campaign updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating campaign: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@campaigns_bp.route('/test-email-config', methods=['POST'])
def test_email_config():
    """
    Test email configuration.
    """
    try:
        data = request.get_json()
        
        # Create temporary email sender with provided config
        smtp_config = data.get('smtp_config')
        sendgrid_key = data.get('sendgrid_api_key')
        
        if smtp_config:
            test_sender = EmailSenderService(smtp_config=smtp_config)
        elif sendgrid_key:
            test_sender = EmailSenderService(sendgrid_api_key=sendgrid_key)
        else:
            test_sender = email_sender  # Use default
        
        # Test connection
        result = test_sender.test_connection()
        
        return jsonify({
            'success': result.get('success', False),
            'test_result': result
        })
        
    except Exception as e:
        logger.error(f"Error testing email config: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@campaigns_bp.route('/email-templates', methods=['GET'])
def get_email_templates():
    """
    Get available email templates.
    """
    try:
        templates = {
            'hiring': {
                'name': 'Hiring Trigger',
                'description': 'For companies currently hiring marketing/sales roles',
                'subject': "Website support for {company_name}'s new {hiring_role}?",
                'preview': "Hi {first_name},\n\nI noticed {company_name} is currently hiring for a {hiring_role}..."
            },
            'funding': {
                'name': 'Funding Trigger',
                'description': 'For recently funded companies',
                'subject': "Congrats on the {funding_stage} - website alignment opportunity",
                'preview': "Hi {first_name},\n\nCongratulations on {company_name}'s recent {funding_stage} round..."
            },
            'outdated_tech': {
                'name': 'Outdated Technology',
                'description': 'For companies using outdated web technologies',
                'subject': "Quick website performance opportunity for {company_name}",
                'preview': "Hi {first_name},\n\nI was researching {industry} companies and came across {company_name}..."
            },
            'general': {
                'name': 'General Outreach',
                'description': 'Generic template for any company',
                'subject': "Website optimization opportunity for {company_name}",
                'preview': "Hi {first_name},\n\nI came across {company_name} while researching innovative {industry} companies..."
            }
        }
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

