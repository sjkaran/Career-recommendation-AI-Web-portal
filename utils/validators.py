"""
Input validation utilities with comprehensive security measures
"""
import re
import html
import bleach
import os
import magic
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlparse
from werkzeug.utils import secure_filename

# Allowed HTML tags and attributes for rich text content
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'a']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}

# File upload security settings
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'document': {'pdf', 'doc', 'docx', 'txt'},
    'resume': {'pdf', 'doc', 'docx'}
}

MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
DANGEROUS_EXTENSIONS = {
    'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar', 
    'php', 'asp', 'aspx', 'jsp', 'py', 'pl', 'sh', 'ps1'
}

def validate_email(email: str) -> bool:
    """Validate email format with enhanced security"""
    if not email or not isinstance(email, str):
        return False
    
    # Basic length check
    if len(email) > 254:  # RFC 5321 limit
        return False
    
    # Sanitize input
    email = email.strip().lower()
    
    # Enhanced email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False
    
    # Additional security checks
    local_part, domain = email.split('@')
    
    # Check local part length (64 characters max)
    if len(local_part) > 64:
        return False
    
    # Check for consecutive dots
    if '..' in email:
        return False
    
    # Check for dangerous patterns
    dangerous_patterns = ['javascript:', 'data:', 'vbscript:', '<script']
    for pattern in dangerous_patterns:
        if pattern in email.lower():
            return False
    
    return True

def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Simple validation for Indian phone numbers
    pattern = r'^[+]?[0-9]{10,15}$'
    return re.match(pattern, phone.replace(' ', '').replace('-', '')) is not None

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """Validate that required fields are present and not empty"""
    errors = []
    
    for field in required_fields:
        if field not in data or not data[field] or str(data[field]).strip() == '':
            errors.append(f"{field} is required")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def sanitize_input(text: str, allow_html: bool = False) -> str:
    """Comprehensive input sanitization with XSS protection"""
    if not text:
        return ""
    
    # Convert to string and strip whitespace
    text = str(text).strip()
    
    if not text:
        return ""
    
    if allow_html:
        # Use bleach to sanitize HTML content
        text = bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
    else:
        # Escape HTML entities for plain text
        text = html.escape(text)
    
    # Remove null bytes and other control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r'javascript\s*:',
        r'data\s*:',
        r'vbscript\s*:',
        r'on\w+\s*=',
        r'<\s*script',
        r'<\s*iframe',
        r'<\s*object',
        r'<\s*embed',
        r'<\s*link',
        r'<\s*meta',
        r'<\s*style'
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text

def validate_and_sanitize_json_field(data: Any, field_name: str, max_length: int = 1000) -> Dict[str, Any]:
    """Validate and sanitize JSON field data"""
    errors = []
    
    if not data:
        return {'valid': True, 'data': None, 'errors': []}
    
    # Convert to string if not already
    if isinstance(data, (dict, list)):
        import json
        try:
            data_str = json.dumps(data)
        except (TypeError, ValueError):
            return {'valid': False, 'data': None, 'errors': [f'{field_name} contains invalid JSON data']}
    else:
        data_str = str(data)
    
    # Check length
    if len(data_str) > max_length:
        errors.append(f'{field_name} exceeds maximum length of {max_length} characters')
    
    # Sanitize the string representation
    sanitized_str = sanitize_input(data_str, allow_html=False)
    
    # Try to parse back to original type
    if isinstance(data, (dict, list)):
        try:
            import json
            sanitized_data = json.loads(sanitized_str)
        except (TypeError, ValueError):
            sanitized_data = sanitized_str
    else:
        sanitized_data = sanitized_str
    
    return {
        'valid': len(errors) == 0,
        'data': sanitized_data,
        'errors': errors
    }

def validate_url(url: str) -> Dict[str, Any]:
    """Validate URL with security checks"""
    errors = []
    
    if not url or not isinstance(url, str):
        return {'valid': False, 'errors': ['URL is required']}
    
    url = url.strip()
    
    # Basic length check
    if len(url) > 2048:
        errors.append('URL is too long (max 2048 characters)')
    
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ['http', 'https']:
            errors.append('URL must use http or https protocol')
        
        # Check for localhost/private IPs in production
        if parsed.hostname:
            hostname = parsed.hostname.lower()
            dangerous_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
            if hostname in dangerous_hosts or hostname.startswith('192.168.') or hostname.startswith('10.'):
                errors.append('Private/local URLs are not allowed')
        
        # Check for dangerous patterns
        dangerous_patterns = ['javascript:', 'data:', 'vbscript:', 'file:']
        for pattern in dangerous_patterns:
            if pattern in url.lower():
                errors.append('URL contains dangerous protocol')
        
    except Exception:
        errors.append('Invalid URL format')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'sanitized_url': sanitize_input(url) if len(errors) == 0 else None
    }

