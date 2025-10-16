import os
from datetime import timedelta

class Config:
    # Basic Flask Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Config
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '../instance/bput_career.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Upload Config
    UPLOAD_FOLDER = os.path.join(basedir, '../uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
    
    # Session Config
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # AI/ML Config
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or 'your-openai-api-key'
    
    # Platform Settings
    CAREER_SCORE_WEIGHTS = {
        'cgpa': 0.20,
        'skills_count': 0.20,
        'certifications': 0.15,
        'projects': 0.15,
        'internship_experience': 0.20,
        'profile_completeness': 0.10
    }