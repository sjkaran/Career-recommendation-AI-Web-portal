from flask import Blueprint, request, jsonify, session
from models.user import User, db
from models.profile import StudentProfile
from models.employer import Employer
from werkzeug.security import check_password_hash
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data.get('email').strip().lower()
        password = data.get('password')
        user_type = data.get('user_type', 'student')
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        is_valid_pwd, pwd_msg = validate_password(password)
        if not is_valid_pwd:
            return jsonify({'error': pwd_msg}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'User already exists with this email'}), 409
        
        # Create new user
        new_user = User(email=email, user_type=user_type)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create profile based on user type
        if user_type == 'student':
            student_profile = StudentProfile(
                user_id=new_user.id,
                full_name=data.get('full_name', ''),
                college_name=data.get('college_name', 'BPUT Affiliated College')
            )
            student_profile.calculate_profile_completeness()
            db.session.add(student_profile)
        
        elif user_type == 'employer':
            employer_profile = Employer(
                user_id=new_user.id,
                company_name=data.get('company_name', ''),
                contact_person=data.get('contact_person', '')
            )
            db.session.add(employer_profile)
        
        db.session.commit()
        
        # Store user in session
        session['user_id'] = new_user.id
        session['user_type'] = new_user.user_type
        
        return jsonify({
            'message': 'User registered successfully',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data.get('email').strip().lower()
        password = data.get('password')
        
        # Find user
        user = User.query.filter_by(email=email, is_active=True).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Store user in session
        session['user_id'] = user.id
        session['user_type'] = user.user_type
        
        # Get profile data based on user type
        profile_data = None
        if user.user_type == 'student' and user.student_profile:
            profile_data = user.student_profile.to_dict()
        elif user.user_type == 'employer' and user.employer_profile:
            profile_data = user.employer_profile.to_dict()
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'profile': profile_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        # Clear session
        session.clear()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        profile_data = None
        if user.user_type == 'student' and user.student_profile:
            profile_data = user.student_profile.to_dict()
        elif user.user_type == 'employer' and user.employer_profile:
            profile_data = user.employer_profile.to_dict()
        
        return jsonify({
            'user': user.to_dict(),
            'profile': profile_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get user: {str(e)}'}), 500