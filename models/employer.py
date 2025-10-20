"""
Employer model with company information and verification status
"""
import json
from datetime import datetime
from database import execute_query, fetch_one, fetch_all


class Employer:
    """Employer model with company information and verification status"""
    
    COMPANY_SIZES = ['1-10', '11-50', '51-200', '201-500', '501-1000', '1000+']
    
    def __init__(self, id=None, user_id=None, company_name=None, 
                 company_description=None, website=None, industry=None,
                 company_size=None, is_verified=False, created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.company_name = company_name
        self.company_description = company_description
        self.website = website
        self.industry = industry
        self.company_size = company_size
        self.is_verified = is_verified
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def create(cls, user_id, company_name, **kwargs):
        """Create a new employer profile"""
        # Check if employer profile already exists for this user
        existing_employer = cls.find_by_user_id(user_id)
        if existing_employer:
            raise ValueError("Employer profile already exists for this user")
        
        employer = cls(user_id=user_id, company_name=company_name, **kwargs)
        employer._save_to_db()
        return employer
    
    @classmethod
    def find_by_id(cls, employer_id):
        """Find employer by ID"""
        query = 'SELECT * FROM employers WHERE id = ?'
        row = fetch_one(query, (employer_id,))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def find_by_user_id(cls, user_id):
        """Find employer by user ID"""
        query = 'SELECT * FROM employers WHERE user_id = ?'
        row = fetch_one(query, (user_id,))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_all_employers(cls, verified_only=False, limit=None, offset=None):
        """Get all employers with optional filtering"""
        query = 'SELECT * FROM employers'
        params = []
        
        if verified_only:
            query += ' WHERE is_verified = 1'
        
        query += ' ORDER BY created_at DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
            if offset:
                query += ' OFFSET ?'
                params.append(offset)
        
        rows = fetch_all(query, params if params else None)
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def search_by_industry(cls, industry):
        """Search employers by industry"""
        query = 'SELECT * FROM employers WHERE industry LIKE ? ORDER BY company_name'
        rows = fetch_all(query, (f'%{industry}%',))
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def _from_row(cls, row):
        """Create Employer instance from database row"""
        return cls(
            id=row['id'],
            user_id=row['user_id'],
            company_name=row['company_name'],
            company_description=row['company_description'],
            website=row['website'],
            industry=row['industry'],
            company_size=row['company_size'],
            is_verified=bool(row['is_verified']),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def update(self, **kwargs):
        """Update employer fields"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
        self._update_in_db()
    
    def verify(self):
        """Mark employer as verified"""
        self.is_verified = True
        self.updated_at = datetime.utcnow()
        query = 'UPDATE employers SET is_verified = 1, updated_at = ? WHERE id = ?'
        execute_query(query, (self.updated_at, self.id))
    
    def unverify(self):
        """Mark employer as unverified"""
        self.is_verified = False
        self.updated_at = datetime.utcnow()
        query = 'UPDATE employers SET is_verified = 0, updated_at = ? WHERE id = ?'
        execute_query(query, (self.updated_at, self.id))
    
    def _save_to_db(self):
        """Save new employer to database"""
        query = '''
            INSERT INTO employers 
            (user_id, company_name, company_description, website, industry, 
             company_size, is_verified, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        now = datetime.utcnow()
        self.created_at = now
        self.updated_at = now
        
        cursor = execute_query(query, (
            self.user_id, self.company_name, self.company_description,
            self.website, self.industry, self.company_size,
            self.is_verified, self.created_at, self.updated_at
        ))
        
        self.id = cursor.lastrowid
    
    def _update_in_db(self):
        """Update existing employer in database"""
        query = '''
            UPDATE employers SET
            company_name = ?, company_description = ?, website = ?, 
            industry = ?, company_size = ?, updated_at = ?
            WHERE id = ?
        '''
        
        execute_query(query, (
            self.company_name, self.company_description, self.website,
            self.industry, self.company_size, self.updated_at, self.id
        ))
    
    def validate(self):
        """Validate employer data"""
        errors = []
        
        if not self.company_name or len(self.company_name.strip()) == 0:
            errors.append("Company name is required")
        
        if self.website and not self._is_valid_url(self.website):
            errors.append("Website must be a valid URL")
        
        if self.company_size and self.company_size not in self.COMPANY_SIZES:
            errors.append(f"Company size must be one of: {self.COMPANY_SIZES}")
        
        return errors
    
    def _is_valid_url(self, url):
        """Basic URL validation"""
        return url.startswith(('http://', 'https://')) and '.' in url
    
    def get_job_postings(self):
        """Get all job postings for this employer"""
        from .job_posting import JobPosting
        return JobPosting.get_by_employer_id(self.id)
    
    def get_active_job_count(self):
        """Get count of active job postings"""
        query = 'SELECT COUNT(*) as count FROM job_postings WHERE employer_id = ? AND status = "active"'
        row = fetch_one(query, (self.id,))
        return row['count'] if row else 0
    
    def to_dict(self):
        """Convert employer to dictionary representation"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'company_description': self.company_description,
            'website': self.website,
            'industry': self.industry,
            'company_size': self.company_size,
            'is_verified': self.is_verified,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def __repr__(self):
        verified_status = "Verified" if self.is_verified else "Unverified"
        return f'<Employer {self.company_name} ({verified_status})>'