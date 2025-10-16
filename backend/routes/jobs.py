from flask import Blueprint, request, jsonify
from models.job import Job, db
from models.application import Application
from sqlalchemy import or_
import math

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/jobs', methods=['GET'])
def get_all_jobs():
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 12))
        search = request.args.get('search', '')
        job_type = request.args.get('type', '')
        category = request.args.get('category', '')
        location = request.args.get('location', '')
        
        # Build base query for active jobs
        query = Job.query.filter_by(is_active=True)
        
        # Apply filters
        if search:
            search_filter = or_(
                Job.title.ilike(f'%{search}%'),
                Job.description.ilike(f'%{search}%'),
                Job.company_name.ilike(f'%{search}%'),
                Job.required_skills.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        if job_type:
            query = query.filter(Job.job_type == job_type)
        
        if category:
            query = query.filter(Job.category.ilike(f'%{category}%'))
        
        if location:
            query = query.filter(Job.location.ilike(f'%{location}%'))
        
        # Get total count before pagination
        total_jobs = query.count()
        total_pages = math.ceil(total_jobs / per_page)
        
        # Apply pagination
        jobs = query.order_by(Job.posted_date.desc())\
                   .offset((page - 1) * per_page)\
                   .limit(per_page).all()
        
        # Get unique values for filters
        job_types = db.session.query(Job.job_type)\
            .filter(Job.job_type.isnot(None), Job.is_active == True)\
            .distinct().all()
        
        categories = db.session.query(Job.category)\
            .filter(Job.category.isnot(None), Job.is_active == True)\
            .distinct().all()
        
        locations = db.session.query(Job.location)\
            .filter(Job.location.isnot(None), Job.is_active == True)\
            .distinct().all()
        
        return jsonify({
            'jobs': [job.to_dict() for job in jobs],
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_jobs': total_jobs,
                'total_pages': total_pages
            },
            'filters': {
                'job_types': [jt[0] for jt in job_types if jt[0]],
                'categories': [cat[0] for cat in categories if cat[0]],
                'locations': [loc[0] for loc in locations if loc[0]]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get jobs: {str(e)}'}), 500

@jobs_bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_job_details(job_id):
    try:
        job = Job.query.filter_by(id=job_id, is_active=True).first()
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Get similar jobs (same category or similar skills)
        similar_jobs = []
        if job.category:
            similar = Job.query.filter(
                Job.id != job_id,
                Job.is_active == True,
                Job.category == job.category
            ).limit(4).all()
            similar_jobs = [sj.to_dict() for sj in similar]
        
        job_data = job.to_dict()
        
        return jsonify({
            'job': job_data,
            'similar_jobs': similar_jobs
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get job details: {str(e)}'}), 500

@jobs_bp.route('/job-stats', methods=['GET'])
def get_job_stats():
    try:
        # Basic job statistics for public view
        total_jobs = Job.query.filter_by(is_active=True).count()
        
        # Jobs by type
        jobs_by_type = db.session.query(
            Job.job_type,
            db.func.count(Job.id)
        ).filter(Job.is_active == True)\
         .group_by(Job.job_type).all()
        
        # Jobs by category (top categories)
        jobs_by_category = db.session.query(
            Job.category,
            db.func.count(Job.id)
        ).filter(
            Job.is_active == True,
            Job.category.isnot(None)
        ).group_by(Job.category)\
         .order_by(db.func.count(Job.id).desc())\
         .limit(10).all()
        
        # Recent jobs count (last 30 days)
        from datetime import datetime, timedelta
        recent_jobs = Job.query.filter(
            Job.is_active == True,
            Job.posted_date >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        return jsonify({
            'total_active_jobs': total_jobs,
            'recent_jobs': recent_jobs,
            'jobs_by_type': dict(jobs_by_type),
            'top_categories': dict(jobs_by_category)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get job stats: {str(e)}'}), 500