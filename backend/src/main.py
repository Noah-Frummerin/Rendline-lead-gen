# main.py
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

# Create a Flask app instance
app = Flask(__name__)
CORS(app)

# Use an environment variable for the database path,
# falling back to a default for local development.
# On Render, the `_render` directory is writable.
# On other platforms, /tmp is a common writable location.
DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.join(os.getcwd(), 'db.sqlite'))

# Configure the SQLAlchemy database connection
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database extension
db = SQLAlchemy(app)

# Import models to ensure they are registered with SQLAlchemy
from .models.company import Company
from .models.user import User

# Import and register blueprints
from .routes.campaigns import campaigns_bp
from .routes.leads import leads_bp
from .routes.validation import validation_bp
from .routes.auth import auth_bp
from .routes.companies import companies_bp

app.register_blueprint(campaigns_bp, url_prefix='/api/campaigns')
app.register_blueprint(leads_bp, url_prefix='/api/leads')
app.register_blueprint(validation_bp, url_prefix='/api/validation')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(companies_bp, url_prefix='/api/companies')

# A basic route to check if the API is running
@app.route('/')
def home():
    return "API is running"

# Create database tables before the first request
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    # Use environment variable for port in production
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)