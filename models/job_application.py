"""
JobApplication model for tracking student applications to job postings
"""
import json
from datetime import datetime
from database import execute_query, fetch_one, fetch_all


class JobApplication:
    """JobApplication model for tracking applications and their status"""
    
    STATUSES = ['pending', 'reviewed', 'shortlisted', 'interviewed', 'hired', 'rejected']
    
    def __init__(self, id=None, job_id=None, student_id=None, status='pending',
                 application_date=None, cover_letter=None, resume_path=None,
                 employer_notes=None, interview_date=None, created_at=None, updated_at=None):
        self.id = id
        self.job_id = job_id
        self.student_id = student_id
        self.status = status
        self.application_date = application_date
        self.cover_letter = cover_letter
        self.resume_path = resume_path
        self.employer_notes = employer_notes
        self.interview_date = interview_date
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def create(cls, job_id, student_id, **kwargs):
        """Create a new job application"""
        # Check if application already exists
        existing_app = cls.find_by_job_and_student(job_id, student_id)
        if existing_app:
            raise ValueError("Application already exists for this job and student")
        
        application = cls(
            job_id=job_id,
            student_id=student_id,
            application_date=datetime.utcnow().date(),
            **kwargs
        )
        application._save_to_db()
        return application
    
    @classmethod
    def find_by_id(cls, application_id):
        """Find application by ID"""
        query = 'SELECT * FROM job_applications WHERE id = ?'
        row = fetch_one(query, (application_id,))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def find_by_job_and_student(cls, job_id, student_id):
        """Find application by job and student"""
        query = 'SELECT * FROM job_applications WHERE job_id = ? AND student_id = ?'
        row = fetch_one(query, (job_id, student_id))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_by_student_id(cls, student_id, status=None):
        """Get all applications for a student"""
        query = 'SELECT * FROM job_applications WHERE student_id = ?'
        params = [student_id]
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        query += ' ORDER BY application_date DESC'
        
        rows = fetch_all(query, params)
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_by_job_id(cls, job_id, status=None):
        """Get all applications for a job"""
        query = 'SELECT * FROM job_applications WHERE job_id = ?'
        params = [job_id]
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        query += ' ORDER BY application_date DESC'
        
        rows = fetch_all(query, params)
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_by_employer_id(cls, employer_id, status=None):
        """Get all applications for an employer's jobs"""
        query = '''
            SELECT ja.* FROM job_applications ja
            JOIN job_postings jp ON ja.job_id = jp.id
            WHERE jp.employer_id = ?
        '''
        params = [employer_id]
        
        if status:
            query += ' AND ja.status = ?'
            params.append(status)
        
        query += ' ORDER BY ja.application_date DESC'
        
        rows = fetch_all(query, params)
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def _from_row(cls, row):
        """Create JobApplication instance from database row"""
        # Parse date fields
        application_date = None
        if row['application_date']:
            try:
                application_date = datetime.strptime(row['application_date'], '%Y-%m-%d').date()
            except ValueError:
                application_date = None
        
        interview_date = None
        if row['interview_date']:
            try:
                interview_date = datetime.strptime(row['interview_date'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                interview_date = None
        
        return cls(
            id=row['id'],
            job_id=row['job_id'],
            student_id=row['student_id'],
            status=row['status'],
            application_date=application_date,
            cover_letter=row['cover_letter'],
            resume_path=row['resume_path'],
            employer_notes=row['employer_notes'],
            interview_date=interview_date,
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def update(self, **kwargs):
        """Update application fields"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
        self._update_in_db()
    
    def update_status(self, new_status, employer_notes=None):
        """Update application status with optional notes"""
        if new_status not in self.STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {self.STATUSES}")
        
        self.status = new_status
        if employer_notes:
            self.employer_notes = employer_notes
        self.updated_at = datetime.utcnow()
        self._update_status_in_db()
    
    def schedule_interview(self, interview_date, notes=None):
        """Schedule interview for application"""
        self.interview_date = interview_date
        self.status = 'interviewed'
        if notes:
            self.employer_notes = notes
        self.updated_at = datetime.utcnow()
        self._update_in_db()
    
    def _save_to_db(self):
        """Save new application to database"""
        query = '''
            INSERT INTO job_applications 
            (job_id, student_id, status, application_date, cover_letter, 
             resume_path, employer_notes, interview_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        now = datetime.utcnow()
        self.created_at = now
        self.updated_at = now
        
        # Convert dates to strings for database storage
        app_date_str = self.application_date.strftime('%Y-%m-%d') if self.application_date else None
        interview_date_str = self.interview_date.strftime('%Y-%m-%d %H:%M:%S') if self.interview_date else None
        
        cursor = execute_query(query, (
            self.job_id, self.student_id, self.status, app_date_str,
            self.cover_letter, self.resume_path, self.employer_notes,
            interview_date_str, self.created_at, self.updated_at
        ))
        
        self.id = cursor.lastrowid
    
    def _update_in_db(self):
        """Update existing application in database"""
        query = '''
            UPDATE job_applications SET
            status = ?, cover_letter = ?, resume_path = ?, employer_notes = ?,
            interview_date = ?, updated_at = ?
            WHERE id = ?
        '''
        
        # Convert dates to strings for database storage
        interview_date_str = self.interview_date.strftime('%Y-%m-%d %H:%M:%S') if self.interview_date else None
        
        execute_query(query, (
            self.status, self.cover_letter, self.resume_path,
            self.employer_notes, interview_date_str, self.updated_at, self.id
        ))
    
    def _update_status_in_db(self):
        """Update only status and notes in database"""
        query = 'UPDATE job_applications SET status = ?, employer_notes = ?, updated_at = ? WHERE id = ?'
        execute_query(query, (self.status, self.employer_notes, self.updated_at, self.id))
    
    def validate(self):
        """Validate application data"""
        errors = []
        
        if not self.job_id:
            errors.append("Job ID is required")
        
        if not self.student_id:
            errors.append("Student ID is required")
        
        if self.status not in self.STATUSES:
            errors.append(f"Status must be one of: {self.STATUSES}")
        
        return errors
    
    def get_job_posting(self):
        """Get the job posting for this application"""
        from .job_posting import JobPosting
        return JobPosting.find_by_id(self.job_id)
    
    def get_student_profile(self):
        """Get the student profile for this application"""
        from .student_profile import StudentProfile
        return StudentProfile.find_by_user_id(self.student_id)
    
    def to_dict(self):
        """Convert application to dictionary representation"""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'student_id': self.student_id,
            'status': self.status,
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'cover_letter': self.cover_letter,
            'resume_path': self.resume_path,
            'employer_notes': self.employer_notes,
            'interview_date': self.interview_date.isoformat() if self.interview_date else None,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def __repr__(self):
        return f'<JobApplication {self.id} ({self.status})>'