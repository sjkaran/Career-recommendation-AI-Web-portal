"""
Authentication blueprint for user registration, login, and session management
"""
from flask import Blueprint, render_template, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register')
def register():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - AI Career Platform</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h3>Register for AI Career Platform</h3>
                        </div>
                        <div class="card-body">
                            <form>
                                <div class="mb-3">
                                    <label class="form-label">Username</label>
                                    <input type="text" class="form-control">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Email</label>
                                    <input type="email" class="form-control">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Password</label>
                                    <input type="password" class="form-control">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Role</label>
                                    <select class="form-control">
                                        <option>Student</option>
                                        <option>Employer</option>
                                        <option>Placement Officer</option>
                                    </select>
                                </div>
                                <button type="button" class="btn btn-primary" onclick="alert('Registration successful!'); window.location.href='/auth/login'">Register</button>
                                <a href="/" class="btn btn-secondary">Back to Home</a>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@auth_bp.route('/login')
def login():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - AI Career Platform</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h3>Login to AI Career Platform</h3>
                        </div>
                        <div class="card-body">
                            <form id="loginForm">
                                <div class="mb-3">
                                    <label class="form-label">Email</label>
                                    <input type="email" id="email" class="form-control" value="student@demo.com">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Password</label>
                                    <input type="password" id="password" class="form-control" value="demo123">
                                </div>
                                <button type="button" class="btn btn-primary" onclick="handleLogin()">Login</button>
                                <a href="/" class="btn btn-secondary">Back to Home</a>
                            </form>
                            <hr>
                            <h5>Demo Credentials:</h5>
                            <ul>
                                <li><strong>Student:</strong> student@demo.com / demo123 → <a href="/student/dashboard">Student Dashboard</a></li>
                                <li><strong>Employer:</strong> employer@demo.com / demo123 → <a href="/employer/dashboard">Employer Dashboard</a></li>
                                <li><strong>Officer:</strong> officer@demo.com / demo123 → <a href="/analytics/dashboard">Analytics Dashboard</a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        function handleLogin() {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (email === 'student@demo.com' && password === 'demo123') {
                alert('Login successful! Redirecting to Student Dashboard...');
                window.location.href = '/student/dashboard';
            } else if (email === 'employer@demo.com' && password === 'demo123') {
                alert('Login successful! Redirecting to Employer Dashboard...');
                window.location.href = '/employer/dashboard';
            } else if (email === 'officer@demo.com' && password === 'demo123') {
                alert('Login successful! Redirecting to Analytics Dashboard...');
                window.location.href = '/analytics/dashboard';
            } else {
                alert('Invalid credentials! Please use the demo credentials provided.');
            }
        }
        </script>
    </body>
    </html>
    '''

@auth_bp.route('/logout')
def logout():
    return redirect(url_for('index'))