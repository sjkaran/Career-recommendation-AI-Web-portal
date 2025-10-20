"""
Main Flask application entry point for AI Career Platform
"""
import os
from flask import Flask
from flask_cors import CORS
from config import Config
from database import init_db
from utils.language_service import init_language_support
from utils.security_middleware import init_security_middleware
from utils.privacy_manager import PrivacyManager

def create_app(config_class=Config):
    """Application factory pattern for Flask app creation"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize CORS for cross-origin requests (with security considerations)
    CORS(app, 
         origins=['http://localhost:3000', 'http://localhost:5000'],  # Restrict origins in production
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Initialize database
    init_db(app)
    
    # Initialize privacy and GDPR compliance tables
    with app.app_context():
        PrivacyManager.initialize_privacy_tables()
    
    # Initialize security middleware
    init_security_middleware(app)
    
    # Initialize language support
    init_language_support(app)
    
    # Register blueprints
    from blueprints.auth import auth_bp
    from blueprints.student import student_bp
    from blueprints.employer import employer_bp
    from blueprints.analytics import analytics_bp
    from blueprints.api import api_bp
    from blueprints.ai_recommendations import ai_bp
    from blueprints.gamification import gamification_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(employer_bp, url_prefix='/employer')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(ai_bp)
    app.register_blueprint(gamification_bp)
    
    # Root route
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')
    
    # Language switching route
    @app.route('/set_language/<language_code>')
    def set_language(language_code):
        from flask import redirect, url_for
        return redirect(url_for('index'))
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)