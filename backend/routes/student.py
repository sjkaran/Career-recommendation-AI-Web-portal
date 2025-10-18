from flask import Blueprint, request, jsonify, session
from backend import User, db
from backend import StudentProfile
from backend import Job
from backend import Application
from utils.helpers import save_uploaded_file, calculate_career_readiness_score, skills_similarity
from ai_engine.resume_parser import parse_resume
from ai_engine.matching_algorithm import get_job_recommendations
from ai_engine.career_recommender import get_career_recommendations
import os

student_bp = Blueprint('student', __name__)

def get_current_student():
    """Get current student profile from session"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    user = User.query.get(user_id)
    if not user or user.user_type != 'student':
        return None
    
    return user.student_profile

@student_bp.route('/profile', methods=['GET'])
def get_profile():
    try:
        student = get_current_student()
        if not student:
            return jsonify({'error': 'Not authenticated or not a student'}), 401
        
        return jsonify({
            'success': True,
            'profile': student.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@student_bp.route('/profile', methods=['POST'])
def update_profile():
    try:
        student = get_current_student()
        if not student:
            return jsonify({'error': 'Not authenticated or not a student'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update profile fields
        updatable_fields = [
            'full_name', 'phone', 'college_name', 'branch', 'semester',
            'cgpa', 'graduation_year', 'skills', 'interests', 'certifications',
            'projects', 'internship_experience', 'work_experience'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(student, field, data[field])
        
        # Calculate profile completeness and career score
        student.calculate_profile_completeness()
        student.career_score = calculate_career_readiness_score(student)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': student.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@student_bp.route('/upload-resume', methods=['POST'])
def upload_resume():
    try:
        student = get_current_student()
        if not student:
            return jsonify({'error': 'Not authenticated or not a student'}), 401
        
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        resume_file = request.files['resume']
        if resume_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save the uploaded file
        filename = save_uploaded_file(resume_file)
        if not filename:
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Update student's resume path
        student.resume_path = filename
        
        # Parse resume
        file_path = os.path.join('uploads', filename)
        resume_data = parse_resume(file_path)
        
        # Update profile with parsed data
        if resume_data:
            if resume_data.get('skills', {}).get('technical'):
                student.skills = ','.join(resume_data['skills']['technical'])
            
            if resume_data.get('education') and len(resume_data['education']) > 0:
                edu = resume_data['education'][0]
                if edu.get('cgpa'):
                    try:
                        student.cgpa = float(edu['cgpa'])
                    except:
                        pass
        
        # Recalculate scores
        student.calculate_profile_completeness()
        student.career_score = calculate_career_readiness_score(student)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Resume uploaded and parsed successfully',
            'resume_data': resume_data,
            'profile': student.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@student_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    try:
        student = get_current_student()
        if not student:
            return jsonify({'error': 'Not authenticated or not a student'}), 401
        
        # Get career recommendations
        recommendations = get_career_recommendations(student)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'career_score': student.career_score
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@student_bp.route('/matched-jobs', methods=['GET'])
def get_matched_jobs():
    try:
        student = get_current_student()
        if not student:
            return jsonify({'error': 'Not authenticated or not a student'}), 401
        
        # Get job recommendations with match scores
        jobs_with_matches = get_job_recommendations(student)
        
        return jsonify({
            'success': True,
            'matched_jobs': jobs_with_matches,
            'total_count': len(jobs_with_matches)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@student_bp.route('/apply/<int:job_id>', methods=['POST'])
def apply_to_job(job_id):
    try:
        student = get_current_student()
        if not student:
            return jsonify({'error': 'Not authenticated or not a student'}), 401
        
        # Check if job exists and is active
        job = Job.query.filter_by(id=job_id, is_active=True).first()
        if not job:
            return jsonify({'error': 'Job not found or not active'}), 404
        
        # Check if already applied
        existing_application = Application.query.filter_by(
            student_id=student.id, job_id=job_id
        ).first()
        
        if existing_application:
            return jsonify({'error': 'Already applied to this job'}), 409
        
        # Calculate match score
        match_score = skills_similarity(student.skills, job.required_skills)
        
        # Get cover letter from request
        cover_letter = ''
        if request.is_json:
            data = request.get_json()
            cover_letter = data.get('cover_letter', '')
        
        # Create new application
        application = Application(
            student_id=student.id,
            job_id=job_id,
            match_score=match_score,
            cover_letter=cover_letter,
            status='pending'
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Application submitted successfully',
            'application': application.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@student_bp.route('/applications', methods=['GET'])
def get_applications():
    try:
        student = get_current_student()
        if not student:
            return jsonify({'error': 'Not authenticated or not a student'}), 401
        
        applications = Application.query.filter_by(student_id=student.id)\
            .order_by(Application.applied_date.desc()).all()
        
        return jsonify({
            'success': True,
            'applications': [app.to_dict() for app in applications],
            'total': len(applications)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@student_bp.route('/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    """Get statistics for student dashboard"""
    try:
        student = get_current_student()
        if not student:
            return jsonify({'error': 'Not authenticated or not a student'}), 401
        
        # Get application statistics
        total_applications = Application.query.filter_by(student_id=student.id).count()
        pending_applications = Application.query.filter_by(
            student_id=student.id, status='pending'
        ).count()
        accepted_applications = Application.query.filter_by(
            student_id=student.id, status='accepted'
        ).count()
        
        # Get matched jobs count
        matched_jobs = get_job_recommendations(student, limit=5)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_applications': total_applications,
                'pending_applications': pending_applications,
                'accepted_applications': accepted_applications,
                'matched_jobs_count': len(matched_jobs),
                'career_score': student.career_score or 0,
                'profile_completeness': student.profile_completeness or 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500