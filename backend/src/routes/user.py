# This file handles user-related routes and logic.
from flask import Blueprint

# Create a Blueprint for user routes
user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def home():
    return 'User routes are working!'