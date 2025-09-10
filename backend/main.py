import sys
import os
from dotenv import load_dotenv
import logging

# Load environment variables from the .env file
load_dotenv()

# Add the 'src' directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask, jsonify
from flask_cors import CORS
from src.routes.leads import leads_bp
from src.routes.companies import companies_bp
from src.routes.campaigns import campaigns_bp
from src.routes.user import user_bp
from src.models.user import db as user_db
from src.models.company import db as company_db
from src.routes.validation import validation_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure the database connection string from an environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_PATH', 'sqlite:///leads.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the Flask app
user_db.init_app(app)
company_db.init_app(app)

# Register blueprints for different parts of the API
app.register_blueprint(leads_bp, url_prefix='/leads')
app.register_blueprint(companies_bp, url_prefix='/companies')
app.register_blueprint(campaigns_bp, url_prefix='/campaigns')
app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(validation_bp, url_prefix='/validation')

# Root endpoint
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Rendline Lead Generation API!",
        "version": "1.0.0",
        "endpoints": [
            "/leads/discover",
            "/leads/companies",
            "/campaigns/generate-emails",
            "/campaigns/send-emails",
            "/validation/validate-contacts"
        ]
    })

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "database": "connected" if user_db.engine else "disconnected"
    })

if __name__ == '__main__':
    with app.app_context():
        try:
            # Create database tables
            user_db.create_all()
            company_db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
    
    # Use environment variable for debug mode in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('PORT', 8000))
    
    logger.info(f"Starting app with debug={debug_mode} on port {port}")
    app.run(host='0.0.0.0', debug=debug_mode, port=port)