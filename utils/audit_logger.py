"""
Comprehensive audit logging system for GDPR compliance and security monitoring
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from flask import request, g
from database import get_db
from utils.auth_helpers import get_current_user

# Set up audit logger
audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)

# Create audit log handler (in production, use a separate log file or database)
audit_handler = logging.FileHandler('audit.log')
audit_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
audit_handler.setFormatter(audit_formatter)
audit_logger.addHandler(audit_handler)

class AuditEventType:
    """Audit event type constants"""
    
    # Authentication events
    LOGIN_SUCCESS = 'login_success'
    LOGIN_FAILURE = 'login_failure'
    LOGOUT = 'logout'
    PASSWORD_CHANGE = 'password_change'
    ACCOUNT_LOCKED = 'account_locked'
    
    # Data access events
    DATA_READ = 'data_read'
    DATA_CREATE = 'data_create'
    DATA_UPDATE = 'data_update'
    DATA_DELETE = 'data_delete'
    DATA_EXPORT = 'data_export'
    
    # Privacy events
    CONSENT_GIVEN = 'consent_given'
    CONSENT_WITHDRAWN = 'consent_withdrawn'
    DATA_ANONYMIZED = 'data_anonymized'
    DATA_PURGED = 'data_purged'
    GDPR_REQUEST = 'gdpr_request'
    
    # Security events
    SECURITY_VIOLATION = 'security_violation'
    RATE_LIMIT_EXCEEDED = 'rate_limit_exceeded'
    SUSPICIOUS_ACTIVITY = 'suspicious_activity'
    UNAUTHORIZED_ACCESS = 'unauthorized_access'
    
    # System events
    SYSTEM_ERROR = 'system_error'
    CONFIGURATION_CHANGE = 'configuration_change'
    BACKUP_CREATED = 'backup_created'

class AuditLogger:
    """Centralized audit logging system"""
    
    @staticmethod
    def log_event(
        event_type: str,
        resource_type: str = None,
        resource_id: str = None,
        details: Dict[str, Any] = None,
        user_id: int = None,
        ip_address: str = None,
        user_agent: str = None,
        success: bool = True,
        error_message: str = None
    ):
        """Log an audit event"""
        
        # Get current user if not provided
        if user_id is None:
            current_user = get_current_user()
            user_id = current_user.id if current_user else None
        
        # Get request context if available
        if ip_address is None and request:
            ip_address = request.remote_addr
        
        if user_agent is None and request:
            user_agent = request.headers.get('User-Agent', '')[:200]
        
        # Create audit entry
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'success': success,
            'error_message': error_message,
            'details': details or {},
            'request_id': getattr(g, 'request_id', None),
            'session_id': getattr(g, 'session_id', None)
        }
        
        # Log to audit logger
        audit_logger.info(json.dumps(audit_entry))
        
        # Store in database for queryable audit trail
        try:
            AuditLogger._store_audit_entry(audit_entry)
        except Exception as e:
            # Don't let audit logging failures break the application
            audit_logger.error(f"Failed to store audit entry in database: {str(e)}")
    
    @staticmethod
    def _store_audit_entry(audit_entry: Dict[str, Any]):
        """Store audit entry in database"""
        db = get_db()
        
        # Create audit_logs table if it doesn't exist
        db.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                user_id INTEGER,
                resource_type TEXT,
                resource_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                details TEXT,
                request_id TEXT,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert audit entry
        db.execute('''
            INSERT INTO audit_logs (
                timestamp, event_type, user_id, resource_type, resource_id,
                ip_address, user_agent, success, error_message, details,
                request_id, session_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            audit_entry['timestamp'],
            audit_entry['event_type'],
            audit_entry['user_id'],
            audit_entry['resource_type'],
            audit_entry['resource_id'],
            audit_entry['ip_address'],
            audit_entry['user_agent'],
            audit_entry['success'],
            audit_entry['error_message'],
            json.dumps(audit_entry['details']),
            audit_entry['request_id'],
            audit_entry['session_id']
        ))
        
        db.commit()
    
    @staticmethod
    def log_data_access(resource_type: str, resource_id: str, action: str, details: Dict = None):
        """Log data access events"""
        event_type = f"data_{action.lower()}"
        AuditLogger.log_event(
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details
        )
    
    @staticmethod
    def log_authentication(event_type: str, user_email: str = None, success: bool = True, details: Dict = None):
        """Log authentication events"""
        AuditLogger.log_event(
            event_type=event_type,
            resource_type='user',
            resource_id=user_email,
            success=success,
            details=details
        )
    
    @staticmethod
    def log_privacy_event(event_type: str, user_id: int, details: Dict = None):
        """Log privacy-related events"""
        AuditLogger.log_event(
            event_type=event_type,
            resource_type='user_privacy',
            resource_id=str(user_id),
            user_id=user_id,
            details=details
        )
    
    @staticmethod
    def log_security_event(event_type: str, details: Dict = None, severity: str = 'medium'):
        """Log security events"""
        security_details = details or {}
        security_details['severity'] = severity
        
        AuditLogger.log_event(
            event_type=event_type,
            resource_type='security',
            details=security_details,
            success=False  # Security events are typically failures
        )
    
    @staticmethod
    def get_audit_logs(
        user_id: int = None,
        event_type: str = None,
        resource_type: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve audit logs with filtering"""
        db = get_db()
        
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        if resource_type:
            query += " AND resource_type = ?"
            params.append(resource_type)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = db.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        logs = []
        for row in rows:
            log_entry = dict(row)
            # Parse JSON details
            if log_entry['details']:
                try:
                    log_entry['details'] = json.loads(log_entry['details'])
                except json.JSONDecodeError:
                    log_entry['details'] = {}
            
            logs.append(log_entry)
        
        return logs
    
    @staticmethod
    def cleanup_old_logs(retention_days: int = 365):
        """Clean up old audit logs (GDPR compliance)"""
        db = get_db()
        
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # Count logs to be deleted
        cursor = db.execute(
            "SELECT COUNT(*) as count FROM audit_logs WHERE timestamp < ?",
            (cutoff_date.isoformat(),)
        )
        count = cursor.fetchone()['count']
        
        # Delete old logs
        db.execute(
            "DELETE FROM audit_logs WHERE timestamp < ?",
            (cutoff_date.isoformat(),)
        )
        db.commit()
        
        # Log the cleanup action
        AuditLogger.log_event(
            event_type='audit_cleanup',
            resource_type='audit_logs',
            details={
                'deleted_count': count,
                'retention_days': retention_days,
                'cutoff_date': cutoff_date.isoformat()
            }
        )
        
        return count