def validate_file_upload(file, file_type: str = 'document') -> Dict[str, Any]:
    """Comprehensive file upload validation and security checks"""
    errors = []
    
    if not file:
        return {'valid': False, 'errors': ['No file provided']}
    
    # Check if file has a filename
    if not file.filename:
        errors.append('File must have a filename')
        return {'valid': False, 'errors': errors}
    
    # Secure the filename
    filename = secure_filename(file.filename)
    if not filename:
        errors.append('Invalid filename')
        return {'valid': False, 'errors': errors}
    
    # Check file extension
    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    # Check against dangerous extensions
    if file_ext in DANGEROUS_EXTENSIONS:
        errors.append(f'File type .{file_ext} is not allowed for security reasons')
    
    # Check against allowed extensions for file type
    allowed_exts = ALLOWED_EXTENSIONS.get(file_type, set())
    if allowed_exts and file_ext not in allowed_exts:
        errors.append(f'File type .{file_ext} is not allowed. Allowed types: {", ".join(allowed_exts)}')
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size > MAX_FILE_SIZE:
        errors.append(f'File size ({file_size} bytes) exceeds maximum allowed size ({MAX_FILE_SIZE} bytes)')
    
    if file_size == 0:
        errors.append('File is empty')
    
    # MIME type validation using python-magic
    try:
        file_content = file.read(1024)  # Read first 1KB for MIME detection
        file.seek(0)  # Reset file pointer
        
        mime_type = magic.from_buffer(file_content, mime=True)
        
        # Define expected MIME types for each file type
        expected_mimes = {
            'image': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            'document': ['application/pdf', 'application/msword', 
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        'text/plain'],
            'resume': ['application/pdf', 'application/msword',
                      'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        }
        
        if file_type in expected_mimes:
            if mime_type not in expected_mimes[file_type]:
                errors.append(f'File content type {mime_type} does not match expected types for {file_type}')
    
    except Exception as e:
        # If magic fails, we'll rely on extension validation
        pass
    
    # Check for embedded scripts in file content (basic check)
    try:
        file.seek(0)
        content_sample = file.read(8192).decode('utf-8', errors='ignore')  # Read first 8KB
        file.seek(0)
        
        script_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'vbscript:',
            r'on\w+\s*=',
            r'<%.*%>',
            r'<?php',
            r'#!/bin/'
        ]
        
        for pattern in script_patterns:
            if re.search(pattern, content_sample, re.IGNORECASE):
                errors.append('File contains potentially malicious content')
                break
    
    except Exception:
        # If content reading fails, continue with other validations
        pass
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'filename': filename,
        'file_size': file_size,
        'file_extension': file_ext
    }

def validate_sql_injection(text: str) -> bool:
    """Check for potential SQL injection patterns"""
    if not text or not isinstance(text, str):
        return True
    
    # Common SQL injection patterns
    sql_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
        r"(--|#|/\*|\*/)",
        r"(\bxp_\w+)",
        r"(\bsp_\w+)",
        r"(\bUNION\s+SELECT)",
        r"(;\s*(DROP|DELETE|INSERT|UPDATE))",
        r"(\'\s*(OR|AND)\s*\'\w*\'\s*=\s*\'\w*\')",
        r"(\d+\s*(OR|AND)\s*\d+\s*=\s*\d+)"
    ]
    
    text_upper = text.upper()
    
    for pattern in sql_patterns:
        if re.search(pattern, text_upper, re.IGNORECASE):
            return False
    
    return True

def validate_xss_patterns(text: str) -> bool:
    """Check for potential XSS patterns"""
    if not text or not isinstance(text, str):
        return True
    
    # Common XSS patterns
    xss_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript\s*:",
        r"vbscript\s*:",
        r"data\s*:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<link[^>]*>",
        r"<meta[^>]*>",
        r"<style[^>]*>.*?</style>",
        r"expression\s*\(",
        r"url\s*\(",
        r"@import",
        r"<\s*img[^>]+src\s*=\s*['\"]?\s*javascript:",
        r"<\s*body[^>]+onload\s*="
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            return False
    
    return True

