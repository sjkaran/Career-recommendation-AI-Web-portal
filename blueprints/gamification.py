"""
Gamification blueprint for points, achievements, and leaderboard endpoints
"""
from flask import Blueprint, jsonify

gamification_bp = Blueprint('gamification', __name__)

@gamification_bp.route('/points')
def points():
    """Student points"""
    return jsonify({'points': 1250, 'message': 'Gamification - demo version'})