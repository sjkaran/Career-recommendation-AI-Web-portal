"""
User model with role-based authentication
"""
import json
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from database import execute_query, fetch_one, fetch_all


class User:
    """User model with role-based fields and authentication"""
    
    ROLES = ['student', 'employer', 'placement_officer']
    
    def __init__(self, id=None, email=None, password_hash=None, role=None, 
                 is_active=True, created_at=None, updated_at=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def create(cls, email, password, role):
        """Create a new user with hashed password"""
        if role not in cls.ROLES:
            raise ValueError(f"Invalid role. Must be one of: {cls.ROLES}")
        
        # Check if user already exists
        existing_user = cls.find_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        password_hash = generate_password_hash(password)
        
        query = '''
            INSERT INTO users (email, password_hash, role, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        now = datetime.utcnow()
        cursor = execute_query(query, (email, password_hash, role, True, now, now))
        
        return cls.find_by_id(cursor.lastrowid)
    
    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID"""
        query = 'SELECT * FROM users WHERE id = ?'
        row = fetch_one(query, (user_id,))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        query = 'SELECT * FROM users WHERE email = ?'
        row = fetch_one(query, (email,))
        
        if row:
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_all_by_role(cls, role):
        """Get all users by role"""
        if role not in cls.ROLES:
            raise ValueError(f"Invalid role. Must be one of: {cls.ROLES}")
        
        query = 'SELECT * FROM users WHERE role = ? AND is_active = 1'
        rows = fetch_all(query, (role,))
        
        return [cls._from_row(row) for row in rows]
    
    @classmethod
    def _from_row(cls, row):
        """Create User instance from database row"""
        return cls(
            id=row['id'],
            email=row['email'],
            password_hash=row['password_hash'],
            role=row['role'],
            is_active=bool(row['is_active']),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def check_password(self, password):
        """Check if provided password matches user's password"""
        return check_password_hash(self.password_hash, password)
    
    def update_password(self, new_password):
        """Update user's password"""
        new_password_hash = generate_password_hash(new_password)
        query = 'UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?'
        execute_query(query, (new_password_hash, datetime.utcnow(), self.id))
        self.password_hash = new_password_hash
    
    def deactivate(self):
        """Deactivate user account"""
        query = 'UPDATE users SET is_active = 0, updated_at = ? WHERE id = ?'
        execute_query(query, (datetime.utcnow(), self.id))
        self.is_active = False
    
    def activate(self):
        """Activate user account"""
        query = 'UPDATE users SET is_active = 1, updated_at = ? WHERE id = ?'
        execute_query(query, (datetime.utcnow(), self.id))
        self.is_active = True
    
    def generate_jwt_token(self, expires_in=None):
        """Generate JWT token for user authentication"""
        if expires_in is None:
            expires_in = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=24))
        
        if isinstance(expires_in, timedelta):
            expires_in = expires_in.total_seconds()
        
        payload = {
            'user_id': self.id,
            'email': self.email,
            'role': self.role,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow()
        }
        
        secret_key = current_app.config.get('JWT_SECRET_KEY', current_app.config['SECRET_KEY'])
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    @staticmethod
    def verify_jwt_token(token):
        """Verify JWT token and return user"""
        try:
            secret_key = current_app.config.get('JWT_SECRET_KEY', current_app.config['SECRET_KEY'])
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = payload['user_id']
            return User.find_by_id(user_id)
        except jwt.ExpiredSignatureError:
            return None  # Token expired
        except jwt.InvalidTokenError:
            return None  # Invalid token
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary representation"""
        data = {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data
    
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'