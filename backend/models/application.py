from .user import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    
    # Application Details
    cover_letter = db.Column(db.Text)
    match_score = db.Column(db.Float)  # AI-calculated match percentage
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, shortlisted
    
    # Timestamps
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student_profile = db.relationship('StudentProfile', backref='applications')
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'job_id': self.job_id,
            'cover_letter': self.cover_letter,
            'match_score': self.match_score,
            'status': self.status,
            'applied_date': self.applied_date.isoformat() if self.applied_date else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'student': self.student_profile.to_dict() if self.student_profile else None,
            'job': self.job.to_dict() if self.job else None
        }
    
    def __repr__(self):
        return f'<Application Student:{self.student_id} Job:{self.job_id} Status:{self.status}>'