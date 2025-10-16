from utils.helpers import calculate_career_readiness_score

def calculate_comprehensive_score(student):
    """
    Calculate comprehensive career readiness score with detailed breakdown
    """
    base_score = calculate_career_readiness_score(student)
    
    breakdown = {
        'academic_performance': 0,
        'technical_skills': 0,
        'practical_experience': 0,
        'certifications': 0,
        'profile_strength': 0
    }
    
    # Academic Performance (CGPA based)
    if student.cgpa:
        if student.cgpa >= 9.0:
            breakdown['academic_performance'] = 100
        elif student.cgpa >= 8.0:
            breakdown['academic_performance'] = 85
        elif student.cgpa >= 7.0:
            breakdown['academic_performance'] = 70
        elif student.cgpa >= 6.0:
            breakdown['academic_performance'] = 55
        else:
            breakdown['academic_performance'] = 40
    
    # Technical Skills (based on number and relevance)
    if student.skills:
        skills_count = len(student.skills.split(','))
        if skills_count >= 8:
            breakdown['technical_skills'] = 100
        elif skills_count >= 5:
            breakdown['technical_skills'] = 75
        elif skills_count >= 3:
            breakdown['technical_skills'] = 50
        else:
            breakdown['technical_skills'] = 25
    
    # Practical Experience
    if student.internship_experience:
        breakdown['practical_experience'] = 80
        if len(student.internship_experience) > 150:  # Detailed description
            breakdown['practical_experience'] = 100
    else:
        breakdown['practical_experience'] = 30
    
    # Certifications
    if student.certifications:
        cert_count = len(student.certifications.split(','))
        breakdown['certifications'] = min(cert_count * 25, 100)  # 4 certs for full score
    
    # Profile Strength (completeness)
    breakdown['profile_strength'] = student.profile_completeness or 0
    
    return {
        'overall_score': base_score,
        'breakdown': breakdown,
        'level': get_career_level(base_score)
    }

def get_career_level(score):
    """
    Get career readiness level based on score
    """
    if score >= 85:
        return 'Excellent'
    elif score >= 70:
        return 'Good'
    elif score >= 55:
        return 'Average'
    elif score >= 40:
        return 'Needs Improvement'
    else:
        return 'Beginner'

def update_student_career_score(student):
    """
    Update student's career score in database
    """
    try:
        from models.user import db
        score_data = calculate_comprehensive_score(student)
        student.career_score = score_data['overall_score']
        db.session.commit()
        return score_data
    except Exception as e:
        print(f"Error updating career score: {e}")
        return None