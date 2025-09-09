from src.models.user import db
from datetime import datetime

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    domain = db.Column(db.String(255), unique=True, nullable=False)
    industry = db.Column(db.String(100))
    employee_count = db.Column(db.Integer)
    funding_stage = db.Column(db.String(50))
    recent_funding_amount = db.Column(db.Float)
    recent_funding_date = db.Column(db.Date)
    website_technologies = db.Column(db.Text)  # JSON string of technologies
    trigger_type = db.Column(db.String(50))  # 'hiring', 'funding', 'tech_stack', etc.
    trigger_details = db.Column(db.Text)  # Additional details about the trigger
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with contacts
    contacts = db.relationship('Contact', backref='company', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain,
            'industry': self.industry,
            'employee_count': self.employee_count,
            'funding_stage': self.funding_stage,
            'recent_funding_amount': self.recent_funding_amount,
            'recent_funding_date': self.recent_funding_date.isoformat() if self.recent_funding_date else None,
            'website_technologies': self.website_technologies,
            'trigger_type': self.trigger_type,
            'trigger_details': self.trigger_details,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    job_title = db.Column(db.String(200))
    linkedin_url = db.Column(db.String(500))
    decision_maker_score = db.Column(db.Float, default=0.0)  # 0-1 score for likelihood of being decision maker
    email_validated = db.Column(db.Boolean, default=False)
    email_validation_result = db.Column(db.String(50))  # 'valid', 'invalid', 'risky', etc.
    contacted = db.Column(db.Boolean, default=False)
    contact_date = db.Column(db.DateTime)
    response_received = db.Column(db.Boolean, default=False)
    response_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'job_title': self.job_title,
            'linkedin_url': self.linkedin_url,
            'decision_maker_score': self.decision_maker_score,
            'email_validated': self.email_validated,
            'email_validation_result': self.email_validation_result,
            'contacted': self.contacted,
            'contact_date': self.contact_date.isoformat() if self.contact_date else None,
            'response_received': self.response_received,
            'response_date': self.response_date.isoformat() if self.response_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class EmailCampaign(db.Model):
    __tablename__ = 'email_campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    trigger_type = db.Column(db.String(50), nullable=False)
    email_template = db.Column(db.Text, nullable=False)
    subject_template = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='draft')  # 'draft', 'active', 'paused', 'completed'
    emails_sent = db.Column(db.Integer, default=0)
    responses_received = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'trigger_type': self.trigger_type,
            'email_template': self.email_template,
            'subject_template': self.subject_template,
            'status': self.status,
            'emails_sent': self.emails_sent,
            'responses_received': self.responses_received,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

