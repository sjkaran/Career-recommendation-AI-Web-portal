"""
PlacementAnalytics model for tracking successful placements
"""
import json
from datetime import datetime, date
from database import execute_query, fetch_one, fetch_all


class PlacementAnalytics:
    """PlacementAnalytics model for tracking successful placements"""
    
    def __init__(self, id=None, student_id=None, job_id=None, placement_date=None,
                 salary=None, company_name=None, job_category=None,
                 student_branch=None, student_district=None, feedback_score=None,
                 created_at=None):
        self.id = id
        self.student_id = student_id
        self.job_id = job_id
        self.placement_date = placement_date
        self.salary = salary
        self.company_name = company_name
        self.job_category = job_category
        self.student_branch = student_branch
        self.student_district = student_district
        self.feedback_score = feedback_score
        self.created_at = created_at
    
    @classmethod
    def create(cls, student_id, job_id, placement_date, company_name, **kwargs):
        """Create a new placement analytics record"""
        placement = cls(
            student_id=student_id,
            job_id=job_id,
            placement_date=placement_date,
            company_name=company_name,
            **kwargs
        )
        placement._save_to_db()
        return placement
    
    @classmethod
    def find_by_id(cls, placement_id):
        """Find placement analytics by ID"""
        query = 'SELECT * FROM placement_analytics WHERE id = ?'
        row = fetch_one(query, (placement_id,))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_by_student_id(cls, student_id):
        """Get all placements for a student"""
        query = 'SELECT * FROM placement_analytics WHERE student_id = ? ORDER BY placement_date DESC'
        rows = fetch_all(query, (student_id,))
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_by_job_id(cls, job_id):
        """Get all placements for a job"""
        query = 'SELECT * FROM placement_analytics WHERE job_id = ? ORDER BY placement_date DESC'
        rows = fetch_all(query, (job_id,))
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_placements_by_date_range(cls, start_date, end_date):
        """Get placements within a date range"""
        query = '''
            SELECT * FROM placement_analytics 
            WHERE placement_date BETWEEN ? AND ?
            ORDER BY placement_date DESC
        '''
        rows = fetch_all(query, (start_date, end_date))
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_placement_trends_by_branch(cls, start_date=None, end_date=None):
        """Get placement trends grouped by branch"""
        query = '''
            SELECT student_branch, COUNT(*) as placement_count, 
                   AVG(salary) as avg_salary, AVG(feedback_score) as avg_feedback
            FROM placement_analytics
        '''
        params = []
        
        if start_date and end_date:
            query += ' WHERE placement_date BETWEEN ? AND ?'
            params.extend([start_date, end_date])
        
        query += ' GROUP BY student_branch ORDER BY placement_count DESC'
        
        rows = fetch_all(query, params if params else None)
        return [dict(row) for row in rows]
    
    @classmethod
    def get_placement_trends_by_district(cls, start_date=None, end_date=None):
        """Get placement trends grouped by district"""
        query = '''
            SELECT student_district, COUNT(*) as placement_count,
                   AVG(salary) as avg_salary, AVG(feedback_score) as avg_feedback
            FROM placement_analytics
        '''
        params = []
        
        if start_date and end_date:
            query += ' WHERE placement_date BETWEEN ? AND ?'
            params.extend([start_date, end_date])
        
        query += ' GROUP BY student_district ORDER BY placement_count DESC'
        
        rows = fetch_all(query, params if params else None)
        return [dict(row) for row in rows]
    
    @classmethod
    def get_industry_wise_placements(cls, start_date=None, end_date=None):
        """Get placement statistics by job category/industry"""
        query = '''
            SELECT job_category, COUNT(*) as placement_count,
                   AVG(salary) as avg_salary, MIN(salary) as min_salary,
                   MAX(salary) as max_salary, AVG(feedback_score) as avg_feedback
            FROM placement_analytics
            WHERE job_category IS NOT NULL
        '''
        params = []
        
        if start_date and end_date:
            query += ' AND placement_date BETWEEN ? AND ?'
            params.extend([start_date, end_date])
        
        query += ' GROUP BY job_category ORDER BY placement_count DESC'
        
        rows = fetch_all(query, params if params else None)
        return [dict(row) for row in rows]
    
    @classmethod
    def get_company_wise_placements(cls, start_date=None, end_date=None, limit=10):
        """Get top companies by placement count"""
        query = '''
            SELECT company_name, COUNT(*) as placement_count,
                   AVG(salary) as avg_salary, AVG(feedback_score) as avg_feedback
            FROM placement_analytics
        '''
        params = []
        
        if start_date and end_date:
            query += ' WHERE placement_date BETWEEN ? AND ?'
            params.extend([start_date, end_date])
        
        query += ' GROUP BY company_name ORDER BY placement_count DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        rows = fetch_all(query, params if params else None)
        return [dict(row) for row in rows]
    
    @classmethod
    def get_salary_statistics(cls, branch=None, district=None, job_category=None):
        """Get salary statistics with optional filters"""
        query = '''
            SELECT COUNT(*) as total_placements, AVG(salary) as avg_salary,
                   MIN(salary) as min_salary, MAX(salary) as max_salary,
                   (SELECT salary FROM placement_analytics 
                    WHERE salary IS NOT NULL ORDER BY salary 
                    LIMIT 1 OFFSET (SELECT COUNT(*) FROM placement_analytics WHERE salary IS NOT NULL) / 2) as median_salary
            FROM placement_analytics
            WHERE salary IS NOT NULL
        '''
        params = []
        
        if branch:
            query += ' AND student_branch = ?'
            params.append(branch)
        
        if district:
            query += ' AND student_district = ?'
            params.append(district)
        
        if job_category:
            query += ' AND job_category = ?'
            params.append(job_category)
        
        row = fetch_one(query, params if params else None)
        return dict(row) if row else {}
    
    @classmethod
    def get_monthly_placement_trends(cls, year=None):
        """Get monthly placement trends for a year"""
        if year is None:
            year = datetime.now().year
        
        query = '''
            SELECT strftime('%m', placement_date) as month,
                   COUNT(*) as placement_count,
                   AVG(salary) as avg_salary
            FROM placement_analytics
            WHERE strftime('%Y', placement_date) = ?
            GROUP BY strftime('%m', placement_date)
            ORDER BY month
        '''
        
        rows = fetch_all(query, (str(year),))
        return [dict(row) for row in rows]
    
    @classmethod
    def _from_row(cls, row):
        """Create PlacementAnalytics instance from database row"""
        # Parse date field
        placement_date = None
        if row['placement_date']:
            try:
                placement_date = datetime.strptime(row['placement_date'], '%Y-%m-%d').date()
            except ValueError:
                placement_date = None
        
        return cls(
            id=row['id'],
            student_id=row['student_id'],
            job_id=row['job_id'],
            placement_date=placement_date,
            salary=row['salary'],
            company_name=row['company_name'],
            job_category=row['job_category'],
            student_branch=row['student_branch'],
            student_district=row['student_district'],
            feedback_score=row['feedback_score'],
            created_at=row['created_at']
        )
    
    def update(self, **kwargs):
        """Update placement analytics fields"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self._update_in_db()
    
    def _save_to_db(self):
        """Save new placement analytics to database"""
        query = '''
            INSERT INTO placement_analytics 
            (student_id, job_id, placement_date, salary, company_name,
             job_category, student_branch, student_district, feedback_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        self.created_at = datetime.utcnow()
        
        # Convert date to string for database storage
        placement_date_str = self.placement_date.strftime('%Y-%m-%d') if self.placement_date else None
        
        cursor = execute_query(query, (
            self.student_id, self.job_id, placement_date_str, self.salary,
            self.company_name, self.job_category, self.student_branch,
            self.student_district, self.feedback_score, self.created_at
        ))
        
        self.id = cursor.lastrowid
    
    def _update_in_db(self):
        """Update existing placement analytics in database"""
        query = '''
            UPDATE placement_analytics SET
            salary = ?, job_category = ?, student_branch = ?,
            student_district = ?, feedback_score = ?
            WHERE id = ?
        '''
        
        execute_query(query, (
            self.salary, self.job_category, self.student_branch,
            self.student_district, self.feedback_score, self.id
        ))
    
    def validate(self):
        """Validate placement analytics data"""
        errors = []
        
        if not self.student_id:
            errors.append("Student ID is required")
        
        if not self.job_id:
            errors.append("Job ID is required")
        
        if not self.placement_date:
            errors.append("Placement date is required")
        elif self.placement_date > date.today():
            errors.append("Placement date cannot be in the future")
        
        if not self.company_name or len(self.company_name.strip()) == 0:
            errors.append("Company name is required")
        
        if self.salary is not None and self.salary < 0:
            errors.append("Salary cannot be negative")
        
        if self.feedback_score is not None and not (0 <= self.feedback_score <= 10):
            errors.append("Feedback score must be between 0 and 10")
        
        return errors
    
    def get_student_profile(self):
        """Get the student profile for this placement"""
        from .student_profile import StudentProfile
        return StudentProfile.find_by_id(self.student_id)
    
    def get_job_posting(self):
        """Get the job posting for this placement"""
        from .job_posting import JobPosting
        return JobPosting.find_by_id(self.job_id)
    
    def to_dict(self):
        """Convert placement analytics to dictionary representation"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'job_id': self.job_id,
            'placement_date': self.placement_date.isoformat() if self.placement_date else None,
            'salary': self.salary,
            'company_name': self.company_name,
            'job_category': self.job_category,
            'student_branch': self.student_branch,
            'student_district': self.student_district,
            'feedback_score': self.feedback_score,
            'created_at': self.created_at
        }
    
    def __repr__(self):
        return f'<PlacementAnalytics {self.company_name} - Student {self.student_id}>'