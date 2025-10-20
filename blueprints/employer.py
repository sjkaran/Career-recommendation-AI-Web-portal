"""
Employer blueprint for job posting and candidate management
"""
from flask import Blueprint

employer_bp = Blueprint('employer', __name__)

@employer_bp.route('/dashboard')
def dashboard():
    """Employer dashboard"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Employer Dashboard - AI Career Platform</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/"><i class="bi bi-mortarboard-fill me-2"></i>AI Career Platform</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/employer/jobs">Job Postings</a>
                    <a class="nav-link" href="/employer/candidates">Candidates</a>
                    <a class="nav-link" href="/auth/logout">Logout</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="row">
                <div class="col-12">
                    <h2><i class="bi bi-building text-primary me-2"></i>Employer Dashboard</h2>
                    <p class="text-muted">Manage your job postings and find the best candidates.</p>
                </div>
            </div>
            
            <div class="row g-4">
                <div class="col-md-6 col-lg-3">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-briefcase text-primary" style="font-size: 3rem;"></i>
                            <h5 class="mt-3">Active Jobs</h5>
                            <h3 class="text-primary">12</h3>
                            <a href="/employer/jobs" class="btn btn-primary btn-sm">Manage Jobs</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6 col-lg-3">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-people text-success" style="font-size: 3rem;"></i>
                            <h5 class="mt-3">Applications</h5>
                            <h3 class="text-success">45</h3>
                            <a href="/employer/applications" class="btn btn-success btn-sm">View Applications</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6 col-lg-3">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-person-check text-warning" style="font-size: 3rem;"></i>
                            <h5 class="mt-3">Shortlisted</h5>
                            <h3 class="text-warning">8</h3>
                            <a href="/employer/shortlisted" class="btn btn-warning btn-sm">Review Candidates</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6 col-lg-3">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-plus-circle text-info" style="font-size: 3rem;"></i>
                            <h5 class="mt-3">Post New Job</h5>
                            <p class="text-muted">Create posting</p>
                            <a href="/employer/post-job" class="btn btn-info btn-sm">Post Job</a>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="bi bi-graph-up me-2"></i>Recent Activity</h5>
                        </div>
                        <div class="card-body">
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>New application for Software Developer position</span>
                                    <small class="text-muted">1 hour ago</small>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Posted Data Analyst job opening</span>
                                    <small class="text-muted">2 days ago</small>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Shortlisted 3 candidates for Frontend Developer</span>
                                    <small class="text-muted">1 week ago</small>
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

@employer_bp.route('/jobs')
def jobs():
    """Job postings management"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Job Postings - AI Career Platform</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/"><i class="bi bi-mortarboard-fill me-2"></i>AI Career Platform</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/employer/dashboard">Dashboard</a>
                    <a class="nav-link" href="/auth/logout">Logout</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <h2><i class="bi bi-briefcase text-primary me-2"></i>Job Postings</h2>
            <div class="card mt-3">
                <div class="card-body">
                    <h5>Active Job Postings</h5>
                    <div class="table-responsive">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Position</th>
                                    <th>Applications</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Software Developer</td>
                                    <td>15</td>
                                    <td><span class="badge bg-success">Active</span></td>
                                    <td><button class="btn btn-sm btn-primary">View</button></td>
                                </tr>
                                <tr>
                                    <td>Data Analyst</td>
                                    <td>8</td>
                                    <td><span class="badge bg-success">Active</span></td>
                                    <td><button class="btn btn-sm btn-primary">View</button></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <a href="/employer/dashboard" class="btn btn-primary">Back to Dashboard</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''