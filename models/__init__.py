"""
Database models for AI Career Platform
"""
from .user import User
from .student_profile import StudentProfile
from .employer import Employer
from .job_posting import JobPosting
from .job_application import JobApplication
from .placement_analytics import PlacementAnalytics
from .skill_demand import SkillDemand

__all__ = [
    'User',
    'StudentProfile', 
    'Employer',
    'JobPosting',
    'JobApplication',
    'PlacementAnalytics',
    'SkillDemand'
]