from .user import db
from datetime import datetime

class Employer(db.Model):
    __tablename__ = 'employers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Company Information
    company_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    industry = db.Column(db.String(100))
    website = db.Column(db.String(200))
    description = db.Column(db.Text)
    address = db.Column(db.Text)
    
    # Verification
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = db.relationship('Job', backref='employer', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'industry': self.industry,
            'website': self.website,
            'description': self.description,
            'address': self.address,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Employer {self.company_name}>'