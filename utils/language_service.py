"""
Simple language service for template functions
"""
from flask import g

def init_language_support(app):
    """Initialize language support"""
    
    @app.context_processor
    def inject_language_functions():
        return {
            'get_current_language': get_current_language,
            'get_supported_languages': get_supported_languages,
            '_': translate
        }

def get_current_language():
    """Get current language code"""
    return getattr(g, 'language', 'en')

def get_supported_languages():
    """Get list of supported languages"""
    return [
        {'code': 'en', 'name': 'English', 'is_current': True},
        {'code': 'or', 'name': 'ଓଡ଼ିଆ', 'is_current': False}
    ]

def translate(key, default=None):
    """Simple translation function"""
    translations = {
        'app_title': 'AI Career Platform',
        'app_subtitle': 'Intelligent career guidance and placement assistance',
        'navigation.home': 'Home',
        'navigation.login': 'Login',
        'navigation.register': 'Register',
        'navigation.logout': 'Logout',
        'navigation.profile': 'Profile',
        'navigation.settings': 'Settings',
        'common.get_started': 'Get Started',
        'common.learn_more': 'Learn More',
        'footer.about': 'About',
        'footer.contact': 'Contact',
        'footer.privacy_policy': 'Privacy Policy',
        'footer.help_center': 'Help Center',
        'footer.faq': 'FAQ',
        'footer.feedback': 'Feedback',
        'footer.copyright': 'All rights reserved'
    }
    
    return translations.get(key, default or key.split('.')[-1].replace('_', ' ').title())