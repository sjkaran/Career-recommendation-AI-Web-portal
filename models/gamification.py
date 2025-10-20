"""
Gamification models for points, achievements, and badges system
"""
import json
from datetime import datetime, timedelta
from database import execute_query, fetch_one, fetch_all


class StudentPoints:
    """Model for tracking student points and engagement metrics"""
    
    # Point values for different activities
    POINT_VALUES = {
        'profile_completion': {
            'personal_info': 50,
            'academic_records': 100,
            'technical_skills': 75,
            'soft_skills': 50,
            'co_curricular': 75,
            'extra_curricular': 50,
            'career_interests': 25
        },
        'platform_engagement': {
            'login': 5,
            'profile_update': 10,
            'job_application': 25,
            'skill_assessment': 50,
            'recommendation_feedback': 15,
            'profile_view_by_employer': 20
        },
        'achievements': {
            'first_job_application': 100,
            'profile_100_percent': 200,
            'skill_master': 150,
            'active_user': 100,
            'top_performer': 300
        }
    }
    
    def __init__(self, id=None, student_id=None, total_points=0, 
                 profile_completion_points=0, engagement_points=0, 
                 achievement_points=0, level=1, created_at=None, updated_at=None):
        self.id = id
        self.student_id = student_id
        self.total_points = total_points
        self.profile_completion_points = profile_completion_points
        self.engagement_points = engagement_points
        self.achievement_points = achievement_points
        self.level = level
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def create_or_get(cls, student_id):
        """Create or get existing points record for student"""
        existing = cls.find_by_student_id(student_id)
        if existing:
            return existing
        
        query = '''
            INSERT INTO student_points 
            (student_id, total_points, profile_completion_points, 
             engagement_points, achievement_points, level, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        now = datetime.utcnow()
        cursor = execute_query(query, (student_id, 0, 0, 0, 0, 1, now, now))
        
        return cls.find_by_id(cursor.lastrowid)
    
    @classmethod
    def find_by_id(cls, points_id):
        """Find points record by ID"""
        query = 'SELECT * FROM student_points WHERE id = ?'
        row = fetch_one(query, (points_id,))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def find_by_student_id(cls, student_id):
        """Find points record by student ID"""
        query = 'SELECT * FROM student_points WHERE student_id = ?'
        row = fetch_one(query, (student_id,))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_leaderboard(cls, limit=10):
        """Get top students by total points"""
        query = '''
            SELECT sp.*, st.first_name, st.last_name, st.profile_completion_score
            FROM student_points sp
            JOIN student_profiles st ON sp.student_id = st.id
            ORDER BY sp.total_points DESC, sp.level DESC
            LIMIT ?
        '''
        rows = fetch_all(query, (limit,))
        
        leaderboard = []
        for row in rows:
            points = cls._from_row(row)
            leaderboard.append({
                'rank': len(leaderboard) + 1,
                'student_name': f"{row['first_name']} {row['last_name']}" if row['first_name'] else "Anonymous",
                'total_points': points.total_points,
                'level': points.level,
                'profile_completion': row['profile_completion_score']
            })
        
        return leaderboard
    
    @classmethod
    def _from_row(cls, row):
        """Create StudentPoints instance from database row"""
        return cls(
            id=row['id'],
            student_id=row['student_id'],
            total_points=row['total_points'],
            profile_completion_points=row['profile_completion_points'],
            engagement_points=row['engagement_points'],
            achievement_points=row['achievement_points'],
            level=row['level'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def add_points(self, category, activity, points=None):
        """Add points for a specific activity"""
        if points is None:
            if category in self.POINT_VALUES and activity in self.POINT_VALUES[category]:
                points = self.POINT_VALUES[category][activity]
            else:
                points = 0
        
        if points <= 0:
            return
        
        # Update category-specific points
        if category == 'profile_completion':
            self.profile_completion_points += points
        elif category == 'platform_engagement':
            self.engagement_points += points
        elif category == 'achievements':
            self.achievement_points += points
        
        # Update total points and level
        self.total_points += points
        self._update_level()
        
        # Log the point activity
        self._log_point_activity(category, activity, points)
        
        # Update in database
        self._update_in_db()
    
    def _update_level(self):
        """Update student level based on total points"""
        # Level calculation: every 500 points = 1 level
        new_level = max(1, (self.total_points // 500) + 1)
        
        if new_level > self.level:
            old_level = self.level
            self.level = new_level
            # Log level up achievement
            self._log_point_activity('achievements', f'level_up_{new_level}', 0, 
                                   f"Leveled up from {old_level} to {new_level}")
    
    def _log_point_activity(self, category, activity, points, description=None):
        """Log point activity for tracking"""
        query = '''
            INSERT INTO point_activities 
            (student_id, category, activity, points, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        
        if description is None:
            description = f"Earned {points} points for {activity}"
        
        execute_query(query, (
            self.student_id, category, activity, points, 
            description, datetime.utcnow()
        ))
    
    def _update_in_db(self):
        """Update points record in database"""
        query = '''
            UPDATE student_points SET
            total_points = ?, profile_completion_points = ?, 
            engagement_points = ?, achievement_points = ?, 
            level = ?, updated_at = ?
            WHERE id = ?
        '''
        
        self.updated_at = datetime.utcnow()
        execute_query(query, (
            self.total_points, self.profile_completion_points,
            self.engagement_points, self.achievement_points,
            self.level, self.updated_at, self.id
        ))
    
    def get_recent_activities(self, limit=10):
        """Get recent point activities for this student"""
        query = '''
            SELECT * FROM point_activities 
            WHERE student_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        '''
        rows = fetch_all(query, (self.student_id, limit))
        
        activities = []
        for row in rows:
            activities.append({
                'category': row['category'],
                'activity': row['activity'],
                'points': row['points'],
                'description': row['description'],
                'created_at': row['created_at']
            })
        
        return activities
    
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'total_points': self.total_points,
            'profile_completion_points': self.profile_completion_points,
            'engagement_points': self.engagement_points,
            'achievement_points': self.achievement_points,
            'level': self.level,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class Achievement:
    """Model for defining achievements and badges"""
    
    # Predefined achievements
    ACHIEVEMENTS = {
        'profile_master': {
            'name': 'Profile Master',
            'description': 'Complete 100% of your profile',
            'icon': 'fas fa-user-check',
            'color': '#28a745',
            'points': 200,
            'criteria': {'profile_completion_score': 100}
        },
        'skill_collector': {
            'name': 'Skill Collector',
            'description': 'Add 10 or more technical skills',
            'icon': 'fas fa-cogs',
            'color': '#007bff',
            'points': 150,
            'criteria': {'technical_skills_count': 10}
        },
        'first_application': {
            'name': 'First Step',
            'description': 'Submit your first job application',
            'icon': 'fas fa-paper-plane',
            'color': '#17a2b8',
            'points': 100,
            'criteria': {'job_applications_count': 1}
        },
        'active_learner': {
            'name': 'Active Learner',
            'description': 'Complete 5 skill assessments',
            'icon': 'fas fa-graduation-cap',
            'color': '#6f42c1',
            'points': 125,
            'criteria': {'skill_assessments_count': 5}
        },
        'networking_pro': {
            'name': 'Networking Pro',
            'description': 'Get viewed by 10 different employers',
            'icon': 'fas fa-handshake',
            'color': '#fd7e14',
            'points': 175,
            'criteria': {'employer_views_count': 10}
        },
        'consistent_user': {
            'name': 'Consistent User',
            'description': 'Login for 7 consecutive days',
            'icon': 'fas fa-calendar-check',
            'color': '#20c997',
            'points': 100,
            'criteria': {'consecutive_login_days': 7}
        },
        'top_performer': {
            'name': 'Top Performer',
            'description': 'Reach the top 10 on the leaderboard',
            'icon': 'fas fa-trophy',
            'color': '#ffc107',
            'points': 300,
            'criteria': {'leaderboard_rank': 10}
        }
    }
    
    def __init__(self, id=None, achievement_key=None, name=None, description=None,
                 icon=None, color=None, points=0, criteria=None, is_active=True,
                 created_at=None):
        self.id = id
        self.achievement_key = achievement_key
        self.name = name
        self.description = description
        self.icon = icon
        self.color = color
        self.points = points
        self.criteria = criteria or {}
        self.is_active = is_active
        self.created_at = created_at
    
    @classmethod
    def initialize_achievements(cls):
        """Initialize predefined achievements in database"""
        for key, achievement_data in cls.ACHIEVEMENTS.items():
            existing = cls.find_by_key(key)
            if not existing:
                cls.create(
                    achievement_key=key,
                    name=achievement_data['name'],
                    description=achievement_data['description'],
                    icon=achievement_data['icon'],
                    color=achievement_data['color'],
                    points=achievement_data['points'],
                    criteria=achievement_data['criteria']
                )
    
    @classmethod
    def create(cls, achievement_key, name, description, icon, color, points, criteria):
        """Create a new achievement"""
        query = '''
            INSERT INTO achievements 
            (achievement_key, name, description, icon, color, points, criteria, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        criteria_json = json.dumps(criteria)
        now = datetime.utcnow()
        
        cursor = execute_query(query, (
            achievement_key, name, description, icon, color, 
            points, criteria_json, True, now
        ))
        
        return cls.find_by_id(cursor.lastrowid)
    
    @classmethod
    def find_by_id(cls, achievement_id):
        """Find achievement by ID"""
        query = 'SELECT * FROM achievements WHERE id = ?'
        row = fetch_one(query, (achievement_id,))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def find_by_key(cls, achievement_key):
        """Find achievement by key"""
        query = 'SELECT * FROM achievements WHERE achievement_key = ?'
        row = fetch_one(query, (achievement_key,))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_all_active(cls):
        """Get all active achievements"""
        query = 'SELECT * FROM achievements WHERE is_active = 1 ORDER BY points DESC'
        rows = fetch_all(query)
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def _from_row(cls, row):
        """Create Achievement instance from database row"""
        criteria = {}
        if row['criteria']:
            try:
                criteria = json.loads(row['criteria'])
            except json.JSONDecodeError:
                criteria = {}
        
        return cls(
            id=row['id'],
            achievement_key=row['achievement_key'],
            name=row['name'],
            description=row['description'],
            icon=row['icon'],
            color=row['color'],
            points=row['points'],
            criteria=criteria,
            is_active=bool(row['is_active']),
            created_at=row['created_at']
        )
    
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'achievement_key': self.achievement_key,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'points': self.points,
            'criteria': self.criteria,
            'is_active': self.is_active,
            'created_at': self.created_at
        }


class StudentAchievement:
    """Model for tracking student achievements and badges"""
    
    def __init__(self, id=None, student_id=None, achievement_id=None, 
                 earned_at=None, is_displayed=True, shared_platforms=None):
        self.id = id
        self.student_id = student_id
        self.achievement_id = achievement_id
        self.earned_at = earned_at
        self.is_displayed = is_displayed
        self.shared_platforms = shared_platforms or []
    
    @classmethod
    def award_achievement(cls, student_id, achievement_key):
        """Award an achievement to a student"""
        # Check if already earned
        existing = cls.find_by_student_and_key(student_id, achievement_key)
        if existing:
            return existing
        
        # Get achievement details
        achievement = Achievement.find_by_key(achievement_key)
        if not achievement:
            return None
        
        # Create student achievement record
        query = '''
            INSERT INTO student_achievements 
            (student_id, achievement_id, earned_at, is_displayed, shared_platforms)
            VALUES (?, ?, ?, ?, ?)
        '''
        
        now = datetime.utcnow()
        shared_platforms_json = json.dumps([])
        
        cursor = execute_query(query, (
            student_id, achievement.id, now, True, shared_platforms_json
        ))
        
        # Award points to student
        from models.gamification import StudentPoints
        points = StudentPoints.create_or_get(student_id)
        points.add_points('achievements', achievement_key, achievement.points)
        
        return cls.find_by_id(cursor.lastrowid)
    
    @classmethod
    def find_by_id(cls, achievement_id):
        """Find student achievement by ID"""
        query = 'SELECT * FROM student_achievements WHERE id = ?'
        row = fetch_one(query, (achievement_id,))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def find_by_student_and_key(cls, student_id, achievement_key):
        """Find student achievement by student ID and achievement key"""
        query = '''
            SELECT sa.* FROM student_achievements sa
            JOIN achievements a ON sa.achievement_id = a.id
            WHERE sa.student_id = ? AND a.achievement_key = ?
        '''
        row = fetch_one(query, (student_id, achievement_key))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_student_achievements(cls, student_id, displayed_only=False):
        """Get all achievements for a student"""
        query = '''
            SELECT sa.*, a.achievement_key, a.name, a.description, 
                   a.icon, a.color, a.points
            FROM student_achievements sa
            JOIN achievements a ON sa.achievement_id = a.id
            WHERE sa.student_id = ?
        '''
        params = [student_id]
        
        if displayed_only:
            query += ' AND sa.is_displayed = 1'
        
        query += ' ORDER BY sa.earned_at DESC'
        
        rows = fetch_all(query, params)
        
        achievements = []
        for row in rows:
            student_achievement = cls._from_row(row)
            achievements.append({
                'id': student_achievement.id,
                'achievement_key': row['achievement_key'],
                'name': row['name'],
                'description': row['description'],
                'icon': row['icon'],
                'color': row['color'],
                'points': row['points'],
                'earned_at': student_achievement.earned_at,
                'is_displayed': student_achievement.is_displayed,
                'shared_platforms': student_achievement.shared_platforms
            })
        
        return achievements
    
    @classmethod
    def _from_row(cls, row):
        """Create StudentAchievement instance from database row"""
        shared_platforms = []
        if row['shared_platforms']:
            try:
                shared_platforms = json.loads(row['shared_platforms'])
            except json.JSONDecodeError:
                shared_platforms = []
        
        return cls(
            id=row['id'],
            student_id=row['student_id'],
            achievement_id=row['achievement_id'],
            earned_at=row['earned_at'],
            is_displayed=bool(row['is_displayed']),
            shared_platforms=shared_platforms
        )
    
    def toggle_display(self):
        """Toggle achievement display status"""
        self.is_displayed = not self.is_displayed
        query = 'UPDATE student_achievements SET is_displayed = ? WHERE id = ?'
        execute_query(query, (self.is_displayed, self.id))
    
    def add_shared_platform(self, platform):
        """Add a platform to shared platforms list"""
        if platform not in self.shared_platforms:
            self.shared_platforms.append(platform)
            self._update_shared_platforms()
    
    def remove_shared_platform(self, platform):
        """Remove a platform from shared platforms list"""
        if platform in self.shared_platforms:
            self.shared_platforms.remove(platform)
            self._update_shared_platforms()
    
    def _update_shared_platforms(self):
        """Update shared platforms in database"""
        shared_platforms_json = json.dumps(self.shared_platforms)
        query = 'UPDATE student_achievements SET shared_platforms = ? WHERE id = ?'
        execute_query(query, (shared_platforms_json, self.id))
    
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'achievement_id': self.achievement_id,
            'earned_at': self.earned_at,
            'is_displayed': self.is_displayed,
            'shared_platforms': self.shared_platforms
        }