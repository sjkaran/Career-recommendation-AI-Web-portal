"""
Module: config.py
Description: Configuration settings for BPUT Career Platform with FREE APIs
Author: AI Assistant for BPUT Career Platform
Date: 2025-10-17
"""

import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration"""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bput-career-platform-secret-key-2025'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '../instance/bput_career_platform.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # FREE AI API Keys
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or 'your-gemini-api-key-here'
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY') or 'your-huggingface-token-here'
    COHERE_API_KEY = os.environ.get('COHERE_API_KEY') or 'your-cohere-api-key-here'
    
    # Email Configuration (Gmail SMTP - FREE)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your-email@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your-gmail-app-password'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@bput-career-platform.com'
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-bput-2025'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # 24 hours
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # 30 days
    
    # Rate Limiting
    RATE_LIMIT_STUDENT = int(os.environ.get('RATE_LIMIT_STUDENT') or 100)  # requests per hour
    RATE_LIMIT_EMPLOYER = int(os.environ.get('RATE_LIMIT_EMPLOYER') or 200)  # requests per hour
    RATE_LIMIT_ADMIN = int(os.environ.get('RATE_LIMIT_ADMIN') or 1000)  # requests per hour
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(basedir, '../uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg'}
    
    # Analytics and Tracking
    TRACK_USER_ACTIVITY = os.environ.get('TRACK_USER_ACTIVITY') or True
    ACTIVITY_LOG_PATH = os.path.join(basedir, '../logs/activity.log')
    
    # Platform Settings
    PLATFORM_NAME = "BPUT Career Platform"
    PLATFORM_VERSION = "1.0.0"
    SUPPORT_EMAIL = "support@bput-career-platform.com"
    
    # Demo Data Settings
    GENERATE_DEMO_DATA = os.environ.get('GENERATE_DEMO_DATA') or True
    DEMO_STUDENTS_COUNT = int(os.environ.get('DEMO_STUDENTS_COUNT') or 50)
    DEMO_EMPLOYERS_COUNT = int(os.environ.get('DEMO_EMPLOYERS_COUNT') or 10)
    DEMO_JOBS_COUNT = int(os.environ.get('DEMO_JOBS_COUNT') or 30)
    
    # Gamification Settings
    ENABLE_GAMIFICATION = os.environ.get('ENABLE_GAMIFICATION') or True
    POINTS_PROFILE_COMPLETION = 50
    POINTS_SKILL_ADDED = 10
    POINTS_RESUME_UPLOAD = 30
    POINTS_JOB_APPLICATION = 20
    POINTS_INTERVIEW_ATTENDED = 100
    POINTS_JOB_OFFER = 500
    POINTS_CERTIFICATE_UPLOAD = 25
    POINTS_PROJECT_ADDED = 40
    
    # Career Readiness Score Weights
    SCORE_WEIGHTS = {
        'academic_performance': 0.20,
        'technical_skills': 0.25,
        'soft_skills': 0.15,
        'projects': 0.15,
        'internships': 0.15,
        'certifications': 0.10
    }
    
    # BPUT Specific Settings
    BPUT_BRANCHES = [
        'Computer Science & Engineering',
        'Electronics & Communication Engineering',
        'Electrical & Electronics Engineering', 
        'Mechanical Engineering',
        'Civil Engineering',
        'Information Technology',
        'Master of Business Administration',
        'Master of Computer Applications'
    ]
    
    BPUT_DISTRICTS = [
        'Khordha', 'Cuttack', 'Puri', 'Ganjam', 'Balasore', 
        'Sambalpur', 'Bhadrak', 'Jajpur', 'Kendrapara', 'Mayurbhanj'
    ]
    
    # Industry Sectors for Odisha
    INDUSTRY_SECTORS = [
        'IT Services', 'Software Development', 'Core Engineering',
        'Manufacturing', 'Construction', 'Healthcare', 'Education',
        'Banking & Finance', 'E-commerce', 'Startups', 'Government',
        'Research & Development', 'Consulting'
    ]

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True  # Log SQL queries

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Security enhancements for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """
    Get configuration based on environment
    
    Args:
        config_name (str): Configuration name (development, testing, production)
    
    Returns:
        Config: Configuration object
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG') or 'default'
    return config.get(config_name, DevelopmentConfig)

# Export configuration
current_config = get_config()