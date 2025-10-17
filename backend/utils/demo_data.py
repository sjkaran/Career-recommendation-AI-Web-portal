"""
Module: demo_data.py
Description: Generate comprehensive demo data for BPUT Career Platform
Author: AI Assistant for BPUT Career Platform
Date: 2025-01-20
Dependencies: Faker, datetime, random
"""

import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.exc import IntegrityError
import json

# Initialize Faker with Indian locale
fake = Faker('en_IN')

# BPUT-specific data
BPUT_BRANCHES = [
    'Computer Science & Engineering',
    'Electronics & Communication Engineering', 
    'Electrical & Electronics Engineering',
    'Mechanical Engineering',
    'Civil Engineering',
    'Information Technology',
    'Master of Business Administration',
    'Master of Computer Applications'
]

BPUT_COLLEGES = [
    'CET, Bhubaneswar',
    'GITA, Bhubaneswar',
    'GIET, Gunupur',
    'CVRCE, Bhubaneswar',
    'ITER, Bhubaneswar',
    'SOA, Bhubaneswar',
    'SILICON, Bhubaneswar',
    'TECHNO, Bhubaneswar'
]

BPUT_DISTRICTS = [
    'Khordha', 'Cuttack', 'Puri', 'Ganjam', 'Balasore',
    'Sambalpur', 'Bhadrak', 'Jajpur', 'Kendrapara', 'Mayurbhanj'
]

TECHNICAL_SKILLS = [
    'Python', 'Java', 'JavaScript', 'C++', 'C', 'C#', 'PHP', 'Ruby',
    'React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring', 'Node.js',
    'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle',
    'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes',
    'Machine Learning', 'Data Science', 'AI', 'Deep Learning',
    'TensorFlow', 'PyTorch', 'scikit-learn', 'Pandas', 'NumPy'
]

SOFT_SKILLS = [
    'Communication', 'Leadership', 'Teamwork', 'Problem Solving',
    'Critical Thinking', 'Time Management', 'Adaptability',
    'Creativity', 'Work Ethic', 'Attention to Detail'
]

INDUSTRY_SECTORS = [
    'IT Services', 'Software Development', 'Core Engineering',
    'Manufacturing', 'Construction', 'Healthcare', 'Education',
    'Banking & Finance', 'E-commerce', 'Startups'
]

JOB_TITLES = {
    'Computer Science & Engineering': [
        'Software Engineer', 'Web Developer', 'Full Stack Developer',
        'Data Scientist', 'Machine Learning Engineer', 'DevOps Engineer',
        'Backend Developer', 'Frontend Developer', 'Mobile App Developer'
    ],
    'Electronics & Communication Engineering': [
        'Electronics Engineer', 'Embedded Systems Engineer',
        'VLSI Design Engineer', 'Communication Engineer',
        'Network Engineer', 'Hardware Engineer'
    ],
    'Electrical & Electronics Engineering': [
        'Electrical Engineer', 'Power Systems Engineer',
        'Control Systems Engineer', 'Instrumentation Engineer'
    ],
    'Mechanical Engineering': [
        'Mechanical Engineer', 'Design Engineer',
        'Production Engineer', 'Quality Engineer'
    ],
    'Civil Engineering': [
        'Civil Engineer', 'Structural Engineer',
        'Site Engineer', 'Project Engineer'
    ],
    'Information Technology': [
        'IT Support', 'System Administrator', 'Network Administrator',
        'Database Administrator', 'IT Consultant'
    ],
    'Master of Business Administration': [
        'Business Analyst', 'Marketing Manager', 'HR Manager',
        'Operations Manager', 'Financial Analyst'
    ],
    'Master of Computer Applications': [
        'Software Developer', 'Application Developer',
        'System Analyst', 'Project Manager'
    ]
}

