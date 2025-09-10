import sys
import os

# Add the 'src' directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask
from flask_cors import CORS
from src.routes.leads import leads_bp
from src.routes.companies import companies_bp
from src.routes.campaigns import campaigns_bp
from src.routes.users import users_bp
from src.models.user import db as user_db
from src.models.company import db as company_db
from src.services.email_generator import email_generator_bp
from src.services.email_sender import email_sender_bp
from src.services.email_validation import email_validation_bp
from src.services.lead_discovery import lead_discovery_bp
from src.validation import validation_bp

# Initialize the Flask application
app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Configure the database connection string from an environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_PATH')

# Initialize the database with the Flask app
user_db.init_app(app)
company_db.init_app(app)

# Register blueprints for different parts of the API
app.register_blueprint(leads_bp, url_prefix='/leads')
app.register_blueprint(companies_bp, url_prefix='/companies')
app.register_blueprint(campaigns_bp, url_prefix='/campaigns')
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(email_generator_bp, url_prefix='/email-generator')
app.register_blueprint(email_sender_bp, url_prefix='/email-sender')
app.register_blueprint(email_validation_bp, url_prefix='/email-validation')
app.register_blueprint(lead_discovery_bp, url_prefix='/lead-discovery')
app.register_blueprint(validation_bp, url_prefix='/validation')

# Root endpoint
@app.route('/')
def home():
    return "Welcome to the backend API!"

if __name__ == '__main__':
    with app.app_context():
        # You would typically not create tables in a production environment
        # but this is useful for development.
        user_db.create_all()
        company_db.create_all()
    app.run(debug=True, port=8000)
