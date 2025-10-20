"""
Authentication helper functions and middleware
"""
import jwt
import bcrypt
import logging
from datetime import datetime, timedelta
from flask import current_app, request, jsonify, g
from functools import wraps
from models.user import User

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_jwt_token(user_id, role):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def decode_jwt_token(token):
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user():
    """Get current authenticated user from request context"""
    return getattr(g, 'current_user', None)

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Extract token from Authorization header
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.warning(f"Missing or invalid authorization header for {request.endpoint}")
                return jsonify({'error': 'Authorization token required'}), 401
            
            token = auth_header.split(' ')[1]
            
            # Verify token and get user
            user = User.verify_jwt_token(token)
            
            if not user:
                logger.warning(f"Invalid or expired token for {request.endpoint}")
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            if not user.is_active:
                logger.warning(f"Inactive user attempted access: {user.email}")
                return jsonify({'error': 'Account is deactivated'}), 401
            
            # Store user in request context
            g.current_user = user
            
            # Log successful authentication
            logger.info(f"Authenticated user {user.email} accessing {request.endpoint}")
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function

def require_role(allowed_roles):
    """Decorator to require specific role(s)"""
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # First ensure user is authenticated
                auth_header = request.headers.get('Authorization')
                
                if not auth_header or not auth_header.startswith('Bearer '):
                    logger.warning(f"Missing authorization header for role-protected endpoint {request.endpoint}")
                    return jsonify({'error': 'Authorization token required'}), 401
                
                token = auth_header.split(' ')[1]
                
                # Verify token and get user
                user = User.verify_jwt_token(token)
                
                if not user:
                    logger.warning(f"Invalid token for role-protected endpoint {request.endpoint}")
                    return jsonify({'error': 'Invalid or expired token'}), 401
                
                if not user.is_active:
                    logger.warning(f"Inactive user attempted role-protected access: {user.email}")
                    return jsonify({'error': 'Account is deactivated'}), 401
                
                # Check if user has required role
                if user.role not in allowed_roles:
                    logger.warning(f"User {user.email} with role {user.role} attempted to access {request.endpoint} requiring roles {allowed_roles}")
                    return jsonify({'error': f'Access denied. Required role(s): {allowed_roles}'}), 403
                
                # Store user in request context
                g.current_user = user
                
                # Log successful authorization
                logger.info(f"Authorized user {user.email} ({user.role}) accessing {request.endpoint}")
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Authorization error: {str(e)}")
                return jsonify({'error': 'Authorization failed'}), 403
        
        return decorated_function
    return decorator

def require_roles(*roles):
    """Alternative decorator syntax for multiple roles"""
    return require_role(list(roles))

def log_user_action(action, details=None):
    """Log user actions for audit trail"""
    try:
        user = get_current_user()
        if user:
            log_entry = {
                'user_id': user.id,
                'user_email': user.email,
                'user_role': user.role,
                'action': action,
                'endpoint': request.endpoint,
                'method': request.method,
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'timestamp': datetime.utcnow().isoformat(),
                'details': details
            }
            
            # In a production system, you would store this in a dedicated audit log table
            logger.info(f"AUDIT: {log_entry}")
            
            return log_entry
    except Exception as e:
        logger.error(f"Audit logging error: {str(e)}")
    
    return None

def audit_log(action):
    """Decorator to automatically log user actions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Execute the function first
            result = f(*args, **kwargs)
            
            # Log the action after successful execution
            try:
                log_user_action(action)
            except Exception as e:
                logger.error(f"Failed to log action {action}: {str(e)}")
            
            return result
        return decorated_function
    return decorator

def check_permission(resource, action):
    """Check if current user has permission for specific resource and action"""
    user = get_current_user()
    if not user:
        return False
    
    # Basic role-based permissions
    permissions = {
        'student': {
            'profile': ['read', 'update'],
            'jobs': ['read'],
            'applications': ['create', 'read', 'update']
        },
        'employer': {
            'jobs': ['create', 'read', 'update', 'delete'],
            'candidates': ['read'],
            'applications': ['read', 'update']
        },
        'placement_officer': {
            'analytics': ['read'],
            'reports': ['create', 'read'],
            'users': ['read'],
            'placements': ['create', 'read', 'update']
        }
    }
    
    user_permissions = permissions.get(user.role, {})
    resource_permissions = user_permissions.get(resource, [])
    
    return action in resource_permissions

def require_permission(resource, action):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            if not check_permission(resource, action):
                user = get_current_user()
                logger.warning(f"User {user.email} denied permission {action} on {resource}")
                return jsonify({'error': f'Permission denied for {action} on {resource}'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator