from utils.helpers import calculate_career_readiness_score

def get_career_recommendations(student):
    """
    Get personalized career recommendations for a student
    """
    try:
        recommendations = {
            'career_paths': [],
            'skill_gaps': [],
            'suggested_courses': [],
            'improvement_areas': []
        }
        
        # Analyze student's current profile
        skills = student.skills.split(',') if student.skills else []
        interests = student.interests.split(',') if student.interests else []
        branch = student.branch.lower() if student.branch else ''
        
        # Get career paths based on branch and skills
        recommendations['career_paths'] = get_career_paths(branch, skills, interests)
        
        # Identify skill gaps
        recommendations['skill_gaps'] = identify_skill_gaps(branch, skills)
        
        # Suggest courses to fill gaps
        recommendations['suggested_courses'] = suggest_courses(recommendations['skill_gaps'])
        
        # Identify improvement areas
        recommendations['improvement_areas'] = identify_improvement_areas(student)
        
        return recommendations
        
    except Exception as e:
        print(f"Error in career recommendations: {e}")
        return {
            'career_paths': [],
            'skill_gaps': [],
            'suggested_courses': [],
            'improvement_areas': []
        }

def get_career_paths(branch, skills, interests):
    """
    Suggest career paths based on branch, skills, and interests
    """
    career_paths = []
    
    # Branch-based career paths
    branch_careers = {
        'cse': [
            {'title': 'Software Developer', 'demand': 'High', 'avg_salary': '6-12 LPA'},
            {'title': 'Data Scientist', 'demand': 'High', 'avg_salary': '8-15 LPA'},
            {'title': 'Web Developer', 'demand': 'Medium', 'avg_salary': '4-8 LPA'},
            {'title': 'AI/ML Engineer', 'demand': 'High', 'avg_salary': '10-18 LPA'},
            {'title': 'DevOps Engineer', 'demand': 'Medium', 'avg_salary': '7-12 LPA'}
        ],
        'ece': [
            {'title': 'Electronics Engineer', 'demand': 'Medium', 'avg_salary': '4-8 LPA'},
            {'title': 'Embedded Systems Engineer', 'demand': 'Medium', 'avg_salary': '5-9 LPA'},
            {'title': 'VLSI Design Engineer', 'demand': 'High', 'avg_salary': '6-12 LPA'},
            {'title': 'IoT Specialist', 'demand': 'Growing', 'avg_salary': '5-10 LPA'}
        ],
        'eee': [
            {'title': 'Electrical Engineer', 'demand': 'Medium', 'avg_salary': '4-7 LPA'},
            {'title': 'Power Systems Engineer', 'demand': 'Medium', 'avg_salary': '5-9 LPA'},
            {'title': 'Control Systems Engineer', 'demand': 'Medium', 'avg_salary': '5-8 LPA'}
        ],
        'mech': [
            {'title': 'Mechanical Design Engineer', 'demand': 'Medium', 'avg_salary': '4-7 LPA'},
            {'title': 'Automobile Engineer', 'demand': 'Medium', 'avg_salary': '4-8 LPA'},
            {'title': 'Production Engineer', 'demand': 'Medium', 'avg_salary': '3-6 LPA'}
        ],
        'civil': [
            {'title': 'Structural Engineer', 'demand': 'Medium', 'avg_salary': '4-7 LPA'},
            {'title': 'Construction Manager', 'demand': 'Medium', 'avg_salary': '5-9 LPA'},
            {'title': 'Site Engineer', 'demand': 'High', 'avg_salary': '3-6 LPA'}
        ]
    }
    
    # Add branch-based careers
    if branch in branch_careers:
        career_paths.extend(branch_careers[branch])
    
    # Skill-based additional careers
    skill_based_careers = []
    if any(skill in ['python', 'java', 'javascript'] for skill in skills):
        skill_based_careers.extend([
            {'title': 'Full Stack Developer', 'demand': 'High', 'avg_salary': '6-12 LPA'},
            {'title': 'Mobile App Developer', 'demand': 'Medium', 'avg_salary': '5-10 LPA'}
        ])
    
    if any(skill in ['machine learning', 'data science', 'ai'] for skill in skills):
        skill_based_careers.extend([
            {'title': 'Data Analyst', 'demand': 'High', 'avg_salary': '5-9 LPA'},
            {'title': 'Business Analyst', 'demand': 'Medium', 'avg_salary': '6-11 LPA'}
        ])
    
    # Remove duplicates
    seen_titles = set()
    unique_careers = []
    
    for career in career_paths + skill_based_careers:
        if career['title'] not in seen_titles:
            unique_careers.append(career)
            seen_titles.add(career['title'])
    
    return unique_careers[:6]  # Return top 6 careers

def identify_skill_gaps(branch, current_skills):
    """
    Identify skill gaps based on branch and current skills
    """
    expected_skills = {
        'cse': ['python', 'java', 'data structures', 'algorithms', 'database', 'git'],
        'ece': ['c', 'c++', 'embedded systems', 'digital electronics', 'matlab'],
        'eee': ['matlab', 'simulink', 'power systems', 'control systems', 'circuit analysis'],
        'mech': ['autocad', 'solidworks', 'thermodynamics', 'manufacturing', 'fea'],
        'civil': ['autocad', 'staad pro', 'construction management', 'surveying']
    }
    
    skill_gaps = []
    
    if branch in expected_skills:
        for skill in expected_skills[branch]:
            if skill not in [s.lower() for s in current_skills]:
                skill_gaps.append(skill)
    
    # Add industry-demanded skills
    industry_demanded = ['communication', 'problem solving', 'teamwork', 'project management']
    for skill in industry_demanded:
        if skill not in [s.lower() for s in current_skills]:
            skill_gaps.append(skill)
    
    return skill_gaps[:5]  # Return top 5 skill gaps

def suggest_courses(skill_gaps):
    """
    Suggest courses to fill skill gaps
    """
    course_suggestions = {
        'python': 'Python for Beginners - Coursera',
        'java': 'Java Programming - Udemy',
        'data structures': 'Data Structures & Algorithms - GeeksforGeeks',
        'communication': 'Effective Communication - LinkedIn Learning',
        'machine learning': 'Machine Learning A-Z - Udemy',
        'web development': 'The Complete Web Developer Bootcamp',
        'database': 'SQL for Data Science - Coursera',
        'git': 'Git Complete Guide - Udemy',
        'problem solving': 'Problem Solving Techniques - HackerRank'
    }
    
    courses = []
    for gap in skill_gaps:
        if gap in course_suggestions:
            courses.append({
                'skill': gap,
                'course': course_suggestions[gap],
                'platform': course_suggestions[gap].split(' - ')[1] if ' - ' in course_suggestions[gap] else 'Various'
            })
    
    return courses

def identify_improvement_areas(student):
    """
    Identify areas for improvement based on student profile
    """
    improvement_areas = []
    
    # Check profile completeness
    if student.profile_completeness < 80:
        improvement_areas.append('Complete your profile to get better recommendations')
    
    # Check skills
    if not student.skills or len(student.skills.split(',')) < 3:
        improvement_areas.append('Add more technical skills to your profile')
    
    # Check projects
    if not student.projects:
        improvement_areas.append('Add project details to showcase your work')
    
    # Check internship experience
    if not student.internship_experience:
        improvement_areas.append('Consider applying for internships to gain experience')
    
    # Check CGPA
    if student.cgpa and student.cgpa < 7.0:
        improvement_areas.append('Focus on improving your academic performance')
    
    return improvement_areas[:3]  # Return top 3 improvement areas