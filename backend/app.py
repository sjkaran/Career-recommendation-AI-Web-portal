from flask import Flask, jsonify, request
import os
from config import Config
from models.user import db
from utils.demo_data import generate_demo_data
from datetime import datetime
from ai_engine.resume_parser import resume_parser
from utils.demo_data import init_demo_data



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
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
    
    # Create tables and demo data
    with app.app_context():
        db.create_all()
        
        # Generate demo data if no users exist
        from models.user import User
        if User.query.count() == 0:
            print("No data found. Generating demo data...")
            stats = generate_demo_data()
            print(f"Demo data generated: {stats}")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'BPUT Career Platform API is running',
            'timestamp': str(datetime.utcnow())
        })
    
    # Demo data reset endpoint (for testing)
    @app.route('/api/reset-demo-data', methods=['POST'])
    def reset_demo_data():
        try:
            stats = generate_demo_data()
            return jsonify({
                'message': 'Demo data reset successfully',
                'stats': stats
            }), 200
        except Exception as e:
            return jsonify({'error': f'Failed to reset demo data: {str(e)}'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

app.cli.command('generate-demo-data')
def generate_demo_data():
    """Generate demo data for testing"""
    from utils.demo_data import init_demo_data
    from models import User, StudentProfile, Employer, Job, Application
    
    models = {
        'User': User,
        'StudentProfile': StudentProfile, 
        'Employer': Employer,
        'Job': Job,
        'Application': Application
    }
    
    init_demo_data(db, models)
    print("Demo data generated successfully!")