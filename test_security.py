#!/usr/bin/env python3
"""
Security testing script for AI Career Platform
Tests input validation, XSS protection, SQL injection prevention, and file upload security
"""
import requests
import json
import tempfile
import os
from typing import Dict, List

class SecurityTester:
    """Security testing utility"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {test_name}: {details}")
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'details': details
        })
    
    def test_xss_protection(self):
        """Test XSS protection in input fields"""
        print("\n=== Testing XSS Protection ===")
        
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "';alert('xss');//",
            "<iframe src=javascript:alert('xss')></iframe>"
        ]
        
        for payload in xss_payloads:
            try:
                # Test registration endpoint
                response = self.session.post(f"{self.base_url}/auth/register", json={
                    'email': f'test{payload}@example.com',
                    'password': 'TestPass123!',
                    'role': 'student',
                    'first_name': payload,
                    'consent_profile': 'true'
                })
                
                # Check if XSS payload was sanitized
                if response.status_code == 400:
                    self.log_test(f"XSS Protection - {payload[:20]}...", True, "Payload rejected")
                elif response.status_code == 201:
                    # Check if payload was sanitized in response
                    response_text = response.text
                    if payload in response_text:
                        self.log_test(f"XSS Protection - {payload[:20]}...", False, "Payload not sanitized")
                    else:
                        self.log_test(f"XSS Protection - {payload[:20]}...", True, "Payload sanitized")
                else:
                    self.log_test(f"XSS Protection - {payload[:20]}...", True, f"Unexpected response: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"XSS Protection - {payload[:20]}...", False, f"Error: {str(e)}")
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        print("\n=== Testing SQL Injection Protection ===")
        
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "' OR 1=1 --",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ]
        
        for payload in sql_payloads:
            try:
                # Test login endpoint
                response = self.session.post(f"{self.base_url}/auth/login", json={
                    'email': payload,
                    'password': 'password'
                })
                
                # SQL injection should be blocked
                if response.status_code == 400:
                    self.log_test(f"SQL Injection Protection - {payload[:20]}...", True, "Payload rejected")
                elif response.status_code == 401:
                    self.log_test(f"SQL Injection Protection - {payload[:20]}...", True, "Invalid credentials (expected)")
                else:
                    self.log_test(f"SQL Injection Protection - {payload[:20]}...", False, f"Unexpected response: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"SQL Injection Protection - {payload[:20]}...", False, f"Error: {str(e)}")
    
    def test_input_validation(self):
        """Test input validation"""
        print("\n=== Testing Input Validation ===")
        
        # Test email validation
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            "a" * 300 + "@example.com"  # Too long
        ]
        
        for email in invalid_emails:
            try:
                response = self.session.post(f"{self.base_url}/auth/register", json={
                    'email': email,
                    'password': 'TestPass123!',
                    'role': 'student',
                    'consent_profile': 'true'
                })
                
                if response.status_code == 400:
                    self.log_test(f"Email Validation - {email[:20]}...", True, "Invalid email rejected")
                else:
                    self.log_test(f"Email Validation - {email[:20]}...", False, f"Invalid email accepted: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Email Validation - {email[:20]}...", False, f"Error: {str(e)}")
        
        # Test password validation
        weak_passwords = [
            "123",
            "password",
            "12345678",
            "PASSWORD",
            "Pass123"  # Missing special character
        ]
        
        for password in weak_passwords:
            try:
                response = self.session.post(f"{self.base_url}/auth/register", json={
                    'email': 'test@example.com',
                    'password': password,
                    'role': 'student',
                    'consent_profile': 'true'
                })
                
                if response.status_code == 400:
                    self.log_test(f"Password Validation - {password}", True, "Weak password rejected")
                else:
                    self.log_test(f"Password Validation - {password}", False, f"Weak password accepted: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Password Validation - {password}", False, f"Error: {str(e)}")
    
    def test_file_upload_security(self):
        """Test file upload security"""
        print("\n=== Testing File Upload Security ===")
        
        # Test dangerous file extensions
        dangerous_files = [
            ('malicious.exe', b'MZ\x90\x00', 'application/x-executable'),
            ('script.js', b'alert("xss");', 'application/javascript'),
            ('shell.php', b'<?php system($_GET["cmd"]); ?>', 'application/x-php'),
            ('virus.bat', b'@echo off\ndel /f /q *.*', 'application/x-msdos-program')
        ]
        
        for filename, content, content_type in dangerous_files:
            try:
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
                    tmp_file.write(content)
                    tmp_file_path = tmp_file.name
                
                # Test file upload (this would need an actual file upload endpoint)
                # For now, we'll test the validation function directly
                from utils.validators import validate_file_upload
                from werkzeug.datastructures import FileStorage
                
                with open(tmp_file_path, 'rb') as f:
                    file_storage = FileStorage(
                        stream=f,
                        filename=filename,
                        content_type=content_type
                    )
                    
                    result = validate_file_upload(file_storage, 'document')
                    
                    if not result['valid']:
                        self.log_test(f"File Upload Security - {filename}", True, "Dangerous file rejected")
                    else:
                        self.log_test(f"File Upload Security - {filename}", False, "Dangerous file accepted")
                
                # Clean up
                os.unlink(tmp_file_path)
                
            except Exception as e:
                self.log_test(f"File Upload Security - {filename}", False, f"Error: {str(e)}")
    
    def test_rate_limiting(self):
        """Test rate limiting"""
        print("\n=== Testing Rate Limiting ===")
        
        try:
            # Make multiple rapid requests to test rate limiting
            responses = []
            for i in range(15):  # Exceed the typical rate limit
                response = self.session.post(f"{self.base_url}/auth/login", json={
                    'email': 'test@example.com',
                    'password': 'wrongpassword'
                })
                responses.append(response.status_code)
            
            # Check if any requests were rate limited (429 status)
            rate_limited = any(status == 429 for status in responses)
            
            if rate_limited:
                self.log_test("Rate Limiting", True, "Rate limiting active")
            else:
                self.log_test("Rate Limiting", False, "No rate limiting detected")
                
        except Exception as e:
            self.log_test("Rate Limiting", False, f"Error: {str(e)}")
    
    def test_security_headers(self):
        """Test security headers"""
        print("\n=== Testing Security Headers ===")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            
            expected_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection',
                'Content-Security-Policy'
            ]
            
            for header in expected_headers:
                if header in response.headers:
                    self.log_test(f"Security Header - {header}", True, f"Present: {response.headers[header]}")
                else:
                    self.log_test(f"Security Header - {header}", False, "Missing")
                    
        except Exception as e:
            self.log_test("Security Headers", False, f"Error: {str(e)}")
    
    def test_gdpr_compliance(self):
        """Test GDPR compliance endpoints"""
        print("\n=== Testing GDPR Compliance ===")
        
        try:
            # Test consent endpoint without authentication
            response = self.session.get(f"{self.base_url}/auth/privacy/consent")
            
            if response.status_code == 401:
                self.log_test("GDPR Consent Endpoint", True, "Requires authentication")
            else:
                self.log_test("GDPR Consent Endpoint", False, f"No authentication required: {response.status_code}")
            
            # Test data request endpoint
            response = self.session.post(f"{self.base_url}/auth/privacy/data-request", json={
                'request_type': 'access'
            })
            
            if response.status_code == 401:
                self.log_test("GDPR Data Request Endpoint", True, "Requires authentication")
            else:
                self.log_test("GDPR Data Request Endpoint", False, f"No authentication required: {response.status_code}")
                
        except Exception as e:
            self.log_test("GDPR Compliance", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all security tests"""
        print("Starting Security Tests for AI Career Platform")
        print("=" * 50)
        
        self.test_input_validation()
        self.test_xss_protection()
        self.test_sql_injection_protection()
        self.test_file_upload_security()
        self.test_rate_limiting()
        self.test_security_headers()
        self.test_gdpr_compliance()
        
        # Summary
        print("\n" + "=" * 50)
        print("SECURITY TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['test']}: {result['details']}")
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    tester = SecurityTester(base_url)
    passed, failed = tester.run_all_tests()
    
    # Exit with error code if tests failed
    sys.exit(1 if failed > 0 else 0)