from .user import db
from datetime import datetime

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employers.id'), nullable=False)
    
    # Job Information
    title = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)  # Job requirements
    required_skills = db.Column(db.Text)  # Comma-separated: "Python,Flask,SQL"
    
    # Job Details
    location = db.Column(db.String(100))
    salary = db.Column(db.String(100))  # "3-5 LPA" or "20000/month"
    job_type = db.Column(db.String(50))  # internship, full-time, part-time
    category = db.Column(db.String(100))  # Software Development, Data Science, etc.
    
    # Application Details
    application_deadline = db.Column(db.DateTime)
    vacancies = db.Column(db.Integer, default=1)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', backref='job', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'employer_id': self.employer_id,
            'title': self.title,
            'company_name': self.company_name,
            'description': self.description,
            'requirements': self.requirements,
            'required_skills': self.required_skills.split(',') if self.required_skills else [],
            'location': self.location,
            'salary': self.salary,
            'job_type': self.job_type,
            'category': self.category,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'vacancies': self.vacancies,
            'is_active': self.is_active,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'employer': self.employer.to_dict() if self.employer else None
        }
    
    def __repr__(self):
        return f'<Job {self.title} - {self.company_name}>'