from models.job import Job
from models.profile import StudentProfile
from utils.helpers import skills_similarity, calculate_career_readiness_score
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def calculate_job_match_score(student, job):
    """
    Calculate comprehensive match score between student and job
    """
    base_score = 0.0
    
    # 1. Skills Match (40% weight)
    skills_score = skills_similarity(student.skills, job.required_skills)
    base_score += skills_score * 0.4
    
    # 2. Career Readiness (20% weight)
    career_score = student.career_score or calculate_career_readiness_score(student)
    base_score += (career_score / 100) * 20  # Convert to 0-20 scale
    
    # 3. Field/Branch Match (15% weight)
    if student.branch and job.category:
        branch_field_map = {
            'cse': ['software development', 'data science', 'web development', 'ai/ml'],
            'ece': ['electronics', 'embedded systems', 'iot', 'hardware'],
            'eee': ['electrical', 'power systems', 'energy', 'automation'],
            'mech': ['mechanical', 'automobile', 'manufacturing', 'design'],
            'civil': ['construction', 'structural', 'environmental', 'transportation']
        }
        
        student_branch = student.branch.lower()
        job_category = job.category.lower()
        
        if student_branch in branch_field_map:
            if any(field in job_category for field in branch_field_map[student_branch]):
                base_score += 15
    
    # 4. Experience Level (15% weight)
    if student.internship_experience:
        # Simple check: if student has internship experience, they get points
        base_score += 10
        if len(student.internship_experience) > 100:  # Detailed experience
            base_score += 5
    
    # 5. CGPA Consideration (10% weight)
    if student.cgpa and student.cgpa >= 7.5:
        base_score += 10
    elif student.cgpa and student.cgpa >= 6.0:
        base_score += 5
    
    return min(round(base_score, 2), 100.0)

def get_job_recommendations(student, limit=10):
    """
    Get job recommendations for a student with match scores
    """
    try:
        # Get all active jobs
        active_jobs = Job.query.filter_by(is_active=True).all()
        
        recommendations = []
        
        for job in active_jobs:
            match_score = calculate_job_match_score(student, job)
            
            # Only recommend jobs with reasonable match score
            if match_score >= 30:  # Minimum 30% match
                job_data = job.to_dict()
                job_data['match_score'] = match_score
                job_data['match_breakdown'] = get_match_breakdown(student, job)
                
                recommendations.append(job_data)
        
        # Sort by match score (descending)
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        return recommendations[:limit]
        
    except Exception as e:
        print(f"Error in job recommendations: {e}")
        return []

def get_match_breakdown(student, job):
    """
    Get detailed breakdown of match factors
    """
    breakdown = {
        'skills_match': skills_similarity(student.skills, job.required_skills),
        'career_readiness': student.career_score or calculate_career_readiness_score(student),
        'field_alignment': 0,
        'experience_level': 0,
        'academic_performance': 0
    }
    
    # Field alignment
    if student.branch and job.category:
        student_branch = student.branch.lower()
        job_category = job.category.lower()
        
        field_keywords = {
            'cse': ['software', 'developer', 'programmer', 'data', 'ai', 'ml', 'web'],
            'ece': ['electronics', 'embedded', 'hardware', 'circuit', 'communication'],
            'eee': ['electrical', 'power', 'energy', 'control', 'systems'],
            'mech': ['mechanical', 'design', 'manufacturing', 'automobile', 'cad'],
            'civil': ['civil', 'construction', 'structural', 'environmental']
        }
        
        if student_branch in field_keywords:
            if any(keyword in job_category for keyword in field_keywords[student_branch]):
                breakdown['field_alignment'] = 100
    
    # Experience level
    if student.internship_experience:
        breakdown['experience_level'] = 80
        if len(student.internship_experience) > 100:
            breakdown['experience_level'] = 100
    
    # Academic performance
    if student.cgpa:
        if student.cgpa >= 8.5:
            breakdown['academic_performance'] = 100
        elif student.cgpa >= 7.0:
            breakdown['academic_performance'] = 75
        elif student.cgpa >= 6.0:
            breakdown['academic_performance'] = 50
        else:
            breakdown['academic_performance'] = 25
    
    return breakdown

def advanced_skills_matching(student_skills, job_skills):
    """
    Advanced skills matching using TF-IDF and cosine similarity
    """
    try:
        if not student_skills or not job_skills:
            return 0.0
        
        # Convert to lists
        student_skill_list = [s.strip().lower() for s in student_skills.split(',')]
        job_skill_list = [s.strip().lower() for s in job_skills.split(',')]
        
        # Create documents for TF-IDF
        student_doc = ' '.join(student_skill_list)
        job_doc = ' '.join(job_skill_list)
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([student_doc, job_doc])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        
        return round(similarity[0][0] * 100, 2)
        
    except Exception as e:
        print(f"Error in advanced skills matching: {e}")
        return skills_similarity(student_skills, job_skills)  # Fallback to basic matching