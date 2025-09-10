import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from flask import Flask, jsonify
from flask_cors import CORS
from src.models.user import db
import logging

# Import blueprints from the correct locations
from src.routes.leads import leads_bp
from src.routes.companies import companies_bp
from src.routes.campaigns import campaigns_bp
from src.routes.users import users_bp
from src.routes.auth import auth_bp
from src.validation import validation_bp

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
db.init_app(app)

# Register blueprints
app.register_blueprint(leads_bp, url_prefix='/leads')
app.register_blueprint(companies_bp, url_prefix='/companies')
app.register_blueprint(campaigns_bp, url_prefix='/campaigns')
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(auth_bp, url_prefix='/auth')
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
        "database": "connected" if db.engine else "disconnected"
    })

if __name__ == '__main__':
    with app.app_context():
        try:
            # Create database tables
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
    
    # Use environment variable for debug mode in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('PORT', 8000))
    
    logger.info(f"Starting application in {'debug' if debug_mode else 'production'} mode on port {port}")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)