class GDPRComplianceLogger:
    """GDPR-specific logging and compliance utilities"""
    
    @staticmethod
    def log_consent(user_id: int, consent_type: str, granted: bool, details: Dict = None):
        """Log user consent events"""
        event_type = AuditEventType.CONSENT_GIVEN if granted else AuditEventType.CONSENT_WITHDRAWN
        
        consent_details = details or {}
        consent_details.update({
            'consent_type': consent_type,
            'granted': granted,
            'consent_timestamp': datetime.utcnow().isoformat()
        })
        
        AuditLogger.log_privacy_event(event_type, user_id, consent_details)
    
    @staticmethod
    def log_data_request(user_id: int, request_type: str, status: str = 'received', details: Dict = None):
        """Log GDPR data requests (access, portability, erasure)"""
        request_details = details or {}
        request_details.update({
            'request_type': request_type,
            'status': status,
            'request_timestamp': datetime.utcnow().isoformat()
        })
        
        AuditLogger.log_privacy_event(AuditEventType.GDPR_REQUEST, user_id, request_details)
    
    @staticmethod
    def log_data_anonymization(user_id: int, data_types: List[str], method: str = 'hash'):
        """Log data anonymization events"""
        AuditLogger.log_privacy_event(
            AuditEventType.DATA_ANONYMIZED,
            user_id,
            {
                'data_types': data_types,
                'anonymization_method': method,
                'anonymized_at': datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def log_data_purge(user_id: int, data_types: List[str], reason: str = 'user_request'):
        """Log data purging events"""
        AuditLogger.log_privacy_event(
            AuditEventType.DATA_PURGED,
            user_id,
            {
                'data_types': data_types,
                'purge_reason': reason,
                'purged_at': datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def generate_compliance_report(user_id: int) -> Dict[str, Any]:
        """Generate GDPR compliance report for a user"""
        # Get all audit logs for the user
        logs = AuditLogger.get_audit_logs(user_id=user_id, limit=1000)
        
        # Categorize events
        consent_events = [log for log in logs if log['event_type'] in [
            AuditEventType.CONSENT_GIVEN, AuditEventType.CONSENT_WITHDRAWN
        ]]
        
        data_access_events = [log for log in logs if log['event_type'].startswith('data_')]
        
        privacy_events = [log for log in logs if log['event_type'] in [
            AuditEventType.GDPR_REQUEST, AuditEventType.DATA_ANONYMIZED, AuditEventType.DATA_PURGED
        ]]
        
        # Generate report
        report = {
            'user_id': user_id,
            'report_generated_at': datetime.utcnow().isoformat(),
            'total_events': len(logs),
            'consent_events': {
                'count': len(consent_events),
                'events': consent_events
            },
            'data_access_events': {
                'count': len(data_access_events),
                'events': data_access_events
            },
            'privacy_events': {
                'count': len(privacy_events),
                'events': privacy_events
            },
            'compliance_status': {
                'has_consent_records': len(consent_events) > 0,
                'has_data_access_logs': len(data_access_events) > 0,
                'last_activity': logs[0]['timestamp'] if logs else None
            }
        }
        
        return report

# Decorator for automatic audit logging
def audit_log(event_type: str, resource_type: str = None):
    """Decorator to automatically log function calls"""
    def decorator(f):
        from functools import wraps
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = datetime.utcnow()
            success = True
            error_message = None
            
            try:
                result = f(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_message = str(e)
                raise
            finally:
                # Log the event
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                AuditLogger.log_event(
                    event_type=event_type,
                    resource_type=resource_type,
                    success=success,
                    error_message=error_message,
                    details={
                        'function_name': f.__name__,
                        'execution_time_seconds': execution_time
                    }
                )
        
        return decorated_function
    return decorator