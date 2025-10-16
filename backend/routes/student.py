from flask import Blueprint, request, jsonify, session
from models.user import User, db
from models.profile import StudentProfile
from models.job import Job
from models.application import Application
from utils.helpers import save_uploaded_file, calculate_career_readiness_score, skills_similarity
from ai_engine.resume_parser import parse_resume
from ai_engine.matching_algorithm import get_job_recommendations
from backend.ai_engine.career_recommender import get_career_recommendations
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
            'profile': student.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

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
            'message': 'Profile updated successfully',
            'profile': student.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500

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
        
        # Parse resume using AI
        resume_data = parse_resume(os.path.join('uploads', filename))
        
        # Update profile with parsed data
        if resume_data:
            if resume_data.get('skills'):
                student.skills = ','.join(resume_data['skills'])
            if resume_data.get('education'):
                # You might want to parse education data more carefully
                pass
        
        # Recalculate scores
        student.calculate_profile_completeness()
        student.career_score = calculate_career_readiness_score(student)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Resume uploaded and parsed successfully',
            'resume_data': resume_data,
            'profile': student.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to upload resume: {str(e)}'}), 500

@student_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    try:
        student = get_current_student()
        if not student:
            return jsonify({'error': 'Not authenticated or not a student'}), 401
        
        # Get career recommendations from AI engine
        recommendations = get_career_recommendations(student)
        
        return jsonify({
            'recommendations': recommendations,
            'career_score': student.career_score
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get recommendations: {str(e)}'}), 500

@student_bp.route('/matched-jobs', methods=['GET'])
def get_matched_jobs():
    try:
        student = get_current_student()
        if not student:
            return jsonify({'error': 'Not authenticated or not a student'}), 401
        
        # Get job recommendations with match scores
        jobs_with_matches = get_job_recommendations(student)
        
        return jsonify({
            'matched_jobs': jobs_with_matches,
            'total_count': len(jobs_with_matches)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get matched jobs: {str(e)}'}), 500

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
        
        # Create new application
        application = Application(
            student_id=student.id,
            job_id=job_id,
            match_score=match_score,
            cover_letter=request.get_json().get('cover_letter', '') if request.is_json else ''
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify({
            'message': 'Application submitted successfully',
            'application': application.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to apply to job: {str(e)}'}), 500

@student_bp.route('/applications', methods=['GET'])
def get_applications():
    try:
        student = get_current_student()
        if not student:
            return jsonify({'error': 'Not authenticated or not a student'}), 401
        
        applications = Application.query.filter_by(student_id=student.id)\
            .order_by(Application.applied_date.desc()).all()
        
        return jsonify({
            'applications': [app.to_dict() for app in applications]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get applications: {str(e)}'}), 500