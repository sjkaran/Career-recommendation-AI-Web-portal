from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

# Initialize extensions
db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.employer import employer_bp
    from routes.admin import admin_bp
    from routes.jobs import jobs_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(employer_bp, url_prefix='/api/employer')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(jobs_bp, url_prefix='/api')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app