"""
Simplified Demo Data Generator for BPUT Career Platform
Generates realistic demo data for demonstration purposes
"""

from models.user import User, db
from models.profile import StudentProfile
from models.employer import Employer
from models.job import Job
from models.application import Application
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import random

# Demo data constants
BRANCHES = ['CSE', 'IT', 'ECE', 'EEE', 'MECH', 'CIVIL']
COLLEGES = ['CET Bhubaneswar', 'GITA', 'GIET Gunupur', 'ITER', 'SOA']
COMPANIES = ['TCS', 'Infosys', 'Wipro', 'Cognizant', 'Accenture', 'Amazon', 'Microsoft', 'Google']
JOB_TYPES = ['internship', 'full-time', 'part-time']
LOCATIONS = ['Bhubaneswar', 'Bangalore', 'Hyderabad', 'Remote', 'Cuttack']

SKILLS = [
    'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'MySQL', 'MongoDB',
    'Machine Learning', 'Data Science', 'AWS', 'Docker', 'Kubernetes',
    'C++', 'HTML', 'CSS', 'Angular', 'Vue.js', 'Django', 'Flask'
]

def generate_demo_data():
    """Generate all demo data"""
    
    try:
        # Clear existing data
        Application.query.delete()
        Job.query.delete()
        StudentProfile.query.delete()
        Employer.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Create admin user
        admin = User(
            email='admin@bput.ac.in',
            user_type='admin',
            is_active=True,
            created_at=datetime.utcnow()
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.flush()
        
        # Generate employers
        employers = []
        for i in range(10):
            user = User(
                email=f'employer{i+1}@company.com' if i > 0 else 'employer@company.com',
                user_type='employer',
                is_active=True,
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
            )
            user.set_password('demo123')
            db.session.add(user)
            db.session.flush()
            
            employer = Employer(
                user_id=user.id,
                company_name=COMPANIES[i % len(COMPANIES)],
                contact_person=f'HR Manager {i+1}',
                phone=f'+91-98765{10000+i}',
                industry='IT Services',
                website=f'https://www.{COMPANIES[i % len(COMPANIES)].lower()}.com',
                description=f'{COMPANIES[i % len(COMPANIES)]} is a leading technology company.',
                address=f'{LOCATIONS[i % len(LOCATIONS)]}, India',
                is_verified=True,
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
            )
            db.session.add(employer)
            employers.append(employer)
        
        db.session.flush()
        
        # Generate students
        students = []
        for i in range(50):
            user = User(
                email=f'student{i+1}@bput.ac.in' if i > 0 else 'student@bput.ac.in',
                user_type='student',
                is_active=True,
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 730))
            )
            user.set_password('demo123')
            db.session.add(user)
            db.session.flush()
            
            branch = random.choice(BRANCHES)
            student_skills = random.sample(SKILLS, random.randint(4, 8))
            
            student = StudentProfile(
                user_id=user.id,
                full_name=f'Student {i+1}',
                phone=f'+91-98765{20000+i}',
                college_name=random.choice(COLLEGES),
                branch=branch,
                semester=random.randint(4, 8),
                cgpa=round(random.uniform(6.0, 9.5), 2),
                graduation_year=random.choice([2024, 2025, 2026]),
                skills=','.join(student_skills),
                interests=f'{branch} Development,AI,Software Engineering',
                certifications='AWS Certified,Python Certification',
                projects='E-commerce Website,Machine Learning Project',
                internship_experience=f'Intern at {random.choice(COMPANIES)}' if random.random() > 0.3 else None,
                career_score=round(random.uniform(60, 95), 2),
                profile_completeness=round(random.uniform(70, 100), 2),
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 730))
            )
            db.session.add(student)
            students.append(student)
        
        db.session.flush()
        
        # Generate jobs
        jobs = []
        job_titles = {
            'CSE': ['Software Engineer', 'Web Developer', 'Data Scientist', 'ML Engineer'],
            'IT': ['System Administrator', 'Network Engineer', 'IT Support'],
            'ECE': ['Electronics Engineer', 'Embedded Systems Engineer'],
            'EEE': ['Electrical Engineer', 'Power Systems Engineer'],
            'MECH': ['Mechanical Engineer', 'Design Engineer'],
            'CIVIL': ['Civil Engineer', 'Site Engineer']
        }
        
        for i in range(30):
            employer = random.choice(employers)
            branch = random.choice(BRANCHES)
            title = random.choice(job_titles.get(branch, ['Software Engineer']))
            job_skills = random.sample(SKILLS, random.randint(3, 6))
            
            job = Job(
                employer_id=employer.id,
                title=title,
                company_name=employer.company_name,
                description=f'We are looking for a talented {title} to join our team.',
                requirements=f'Strong knowledge of {", ".join(job_skills[:3])}',
                required_skills=','.join(job_skills),
                location=random.choice(LOCATIONS),
                salary=f'{random.randint(3, 12)}-{random.randint(3, 12)+2} LPA',
                job_type=random.choice(JOB_TYPES),
                category=branch,
                application_deadline=datetime.utcnow() + timedelta(days=random.randint(30, 90)),
                vacancies=random.randint(1, 10),
                is_active=True,
                posted_date=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(job)
            jobs.append(job)
        
        db.session.flush()
        
        # Generate applications
        applications = []
        for student in students[:40]:  # 40 out of 50 students have applications
            num_applications = random.randint(1, 5)
            applied_jobs = random.sample(jobs, min(num_applications, len(jobs)))
            
            for job in applied_jobs:
                # Calculate match score based on skills
                student_skills_set = set(student.skills.split(','))
                job_skills_set = set(job.required_skills.split(','))
                common_skills = len(student_skills_set.intersection(job_skills_set))
                total_skills = len(student_skills_set.union(job_skills_set))
                match_score = (common_skills / total_skills * 100) if total_skills > 0 else 50
                
                application = Application(
                    student_id=student.id,
                    job_id=job.id,
                    cover_letter='I am interested in this position and believe I am a good fit.',
                    match_score=round(match_score, 2),
                    status=random.choice(['pending', 'pending', 'pending', 'accepted', 'rejected']),
                    applied_date=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                db.session.add(application)
                applications.append(application)
        
        db.session.commit()
        
        return {
            'students': len(students),
            'employers': len(employers),
            'jobs': len(jobs),
            'applications': len(applications)
        }
        
    except Exception as e:
        db.session.rollback()
        print(f"Error generating demo data: {e}")
        raise e