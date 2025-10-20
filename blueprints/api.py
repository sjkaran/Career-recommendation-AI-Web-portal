"""
General API blueprint for common endpoints and utilities
"""
from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)

@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'AI Career Platform API is running'})

@api_bp.route('/demo/stats')
def demo_stats():
    """Demo statistics"""
    return jsonify({
        'total_students': 1200,
        'total_placements': 450,
        'placement_rate': 87.5,
        'active_jobs': 125
    })