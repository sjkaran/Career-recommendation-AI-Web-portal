import os
import uuid
from werkzeug.utils import secure_filename
from config import Config

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save uploaded file with unique filename"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        
        # Secure the filename
        filename = secure_filename(unique_filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        # Ensure upload directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save file
        file.save(file_path)
        return filename
    
    return None

def calculate_career_readiness_score(student_profile, weights=None):
    """Calculate career readiness score based on multiple factors"""
    if weights is None:
        weights = Config.CAREER_SCORE_WEIGHTS
    
    score = 0.0
    
    # CGPA component (0-20 points)
    if student_profile.cgpa:
        cgpa_score = min(student_profile.cgpa / 10.0 * 20, 20)
        score += cgpa_score * weights['cgpa']
    
    # Skills count component (0-20 points)
    if student_profile.skills:
        skills_count = len(student_profile.skills.split(','))
        skills_score = min(skills_count * 2, 20)  # Max 10 skills for full points
        score += skills_score * weights['skills_count']
    
    # Certifications component (0-15 points)
    if student_profile.certifications:
        cert_count = len(student_profile.certifications.split(','))
        cert_score = min(cert_count * 3, 15)  # Max 5 certs for full points
        score += cert_score * weights['certifications']
    
    # Projects component (0-15 points)
    if student_profile.projects:
        # Simple check - if projects exist, give points
        projects_score = 10  # Base score for having projects
        if len(student_profile.projects) > 200:  # More detailed projects
            projects_score = 15
        score += projects_score * weights['projects']
    
    # Internship experience component (0-20 points)
    if student_profile.internship_experience:
        internship_score = 15  # Base score for having internship
        if len(student_profile.internship_experience) > 100:  # Detailed experience
            internship_score = 20
        score += internship_score * weights['internship_experience']
    
    # Profile completeness component (0-10 points)
    profile_complete_score = student_profile.profile_completeness * 0.1
    score += profile_complete_score * weights['profile_completeness']
    
    return min(round(score, 2), 100.0)

def skills_similarity(student_skills, job_skills):
    """Calculate similarity between student skills and job required skills"""
    if not student_skills or not job_skills:
        return 0.0
    
    # Convert comma-separated strings to sets
    student_skill_set = set([s.strip().lower() for s in student_skills.split(',')])
    job_skill_set = set([s.strip().lower() for s in job_skills.split(',')])
    
    # Calculate Jaccard similarity
    if not student_skill_set or not job_skill_set:
        return 0.0
    
    intersection = len(student_skill_set.intersection(job_skill_set))
    union = len(student_skill_set.union(job_skill_set))
    
    similarity = intersection / union if union > 0 else 0.0
    return round(similarity * 100, 2)