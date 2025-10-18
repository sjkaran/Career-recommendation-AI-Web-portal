# backend/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    user_type = db.Column(db.String(20), nullable=False)  # student, employer, admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    enrollment_no = db.Column(db.String(20), unique=True)
    branch = db.Column(db.String(50))
    college = db.Column(db.String(100))
    current_cgpa = db.Column(db.Float)
    skills = db.Column(db.Text)  # JSON string of skills
    career_goals = db.Column(db.Text)
    resume_file_path = db.Column(db.String(200))
    profile_completion = db.Column(db.Integer, default=0)
    career_readiness_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='student_profile')

class Employer(db.Model):
    __tablename__ = 'employers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(50))
    company_size = db.Column(db.String(20))
    website = db.Column(db.String(200))
    description = db.Column(db.Text)
    contact_person = db.Column(db.String(100))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='employer_profile')

class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employers.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(20))  # internship, full_time, part_time
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    skills_required = db.Column(db.Text)  # JSON string
    location = db.Column(db.String(100))
    salary_range = db.Column(db.String(50))
    application_deadline = db.Column(db.DateTime)
    vacancies = db.Column(db.Integer, default=1)
    category = db.Column(db.String(50))
    experience_required = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employer = db.relationship('Employer', backref='jobs')

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    status = db.Column(db.String(20), default='applied')  # applied, under_review, interview, rejected, accepted
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    cover_letter = db.Column(db.Text)
    match_score = db.Column(db.Integer)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student = db.relationship('StudentProfile', backref='applications')
    job = db.relationship('Job', backref='applications')