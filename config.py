"""
Configuration settings for AI Career Platform
"""
import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///career_platform.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # AI API settings
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # AI Service Configuration
    AI_RATE_LIMIT_CALLS = int(os.environ.get('AI_RATE_LIMIT_CALLS', 100))
    AI_RATE_LIMIT_WINDOW = int(os.environ.get('AI_RATE_LIMIT_WINDOW', 3600))
    AI_FALLBACK_ENABLED = os.environ.get('AI_FALLBACK_ENABLED', 'true').lower() in ['true', 'on', '1']
    AI_CACHE_ENABLED = os.environ.get('AI_CACHE_ENABLED', 'true').lower() in ['true', 'on', '1']
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    
    # Email settings (for notifications)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Security settings
    BCRYPT_LOG_ROUNDS = 12
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    
    # Security headers and CSP
    SECURITY_HEADERS_ENABLED = True
    CSP_ENABLED = True
    
    # Session security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # GDPR and Privacy
    DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS', 2555))  # 7 years default
    AUDIT_LOG_RETENTION_DAYS = int(os.environ.get('AUDIT_LOG_RETENTION_DAYS', 365))  # 1 year
    
    # File upload security
    ALLOWED_EXTENSIONS = {
        'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
        'document': {'pdf', 'doc', 'docx', 'txt'},
        'resume': {'pdf', 'doc', 'docx'}
    }
    
    # Input validation
    MAX_STRING_LENGTH = 10000
    MAX_LIST_LENGTH = 1000
    
    # Security monitoring
    SECURITY_MONITORING_ENABLED = True
    FAILED_LOGIN_THRESHOLD = 5
    ACCOUNT_LOCKOUT_DURATION = 1800  # 30 minutes

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///career_platform_dev.db'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///career_platform.db'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}