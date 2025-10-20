"""
Student blueprint for profile management and career recommendations
"""
from flask import Blueprint, render_template

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
def dashboard():
    """Student dashboard"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Dashboard - AI Career Platform</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    </head>
    <body class="bg-light">
        <!-- Navigation -->
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/"><i class="bi bi-mortarboard-fill me-2"></i>AI Career Platform</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/student/profile">Profile</a>
                    <a class="nav-link" href="/student/recommendations">Recommendations</a>
                    <a class="nav-link" href="/auth/logout">Logout</a>
                </div>
            </div>
        </nav>
        
        <!-- Dashboard Content -->
        <div class="container mt-4">
            <div class="row">
                <div class="col-12">
                    <h2><i class="bi bi-mortarboard text-primary me-2"></i>Student Dashboard</h2>
                    <p class="text-muted">Welcome back! Here's your career progress overview.</p>
                </div>
            </div>
            
            <div class="row g-4">
                <!-- Profile Completion -->
                <div class="col-md-6 col-lg-3">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-person-circle text-primary" style="font-size: 3rem;"></i>
                            <h5 class="mt-3">Profile</h5>
                            <p class="text-muted">85% Complete</p>
                            <a href="/student/profile" class="btn btn-primary btn-sm">Update Profile</a>
                        </div>
                    </div>
                </div>
                
                <!-- Career Recommendations -->
                <div class="col-md-6 col-lg-3">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-robot text-success" style="font-size: 3rem;"></i>
                            <h5 class="mt-3">AI Recommendations</h5>
                            <p class="text-muted">5 New Suggestions</p>
                            <a href="/student/recommendations" class="btn btn-success btn-sm">View Recommendations</a>
                        </div>
                    </div>
                </div>
                
                <!-- Job Applications -->
                <div class="col-md-6 col-lg-3">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-briefcase text-warning" style="font-size: 3rem;"></i>
                            <h5 class="mt-3">Applications</h5>
                            <p class="text-muted">3 Active</p>
                            <a href="/student/applications" class="btn btn-warning btn-sm">Manage Applications</a>
                        </div>
                    </div>
                </div>
                
                <!-- Skill Assessment -->
                <div class="col-md-6 col-lg-3">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-graph-up text-info" style="font-size: 3rem;"></i>
                            <h5 class="mt-3">Skills</h5>
                            <p class="text-muted">Take Assessment</p>
                            <a href="/student/skills" class="btn btn-info btn-sm">Assess Skills</a>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Recent Activity -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="bi bi-clock-history me-2"></i>Recent Activity</h5>
                        </div>
                        <div class="card-body">
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Applied to Software Developer position at TechCorp</span>
                                    <small class="text-muted">2 hours ago</small>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Completed Python skill assessment</span>
                                    <small class="text-muted">1 day ago</small>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Updated profile information</span>
                                    <small class="text-muted">3 days ago</small>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@student_bp.route('/skills')
def skills_assessment():
    """AI-powered skills assessment page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Skills Assessment - AI Career Platform</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
        <style>
            .skill-card {
                transition: all 0.3s ease;
                cursor: pointer;
            }
            .skill-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }
            .skill-level {
                height: 6px;
                border-radius: 3px;
                background: #e9ecef;
                overflow: hidden;
            }
            .skill-level-fill {
                height: 100%;
                transition: width 0.6s ease;
            }
            .assessment-progress {
                height: 8px;
                border-radius: 4px;
                background: #e9ecef;
            }
        </style>
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/"><i class="bi bi-mortarboard-fill me-2"></i>AI Career Platform</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/student/dashboard">Dashboard</a>
                    <a class="nav-link" href="/student/recommendations">AI Recommendations</a>
                    <a class="nav-link" href="/auth/logout">Logout</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <!-- Header -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="d-flex align-items-center">
                        <i class="bi bi-clipboard-check text-primary me-3" style="font-size: 2.5rem;"></i>
                        <div>
                            <h2 class="mb-1">AI Skills Assessment</h2>
                            <p class="text-muted mb-0">Evaluate your current skills and get personalized improvement suggestions</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Assessment Progress -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card bg-primary text-white">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="mb-0">Assessment Progress</h5>
                                <span class="badge bg-light text-primary">75% Complete</span>
                            </div>
                            <div class="assessment-progress">
                                <div class="bg-warning" style="width: 75%; height: 100%; border-radius: 4px;"></div>
                            </div>
                            <small class="mt-2 d-block">6 of 8 skill categories assessed</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Current Skills Overview -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="bi bi-graph-up me-2"></i>Your Current Skills Profile</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <!-- Programming Languages -->
                                <div class="col-lg-6 mb-4">
                                    <h6 class="text-primary">Programming Languages</h6>
                                    
                                    <div class="mb-3">
                                        <div class="d-flex justify-content-between align-items-center mb-1">
                                            <span class="fw-medium">Python</span>
                                            <span class="badge bg-success">Advanced</span>
                                        </div>
                                        <div class="skill-level">
                                            <div class="skill-level-fill bg-success" style="width: 85%"></div>
                                        </div>
                                        <small class="text-muted">Last assessed: 2 days ago</small>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <div class="d-flex justify-content-between align-items-center mb-1">
                                            <span class="fw-medium">JavaScript</span>
                                            <span class="badge bg-info">Intermediate</span>
                                        </div>
                                        <div class="skill-level">
                                            <div class="skill-level-fill bg-info" style="width: 70%"></div>
                                        </div>
                                        <small class="text-muted">Last assessed: 1 week ago</small>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <div class="d-flex justify-content-between align-items-center mb-1">
                                            <span class="fw-medium">Java</span>
                                            <span class="badge bg-warning">Beginner</span>
                                        </div>
                                        <div class="skill-level">
                                            <div class="skill-level-fill bg-warning" style="width: 45%"></div>
                                        </div>
                                        <small class="text-muted">Last assessed: 3 weeks ago</small>
                                    </div>
                                </div>
                                
                                <!-- Frameworks & Tools -->
                                <div class="col-lg-6 mb-4">
                                    <h6 class="text-primary">Frameworks & Tools</h6>
                                    
                                    <div class="mb-3">
                                        <div class="d-flex justify-content-between align-items-center mb-1">
                                            <span class="fw-medium">React</span>
                                            <span class="badge bg-info">Intermediate</span>
                                        </div>
                                        <div class="skill-level">
                                            <div class="skill-level-fill bg-info" style="width: 75%"></div>
                                        </div>
                                        <small class="text-muted">Last assessed: 5 days ago</small>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <div class="d-flex justify-content-between align-items-center mb-1">
                                            <span class="fw-medium">Node.js</span>
                                            <span class="badge bg-danger">Needs Improvement</span>
                                        </div>
                                        <div class="skill-level">
                                            <div class="skill-level-fill bg-danger" style="width: 25%"></div>
                                        </div>
                                        <small class="text-muted">Not assessed yet</small>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <div class="d-flex justify-content-between align-items-center mb-1">
                                            <span class="fw-medium">Git</span>
                                            <span class="badge bg-info">Intermediate</span>
                                        </div>
                                        <div class="skill-level">
                                            <div class="skill-level-fill bg-info" style="width: 65%"></div>
                                        </div>
                                        <small class="text-muted">Last assessed: 1 week ago</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Available Assessments -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="bi bi-list-check me-2"></i>Available Skill Assessments</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <!-- Technical Skills -->
                                <div class="col-lg-4 col-md-6 mb-3">
                                    <div class="skill-card card h-100 border-primary">
                                        <div class="card-body text-center">
                                            <i class="bi bi-code-slash text-primary" style="font-size: 3rem;"></i>
                                            <h6 class="mt-3">Node.js Assessment</h6>
                                            <p class="text-muted small">Backend development with Node.js</p>
                                            <div class="mb-3">
                                                <span class="badge bg-primary">20 Questions</span>
                                                <span class="badge bg-secondary">30 mins</span>
                                            </div>
                                            <button class="btn btn-primary btn-sm" onclick="startAssessment('nodejs')">
                                                <i class="bi bi-play me-1"></i>Start Assessment
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="col-lg-4 col-md-6 mb-3">
                                    <div class="skill-card card h-100 border-success">
                                        <div class="card-body text-center">
                                            <i class="bi bi-database text-success" style="font-size: 3rem;"></i>
                                            <h6 class="mt-3">Database Skills</h6>
                                            <p class="text-muted small">SQL, MongoDB, Database Design</p>
                                            <div class="mb-3">
                                                <span class="badge bg-success">25 Questions</span>
                                                <span class="badge bg-secondary">35 mins</span>
                                            </div>
                                            <button class="btn btn-success btn-sm" onclick="startAssessment('database')">
                                                <i class="bi bi-play me-1"></i>Start Assessment
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="col-lg-4 col-md-6 mb-3">
                                    <div class="skill-card card h-100 border-info">
                                        <div class="card-body text-center">
                                            <i class="bi bi-cloud text-info" style="font-size: 3rem;"></i>
                                            <h6 class="mt-3">Cloud Computing</h6>
                                            <p class="text-muted small">AWS, Docker, DevOps basics</p>
                                            <div class="mb-3">
                                                <span class="badge bg-info">18 Questions</span>
                                                <span class="badge bg-secondary">25 mins</span>
                                            </div>
                                            <button class="btn btn-info btn-sm" onclick="startAssessment('cloud')">
                                                <i class="bi bi-play me-1"></i>Start Assessment
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="col-lg-4 col-md-6 mb-3">
                                    <div class="skill-card card h-100 border-warning">
                                        <div class="card-body text-center">
                                            <i class="bi bi-robot text-warning" style="font-size: 3rem;"></i>
                                            <h6 class="mt-3">Machine Learning</h6>
                                            <p class="text-muted small">ML algorithms, Data Science</p>
                                            <div class="mb-3">
                                                <span class="badge bg-warning">30 Questions</span>
                                                <span class="badge bg-secondary">45 mins</span>
                                            </div>
                                            <button class="btn btn-warning btn-sm" onclick="startAssessment('ml')">
                                                <i class="bi bi-play me-1"></i>Retake Assessment
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="col-lg-4 col-md-6 mb-3">
                                    <div class="skill-card card h-100 border-secondary">
                                        <div class="card-body text-center">
                                            <i class="bi bi-people text-secondary" style="font-size: 3rem;"></i>
                                            <h6 class="mt-3">Soft Skills</h6>
                                            <p class="text-muted small">Communication, Leadership, Teamwork</p>
                                            <div class="mb-3">
                                                <span class="badge bg-secondary">15 Questions</span>
                                                <span class="badge bg-secondary">20 mins</span>
                                            </div>
                                            <button class="btn btn-secondary btn-sm" onclick="startAssessment('soft')">
                                                <i class="bi bi-play me-1"></i>Start Assessment
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="col-lg-4 col-md-6 mb-3">
                                    <div class="skill-card card h-100 border-dark">
                                        <div class="card-body text-center">
                                            <i class="bi bi-shield-check text-dark" style="font-size: 3rem;"></i>
                                            <h6 class="mt-3">Cybersecurity</h6>
                                            <p class="text-muted small">Security fundamentals, Best practices</p>
                                            <div class="mb-3">
                                                <span class="badge bg-dark">22 Questions</span>
                                                <span class="badge bg-secondary">30 mins</span>
                                            </div>
                                            <button class="btn btn-dark btn-sm" onclick="startAssessment('security')">
                                                <i class="bi bi-play me-1"></i>Start Assessment
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- AI Insights -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card bg-light">
                        <div class="card-body">
                            <div class="row align-items-center">
                                <div class="col-md-8">
                                    <h5><i class="bi bi-lightbulb text-warning me-2"></i>AI Insights</h5>
                                    <p class="mb-2">Based on your current skill profile, focusing on <strong>Node.js</strong> and <strong>Database skills</strong> will significantly boost your full-stack development capabilities.</p>
                                    <small class="text-muted">Completing these assessments will unlock personalized learning paths and job recommendations.</small>
                                </div>
                                <div class="col-md-4 text-center">
                                    <button class="btn btn-warning" onclick="alert('AI coaching feature coming soon!')">
                                        <i class="bi bi-robot me-2"></i>Get AI Coaching
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="row">
                <div class="col-12 text-center">
                    <a href="/student/dashboard" class="btn btn-primary me-3">
                        <i class="bi bi-arrow-left me-2"></i>Back to Dashboard
                    </a>
                    <a href="/student/recommendations" class="btn btn-success me-3">
                        <i class="bi bi-robot me-2"></i>View AI Recommendations
                    </a>
                    <button class="btn btn-info" onclick="alert('Skill report feature coming soon!')">
                        <i class="bi bi-file-earmark-pdf me-2"></i>Download Skill Report
                    </button>
                </div>
            </div>
        </div>
        
        <script>
        function startAssessment(skillType) {
            const skillNames = {
                'nodejs': 'Node.js',
                'database': 'Database Skills',
                'cloud': 'Cloud Computing',
                'ml': 'Machine Learning',
                'soft': 'Soft Skills',
                'security': 'Cybersecurity'
            };
            
            alert(`Starting ${skillNames[skillType]} assessment...\\n\\nThis is a demo version. In the full application, this would launch an interactive assessment with real-time AI evaluation.`);
        }
        
        // Animate skill bars on page load
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(() => {
                const skillBars = document.querySelectorAll('.skill-level-fill');
                skillBars.forEach(bar => {
                    const width = bar.style.width;
                    bar.style.width = '0%';
                    setTimeout(() => {
                        bar.style.width = width;
                    }, 100);
                });
            }, 500);
        });
        </script>
    </body>
    </html>
    '''

@student_bp.route('/applications')
def applications():
    """Student job applications page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Applications - AI Career Platform</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/"><i class="bi bi-mortarboard-fill me-2"></i>AI Career Platform</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/student/dashboard">Dashboard</a>
                    <a class="nav-link" href="/auth/logout">Logout</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <h2><i class="bi bi-briefcase text-primary me-2"></i>My Job Applications</h2>
            
            <div class="card mt-3">
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Position</th>
                                    <th>Company</th>
                                    <th>Applied Date</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Software Developer</td>
                                    <td>TechCorp</td>
                                    <td>2024-01-15</td>
                                    <td><span class="badge bg-warning">Under Review</span></td>
                                    <td><button class="btn btn-sm btn-primary">View Details</button></td>
                                </tr>
                                <tr>
                                    <td>Frontend Developer</td>
                                    <td>WebSoft</td>
                                    <td>2024-01-12</td>
                                    <td><span class="badge bg-success">Interview Scheduled</span></td>
                                    <td><button class="btn btn-sm btn-primary">View Details</button></td>
                                </tr>
                                <tr>
                                    <td>Data Analyst</td>
                                    <td>DataCorp</td>
                                    <td>2024-01-10</td>
                                    <td><span class="badge bg-info">Applied</span></td>
                                    <td><button class="btn btn-sm btn-primary">View Details</button></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <a href="/student/dashboard" class="btn btn-primary">Back to Dashboard</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@student_bp.route('/profile')
def profile():
    """Student profile page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Profile - AI Career Platform</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/"><i class="bi bi-mortarboard-fill me-2"></i>AI Career Platform</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/student/dashboard">Dashboard</a>
                    <a class="nav-link" href="/auth/logout">Logout</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <h2><i class="bi bi-person-circle text-primary me-2"></i>Student Profile</h2>
            <div class="card mt-3">
                <div class="card-body">
                    <h5>Demo Student Profile</h5>
                    <p><strong>Name:</strong> John Doe</p>
                    <p><strong>Email:</strong> student@demo.com</p>
                    <p><strong>Branch:</strong> Computer Science Engineering</p>
                    <p><strong>Year:</strong> Final Year</p>
                    <p><strong>Skills:</strong> Python, JavaScript, React, Machine Learning</p>
                    <a href="/student/dashboard" class="btn btn-primary">Back to Dashboard</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@student_bp.route('/recommendations')
def recommendations():
    """AI-powered career and skill recommendations"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Recommendations - AI Career Platform</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
        <style>
            .ai-badge {
                background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 15px;
                font-size: 0.75rem;
                font-weight: 600;
            }
            .skill-progress {
                height: 8px;
                border-radius: 4px;
                background: #e9ecef;
                overflow: hidden;
            }
            .skill-progress-bar {
                height: 100%;
                transition: width 0.6s ease;
            }
            .recommendation-card {
                border-left: 4px solid #28a745;
                transition: transform 0.2s ease;
            }
            .recommendation-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            .priority-high { border-left-color: #dc3545; }
            .priority-medium { border-left-color: #ffc107; }
            .priority-low { border-left-color: #28a745; }
        </style>
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/"><i class="bi bi-mortarboard-fill me-2"></i>AI Career Platform</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/student/dashboard">Dashboard</a>
                    <a class="nav-link" href="/student/skills">Skills Assessment</a>
                    <a class="nav-link" href="/auth/logout">Logout</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <!-- Header -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="d-flex align-items-center mb-3">
                        <i class="bi bi-robot text-success me-3" style="font-size: 2.5rem;"></i>
                        <div>
                            <h2 class="mb-1">AI Career & Skill Recommendations</h2>
                            <p class="text-muted mb-0">Personalized insights based on your profile and market trends</p>
                        </div>
                        <span class="ai-badge ms-auto">AI POWERED</span>
                    </div>
                </div>
            </div>
            
            <!-- AI Analysis Summary -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card" style="background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%); border: none;">
                        <div class="card-body text-white">
                            <div class="row align-items-center">
                                <div class="col-md-8">
                                    <h5 class="text-white mb-3"><i class="bi bi-lightbulb me-2 text-warning"></i>AI Analysis Summary</h5>
                                    <p class="mb-2 text-white" style="font-size: 1.1rem;">Based on your Computer Science background and current skills (Python, JavaScript, React, ML), our AI recommends focusing on <strong class="text-warning">Full Stack Development</strong> and <strong class="text-warning">Data Science</strong> paths.</p>
                                    <small class="text-light"><i class="bi bi-clock me-1 text-warning"></i>Analysis updated 2 hours ago</small>
                                </div>
                                <div class="col-md-4 text-center">
                                    <div class="display-4 fw-bold text-warning mb-2">92%</div>
                                    <div class="text-white fw-medium">Career Match Score</div>
                                    <div class="mt-2">
                                        <span class="badge bg-warning text-dark px-3 py-2">Excellent Match</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Skills to Focus On -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h5 class="mb-0"><i class="bi bi-target me-2"></i>Priority Skills to Focus On</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <!-- High Priority Skills -->
                                <div class="col-lg-4 mb-4">
                                    <h6 class="text-danger"><i class="bi bi-exclamation-triangle me-2"></i>High Priority</h6>
                                    
                                    <div class="recommendation-card card mb-3 priority-high">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between align-items-center mb-2">
                                                <h6 class="mb-0">Node.js</h6>
                                                <span class="badge bg-danger">Critical</span>
                                            </div>
                                            <p class="text-muted small mb-2">Essential for full-stack development. 89% of job postings require this.</p>
                                            <div class="skill-progress mb-2">
                                                <div class="skill-progress-bar bg-danger" style="width: 15%"></div>
                                            </div>
                                            <div class="d-flex justify-content-between small">
                                                <span>Current: 15%</span>
                                                <span>Target: 80%</span>
                                            </div>
                                            <div class="mt-2">
                                                <button class="btn btn-outline-primary btn-sm me-2">Learn Path</button>
                                                <button class="btn btn-outline-secondary btn-sm">Resources</button>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="recommendation-card card mb-3 priority-high">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between align-items-center mb-2">
                                                <h6 class="mb-0">Docker</h6>
                                                <span class="badge bg-danger">Critical</span>
                                            </div>
                                            <p class="text-muted small mb-2">DevOps skill in high demand. 76% salary increase potential.</p>
                                            <div class="skill-progress mb-2">
                                                <div class="skill-progress-bar bg-danger" style="width: 10%"></div>
                                            </div>
                                            <div class="d-flex justify-content-between small">
                                                <span>Current: 10%</span>
                                                <span>Target: 75%</span>
                                            </div>
                                            <div class="mt-2">
                                                <button class="btn btn-outline-primary btn-sm me-2">Learn Path</button>
                                                <button class="btn btn-outline-secondary btn-sm">Resources</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Medium Priority Skills -->
                                <div class="col-lg-4 mb-4">
                                    <h6 class="text-warning"><i class="bi bi-dash-circle me-2"></i>Medium Priority</h6>
                                    
                                    <div class="recommendation-card card mb-3 priority-medium">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between align-items-center mb-2">
                                                <h6 class="mb-0">AWS Cloud</h6>
                                                <span class="badge bg-warning">Important</span>
                                            </div>
                                            <p class="text-muted small mb-2">Cloud skills are increasingly valuable. 65% of companies use AWS.</p>
                                            <div class="skill-progress mb-2">
                                                <div class="skill-progress-bar bg-warning" style="width: 25%"></div>
                                            </div>
                                            <div class="d-flex justify-content-between small">
                                                <span>Current: 25%</span>
                                                <span>Target: 70%</span>
                                            </div>
                                            <div class="mt-2">
                                                <button class="btn btn-outline-primary btn-sm me-2">Learn Path</button>
                                                <button class="btn btn-outline-secondary btn-sm">Resources</button>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="recommendation-card card mb-3 priority-medium">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between align-items-center mb-2">
                                                <h6 class="mb-0">TypeScript</h6>
                                                <span class="badge bg-warning">Important</span>
                                            </div>
                                            <p class="text-muted small mb-2">Enhances JavaScript development. Growing demand in React projects.</p>
                                            <div class="skill-progress mb-2">
                                                <div class="skill-progress-bar bg-warning" style="width: 40%"></div>
                                            </div>
                                            <div class="d-flex justify-content-between small">
                                                <span>Current: 40%</span>
                                                <span>Target: 85%</span>
                                            </div>
                                            <div class="mt-2">
                                                <button class="btn btn-outline-primary btn-sm me-2">Learn Path</button>
                                                <button class="btn btn-outline-secondary btn-sm">Resources</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Enhancement Skills -->
                                <div class="col-lg-4 mb-4">
                                    <h6 class="text-success"><i class="bi bi-check-circle me-2"></i>Enhancement Skills</h6>
                                    
                                    <div class="recommendation-card card mb-3 priority-low">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between align-items-center mb-2">
                                                <h6 class="mb-0">GraphQL</h6>
                                                <span class="badge bg-success">Nice to Have</span>
                                            </div>
                                            <p class="text-muted small mb-2">Modern API technology. Complements your React skills well.</p>
                                            <div class="skill-progress mb-2">
                                                <div class="skill-progress-bar bg-success" style="width: 20%"></div>
                                            </div>
                                            <div class="d-flex justify-content-between small">
                                                <span>Current: 20%</span>
                                                <span>Target: 60%</span>
                                            </div>
                                            <div class="mt-2">
                                                <button class="btn btn-outline-primary btn-sm me-2">Learn Path</button>
                                                <button class="btn btn-outline-secondary btn-sm">Resources</button>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="recommendation-card card mb-3 priority-low">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between align-items-center mb-2">
                                                <h6 class="mb-0">TensorFlow</h6>
                                                <span class="badge bg-success">Nice to Have</span>
                                            </div>
                                            <p class="text-muted small mb-2">Strengthen your ML foundation for data science roles.</p>
                                            <div class="skill-progress mb-2">
                                                <div class="skill-progress-bar bg-success" style="width: 35%"></div>
                                            </div>
                                            <div class="d-flex justify-content-between small">
                                                <span>Current: 35%</span>
                                                <span>Target: 70%</span>
                                            </div>
                                            <div class="mt-2">
                                                <button class="btn btn-outline-primary btn-sm me-2">Learn Path</button>
                                                <button class="btn btn-outline-secondary btn-sm">Resources</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Career Path Recommendations -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <h5 class="mb-0"><i class="bi bi-compass me-2"></i>Recommended Career Paths</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-lg-6 mb-3">
                                    <div class="card h-100 border-success">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between align-items-center mb-3">
                                                <h5 class="text-success mb-0">Full Stack Developer</h5>
                                                <span class="badge bg-success">95% Match</span>
                                            </div>
                                            <p class="text-muted">Perfect fit for your JavaScript and React skills. High demand in the market.</p>
                                            
                                            <h6 class="mt-3">Skills Needed:</h6>
                                            <div class="d-flex flex-wrap gap-1 mb-3">
                                                <span class="badge bg-success">React ✓</span>
                                                <span class="badge bg-success">JavaScript ✓</span>
                                                <span class="badge bg-danger">Node.js</span>
                                                <span class="badge bg-warning">MongoDB</span>
                                                <span class="badge bg-warning">Express.js</span>
                                            </div>
                                            
                                            <div class="row text-center">
                                                <div class="col-4">
                                                    <div class="fw-bold text-success">₹8.5L</div>
                                                    <small class="text-muted">Avg Salary</small>
                                                </div>
                                                <div class="col-4">
                                                    <div class="fw-bold text-primary">1,250</div>
                                                    <small class="text-muted">Open Jobs</small>
                                                </div>
                                                <div class="col-4">
                                                    <div class="fw-bold text-info">6 months</div>
                                                    <small class="text-muted">Learning Time</small>
                                                </div>
                                            </div>
                                            
                                            <div class="mt-3">
                                                <button class="btn btn-success btn-sm me-2">Start Learning Path</button>
                                                <button class="btn btn-outline-primary btn-sm">View Jobs</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="col-lg-6 mb-3">
                                    <div class="card h-100 border-info">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between align-items-center mb-3">
                                                <h5 class="text-info mb-0">Data Scientist</h5>
                                                <span class="badge bg-info">88% Match</span>
                                            </div>
                                            <p class="text-muted">Your ML background is valuable. Python skills give you an advantage.</p>
                                            
                                            <h6 class="mt-3">Skills Needed:</h6>
                                            <div class="d-flex flex-wrap gap-1 mb-3">
                                                <span class="badge bg-success">Python ✓</span>
                                                <span class="badge bg-success">Machine Learning ✓</span>
                                                <span class="badge bg-warning">Pandas</span>
                                                <span class="badge bg-warning">SQL</span>
                                                <span class="badge bg-danger">Tableau</span>
                                            </div>
                                            
                                            <div class="row text-center">
                                                <div class="col-4">
                                                    <div class="fw-bold text-success">₹12L</div>
                                                    <small class="text-muted">Avg Salary</small>
                                                </div>
                                                <div class="col-4">
                                                    <div class="fw-bold text-primary">890</div>
                                                    <small class="text-muted">Open Jobs</small>
                                                </div>
                                                <div class="col-4">
                                                    <div class="fw-bold text-info">8 months</div>
                                                    <small class="text-muted">Learning Time</small>
                                                </div>
                                            </div>
                                            
                                            <div class="mt-3">
                                                <button class="btn btn-info btn-sm me-2">Start Learning Path</button>
                                                <button class="btn btn-outline-primary btn-sm">View Jobs</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Learning Resources -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="bi bi-book me-2"></i>Recommended Learning Resources</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-4 mb-3">
                                    <div class="card bg-light">
                                        <div class="card-body text-center">
                                            <i class="bi bi-play-circle text-primary" style="font-size: 2rem;"></i>
                                            <h6 class="mt-2">Video Courses</h6>
                                            <p class="text-muted small">Interactive learning paths</p>
                                            <button class="btn btn-outline-primary btn-sm">Browse Courses</button>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <div class="card bg-light">
                                        <div class="card-body text-center">
                                            <i class="bi bi-code-slash text-success" style="font-size: 2rem;"></i>
                                            <h6 class="mt-2">Practice Projects</h6>
                                            <p class="text-muted small">Hands-on coding challenges</p>
                                            <button class="btn btn-outline-success btn-sm">Start Coding</button>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <div class="card bg-light">
                                        <div class="card-body text-center">
                                            <i class="bi bi-award text-warning" style="font-size: 2rem;"></i>
                                            <h6 class="mt-2">Certifications</h6>
                                            <p class="text-muted small">Industry-recognized credentials</p>
                                            <button class="btn btn-outline-warning btn-sm">Get Certified</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="row">
                <div class="col-12 text-center">
                    <a href="/student/dashboard" class="btn btn-primary me-3">
                        <i class="bi bi-arrow-left me-2"></i>Back to Dashboard
                    </a>
                    <button class="btn btn-success me-3" onclick="alert('Skill assessment feature coming soon!')">
                        <i class="bi bi-clipboard-check me-2"></i>Take Skill Assessment
                    </button>
                    <button class="btn btn-info" onclick="alert('Learning plan feature coming soon!')">
                        <i class="bi bi-calendar-plus me-2"></i>Create Learning Plan
                    </button>
                </div>
            </div>
        </div>
        
        <script>
        // Animate progress bars on page load
        document.addEventListener('DOMContentLoaded', function() {
            const progressBars = document.querySelectorAll('.skill-progress-bar');
            progressBars.forEach(bar => {
                const width = bar.style.width;
                bar.style.width = '0%';
                setTimeout(() => {
                    bar.style.width = width;
                }, 500);
            });
        });
        </script>
    </body>
    </html>
    '''