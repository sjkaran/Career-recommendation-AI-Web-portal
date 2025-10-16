from flask import Blueprint, request, jsonify, session
from models.user import User, db
from models.profile import StudentProfile
from models.employer import Employer
from models.job import Job
from models.application import Application
from sqlalchemy import func, text
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

def is_admin():
    """Check if current user is admin"""
    user_id = session.get('user_id')
    if not user_id:
        return False
    
    user = User.query.get(user_id)
    return user and user.user_type == 'admin'

@admin_bp.route('/stats', methods=['GET'])
def get_admin_stats():
    try:
        if not is_admin():
            return jsonify({'error': 'Not authenticated or not an admin'}), 401
        
        # Overall platform statistics
        total_students = User.query.filter_by(user_type='student').count()
        total_employers = User.query.filter_by(user_type='employer').count()
        total_jobs = Job.query.count()
        total_applications = Application.query.count()
        
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        recent_students = User.query.filter(
            User.user_type == 'student',
            User.created_at >= thirty_days_ago
        ).count()
        
        recent_employers = User.query.filter(
            User.user_type == 'employer',
            User.created_at >= thirty_days_ago
        ).count()
        
        recent_jobs = Job.query.filter(Job.posted_date >= thirty_days_ago).count()
        recent_applications = Application.query.filter(Application.applied_date >= thirty_days_ago).count()
        
        # Application status breakdown
        app_status = db.session.query(
            Application.status,
            func.count(Application.id)
        ).group_by(Application.status).all()
        
        status_breakdown = {status: count for status, count in app_status}
        
        return jsonify({
            'overall_stats': {
                'total_students': total_students,
                'total_employers': total_employers,
                'total_jobs': total_jobs,
                'total_applications': total_applications
            },
            'recent_activity': {
                'new_students': recent_students,
                'new_employers': recent_employers,
                'new_jobs': recent_jobs,
                'new_applications': recent_applications
            },
            'application_status': status_breakdown
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get admin stats: {str(e)}'}), 500

@admin_bp.route('/students', methods=['GET'])
def get_all_students():
    try:
        if not is_admin():
            return jsonify({'error': 'Not authenticated or not an admin'}), 401
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        branch = request.args.get('branch')
        
        # Build query
        query = StudentProfile.query
        
        if branch:
            query = query.filter(StudentProfile.branch == branch)
        
        # Paginate results
        students_pagination = query.order_by(StudentProfile.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        students = [student.to_dict() for student in students_pagination.items]
        
        # Get branch list for filters
        branches = db.session.query(StudentProfile.branch)\
            .filter(StudentProfile.branch.isnot(None))\
            .distinct().all()
        
        branch_list = [branch[0] for branch in branches if branch[0]]
        
        return jsonify({
            'students': students,
            'branches': branch_list,
            'total': students_pagination.total,
            'pages': students_pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get students: {str(e)}'}), 500

@admin_bp.route('/jobs', methods=['GET'])
def get_all_jobs():
    try:
        if not is_admin():
            return jsonify({'error': 'Not authenticated or not an admin'}), 401
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        status = request.args.get('status', 'all')  # all, active, inactive
        
        # Build query
        query = Job.query
        
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

@admin_bp.route('/skill-gaps', methods=['GET'])
def get_skill_gaps():
    try:
        if not is_admin():
            return jsonify({'error': 'Not authenticated or not an admin'}), 401
        
        # Get all student skills
        students_with_skills = StudentProfile.query.filter(
            StudentProfile.skills.isnot(None),
            StudentProfile.skills != ''
        ).all()
        
        # Aggregate skills
        all_skills = {}
        for student in students_with_skills:
            if student.skills:
                skills_list = [s.strip().lower() for s in student.skills.split(',')]
                for skill in skills_list:
                    all_skills[skill] = all_skills.get(skill, 0) + 1
        
        # Get job required skills
        jobs_with_skills = Job.query.filter(
            Job.required_skills.isnot(None),
            Job.required_skills != '',
            Job.is_active == True
        ).all()
        
        job_skills = {}
        for job in jobs_with_skills:
            if job.required_skills:
                skills_list = [s.strip().lower() for s in job.required_skills.split(',')]
                for skill in skills_list:
                    job_skills[skill] = job_skills.get(skill, 0) + 1
        
        # Find skill gaps (skills in high demand but low supply)
        skill_gaps = []
        for skill, job_count in job_skills.items():
            student_count = all_skills.get(skill, 0)
            gap_score = job_count - (student_count / len(students_with_skills) * len(jobs_with_skills) if students_with_skills else 0)
            
            if gap_score > 0:
                skill_gaps.append({
                    'skill': skill,
                    'demand': job_count,
                    'supply': student_count,
                    'gap_score': round(gap_score, 2)
                })
        
        # Sort by gap score (descending)
        skill_gaps.sort(key=lambda x: x['gap_score'], reverse=True)
        
        return jsonify({
            'skill_gaps': skill_gaps[:20],  # Top 20 skill gaps
            'total_students_analyzed': len(students_with_skills),
            'total_jobs_analyzed': len(jobs_with_skills)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get skill gaps: {str(e)}'}), 500

@admin_bp.route('/placement-trends', methods=['GET'])
def get_placement_trends():
    try:
        if not is_admin():
            return jsonify({'error': 'Not authenticated or not an admin'}), 401
        
        # Placement by branch
        placement_by_branch = db.session.query(
            StudentProfile.branch,
            func.count(StudentProfile.id),
            func.avg(StudentProfile.career_score)
        ).filter(StudentProfile.branch.isnot(None))\
         .group_by(StudentProfile.branch).all()
        
        branch_trends = []
        for branch, count, avg_score in placement_by_branch:
            # Count applications for this branch
            applications_count = db.session.query(Application)\
                .join(StudentProfile)\
                .filter(StudentProfile.branch == branch)\
                .count()
            
            # Count accepted applications
            accepted_count = db.session.query(Application)\
                .join(StudentProfile)\
                .filter(
                    StudentProfile.branch == branch,
                    Application.status == 'accepted'
                ).count()
            
            placement_rate = (accepted_count / applications_count * 100) if applications_count > 0 else 0
            
            branch_trends.append({
                'branch': branch,
                'student_count': count,
                'average_career_score': round(avg_score, 2) if avg_score else 0,
                'applications_count': applications_count,
                'placement_rate': round(placement_rate, 2)
            })
        
        # Monthly registration trend (last 6 months)
        monthly_trends = []
        for i in range(5, -1, -1):
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_start = month_start - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            month_name = month_start.strftime('%b %Y')
            
            # Student registrations
            student_registrations = User.query.filter(
                User.user_type == 'student',
                User.created_at >= month_start,
                User.created_at < month_end
            ).count()
            
            # Job postings
            job_postings = Job.query.filter(
                Job.posted_date >= month_start,
                Job.posted_date < month_end
            ).count()
            
            monthly_trends.append({
                'month': month_name,
                'student_registrations': student_registrations,
                'job_postings': job_postings
            })
        
        return jsonify({
            'branch_trends': branch_trends,
            'monthly_trends': monthly_trends
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get placement trends: {str(e)}'}), 500

@admin_bp.route('/employers', methods=['GET'])
def get_all_employers():
    try:
        if not is_admin():
            return jsonify({'error': 'Not authenticated or not an admin'}), 401
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        employers_pagination = Employer.query.order_by(Employer.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        employers = [employer.to_dict() for employer in employers_pagination.items]
        
        return jsonify({
            'employers': employers,
            'total': employers_pagination.total,
            'pages': employers_pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get employers: {str(e)}'}), 500