class DemoDataGenerator:
    """Generate comprehensive demo data for BPUT Career Platform"""
    
    def __init__(self, db, models):
        self.db = db
        self.models = models
        self.fake = Faker('en_IN')
        
    def generate_all_demo_data(self, students_count=50, employers_count=10, jobs_count=30):
        """Generate all demo data"""
        print("Generating demo data for BPUT Career Platform...")
        
        # Clear existing demo data
        self.clear_demo_data()
        
        # Generate data in order
        employers = self.generate_employers(employers_count)
        students = self.generate_students(students_count)
        jobs = self.generate_jobs(jobs_count, employers)
        applications = self.generate_applications(students, jobs)
        self.generate_placements(students, jobs)
        
        print(f"Demo data generation completed:")
        print(f"- Students: {len(students)}")
        print(f"- Employers: {len(employers)}")
        print(f"- Jobs: {len(jobs)}")
        print(f"- Applications: {len(applications)}")
        
        return {
            'students': students,
            'employers': employers,
            'jobs': jobs,
            'applications': applications
        }
    
    def clear_demo_data(self):
        """Clear existing demo data"""
        try:
            # Delete in correct order to maintain foreign key constraints
            self.models.Application.query.delete()
            self.models.Job.query.delete()
            self.models.StudentProfile.query.delete()
            self.models.Employer.query.delete()
            self.models.User.query.delete()
            
            self.db.session.commit()
            print("Existing demo data cleared")
        except Exception as e:
            self.db.session.rollback()
            print(f"Error clearing demo data: {e}")
    
    def generate_employers(self, count=10):
        """Generate employer demo data"""
        employers = []
        
        company_names = [
            'Infosys Odisha', 'TCS Bhubaneswar', 'Wipro Odisha', 'Tech Mahindra',
            'Capgemini India', 'Accenture', 'Cognizant', 'IBM India',
            'Microsoft India', 'Google India', 'Amazon India', 'Oracle India',
            'Intel Odisha', 'HCL Technologies', 'L&T Infotech'
        ]
        
        for i in range(count):
            try:
                user = self.models.User(
                    username=f'employer_{i+1}',
                    email=self.fake.company_email(),
                    password_hash='demo123',  # In real app, use proper hashing
                    user_type='employer',
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                self.db.session.add(user)
                self.db.session.flush()  # Get user ID
                
                employer = self.models.Employer(
                    user_id=user.id,
                    company_name=company_names[i % len(company_names)],
                    industry=random.choice(INDUSTRY_SECTORS),
                    company_size=random.choice(['1-50', '51-200', '201-500', '501-1000', '1000+']),
                    website=self.fake.url(),
                    description=self.fake.text(max_nb_chars=200),
                    contact_person=self.fake.name(),
                    contact_email=user.email,
                    contact_phone=self.fake.phone_number()[:15],
                    address=self.fake.address(),
                    city='Bhubaneswar',
                    state='Odisha',
                    verified=True,
                    created_at=datetime.utcnow()
                )
                self.db.session.add(employer)
                employers.append(employer)
                
            except IntegrityError:
                self.db.session.rollback()
                continue
        
        self.db.session.commit()
        print(f"Generated {len(employers)} employers")
        return employers
    
    def generate_students(self, count=50):
        """Generate student demo data"""
        students = []
        
        for i in range(count):
            try:
                user = self.models.User(
                    username=f'student_{i+1}',
                    email=self.fake.email(),
                    password_hash='demo123',  # In real app, use proper hashing
                    user_type='student',
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                self.db.session.add(user)
                self.db.session.flush()
                
                branch = random.choice(BPUT_BRANCHES)
                district = random.choice(BPUT_DISTRICTS)
                cgpa = round(random.uniform(6.0, 9.5), 2)
                
                student = self.models.StudentProfile(
                    user_id=user.id,
                    full_name=self.fake.name(),
                    enrollment_no=f'BPUT{random.randint(100000, 999999)}',
                    branch=branch,
                    college=random.choice(BPUT_COLLEGES),
                    district=district,
                    current_cgpa=cgpa,
                    expected_graduation=random.randint(2024, 2026),
                    phone_number=self.fake.phone_number()[:15],
                    address=self.fake.address(),
                    bio=self.fake.text(max_nb_chars=150),
                    career_goals=self.fake.text(max_nb_chars=100),
                    preferred_locations=json.dumps([district, 'Bhubaneswar', 'Remote']),
                    skills=json.dumps(self._generate_student_skills(branch)),
                    certifications=json.dumps(self._generate_certifications()),
                    projects=json.dumps(self._generate_projects(branch)),
                    internships=json.dumps(self._generate_internships()),
                    resume_file_path=f'/resumes/student_{i+1}.pdf',
                    profile_completion=random.randint(70, 100),
                    career_readiness_score=random.randint(60, 95),
                    is_verified=True,
                    created_at=datetime.utcnow()
                )
                self.db.session.add(student)
                students.append(student)
                
            except IntegrityError:
                self.db.session.rollback()
                continue
        
        self.db.session.commit()
        print(f"Generated {len(students)} students")
        return students
    
    def generate_jobs(self, count=30, employers=None):
        """Generate job/internship demo data"""
        jobs = []
        
        job_types = ['internship', 'full_time', 'part_time']
        locations = ['Bhubaneswar', 'Remote', 'Hybrid', 'Cuttack', 'Puri']
        
        for i in range(count):
            try:
                employer = random.choice(employers) if employers else None
                if not employer:
                    continue
                
                branch = random.choice(BPUT_BRANCHES)
                job_title = random.choice(JOB_TITLES.get(branch, ['Software Engineer']))
                
                job = self.models.Job(
                    employer_id=employer.id,
                    title=job_title,
                    job_type=random.choice(job_types),
                    description=self.fake.text(max_nb_chars=500),
                    requirements=self.fake.text(max_nb_chars=300),
                    skills_required=json.dumps(self._generate_required_skills(branch)),
                    location=random.choice(locations),
                    salary_range=random.choice(['3-5 LPA', '5-8 LPA', '8-12 LPA', '12+ LPA']),
                    application_deadline=datetime.utcnow() + timedelta(days=random.randint(30, 90)),
                    vacancies=random.randint(1, 10),
                    category=branch,
                    experience_required=random.choice(['Fresher', '0-1 years', '1-2 years', '2-3 years']),
                    is_active=True,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                self.db.session.add(job)
                jobs.append(job)
                
            except Exception as e:
                print(f"Error generating job {i}: {e}")
                continue
        
        self.db.session.commit()
        print(f"Generated {len(jobs)} jobs")
        return jobs
    
    def generate_applications(self, students, jobs):
        """Generate job application demo data"""
        applications = []
        
        application_statuses = ['applied', 'under_review', 'interview', 'rejected', 'accepted']
        
        for student in students:
            # Each student applies to 2-8 random jobs
            applications_count = random.randint(2, 8)
            applied_jobs = random.sample(jobs, min(applications_count, len(jobs)))
            
            for job in applied_jobs:
                try:
                    applied_date = datetime.utcnow() - timedelta(days=random.randint(1, 60))
                    
                    # Determine status with realistic probabilities
                    status_weights = [0.4, 0.3, 0.15, 0.1, 0.05]  # applied, under_review, interview, rejected, accepted
                    status = random.choices(application_statuses, weights=status_weights)[0]
                    
                    application = self.models.Application(
                        student_id=student.id,
                        job_id=job.id,
                        status=status,
                        applied_date=applied_date,
                        cover_letter=self.fake.text(max_nb_chars=200),
                        match_score=random.randint(60, 95),
                        updated_at=applied_date
                    )
                    self.db.session.add(application)
                    applications.append(application)
                    
                except Exception as e:
                    print(f"Error generating application: {e}")
                    continue
        
        self.db.session.commit()
        print(f"Generated {len(applications)} applications")
        return applications
    
    def generate_placements(self, students, jobs):
        """Generate placement data for some students"""
        placed_students = random.sample(students, min(10, len(students) // 3))
        
        for student in placed_students:
            try:
                # Find accepted applications for this student
                accepted_app = self.models.Application.query.filter_by(
                    student_id=student.id,
                    status='accepted'
                ).first()
                
                if not accepted_app:
                    # Create a placement record
                    job = random.choice(jobs)
                    placement = self.models.Placement(
                        student_id=student.id,
                        employer_id=job.employer_id,
                        job_title=job.title,
                        salary=random.choice(['4.5 LPA', '6 LPA', '7.5 LPA', '9 LPA']),
                        placement_date=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                        placement_type='campus',
                        status='completed'
                    )
                    self.db.session.add(placement)
                    
            except Exception as e:
                print(f"Error generating placement: {e}")
                continue
        
        self.db.session.commit()
        print(f"Generated placements for {len(placed_students)} students")
    
    def _generate_student_skills(self, branch):
        """Generate realistic skills based on branch"""
        base_skills = []
        
        # Branch-specific skills
        if 'Computer' in branch or 'IT' in branch:
            base_skills.extend(random.sample([
                'Python', 'Java', 'JavaScript', 'React', 'Node.js',
                'MySQL', 'MongoDB', 'AWS', 'Docker'
            ], random.randint(4, 8)))
        elif 'Electronics' in branch:
            base_skills.extend(random.sample([
                'C++', 'Embedded Systems', 'VLSI', 'MATLAB',
                'Circuit Design', 'Digital Electronics'
            ], random.randint(3, 6)))
        elif 'Electrical' in branch:
            base_skills.extend(random.sample([
                'MATLAB', 'Simulink', 'Power Systems', 'Control Systems',
                'Electrical Machines', 'PLC'
            ], random.randint(3, 6)))
        elif 'Mechanical' in branch:
            base_skills.extend(random.sample([
                'AutoCAD', 'SolidWorks', 'CATIA', 'ANSYS',
                'Thermodynamics', 'Machine Design'
            ], random.randint(3, 6)))
        elif 'Civil' in branch:
            base_skills.extend(random.sample([
                'AutoCAD', 'STAAD Pro', 'Revit', 'ETABS',
                'Construction Management', 'Surveying'
            ], random.randint(3, 6)))
        else:  # MBA/MCA
            base_skills.extend(random.sample([
                'Project Management', 'Communication', 'Leadership',
                'Business Analysis', 'Marketing', 'Finance'
            ], random.randint(4, 7)))
        
        # Add some soft skills
        soft_skills = random.sample(SOFT_SKILLS, random.randint(2, 4))
        
        return {
            'technical': base_skills,
            'soft': soft_skills
        }
    
    def _generate_required_skills(self, branch):
        """Generate required skills for jobs based on branch"""
        if 'Computer' in branch or 'IT' in branch:
            return random.sample([
                'Python', 'Java', 'JavaScript', 'React', 'Node.js',
                'SQL', 'MongoDB', 'AWS', 'Docker', 'Git'
            ], random.randint(3, 6))
        elif 'Electronics' in branch:
            return random.sample([
                'C++', 'Embedded C', 'VLSI', 'MATLAB',
                'Circuit Design', 'PCB Design'
            ], random.randint(2, 4))
        else:
            return random.sample(TECHNICAL_SKILLS, random.randint(3, 5))
    
    def _generate_certifications(self):
        """Generate certifications for students"""
        certs = [
            'AWS Certified Cloud Practitioner',
            'Google Cloud Associate',
            'Microsoft Azure Fundamentals',
            'Python Programming Certification',
            'Java Certification',
            'Data Science Specialization',
            'Machine Learning Certification'
        ]
        return random.sample(certs, random.randint(1, 3))
    
    def _generate_projects(self, branch):
        """Generate projects for students"""
        projects = []
        
        project_templates = {
            'Computer Science & Engineering': [
                'E-commerce Website', 'Machine Learning Model', 'Mobile App',
                'Blockchain Application', 'IoT System', 'Chatbot'
            ],
            'Electronics & Communication Engineering': [
                'IoT Device', 'Robotic System', 'Communication Protocol',
                'Signal Processing Tool', 'Embedded System'
            ],
            'Electrical & Electronics Engineering': [
                'Power System Analysis', 'Motor Control System',
                'Renewable Energy System', 'Smart Grid Implementation'
            ],
            'Mechanical Engineering': [
                'CAD Model Design', 'Thermal Analysis System',
                'Automation System', 'Product Design'
            ],
            'Civil Engineering': [
                'Structural Analysis', 'Building Design',
                'Construction Planning', 'Surveying System'
            ]
        }
        
        template_projects = project_templates.get(branch, ['Academic Project'])
        
        for i in range(random.randint(1, 3)):
            project_name = f"{random.choice(template_projects)} {i+1}"
            projects.append({
                'name': project_name,
                'description': self.fake.text(max_nb_chars=100),
                'technologies': random.sample(TECHNICAL_SKILLS, random.randint(2, 4)),
                'duration': f"{random.randint(1, 6)} months"
            })
        
        return projects
    
    def _generate_internships(self):
        """Generate internship data for students"""
        internships = []
        
        companies = ['Infosys', 'TCS', 'Wipro', 'Tech Mahindra', 'Startup Inc']
        
        for i in range(random.randint(0, 2)):  # 0-2 internships
            internships.append({
                'company': random.choice(companies),
                'role': random.choice(['Intern', 'Trainee', 'Developer']),
                'duration': f"{random.randint(1, 6)} months",
                'description': self.fake.text(max_nb_chars=80)
            })
        
        return internships

def init_demo_data(db, models, students_count=50, employers_count=10, jobs_count=30):
    """
    Initialize demo data for the application
    
    Args:
        db: SQLAlchemy database instance
        models: Module containing database models
        students_count: Number of demo students to generate
        employers_count: Number of demo employers to generate  
        jobs_count: Number of demo jobs to generate
    
    Returns:
        dict: Generated demo data
    """
    generator = DemoDataGenerator(db, models)
    return generator.generate_all_demo_data(students_count, employers_count, jobs_count)

# Test function
if __name__ == "__main__":
    # This would be used for testing the demo data generator
    print("Demo Data Generator for BPUT Career Platform")
    print("Run this through Flask application context")