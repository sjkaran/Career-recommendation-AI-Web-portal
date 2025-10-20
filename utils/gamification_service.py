"""
Gamification service for managing points, achievements, and engagement tracking
"""
from datetime import datetime, timedelta
from models.gamification import StudentPoints, Achievement, StudentAchievement
from models.student_profile import StudentProfile
from models.job_application import JobApplication
from database import fetch_one, fetch_all


class GamificationService:
    """Service for handling gamification logic and achievement checking"""
    
    @staticmethod
    def initialize_gamification():
        """Initialize gamification system with predefined achievements"""
        Achievement.initialize_achievements()
    
    @staticmethod
    def award_profile_completion_points(student_id, section):
        """Award points for completing profile sections"""
        points = StudentPoints.create_or_get(student_id)
        
        # Award points based on section completed
        if section in StudentPoints.POINT_VALUES['profile_completion']:
            points.add_points('profile_completion', section)
            
            # Check for profile completion achievements
            GamificationService._check_profile_achievements(student_id)
    
    @staticmethod
    def award_engagement_points(student_id, activity):
        """Award points for platform engagement activities"""
        points = StudentPoints.create_or_get(student_id)
        
        # Award points for engagement activity
        if activity in StudentPoints.POINT_VALUES['platform_engagement']:
            points.add_points('platform_engagement', activity)
            
            # Check for engagement-based achievements
            GamificationService._check_engagement_achievements(student_id)
    
    @staticmethod
    def check_all_achievements(student_id):
        """Check all possible achievements for a student"""
        GamificationService._check_profile_achievements(student_id)
        GamificationService._check_engagement_achievements(student_id)
        GamificationService._check_application_achievements(student_id)
        GamificationService._check_leaderboard_achievements(student_id)
    
    @staticmethod
    def _check_profile_achievements(student_id):
        """Check profile-related achievements"""
        profile = StudentProfile.find_by_user_id(student_id)
        if not profile:
            return
        
        # Profile Master achievement (100% completion)
        if profile.profile_completion_score >= 100:
            StudentAchievement.award_achievement(profile.id, 'profile_master')
        
        # Skill Collector achievement (10+ technical skills)
        if profile.technical_skills and len(profile.technical_skills) >= 10:
            StudentAchievement.award_achievement(profile.id, 'skill_collector')
    
    @staticmethod
    def _check_engagement_achievements(student_id):
        """Check engagement-related achievements"""
        # Consistent User achievement (7 consecutive login days)
        consecutive_days = GamificationService._get_consecutive_login_days(student_id)
        if consecutive_days >= 7:
            profile = StudentProfile.find_by_user_id(student_id)
            if profile:
                StudentAchievement.award_achievement(profile.id, 'consistent_user')
        
        # Networking Pro achievement (10+ employer views)
        employer_views = GamificationService._get_employer_views_count(student_id)
        if employer_views >= 10:
            profile = StudentProfile.find_by_user_id(student_id)
            if profile:
                StudentAchievement.award_achievement(profile.id, 'networking_pro')
    
    @staticmethod
    def _check_application_achievements(student_id):
        """Check application-related achievements"""
        profile = StudentProfile.find_by_user_id(student_id)
        if not profile:
            return
        
        # First Application achievement
        application_count = GamificationService._get_application_count(profile.id)
        if application_count >= 1:
            StudentAchievement.award_achievement(profile.id, 'first_application')
    
    @staticmethod
    def _check_leaderboard_achievements(student_id):
        """Check leaderboard-related achievements"""
        profile = StudentProfile.find_by_user_id(student_id)
        if not profile:
            return
        
        # Top Performer achievement (top 10 on leaderboard)
        leaderboard = StudentPoints.get_leaderboard(10)
        student_ranks = [entry for entry in leaderboard if entry.get('student_id') == profile.id]
        
        if student_ranks and student_ranks[0]['rank'] <= 10:
            StudentAchievement.award_achievement(profile.id, 'top_performer')
    
    @staticmethod
    def _get_consecutive_login_days(student_id):
        """Get consecutive login days for a student"""
        # This would require login tracking - for now return a placeholder
        # In a real implementation, you'd track login dates in a separate table
        query = '''
            SELECT COUNT(DISTINCT DATE(created_at)) as login_days
            FROM point_activities 
            WHERE student_id = ? AND activity = 'login'
            AND created_at >= date('now', '-7 days')
        '''
        
        result = fetch_one(query, (student_id,))
        return result['login_days'] if result else 0
    
    @staticmethod
    def _get_employer_views_count(student_id):
        """Get count of employer profile views"""
        # This would require view tracking - for now return a placeholder
        query = '''
            SELECT COUNT(*) as view_count
            FROM point_activities 
            WHERE student_id = ? AND activity = 'profile_view_by_employer'
        '''
        
        result = fetch_one(query, (student_id,))
        return result['view_count'] if result else 0
    
    @staticmethod
    def _get_application_count(student_profile_id):
        """Get count of job applications for a student"""
        query = 'SELECT COUNT(*) as app_count FROM job_applications WHERE student_id = ?'
        result = fetch_one(query, (student_profile_id,))
        return result['app_count'] if result else 0
    
    @staticmethod
    def get_student_gamification_data(student_id):
        """Get comprehensive gamification data for a student"""
        profile = StudentProfile.find_by_user_id(student_id)
        if not profile:
            return None
        
        # Get points data
        points = StudentPoints.create_or_get(profile.id)
        
        # Get achievements
        achievements = StudentAchievement.get_student_achievements(profile.id)
        
        # Get recent activities
        recent_activities = points.get_recent_activities(5)
        
        # Get leaderboard position
        leaderboard = StudentPoints.get_leaderboard(100)
        student_rank = None
        for i, entry in enumerate(leaderboard):
            if entry.get('student_id') == profile.id:
                student_rank = i + 1
                break
        
        # Get available achievements (not yet earned)
        all_achievements = Achievement.get_all_active()
        earned_keys = [ach['achievement_key'] for ach in achievements]
        available_achievements = [
            ach.to_dict() for ach in all_achievements 
            if ach.achievement_key not in earned_keys
        ]
        
        return {
            'points': points.to_dict(),
            'achievements': achievements,
            'recent_activities': recent_activities,
            'leaderboard_rank': student_rank,
            'available_achievements': available_achievements,
            'progress_to_next_level': GamificationService._get_progress_to_next_level(points),
            'achievement_progress': GamificationService._get_achievement_progress(profile.id)
        }
    
    @staticmethod
    def _get_progress_to_next_level(points):
        """Calculate progress to next level"""
        current_level_points = (points.level - 1) * 500
        next_level_points = points.level * 500
        progress_points = points.total_points - current_level_points
        points_needed = next_level_points - points.total_points
        
        return {
            'current_level': points.level,
            'next_level': points.level + 1,
            'progress_points': progress_points,
            'points_needed': max(0, points_needed),
            'progress_percentage': min(100, (progress_points / 500) * 100)
        }
    
    @staticmethod
    def _get_achievement_progress(student_profile_id):
        """Get progress towards available achievements"""
        profile = StudentProfile.find_by_id(student_profile_id)
        if not profile:
            return {}
        
        progress = {}
        
        # Profile completion progress
        progress['profile_master'] = {
            'current': profile.profile_completion_score,
            'target': 100,
            'percentage': profile.profile_completion_score
        }
        
        # Skill collector progress
        skill_count = len(profile.technical_skills) if profile.technical_skills else 0
        progress['skill_collector'] = {
            'current': skill_count,
            'target': 10,
            'percentage': min(100, (skill_count / 10) * 100)
        }
        
        # Application progress
        app_count = GamificationService._get_application_count(student_profile_id)
        progress['first_application'] = {
            'current': app_count,
            'target': 1,
            'percentage': min(100, app_count * 100)
        }
        
        return progress
    
    @staticmethod
    def get_leaderboard_with_context(student_id, limit=10):
        """Get leaderboard with current student's context"""
        leaderboard = StudentPoints.get_leaderboard(limit)
        
        # Find student's position if not in top list
        profile = StudentProfile.find_by_user_id(student_id)
        student_entry = None
        
        if profile:
            points = StudentPoints.find_by_student_id(profile.id)
            if points:
                # Get student's rank
                query = '''
                    SELECT COUNT(*) + 1 as rank
                    FROM student_points 
                    WHERE total_points > ?
                '''
                result = fetch_one(query, (points.total_points,))
                student_rank = result['rank'] if result else None
                
                student_entry = {
                    'rank': student_rank,
                    'student_name': f"{profile.first_name} {profile.last_name}" if profile.first_name else "You",
                    'total_points': points.total_points,
                    'level': points.level,
                    'profile_completion': profile.profile_completion_score,
                    'is_current_user': True
                }
        
        return {
            'leaderboard': leaderboard,
            'student_entry': student_entry,
            'total_students': GamificationService._get_total_students_count()
        }
    
    @staticmethod
    def _get_total_students_count():
        """Get total number of students with points"""
        query = 'SELECT COUNT(*) as total FROM student_points'
        result = fetch_one(query)
        return result['total'] if result else 0
    
    @staticmethod
    def simulate_profile_update(student_id):
        """Simulate profile update for testing gamification"""
        # Award engagement points for profile update
        GamificationService.award_engagement_points(student_id, 'profile_update')
        
        # Check all achievements
        GamificationService.check_all_achievements(student_id)
        
        return True
    
    @staticmethod
    def simulate_login(student_id):
        """Simulate login for testing gamification"""
        # Award engagement points for login
        GamificationService.award_engagement_points(student_id, 'login')
        
        # Check engagement achievements
        GamificationService._check_engagement_achievements(student_id)
        
        return True