def comprehensive_input_validation(data: Dict[str, Any], validation_rules: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Comprehensive input validation with custom rules
    
    validation_rules format:
    {
        'field_name': {
            'required': True/False,
            'type': 'string'/'int'/'float'/'email'/'url'/'list'/'dict',
            'min_length': int,
            'max_length': int,
            'allow_html': True/False,
            'custom_pattern': regex_pattern,
            'sanitize': True/False
        }
    }
    """
    errors = []
    sanitized_data = {}
    
    for field_name, rules in validation_rules.items():
        field_value = data.get(field_name)
        
        # Check required fields
        if rules.get('required', False):
            if field_value is None or (isinstance(field_value, str) and not field_value.strip()):
                errors.append(f'{field_name} is required')
                continue
        
        # Skip validation for optional empty fields
        if field_value is None or (isinstance(field_value, str) and not field_value.strip()):
            sanitized_data[field_name] = field_value
            continue
        
        # Type validation
        field_type = rules.get('type', 'string')
        
        if field_type == 'email':
            if not validate_email(str(field_value)):
                errors.append(f'{field_name} must be a valid email address')
                continue
            sanitized_data[field_name] = str(field_value).strip().lower()
        
        elif field_type == 'url':
            url_validation = validate_url(str(field_value))
            if not url_validation['valid']:
                errors.extend([f'{field_name}: {error}' for error in url_validation['errors']])
                continue
            sanitized_data[field_name] = url_validation['sanitized_url']
        
        elif field_type in ['string', 'text']:
            text_value = str(field_value)
            
            # Length validation
            min_len = rules.get('min_length', 0)
            max_len = rules.get('max_length', 10000)
            
            if len(text_value) < min_len:
                errors.append(f'{field_name} must be at least {min_len} characters long')
                continue
            
            if len(text_value) > max_len:
                errors.append(f'{field_name} must not exceed {max_len} characters')
                continue
            
            # Security validation
            if not validate_sql_injection(text_value):
                errors.append(f'{field_name} contains potentially dangerous SQL patterns')
                continue
            
            if not validate_xss_patterns(text_value):
                errors.append(f'{field_name} contains potentially dangerous script patterns')
                continue
            
            # Custom pattern validation
            if 'custom_pattern' in rules:
                if not re.match(rules['custom_pattern'], text_value):
                    errors.append(f'{field_name} format is invalid')
                    continue
            
            # Sanitization
            if rules.get('sanitize', True):
                allow_html = rules.get('allow_html', False)
                sanitized_data[field_name] = sanitize_input(text_value, allow_html=allow_html)
            else:
                sanitized_data[field_name] = text_value
        
        elif field_type == 'int':
            try:
                sanitized_data[field_name] = int(field_value)
            except (ValueError, TypeError):
                errors.append(f'{field_name} must be a valid integer')
        
        elif field_type == 'float':
            try:
                sanitized_data[field_name] = float(field_value)
            except (ValueError, TypeError):
                errors.append(f'{field_name} must be a valid number')
        
        elif field_type == 'list':
            if not isinstance(field_value, list):
                errors.append(f'{field_name} must be a list')
                continue
            
            # Sanitize list items if they are strings
            sanitized_list = []
            for item in field_value:
                if isinstance(item, str):
                    if rules.get('sanitize', True):
                        sanitized_item = sanitize_input(item, allow_html=rules.get('allow_html', False))
                    else:
                        sanitized_item = item
                    sanitized_list.append(sanitized_item)
                else:
                    sanitized_list.append(item)
            
            sanitized_data[field_name] = sanitized_list
        
        elif field_type == 'dict':
            if not isinstance(field_value, dict):
                errors.append(f'{field_name} must be a dictionary')
                continue
            
            sanitized_data[field_name] = field_value
        
        else:
            # Default: treat as string
            sanitized_data[field_name] = sanitize_input(str(field_value))
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'data': sanitized_data
    }


def validate_academic_data(academic_records: Dict[str, Any]) -> Dict[str, Any]:
    """Validate academic records data"""
    errors = []
    
    if not isinstance(academic_records, dict):
        return {
            'valid': False,
            'errors': ['Academic records must be a dictionary']
        }
    
    # Validate CGPA
    if 'cgpa' in academic_records:
        try:
            cgpa = float(academic_records['cgpa'])
            if not (0 <= cgpa <= 10):
                errors.append("CGPA must be between 0 and 10")
        except (ValueError, TypeError):
            errors.append("CGPA must be a valid number")
    
    # Validate year
    if 'year' in academic_records:
        try:
            year = int(academic_records['year'])
            from datetime import datetime
            current_year = datetime.now().year
            if not (1900 <= year <= current_year + 10):
                errors.append("Year must be a valid year")
        except (ValueError, TypeError):
            errors.append("Year must be a valid number")
    
    # Validate branch
    if 'branch' in academic_records:
        branch = str(academic_records['branch']).strip()
        if len(branch) < 2:
            errors.append("Branch name must be at least 2 characters long")
    
    # Validate university
    if 'university' in academic_records:
        university = str(academic_records['university']).strip()
        if len(university) < 2:
            errors.append("University name must be at least 2 characters long")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def validate_skills_data(technical_skills: List[str], soft_skills: List[str]) -> Dict[str, Any]:
    """Validate skills data"""
    errors = []
    
    # Validate technical skills
    if not isinstance(technical_skills, list):
        errors.append("Technical skills must be a list")
    else:
        for i, skill in enumerate(technical_skills):
            if not isinstance(skill, str) or len(skill.strip()) == 0:
                errors.append(f"Technical skill {i+1} must be a non-empty string")
            elif len(skill.strip()) > 100:
                errors.append(f"Technical skill {i+1} is too long (max 100 characters)")
    
    # Validate soft skills
    if not isinstance(soft_skills, list):
        errors.append("Soft skills must be a list")
    else:
        for i, skill in enumerate(soft_skills):
            if not isinstance(skill, str) or len(skill.strip()) == 0:
                errors.append(f"Soft skill {i+1} must be a non-empty string")
            elif len(skill.strip()) > 100:
                errors.append(f"Soft skill {i+1} is too long (max 100 characters)")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def validate_activities_data(co_curricular: List[Dict], extra_curricular: List[Dict]) -> Dict[str, Any]:
    """Validate activities data"""
    errors = []
    
    # Validate co-curricular activities
    if not isinstance(co_curricular, list):
        errors.append("Co-curricular activities must be a list")
    else:
        for i, activity in enumerate(co_curricular):
            if isinstance(activity, dict):
                if 'name' not in activity or not activity['name']:
                    errors.append(f"Co-curricular activity {i+1} must have a name")
            elif isinstance(activity, str):
                if len(activity.strip()) == 0:
                    errors.append(f"Co-curricular activity {i+1} cannot be empty")
            else:
                errors.append(f"Co-curricular activity {i+1} must be a string or dictionary")
    
    # Validate extra-curricular activities
    if not isinstance(extra_curricular, list):
        errors.append("Extra-curricular activities must be a list")
    else:
        for i, activity in enumerate(extra_curricular):
            if isinstance(activity, dict):
                if 'name' not in activity or not activity['name']:
                    errors.append(f"Extra-curricular activity {i+1} must have a name")
            elif isinstance(activity, str):
                if len(activity.strip()) == 0:
                    errors.append(f"Extra-curricular activity {i+1} cannot be empty")
            else:
                errors.append(f"Extra-curricular activity {i+1} must be a string or dictionary")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def validate_profile_completeness(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate overall profile completeness and provide suggestions"""
    suggestions = []
    completion_score = 0
    
    # Check personal information (20 points)
    if profile_data.get('first_name') and profile_data.get('last_name'):
        completion_score += 15
        if profile_data.get('phone'):
            completion_score += 5
    else:
        suggestions.append("Add your full name")
        if not profile_data.get('phone'):
            suggestions.append("Add your phone number")
    
    # Check academic records (25 points)
    academic_records = profile_data.get('academic_records', {})
    if academic_records:
        required_academic_fields = ['cgpa', 'branch', 'year', 'university']
        filled_academic = sum(1 for field in required_academic_fields if academic_records.get(field))
        completion_score += (filled_academic / len(required_academic_fields)) * 25
        
        if filled_academic < len(required_academic_fields):
            missing_fields = [field for field in required_academic_fields if not academic_records.get(field)]
            suggestions.append(f"Complete academic records: {', '.join(missing_fields)}")
    else:
        suggestions.append("Add your academic records")
    
    # Check technical skills (20 points)
    technical_skills = profile_data.get('technical_skills', [])
    if len(technical_skills) >= 3:
        completion_score += 20
    elif len(technical_skills) > 0:
        completion_score += (len(technical_skills) / 3) * 20
        suggestions.append(f"Add {3 - len(technical_skills)} more technical skills")
    else:
        suggestions.append("Add at least 3 technical skills")
    
    # Check soft skills (15 points)
    soft_skills = profile_data.get('soft_skills', [])
    if len(soft_skills) >= 3:
        completion_score += 15
    elif len(soft_skills) > 0:
        completion_score += (len(soft_skills) / 3) * 15
        suggestions.append(f"Add {3 - len(soft_skills)} more soft skills")
    else:
        suggestions.append("Add at least 3 soft skills")
    
    # Check activities (20 points total)
    co_curricular = profile_data.get('co_curricular', [])
    extra_curricular = profile_data.get('extra_curricular', [])
    
    if co_curricular:
        completion_score += 10
    else:
        suggestions.append("Add co-curricular activities")
    
    if extra_curricular:
        completion_score += 10
    else:
        suggestions.append("Add extra-curricular activities")
    
    # Career interests bonus
    career_interests = profile_data.get('career_interests', [])
    if not career_interests:
        suggestions.append("Add your career interests for better recommendations")
    
    return {
        'completion_score': min(100, int(completion_score)),
        'suggestions': suggestions,
        'is_complete': completion_score >= 80
    }