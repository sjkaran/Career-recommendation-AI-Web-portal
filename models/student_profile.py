"""
StudentProfile model with comprehensive fields and JSON handling
"""
import json
from datetime import datetime
from database import execute_query, fetch_one, fetch_all


class StudentProfile:
    """StudentProfile model with academic, skills, and activity fields"""
    
    # Profile completion weights for scoring
    COMPLETION_WEIGHTS = {
        'personal_info': 15,
        'academic_records': 25,
        'technical_skills': 20,
        'soft_skills': 15,
        'co_curricular': 15,
        'extra_curricular': 10
    }
    
    def __init__(self, id=None, user_id=None, first_name=None, last_name=None,
                 phone=None, academic_records=None, technical_skills=None,
                 soft_skills=None, co_curricular=None, extra_curricular=None,
                 career_interests=None, profile_completion_score=0,
                 created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.academic_records = academic_records or {}
        self.technical_skills = technical_skills or []
        self.soft_skills = soft_skills or []
        self.co_curricular = co_curricular or []
        self.extra_curricular = extra_curricular or []
        self.career_interests = career_interests or []
        self.profile_completion_score = profile_completion_score
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def create(cls, user_id, **kwargs):
        """Create a new student profile"""
        # Check if profile already exists for this user
        existing_profile = cls.find_by_user_id(user_id)
        if existing_profile:
            raise ValueError("Profile already exists for this user")
        
        profile = cls(user_id=user_id, **kwargs)
        profile._save_to_db()
        return profile
    
    @classmethod
    def find_by_id(cls, profile_id):
        """Find student profile by ID"""
        query = 'SELECT * FROM student_profiles WHERE id = ?'
        row = fetch_one(query, (profile_id,))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def find_by_user_id(cls, user_id):
        """Find student profile by user ID"""
        query = 'SELECT * FROM student_profiles WHERE user_id = ?'
        row = fetch_one(query, (user_id,))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_all_profiles(cls, limit=None, offset=None):
        """Get all student profiles with optional pagination"""
        query = 'SELECT * FROM student_profiles ORDER BY created_at DESC'
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
    def search_by_skills(cls, skills):
        """Search profiles by technical skills"""
        if not skills:
            return []
        
        # Create a LIKE pattern for each skill
        skill_conditions = []
        params = []
        
        for skill in skills:
            skill_conditions.append('technical_skills LIKE ?')
            params.append(f'%{skill}%')
        
        query = f'''
            SELECT * FROM student_profiles 
            WHERE {' OR '.join(skill_conditions)}
            ORDER BY profile_completion_score DESC
        '''
        
        rows = fetch_all(query, params)
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def search_profiles(cls, skills=None, experience_level=None, location=None, major=None):
        """Search student profiles with multiple filters"""
        query = 'SELECT * FROM student_profiles WHERE 1=1'
        params = []
        
        # Filter by skills
        if skills:
            skill_conditions = []
            for skill in skills:
                skill_conditions.append('(technical_skills LIKE ? OR soft_skills LIKE ?)')
                params.extend([f'%{skill}%', f'%{skill}%'])
            
            if skill_conditions:
                query += f' AND ({" OR ".join(skill_conditions)})'
        
        # Filter by major (in academic records)
        if major:
            query += ' AND academic_records LIKE ?'
            params.append(f'%{major}%')
        
        # Filter by location (in personal info or academic records)
        if location:
            query += ' AND (academic_records LIKE ? OR first_name LIKE ?)'
            params.extend([f'%{location}%', f'%{location}%'])
        
        # Experience level filtering would need additional logic based on profile data
        # For now, we'll order by profile completion score as a proxy
        query += ' ORDER BY profile_completion_score DESC'
        
        rows = fetch_all(query, params)
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def _from_row(cls, row):
        """Create StudentProfile instance from database row"""
        return cls(
            id=row['id'],
            user_id=row['user_id'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            phone=row['phone'],
            academic_records=cls._parse_json_field(row['academic_records']),
            technical_skills=cls._parse_json_field(row['technical_skills']),
            soft_skills=cls._parse_json_field(row['soft_skills']),
            co_curricular=cls._parse_json_field(row['co_curricular']),
            extra_curricular=cls._parse_json_field(row['extra_curricular']),
            career_interests=cls._parse_json_field(row['career_interests']),
            profile_completion_score=row['profile_completion_score'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    @staticmethod
    def _parse_json_field(field_value):
        """Parse JSON field from database"""
        if field_value is None:
            return {}
        try:
            return json.loads(field_value)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @staticmethod
    def _serialize_json_field(field_value):
        """Serialize field to JSON for database storage"""
        if field_value is None:
            return json.dumps({})
        return json.dumps(field_value)
    
    def update(self, **kwargs):
        """Update profile fields"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
        self._calculate_completion_score()
        self._update_in_db()
    
    def _save_to_db(self):
        """Save new profile to database"""
        self._calculate_completion_score()
        
        query = '''
            INSERT INTO student_profiles 
            (user_id, first_name, last_name, phone, academic_records, 
             technical_skills, soft_skills, co_curricular, extra_curricular, 
             career_interests, profile_completion_score, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        now = datetime.utcnow()
        self.created_at = now
        self.updated_at = now
        
        cursor = execute_query(query, (
            self.user_id, self.first_name, self.last_name, self.phone,
            self._serialize_json_field(self.academic_records),
            self._serialize_json_field(self.technical_skills),
            self._serialize_json_field(self.soft_skills),
            self._serialize_json_field(self.co_curricular),
            self._serialize_json_field(self.extra_curricular),
            self._serialize_json_field(self.career_interests),
            self.profile_completion_score, self.created_at, self.updated_at
        ))
        
        self.id = cursor.lastrowid
    
    def _update_in_db(self):
        """Update existing profile in database"""
        query = '''
            UPDATE student_profiles SET
            first_name = ?, last_name = ?, phone = ?, academic_records = ?,
            technical_skills = ?, soft_skills = ?, co_curricular = ?,
            extra_curricular = ?, career_interests = ?, 
            profile_completion_score = ?, updated_at = ?
            WHERE id = ?
        '''
        
        execute_query(query, (
            self.first_name, self.last_name, self.phone,
            self._serialize_json_field(self.academic_records),
            self._serialize_json_field(self.technical_skills),
            self._serialize_json_field(self.soft_skills),
            self._serialize_json_field(self.co_curricular),
            self._serialize_json_field(self.extra_curricular),
            self._serialize_json_field(self.career_interests),
            self.profile_completion_score, self.updated_at, self.id
        ))
    
    def _calculate_completion_score(self):
        """Calculate profile completion score based on filled fields"""
        score = 0
        
        # Personal info (15%)
        if self.first_name and self.last_name and self.phone:
            score += self.COMPLETION_WEIGHTS['personal_info']
        
        # Academic records (25%)
        if self.academic_records and len(self.academic_records) > 0:
            # Check for key academic fields
            required_fields = ['cgpa', 'branch', 'year', 'university']
            filled_fields = sum(1 for field in required_fields if field in self.academic_records)
            score += (filled_fields / len(required_fields)) * self.COMPLETION_WEIGHTS['academic_records']
        
        # Technical skills (20%)
        if self.technical_skills and len(self.technical_skills) >= 3:
            score += self.COMPLETION_WEIGHTS['technical_skills']
        elif self.technical_skills and len(self.technical_skills) > 0:
            score += (len(self.technical_skills) / 3) * self.COMPLETION_WEIGHTS['technical_skills']
        
        # Soft skills (15%)
        if self.soft_skills and len(self.soft_skills) >= 3:
            score += self.COMPLETION_WEIGHTS['soft_skills']
        elif self.soft_skills and len(self.soft_skills) > 0:
            score += (len(self.soft_skills) / 3) * self.COMPLETION_WEIGHTS['soft_skills']
        
        # Co-curricular activities (15%)
        if self.co_curricular and len(self.co_curricular) > 0:
            score += self.COMPLETION_WEIGHTS['co_curricular']
        
        # Extra-curricular activities (10%)
        if self.extra_curricular and len(self.extra_curricular) > 0:
            score += self.COMPLETION_WEIGHTS['extra_curricular']
        
        self.profile_completion_score = min(100, int(score))
    
    def validate_academic_records(self):
        """Validate academic records data"""
        errors = []
        
        if not isinstance(self.academic_records, dict):
            errors.append("Academic records must be a dictionary")
            return errors
        
        # Validate CGPA
        if 'cgpa' in self.academic_records:
            try:
                cgpa = float(self.academic_records['cgpa'])
                if not (0 <= cgpa <= 10):
                    errors.append("CGPA must be between 0 and 10")
            except (ValueError, TypeError):
                errors.append("CGPA must be a valid number")
        
        # Validate year
        if 'year' in self.academic_records:
            try:
                year = int(self.academic_records['year'])
                current_year = datetime.now().year
                if not (1900 <= year <= current_year + 10):
                    errors.append("Year must be a valid year")
            except (ValueError, TypeError):
                errors.append("Year must be a valid number")
        
        return errors
    
    def validate_skills(self):
        """Validate skills data"""
        errors = []
        
        # Validate technical skills
        if not isinstance(self.technical_skills, list):
            errors.append("Technical skills must be a list")
        else:
            for skill in self.technical_skills:
                if not isinstance(skill, str) or len(skill.strip()) == 0:
                    errors.append("Each technical skill must be a non-empty string")
                    break
        
        # Validate soft skills
        if not isinstance(self.soft_skills, list):
            errors.append("Soft skills must be a list")
        else:
            for skill in self.soft_skills:
                if not isinstance(skill, str) or len(skill.strip()) == 0:
                    errors.append("Each soft skill must be a non-empty string")
                    break
        
        return errors
    
    def get_profile_summary(self):
        """Get a text summary of the profile for AI processing"""
        summary_parts = []
        
        if self.first_name and self.last_name:
            summary_parts.append(f"Name: {self.first_name} {self.last_name}")
        
        if self.academic_records:
            if 'branch' in self.academic_records:
                summary_parts.append(f"Branch: {self.academic_records['branch']}")
            if 'cgpa' in self.academic_records:
                summary_parts.append(f"CGPA: {self.academic_records['cgpa']}")
        
        if self.technical_skills:
            summary_parts.append(f"Technical Skills: {', '.join(self.technical_skills)}")
        
        if self.soft_skills:
            summary_parts.append(f"Soft Skills: {', '.join(self.soft_skills)}")
        
        if self.career_interests:
            summary_parts.append(f"Career Interests: {', '.join(self.career_interests)}")
        
        return ". ".join(summary_parts)
    
    def to_dict(self):
        """Convert profile to dictionary representation"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'academic_records': self.academic_records,
            'technical_skills': self.technical_skills,
            'soft_skills': self.soft_skills,
            'co_curricular': self.co_curricular,
            'extra_curricular': self.extra_curricular,
            'career_interests': self.career_interests,
            'profile_completion_score': self.profile_completion_score,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def __repr__(self):
        name = f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else "Unknown"
        return f'<StudentProfile {name} (Score: {self.profile_completion_score}%)>' 
   def _get_completion_breakdown(self):
        """Get detailed breakdown of profile completion by section"""
        breakdown = {}
        
        # Personal info (15%)
        personal_score = 0
        if self.first_name and self.last_name and self.phone:
            personal_score = self.COMPLETION_WEIGHTS['personal_info']
        breakdown['personal_info'] = {
            'score': personal_score,
            'max_score': self.COMPLETION_WEIGHTS['personal_info'],
            'completed': personal_score > 0,
            'fields': {
                'first_name': bool(self.first_name),
                'last_name': bool(self.last_name),
                'phone': bool(self.phone)
            }
        }
        
        # Academic records (25%)
        academic_score = 0
        academic_fields = {}
        if self.academic_records and len(self.academic_records) > 0:
            required_fields = ['cgpa', 'branch', 'year', 'university']
            filled_fields = 0
            for field in required_fields:
                field_filled = field in self.academic_records and self.academic_records[field]
                academic_fields[field] = field_filled
                if field_filled:
                    filled_fields += 1
            academic_score = (filled_fields / len(required_fields)) * self.COMPLETION_WEIGHTS['academic_records']
        
        breakdown['academic_records'] = {
            'score': academic_score,
            'max_score': self.COMPLETION_WEIGHTS['academic_records'],
            'completed': academic_score >= self.COMPLETION_WEIGHTS['academic_records'] * 0.8,
            'fields': academic_fields
        }
        
        # Technical skills (20%)
        tech_skills_score = 0
        if self.technical_skills and len(self.technical_skills) >= 3:
            tech_skills_score = self.COMPLETION_WEIGHTS['technical_skills']
        elif self.technical_skills and len(self.technical_skills) > 0:
            tech_skills_score = (len(self.technical_skills) / 3) * self.COMPLETION_WEIGHTS['technical_skills']
        
        breakdown['technical_skills'] = {
            'score': tech_skills_score,
            'max_score': self.COMPLETION_WEIGHTS['technical_skills'],
            'completed': len(self.technical_skills) >= 3 if self.technical_skills else False,
            'count': len(self.technical_skills) if self.technical_skills else 0,
            'required_count': 3
        }
        
        # Soft skills (15%)
        soft_skills_score = 0
        if self.soft_skills and len(self.soft_skills) >= 3:
            soft_skills_score = self.COMPLETION_WEIGHTS['soft_skills']
        elif self.soft_skills and len(self.soft_skills) > 0:
            soft_skills_score = (len(self.soft_skills) / 3) * self.COMPLETION_WEIGHTS['soft_skills']
        
        breakdown['soft_skills'] = {
            'score': soft_skills_score,
            'max_score': self.COMPLETION_WEIGHTS['soft_skills'],
            'completed': len(self.soft_skills) >= 3 if self.soft_skills else False,
            'count': len(self.soft_skills) if self.soft_skills else 0,
            'required_count': 3
        }
        
        # Co-curricular activities (15%)
        co_curricular_score = 0
        if self.co_curricular and len(self.co_curricular) > 0:
            co_curricular_score = self.COMPLETION_WEIGHTS['co_curricular']
        
        breakdown['co_curricular'] = {
            'score': co_curricular_score,
            'max_score': self.COMPLETION_WEIGHTS['co_curricular'],
            'completed': bool(self.co_curricular and len(self.co_curricular) > 0),
            'count': len(self.co_curricular) if self.co_curricular else 0
        }
        
        # Extra-curricular activities (10%)
        extra_curricular_score = 0
        if self.extra_curricular and len(self.extra_curricular) > 0:
            extra_curricular_score = self.COMPLETION_WEIGHTS['extra_curricular']
        
        breakdown['extra_curricular'] = {
            'score': extra_curricular_score,
            'max_score': self.COMPLETION_WEIGHTS['extra_curricular'],
            'completed': bool(self.extra_curricular and len(self.extra_curricular) > 0),
            'count': len(self.extra_curricular) if self.extra_curricular else 0
        }
        
        return breakdown
    
    def _get_completion_suggestions(self):
        """Get suggestions for improving profile completion"""
        suggestions = []
        breakdown = self._get_completion_breakdown()
        
        # Personal info suggestions
        if not breakdown['personal_info']['completed']:
            missing_fields = [field for field, filled in breakdown['personal_info']['fields'].items() if not filled]
            if missing_fields:
                suggestions.append(f"Complete personal information: {', '.join(missing_fields)}")
        
        # Academic records suggestions
        if not breakdown['academic_records']['completed']:
            if not self.academic_records:
                suggestions.append("Add your academic records (CGPA, branch, year, university)")
            else:
                missing_fields = [field for field, filled in breakdown['academic_records']['fields'].items() if not filled]
                if missing_fields:
                    suggestions.append(f"Complete academic records: {', '.join(missing_fields)}")
        
        # Technical skills suggestions
        if not breakdown['technical_skills']['completed']:
            current_count = breakdown['technical_skills']['count']
            required_count = breakdown['technical_skills']['required_count']
            if current_count == 0:
                suggestions.append("Add your technical skills (programming languages, tools, frameworks)")
            else:
                suggestions.append(f"Add {required_count - current_count} more technical skills")
        
        # Soft skills suggestions
        if not breakdown['soft_skills']['completed']:
            current_count = breakdown['soft_skills']['count']
            required_count = breakdown['soft_skills']['required_count']
            if current_count == 0:
                suggestions.append("Add your soft skills (communication, leadership, teamwork)")
            else:
                suggestions.append(f"Add {required_count - current_count} more soft skills")
        
        # Activities suggestions
        if not breakdown['co_curricular']['completed']:
            suggestions.append("Add co-curricular activities (clubs, competitions, certifications)")
        
        if not breakdown['extra_curricular']['completed']:
            suggestions.append("Add extra-curricular activities (sports, volunteering, hobbies)")
        
        # Career interests
        if not self.career_interests or len(self.career_interests) == 0:
            suggestions.append("Add your career interests to get better recommendations")
        
        return suggestions
    
    def _get_next_step(self, progress):
        """Get the next step the user should complete"""
        if not progress['step1_personal']:
            return {
                'step': 1,
                'title': 'Personal Information',
                'description': 'Complete your basic personal details'
            }
        elif not progress['step2_academic']:
            return {
                'step': 2,
                'title': 'Academic Records',
                'description': 'Add your academic information and achievements'
            }
        elif not progress['step3_skills']:
            return {
                'step': 3,
                'title': 'Skills',
                'description': 'List your technical and soft skills'
            }
        elif not progress['step4_activities']:
            return {
                'step': 4,
                'title': 'Activities & Interests',
                'description': 'Add your activities and career interests'
            }
        else:
            return {
                'step': 'complete',
                'title': 'Profile Complete',
                'description': 'Your profile is complete! Keep it updated for better recommendations.'
            }
    
    def get_validation_summary(self):
        """Get comprehensive validation summary for the profile"""
        validation_results = {
            'personal_info': {
                'valid': bool(self.first_name and self.last_name),
                'errors': []
            },
            'academic_records': {
                'valid': True,
                'errors': self.validate_academic_records()
            },
            'skills': {
                'valid': True,
                'errors': self.validate_skills()
            }
        }
        
        # Update validity based on errors
        validation_results['academic_records']['valid'] = len(validation_results['academic_records']['errors']) == 0
        validation_results['skills']['valid'] = len(validation_results['skills']['errors']) == 0
        
        # Add personal info validation errors
        if not self.first_name:
            validation_results['personal_info']['errors'].append("First name is required")
        if not self.last_name:
            validation_results['personal_info']['errors'].append("Last name is required")
        
        validation_results['personal_info']['valid'] = len(validation_results['personal_info']['errors']) == 0
        
        # Overall validation
        all_valid = all(section['valid'] for section in validation_results.values())
        total_errors = sum(len(section['errors']) for section in validation_results.values())
        
        return {
            'overall_valid': all_valid,
            'total_errors': total_errors,
            'sections': validation_results
        }