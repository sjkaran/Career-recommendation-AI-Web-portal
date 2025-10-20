"""
JobPosting model with requirement specifications and application tracking
"""
import json
from datetime import datetime, date
from database import execute_query, fetch_one, fetch_all


class JobPosting:
    """JobPosting model with requirement specifications"""
    
    STATUSES = ['active', 'closed', 'draft']
    EXPERIENCE_LEVELS = ['entry', 'junior', 'mid', 'senior', 'lead']
    
    def __init__(self, id=None, employer_id=None, title=None, description=None,
                 required_skills=None, preferred_qualifications=None,
                 experience_level=None, location=None, salary_range=None,
                 application_deadline=None, status='draft', created_at=None, updated_at=None):
        self.id = id
        self.employer_id = employer_id
        self.title = title
        self.description = description
        self.required_skills = required_skills or []
        self.preferred_qualifications = preferred_qualifications or []
        self.experience_level = experience_level
        self.location = location
        self.salary_range = salary_range or {}
        self.application_deadline = application_deadline
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def create(cls, employer_id, title, description, **kwargs):
        """Create a new job posting"""
        job_posting = cls(
            employer_id=employer_id,
            title=title,
            description=description,
            **kwargs
        )
        job_posting._save_to_db()
        return job_posting
    
    @classmethod
    def find_by_id(cls, job_id):
        """Find job posting by ID"""
        query = 'SELECT * FROM job_postings WHERE id = ?'
        row = fetch_one(query, (job_id,))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_by_employer_id(cls, employer_id, status=None):
        """Get all job postings for an employer"""
        query = 'SELECT * FROM job_postings WHERE employer_id = ?'
        params = [employer_id]
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        query += ' ORDER BY created_at DESC'
        
        rows = fetch_all(query, params)
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_active_jobs(cls, limit=None, offset=None):
        """Get all active job postings"""
        query = '''
            SELECT * FROM job_postings 
            WHERE status = "active" AND (application_deadline IS NULL OR application_deadline > date('now'))
            ORDER BY created_at DESC
        '''
        params = []
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
            if offset:
                query += ' OFFSET ?'
                params.append(offset)
        
        rows = fetch_all(query, params if params else None)
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def search_jobs(cls, keywords=None, location=None, experience_level=None, skills=None):
        """Search job postings with filters"""
        query = 'SELECT * FROM job_postings WHERE status = "active"'
        params = []
        
        if keywords:
            query += ' AND (title LIKE ? OR description LIKE ?)'
            keyword_pattern = f'%{keywords}%'
            params.extend([keyword_pattern, keyword_pattern])
        
        if location:
            query += ' AND location LIKE ?'
            params.append(f'%{location}%')
        
        if experience_level:
            query += ' AND experience_level = ?'
            params.append(experience_level)
        
        if skills:
            # Search for any of the provided skills in required_skills
            skill_conditions = []
            for skill in skills:
                skill_conditions.append('required_skills LIKE ?')
                params.append(f'%{skill}%')
            
            if skill_conditions:
                query += f' AND ({" OR ".join(skill_conditions)})'
        
        query += ' ORDER BY created_at DESC'
        
        rows = fetch_all(query, params)
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def _from_row(cls, row):
        """Create JobPosting instance from database row"""
        # Parse date field
        application_deadline = None
        if row['application_deadline']:
            try:
                application_deadline = datetime.strptime(row['application_deadline'], '%Y-%m-%d').date()
            except ValueError:
                application_deadline = None
        
        return cls(
            id=row['id'],
            employer_id=row['employer_id'],
            title=row['title'],
            description=row['description'],
            required_skills=cls._parse_json_field(row['required_skills']),
            preferred_qualifications=cls._parse_json_field(row['preferred_qualifications']),
            experience_level=row['experience_level'],
            location=row['location'],
            salary_range=cls._parse_json_field(row['salary_range']),
            application_deadline=application_deadline,
            status=row['status'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    @staticmethod
    def _parse_json_field(field_value):
        """Parse JSON field from database"""
        if field_value is None:
            return []
        try:
            return json.loads(field_value)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @staticmethod
    def _serialize_json_field(field_value):
        """Serialize field to JSON for database storage"""
        if field_value is None:
            return json.dumps([])
        return json.dumps(field_value)
    
    def update(self, **kwargs):
        """Update job posting fields"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
        self._update_in_db()
    
    def activate(self):
        """Activate job posting"""
        self.status = 'active'
        self.updated_at = datetime.utcnow()
        self._update_status_in_db()
    
    def close(self):
        """Close job posting"""
        self.status = 'closed'
        self.updated_at = datetime.utcnow()
        self._update_status_in_db()
    
    def set_draft(self):
        """Set job posting to draft"""
        self.status = 'draft'
        self.updated_at = datetime.utcnow()
        self._update_status_in_db()
    
    def is_expired(self):
        """Check if job posting has expired"""
        if not self.application_deadline:
            return False
        return self.application_deadline < date.today()
    
    def is_active(self):
        """Check if job posting is active and not expired"""
        return self.status == 'active' and not self.is_expired()
    
    def _save_to_db(self):
        """Save new job posting to database"""
        query = '''
            INSERT INTO job_postings 
            (employer_id, title, description, required_skills, preferred_qualifications,
             experience_level, location, salary_range, application_deadline, 
             status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        now = datetime.utcnow()
        self.created_at = now
        self.updated_at = now
        
        # Convert date to string for database storage
        deadline_str = self.application_deadline.strftime('%Y-%m-%d') if self.application_deadline else None
        
        cursor = execute_query(query, (
            self.employer_id, self.title, self.description,
            self._serialize_json_field(self.required_skills),
            self._serialize_json_field(self.preferred_qualifications),
            self.experience_level, self.location,
            self._serialize_json_field(self.salary_range),
            deadline_str, self.status, self.created_at, self.updated_at
        ))
        
        self.id = cursor.lastrowid
    
    def _update_in_db(self):
        """Update existing job posting in database"""
        query = '''
            UPDATE job_postings SET
            title = ?, description = ?, required_skills = ?, preferred_qualifications = ?,
            experience_level = ?, location = ?, salary_range = ?, application_deadline = ?,
            status = ?, updated_at = ?
            WHERE id = ?
        '''
        
        # Convert date to string for database storage
        deadline_str = self.application_deadline.strftime('%Y-%m-%d') if self.application_deadline else None
        
        execute_query(query, (
            self.title, self.description,
            self._serialize_json_field(self.required_skills),
            self._serialize_json_field(self.preferred_qualifications),
            self.experience_level, self.location,
            self._serialize_json_field(self.salary_range),
            deadline_str, self.status, self.updated_at, self.id
        ))
    
    def _update_status_in_db(self):
        """Update only status and updated_at in database"""
        query = 'UPDATE job_postings SET status = ?, updated_at = ? WHERE id = ?'
        execute_query(query, (self.status, self.updated_at, self.id))
    
    def validate(self):
        """Validate job posting data"""
        errors = []
        
        if not self.title or len(self.title.strip()) == 0:
            errors.append("Job title is required")
        
        if not self.description or len(self.description.strip()) == 0:
            errors.append("Job description is required")
        
        if self.status not in self.STATUSES:
            errors.append(f"Status must be one of: {self.STATUSES}")
        
        if self.experience_level and self.experience_level not in self.EXPERIENCE_LEVELS:
            errors.append(f"Experience level must be one of: {self.EXPERIENCE_LEVELS}")
        
        if self.application_deadline and self.application_deadline < date.today():
            errors.append("Application deadline cannot be in the past")
        
        # Validate salary range
        if self.salary_range and isinstance(self.salary_range, dict):
            if 'min' in self.salary_range and 'max' in self.salary_range:
                try:
                    min_salary = float(self.salary_range['min'])
                    max_salary = float(self.salary_range['max'])
                    if min_salary > max_salary:
                        errors.append("Minimum salary cannot be greater than maximum salary")
                except (ValueError, TypeError):
                    errors.append("Salary values must be valid numbers")
        
        return errors
    
    def get_requirements_text(self):
        """Get a text representation of job requirements for AI processing"""
        requirements = []
        
        if self.title:
            requirements.append(f"Position: {self.title}")
        
        if self.required_skills:
            requirements.append(f"Required Skills: {', '.join(self.required_skills)}")
        
        if self.preferred_qualifications:
            requirements.append(f"Preferred Qualifications: {', '.join(self.preferred_qualifications)}")
        
        if self.experience_level:
            requirements.append(f"Experience Level: {self.experience_level}")
        
        if self.location:
            requirements.append(f"Location: {self.location}")
        
        return ". ".join(requirements)
    
    def get_employer(self):
        """Get the employer for this job posting"""
        from .employer import Employer
        return Employer.find_by_id(self.employer_id)
    
    def to_dict(self):
        """Convert job posting to dictionary representation"""
        return {
            'id': self.id,
            'employer_id': self.employer_id,
            'title': self.title,
            'description': self.description,
            'required_skills': self.required_skills,
            'preferred_qualifications': self.preferred_qualifications,
            'experience_level': self.experience_level,
            'location': self.location,
            'salary_range': self.salary_range,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'status': self.status,
            'is_active': self.is_active(),
            'is_expired': self.is_expired(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def __repr__(self):
        return f'<JobPosting {self.title} ({self.status})>'