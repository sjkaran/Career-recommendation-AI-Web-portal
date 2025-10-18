"""
BPUT Career Platform - Main Application Entry Point
Simplified for demo with free APIs
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'bput-career-demo-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bput_career_demo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for frontend
CORS(app, supports_credentials=True)

# Initialize database
from backend import db

db.init_app(app)

# Import blueprints
from routes.auth import auth_bp
from routes.student import student_bp
from routes.employer import employer_bp
from routes.admin import admin_bp
from routes.jobs import jobs_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(student_bp, url_prefix='/api/student')
app.register_blueprint(employer_bp, url_prefix='/api/employer')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(jobs_bp, url_prefix='/api')

# Create database tables and generate demo data
with app.app_context():
    db.create_all()
    
    # Check if we need to generate demo data
    from backend import User
    if User.query.count() == 0:
        print("\n" + "="*60)
        print("🚀 BPUT Career Platform - First Time Setup")
        print("="*60)
        print("\nGenerating demo data...")
        
        from utils.demo_data import generate_demo_data
        stats = generate_demo_data()
        
        print("\n✅ Demo data generated successfully!")
        print(f"   📊 Students: {stats.get('students', 0)}")
        print(f"   🏢 Employers: {stats.get('employers', 0)}")
        print(f"   💼 Jobs: {stats.get('jobs', 0)}")
        print(f"   📝 Applications: {stats.get('applications', 0)}")
        print("\n" + "="*60)
        print("Demo Accounts Created:")
        print("="*60)
        print("👨‍🎓 Student Login:")
        print("   Email: student@bput.ac.in")
        print("   Password: demo123")
        print("\n🏢 Employer Login:")
        print("   Email: employer@company.com")
        print("   Password: demo123")
        print("\n👨‍💼 Admin Login:")
        print("   Email: admin@bput.ac.in")
        print("   Password: admin123")
        print("="*60 + "\n")

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if API is running"""
    return jsonify({
        'status': 'healthy',
        'message': 'BPUT Career Platform API is running',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0-demo'
    }), 200

# API documentation endpoint
@app.route('/api', methods=['GET'])
def api_info():
    """API information and available endpoints"""
    return jsonify({
        'name': 'BPUT Career Platform API',
        'version': '1.0.0-demo',
        'endpoints': {
            'auth': {
                'POST /api/auth/register': 'Register new user',
                'POST /api/auth/login': 'Login user',
                'POST /api/auth/logout': 'Logout user',
                'GET /api/auth/me': 'Get current user'
            },
            'student': {
                'GET /api/student/profile': 'Get student profile',
                'POST /api/student/profile': 'Update student profile',
                'POST /api/student/upload-resume': 'Upload and parse resume',
                'GET /api/student/recommendations': 'Get career recommendations',
                'GET /api/student/matched-jobs': 'Get AI-matched jobs',
                'POST /api/student/apply/<job_id>': 'Apply to a job',
                'GET /api/student/applications': 'Get my applications'
            },
            'employer': {
                'GET /api/employer/profile': 'Get employer profile',
                'POST /api/employer/profile': 'Update employer profile',
                'POST /api/employer/jobs': 'Post a new job',
                'GET /api/employer/jobs': 'Get posted jobs',
                'PUT /api/employer/jobs/<job_id>': 'Update job',
                'GET /api/employer/applications': 'Get applications',
                'PUT /api/employer/application/<application_id>': 'Update application status'
            },
            'admin': {
                'GET /api/admin/stats': 'Get platform statistics',
                'GET /api/admin/students': 'Get all students',
                'GET /api/admin/jobs': 'Get all jobs',
                'GET /api/admin/skill-gaps': 'Skill gap analysis',
                'GET /api/admin/placement-trends': 'Placement trends'
            },
            'public': {
                'GET /api/jobs': 'Browse all jobs',
                'GET /api/jobs/<job_id>': 'Get job details',
                'GET /api/job-stats': 'Job statistics'
            }
        }
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested URL was not found on the server'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on the server'
    }), 500

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        'error': 'Forbidden',
        'message': 'You do not have permission to access this resource'
    }), 403

# Demo data reset endpoint (for testing)
@app.route('/api/reset-demo', methods=['POST'])
def reset_demo_data():
    """Reset demo data (use with caution!)"""
    try:
        from utils.demo_data import generate_demo_data
        stats = generate_demo_data()
        
        return jsonify({
            'success': True,
            'message': 'Demo data reset successfully',
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Run the application
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎓 BPUT Career Platform - Starting Server")
    print("="*60)
    print("\n📍 Server running at: http://localhost:5000")
    print("📚 API documentation: http://localhost:5000/api")
    print("💚 Health check: http://localhost:5000/api/health")
    print("\n⚠️  Press CTRL+C to stop the server\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )