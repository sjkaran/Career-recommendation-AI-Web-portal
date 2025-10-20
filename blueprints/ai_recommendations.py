"""
AI Recommendations Blueprint
"""
from flask import Blueprint, jsonify

ai_bp = Blueprint('ai_recommendations', __name__)

@ai_bp.route('/recommendations')
def recommendations():
    """AI career recommendations"""
    return jsonify({
        'career_paths': ['Software Developer', 'Data Scientist', 'AI Engineer'],
        'message': 'AI recommendations - demo version'
    })