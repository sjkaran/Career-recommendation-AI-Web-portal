from flask import Blueprint, request, jsonify, session
from models.user import User, db
from models.employer import Employer
from models.job import Job
from models.application import Application
from models.profile import StudentProfile
from utils.helpers import save_uploaded_file, skills_similarity
from datetime import datetime

employer_bp = Blueprint('employer', __name__)

def get_current_employer():
    """Get current employer profile from session"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    user = User.query.get(user_id)
    if not user or user.user_type != 'employer':
        return None
    
    return user.employer_profile

@employer_bp.route('/profile', methods=['GET'])
def get_profile():
    try:
        employer = get_current_employer()
        if not employer:
            return jsonify({'error': 'Not authenticated or not an employer'}), 401
        
        return jsonify({
            'profile': employer.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@employer_bp.route('/profile', methods=['POST'])
def update_profile():
    try:
        employer = get_current_employer()
        if not employer:
            return jsonify({'error': 'Not authenticated or not an employer'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update profile fields
        updatable_fields = [
            'company_name', 'contact_person', 'phone', 'industry',
            'website', 'description', 'address'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(employer, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': employer.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500

@employer_bp.route('/jobs', methods=['POST'])
def post_job():
    try:
        employer = get_current_employer()
        if not employer:
            return jsonify({'error': 'Not authenticated or not an employer'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['title', 'description', 'required_skills']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse application deadline
        application_deadline = None
        if data.get('application_deadline'):
            try:
                application_deadline = datetime.fromisoformat(data['application_deadline'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid application deadline format'}), 400
        
        # Create new job
        new_job = Job(
            employer_id=employer.id,
            title=data['title'],
            company_name=employer.company_name,
            description=data['description'],
            requirements=data.get('requirements', ''),
            required_skills=data['required_skills'],
            location=data.get('location', ''),
            salary=data.get('salary', ''),
            job_type=data.get('job_type', 'full-time'),
            category=data.get('category', ''),
            application_deadline=application_deadline,
            vacancies=data.get('vacancies', 1)
        )
        
        db.session.add(new_job)
        db.session.commit()
        
        return jsonify({
            'message': 'Job posted successfully',
            'job': new_job.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to post job: {str(e)}'}), 500

@employer_bp.route('/jobs', methods=['GET'])
def get_employer_jobs():
    try:
        employer = get_current_employer()
        if not employer:
            return jsonify({'error': 'Not authenticated or not an employer'}), 401
        
        # Get query parameters for filtering
        status = request.args.get('status', 'all')  # all, active, inactive
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = Job.query.filter_by(employer_id=employer.id)
        
        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)
        
        # Paginate results
        jobs_pagination = query.order_by(Job.posted_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        jobs = [job.to_dict() for job in jobs_pagination.items]
        
        return jsonify({
            'jobs': jobs,
            'total': jobs_pagination.total,
            'pages': jobs_pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get jobs: {str(e)}'}), 500

@employer_bp.route('/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    try:
        employer = get_current_employer()
        if not employer:
            return jsonify({'error': 'Not authenticated or not an employer'}), 401
        
        job = Job.query.filter_by(id=job_id, employer_id=employer.id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update job fields
        updatable_fields = [
            'title', 'description', 'requirements', 'required_skills',
            'location', 'salary', 'job_type', 'category', 'vacancies', 'is_active'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(job, field, data[field])
        
        # Update application deadline if provided
        if data.get('application_deadline'):
            try:
                job.application_deadline = datetime.fromisoformat(data['application_deadline'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid application deadline format'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': 'Job updated successfully',
            'job': job.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update job: {str(e)}'}), 500

@employer_bp.route('/applications', methods=['GET'])
def get_applications():
    try:
        employer = get_current_employer()
        if not employer:
            return jsonify({'error': 'Not authenticated or not an employer'}), 401
        
        # Get query parameters
        job_id = request.args.get('job_id')
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = db.session.query(Application).join(Job).filter(Job.employer_id == employer.id)
        
        if job_id:
            query = query.filter(Application.job_id == job_id)
        
        if status:
            query = query.filter(Application.status == status)
        
        # Paginate results
        applications_pagination = query.order_by(Application.applied_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        applications = [app.to_dict() for app in applications_pagination.items]
        
        # Get job list for filter dropdown
        jobs = Job.query.filter_by(employer_id=employer.id, is_active=True).all()
        
        return jsonify({
            'applications': applications,
            'jobs': [{'id': job.id, 'title': job.title} for job in jobs],
            'total': applications_pagination.total,
            'pages': applications_pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get applications: {str(e)}'}), 500

@employer_bp.route('/application/<int:application_id>', methods=['PUT'])
def update_application_status(application_id):
    try:
        employer = get_current_employer()
        if not employer:
            return jsonify({'error': 'Not authenticated or not an employer'}), 401
        
        # Find application and verify it belongs to employer's job
        application = db.session.query(Application)\
            .join(Job)\
            .filter(
                Application.id == application_id,
                Job.employer_id == employer.id
            ).first()
        
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        data = request.get_json()
        if not data or not data.get('status'):
            return jsonify({'error': 'Status is required'}), 400
        
        valid_statuses = ['pending', 'shortlisted', 'accepted', 'rejected']
        new_status = data['status'].lower()
        
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        
        # Update application status
        application.status = new_status
        
        db.session.commit()
        
        return jsonify({
            'message': f'Application {new_status} successfully',
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update application: {str(e)}'}), 500

@employer_bp.route('/stats', methods=['GET'])
def get_employer_stats():
    try:
        employer = get_current_employer()
        if not employer:
            return jsonify({'error': 'Not authenticated or not an employer'}), 401
        
        # Basic statistics
        total_jobs = Job.query.filter_by(employer_id=employer.id).count()
        active_jobs = Job.query.filter_by(employer_id=employer.id, is_active=True).count()
        
        total_applications = db.session.query(Application)\
            .join(Job)\
            .filter(Job.employer_id == employer.id)\
            .count()
        
        # Application status breakdown
        status_breakdown = db.session.query(
            Application.status,
            db.func.count(Application.id)
        ).join(Job).filter(Job.employer_id == employer.id)\
         .group_by(Application.status).all()
        
        status_stats = {status: count for status, count in status_breakdown}
        
        # Recent applications (last 30 days)
        recent_applications = db.session.query(Application)\
            .join(Job)\
            .filter(
                Job.employer_id == employer.id,
                Application.applied_date >= db.func.date('now', '-30 days')
            ).count()
        
        return jsonify({
            'stats': {
                'total_jobs': total_jobs,
                'active_jobs': active_jobs,
                'total_applications': total_applications,
                'recent_applications': recent_applications,
                'application_status': status_stats
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get stats: {str(e)}'}), 500