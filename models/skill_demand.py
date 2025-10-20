"""
SkillDemand model for industry trend analysis
"""
import json
from datetime import datetime, date
from database import execute_query, fetch_one, fetch_all


class SkillDemand:
    """SkillDemand model for tracking skill demand trends in the industry"""
    
    def __init__(self, id=None, skill_name=None, industry=None, demand_score=None,
                 job_count=None, avg_salary=None, growth_rate=None,
                 analysis_date=None, created_at=None, updated_at=None):
        self.id = id
        self.skill_name = skill_name
        self.industry = industry
        self.demand_score = demand_score  # 0-100 score indicating demand level
        self.job_count = job_count  # Number of jobs requiring this skill
        self.avg_salary = avg_salary  # Average salary for jobs requiring this skill
        self.growth_rate = growth_rate  # Percentage growth in demand
        self.analysis_date = analysis_date
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def create(cls, skill_name, industry, demand_score, **kwargs):
        """Create a new skill demand record"""
        skill_demand = cls(
            skill_name=skill_name,
            industry=industry,
            demand_score=demand_score,
            **kwargs
        )
        skill_demand._save_to_db()
        return skill_demand
    
    @classmethod
    def find_by_id(cls, skill_demand_id):
        """Find skill demand by ID"""
        query = 'SELECT * FROM skill_demand WHERE id = ?'
        row = fetch_one(query, (skill_demand_id,))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def find_by_skill_and_industry(cls, skill_name, industry):
        """Find skill demand by skill name and industry"""
        query = 'SELECT * FROM skill_demand WHERE skill_name = ? AND industry = ?'
        row = fetch_one(query, (skill_name, industry))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_top_skills_by_demand(cls, industry=None, limit=20):
        """Get top skills by demand score"""
        query = '''
            SELECT * FROM skill_demand
        '''
        params = []
        
        if industry:
            query += ' WHERE industry = ?'
            params.append(industry)
        
        query += ' ORDER BY demand_score DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        rows = fetch_all(query, params if params else None)
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_skills_by_industry(cls, industry):
        """Get all skills for a specific industry"""
        query = '''
            SELECT * FROM skill_demand 
            WHERE industry = ? 
            ORDER BY demand_score DESC
        '''
        rows = fetch_all(query, (industry,))
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_trending_skills(cls, growth_threshold=10.0):
        """Get skills with high growth rate"""
        query = '''
            SELECT * FROM skill_demand 
            WHERE growth_rate >= ? 
            ORDER BY growth_rate DESC
        '''
        rows = fetch_all(query, (growth_threshold,))
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def get_skill_gap_analysis(cls, student_skills, target_industry=None):
        """Analyze skill gaps for a student based on industry demand"""
        if not student_skills:
            return {'missing_skills': [], 'matching_skills': [], 'recommendations': []}
        
        # Get industry demand data
        query = '''
            SELECT skill_name, demand_score, avg_salary, industry
            FROM skill_demand
        '''
        params = []
        
        if target_industry:
            query += ' WHERE industry = ?'
            params.append(target_industry)
        
        query += ' ORDER BY demand_score DESC'
        
        rows = fetch_all(query, params if params else None)
        industry_skills = [dict(row) for row in rows]
        
        # Normalize student skills for comparison
        student_skills_lower = [skill.lower().strip() for skill in student_skills]
        
        matching_skills = []
        missing_skills = []
        
        for skill_data in industry_skills:
            skill_name = skill_data['skill_name'].lower().strip()
            
            if skill_name in student_skills_lower:
                matching_skills.append(skill_data)
            else:
                missing_skills.append(skill_data)
        
        # Generate recommendations based on high-demand missing skills
        recommendations = []
        for skill in missing_skills[:10]:  # Top 10 missing skills
            if skill['demand_score'] >= 70:  # High demand threshold
                recommendations.append({
                    'skill': skill['skill_name'],
                    'reason': f"High demand skill (Score: {skill['demand_score']}) with avg salary: ${skill['avg_salary']:.0f}" if skill['avg_salary'] else f"High demand skill (Score: {skill['demand_score']})",
                    'priority': 'high' if skill['demand_score'] >= 85 else 'medium'
                })
        
        return {
            'matching_skills': matching_skills,
            'missing_skills': missing_skills[:20],  # Limit to top 20
            'recommendations': recommendations
        }
    
    @classmethod
    def analyze_job_postings_for_skills(cls):
        """Analyze current job postings to update skill demand data"""
        from .job_posting import JobPosting
        
        # Get all active job postings
        active_jobs = JobPosting.get_active_jobs()
        
        skill_stats = {}
        
        for job in active_jobs:
            # Get employer to determine industry
            employer = job.get_employer()
            industry = employer.industry if employer else 'General'
            
            # Process required skills
            for skill in job.required_skills:
                skill_key = (skill.lower().strip(), industry)
                
                if skill_key not in skill_stats:
                    skill_stats[skill_key] = {
                        'skill_name': skill,
                        'industry': industry,
                        'job_count': 0,
                        'salary_sum': 0,
                        'salary_count': 0
                    }
                
                skill_stats[skill_key]['job_count'] += 1
                
                # Add salary data if available
                if job.salary_range and isinstance(job.salary_range, dict):
                    if 'min' in job.salary_range and 'max' in job.salary_range:
                        try:
                            avg_job_salary = (float(job.salary_range['min']) + float(job.salary_range['max'])) / 2
                            skill_stats[skill_key]['salary_sum'] += avg_job_salary
                            skill_stats[skill_key]['salary_count'] += 1
                        except (ValueError, TypeError):
                            pass
        
        # Update or create skill demand records
        analysis_date = date.today()
        
        for (skill_name, industry), stats in skill_stats.items():
            # Calculate demand score based on job count (normalized to 0-100)
            max_job_count = max([s['job_count'] for s in skill_stats.values()] + [1])
            demand_score = min(100, (stats['job_count'] / max_job_count) * 100)
            
            # Calculate average salary
            avg_salary = None
            if stats['salary_count'] > 0:
                avg_salary = stats['salary_sum'] / stats['salary_count']
            
            # Check if record exists
            existing_record = cls.find_by_skill_and_industry(skill_name, industry)
            
            if existing_record:
                # Calculate growth rate
                growth_rate = 0
                if existing_record.job_count > 0:
                    growth_rate = ((stats['job_count'] - existing_record.job_count) / existing_record.job_count) * 100
                
                # Update existing record
                existing_record.update(
                    demand_score=demand_score,
                    job_count=stats['job_count'],
                    avg_salary=avg_salary,
                    growth_rate=growth_rate,
                    analysis_date=analysis_date
                )
            else:
                # Create new record
                cls.create(
                    skill_name=skill_name,
                    industry=industry,
                    demand_score=demand_score,
                    job_count=stats['job_count'],
                    avg_salary=avg_salary,
                    growth_rate=0,  # No growth rate for new skills
                    analysis_date=analysis_date
                )
        
        return len(skill_stats)
    
    @classmethod
    def _from_row(cls, row):
        """Create SkillDemand instance from database row"""
        # Parse date field
        analysis_date = None
        if row['analysis_date']:
            try:
                analysis_date = datetime.strptime(row['analysis_date'], '%Y-%m-%d').date()
            except ValueError:
                analysis_date = None
        
        return cls(
            id=row['id'],
            skill_name=row['skill_name'],
            industry=row['industry'],
            demand_score=row['demand_score'],
            job_count=row['job_count'],
            avg_salary=row['avg_salary'],
            growth_rate=row['growth_rate'],
            analysis_date=analysis_date,
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def update(self, **kwargs):
        """Update skill demand fields"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
        self._update_in_db()
    
    def _save_to_db(self):
        """Save new skill demand to database"""
        # First, create the table if it doesn't exist
        self._create_table_if_not_exists()
        
        query = '''
            INSERT INTO skill_demand 
            (skill_name, industry, demand_score, job_count, avg_salary,
             growth_rate, analysis_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        now = datetime.utcnow()
        self.created_at = now
        self.updated_at = now
        
        # Convert date to string for database storage
        analysis_date_str = self.analysis_date.strftime('%Y-%m-%d') if self.analysis_date else None
        
        cursor = execute_query(query, (
            self.skill_name, self.industry, self.demand_score, self.job_count,
            self.avg_salary, self.growth_rate, analysis_date_str,
            self.created_at, self.updated_at
        ))
        
        self.id = cursor.lastrowid
    
    def _update_in_db(self):
        """Update existing skill demand in database"""
        query = '''
            UPDATE skill_demand SET
            demand_score = ?, job_count = ?, avg_salary = ?, growth_rate = ?,
            analysis_date = ?, updated_at = ?
            WHERE id = ?
        '''
        
        # Convert date to string for database storage
        analysis_date_str = self.analysis_date.strftime('%Y-%m-%d') if self.analysis_date else None
        
        execute_query(query, (
            self.demand_score, self.job_count, self.avg_salary, self.growth_rate,
            analysis_date_str, self.updated_at, self.id
        ))
    
    def _create_table_if_not_exists(self):
        """Create skill_demand table if it doesn't exist"""
        query = '''
            CREATE TABLE IF NOT EXISTS skill_demand (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT NOT NULL,
                industry TEXT NOT NULL,
                demand_score REAL DEFAULT 0,
                job_count INTEGER DEFAULT 0,
                avg_salary REAL,
                growth_rate REAL DEFAULT 0,
                analysis_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(skill_name, industry)
            )
        '''
        execute_query(query)
    
    def validate(self):
        """Validate skill demand data"""
        errors = []
        
        if not self.skill_name or len(self.skill_name.strip()) == 0:
            errors.append("Skill name is required")
        
        if not self.industry or len(self.industry.strip()) == 0:
            errors.append("Industry is required")
        
        if self.demand_score is not None and not (0 <= self.demand_score <= 100):
            errors.append("Demand score must be between 0 and 100")
        
        if self.job_count is not None and self.job_count < 0:
            errors.append("Job count cannot be negative")
        
        if self.avg_salary is not None and self.avg_salary < 0:
            errors.append("Average salary cannot be negative")
        
        return errors
    
    def to_dict(self):
        """Convert skill demand to dictionary representation"""
        return {
            'id': self.id,
            'skill_name': self.skill_name,
            'industry': self.industry,
            'demand_score': self.demand_score,
            'job_count': self.job_count,
            'avg_salary': self.avg_salary,
            'growth_rate': self.growth_rate,
            'analysis_date': self.analysis_date.isoformat() if self.analysis_date else None,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def __repr__(self):
        return f'<SkillDemand {self.skill_name} in {self.industry} (Score: {self.demand_score})>'