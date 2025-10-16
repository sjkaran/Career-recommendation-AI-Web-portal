from .user import db
from datetime import datetime

class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Personal Information
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    
    # Academic Information
    college_name = db.Column(db.String(200), default='BPUT Affiliated College')
    branch = db.Column(db.String(50))  # CSE, EEE, ECE, etc.
    semester = db.Column(db.Integer)
    cgpa = db.Column(db.Float)
    graduation_year = db.Column(db.Integer)
    
    # Skills and Interests
    skills = db.Column(db.Text)  # Comma-separated: "Python,Java,ML"
    interests = db.Column(db.Text)  # Career interests
    certifications = db.Column(db.Text)  # Comma-separated certifications
    projects = db.Column(db.Text)  # Project descriptions
    
    # Experience
    internship_experience = db.Column(db.Text)
    work_experience = db.Column(db.Text)
    
    # Files and Scores
    resume_path = db.Column(db.String(500))
    career_score = db.Column(db.Float, default=0.0)
    profile_completeness = db.Column(db.Float, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'phone': self.phone,
            'college_name': self.college_name,
            'branch': self.branch,
            'semester': self.semester,
            'cgpa': self.cgpa,
            'graduation_year': self.graduation_year,
            'skills': self.skills.split(',') if self.skills else [],
            'interests': self.interests.split(',') if self.interests else [],
            'certifications': self.certifications.split(',') if self.certifications else [],
            'projects': self.projects,
            'internship_experience': self.internship_experience,
            'work_experience': self.work_experience,
            'resume_path': self.resume_path,
            'career_score': self.career_score,
            'profile_completeness': self.profile_completeness,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def calculate_profile_completeness(self):
        """Calculate how complete the student profile is"""
        fields = [
            self.full_name, self.phone, self.branch, self.semester, 
            self.cgpa, self.skills, self.interests
        ]
        completed = sum(1 for field in fields if field)
        total = len(fields)
        self.profile_completeness = (completed / total) * 100
        return self.profile_completeness
    
    def __repr__(self):
        return f'<StudentProfile {self.full_name}>'