"""
Analytics blueprint for placement officers and dashboard data
"""
from flask import Blueprint, render_template, jsonify

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard')
def dashboard():
    """Analytics dashboard"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Analytics Dashboard - AI Career Platform</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/"><i class="bi bi-mortarboard-fill me-2"></i>AI Career Platform</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/analytics/reports">Reports</a>
                    <a class="nav-link" href="/analytics/students">Students</a>
                    <a class="nav-link" href="/auth/logout">Logout</a>
                </div>
            </div>
        </nav>
        
        <div class="container-fluid mt-4">
            <div class="row">
                <div class="col-12">
                    <h2><i class="bi bi-graph-up text-primary me-2"></i>Analytics Dashboard</h2>
                    <p class="text-muted">Comprehensive placement and career analytics for BPUT</p>
                </div>
            </div>
            
            <!-- Key Metrics -->
            <div class="row g-4 mb-4">
                <div class="col-lg-3 col-md-6">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-briefcase text-success" style="font-size: 3rem;"></i>
                            <h3 class="mt-3 text-success">450</h3>
                            <p class="text-muted">Total Placements</p>
                            <small class="text-success">+12% from last period</small>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-currency-rupee text-primary" style="font-size: 3rem;"></i>
                            <h3 class="mt-3 text-primary">₹6.5L</h3>
                            <p class="text-muted">Average Salary</p>
                            <small class="text-success">+8% from last period</small>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-graph-up text-info" style="font-size: 3rem;"></i>
                            <h3 class="mt-3 text-info">87.5%</h3>
                            <p class="text-muted">Placement Rate</p>
                            <small class="text-success">+5% from last period</small>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-building text-warning" style="font-size: 3rem;"></i>
                            <h3 class="mt-3 text-warning">85</h3>
                            <p class="text-muted">Partner Companies</p>
                            <small class="text-success">+3 new this month</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Charts Row -->
            <div class="row g-4 mb-4">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-header">
                            <h5>Placement Trends</h5>
                        </div>
                        <div class="card-body">
                            <canvas id="placementChart" height="100"></canvas>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-4">
                    <div class="card">
                        <div class="card-header">
                            <h5>Branch Performance</h5>
                        </div>
                        <div class="card-body">
                            <canvas id="branchChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Additional Analytics -->
            <div class="row g-4">
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Top Skills in Demand</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <div class="d-flex justify-content-between">
                                    <span>Python</span>
                                    <span>95%</span>
                                </div>
                                <div class="progress">
                                    <div class="progress-bar bg-success" style="width: 95%"></div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <div class="d-flex justify-content-between">
                                    <span>JavaScript</span>
                                    <span>88%</span>
                                </div>
                                <div class="progress">
                                    <div class="progress-bar bg-info" style="width: 88%"></div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <div class="d-flex justify-content-between">
                                    <span>React</span>
                                    <span>82%</span>
                                </div>
                                <div class="progress">
                                    <div class="progress-bar bg-warning" style="width: 82%"></div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <div class="d-flex justify-content-between">
                                    <span>Machine Learning</span>
                                    <span>75%</span>
                                </div>
                                <div class="progress">
                                    <div class="progress-bar bg-primary" style="width: 75%"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Top Recruiting Companies</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <div class="d-flex align-items-center">
                                    <i class="bi bi-building text-primary me-3" style="font-size: 1.5rem;"></i>
                                    <div>
                                        <div class="fw-bold">TCS</div>
                                        <small class="text-muted">Technology</small>
                                    </div>
                                </div>
                                <div class="text-end">
                                    <div class="fw-bold">45</div>
                                    <small class="text-muted">hires</small>
                                </div>
                            </div>
                            
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <div class="d-flex align-items-center">
                                    <i class="bi bi-building text-success me-3" style="font-size: 1.5rem;"></i>
                                    <div>
                                        <div class="fw-bold">Infosys</div>
                                        <small class="text-muted">Technology</small>
                                    </div>
                                </div>
                                <div class="text-end">
                                    <div class="fw-bold">38</div>
                                    <small class="text-muted">hires</small>
                                </div>
                            </div>
                            
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <div class="d-flex align-items-center">
                                    <i class="bi bi-building text-warning me-3" style="font-size: 1.5rem;"></i>
                                    <div>
                                        <div class="fw-bold">Wipro</div>
                                        <small class="text-muted">Technology</small>
                                    </div>
                                </div>
                                <div class="text-end">
                                    <div class="fw-bold">32</div>
                                    <small class="text-muted">hires</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        // Placement Trends Chart
        const placementCtx = document.getElementById('placementChart').getContext('2d');
        new Chart(placementCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Placements',
                    data: [65, 78, 90, 81, 95, 105],
                    borderColor: 'rgb(37, 99, 235)',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        // Branch Performance Chart
        const branchCtx = document.getElementById('branchChart').getContext('2d');
        new Chart(branchCtx, {
            type: 'doughnut',
            data: {
                labels: ['CSE', 'IT', 'ECE', 'EE', 'ME'],
                datasets: [{
                    data: [35, 25, 20, 12, 8],
                    backgroundColor: [
                        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        </script>
    </body>
    </html>
    '''

# Additional routes for the analytics dashboard
@analytics_bp.route('/api/stats')
def api_stats():
    """API endpoint for dashboard stats"""
    return jsonify({
        'total_students': 1200,
        'total_placements': 450,
        'placement_rate': 87.5,
        'active_jobs': 125,
        'top_skills': ['Python', 'JavaScript', 'React', 'Machine Learning'],
        'top_companies': ['TechCorp', 'DataSoft', 'InnovateLabs']
    })

@analytics_bp.route('/reports')
def reports():
    """Reports page"""
    return jsonify({'message': 'Reports page - coming soon'})

@analytics_bp.route('/students')
def students():
    """Students analytics page"""
    return jsonify({'message': 'Students analytics - coming soon'})

@analytics_bp.route('/placements')
def placements():
    """Placements page"""
    return jsonify({'message': 'Placements page - coming soon'})

@analytics_bp.route('/settings')
def settings():
    """Settings page"""
    return jsonify({'message': 'Settings page - coming soon'})