#!/usr/bin/env python3
"""
Minimal test application to test report generation functionality
"""
import os
import sys
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from datetime import datetime

# Simple Flask app for testing
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'
CORS(app)

# Mock data for testing
MOCK_PLACEMENT_DATA = [
    {
        'id': 1,
        'student_id': 1,
        'company_name': 'TechCorp',
        'job_category': 'Technology',
        'salary': 500000,
        'student_branch': 'Computer Science Engineering',
        'placement_date': '2024-01-15',
        'feedback_score': 8.5
    },
    {
        'id': 2,
        'student_id': 2,
        'company_name': 'DataSoft',
        'job_category': 'Technology',
        'salary': 450000,
        'student_branch': 'Information Technology',
        'placement_date': '2024-02-10',
        'feedback_score': 9.0
    },
    {
        'id': 3,
        'student_id': 3,
        'company_name': 'FinanceHub',
        'job_category': 'Finance',
        'salary': 600000,
        'student_branch': 'Computer Science Engineering',
        'placement_date': '2024-03-05',
        'feedback_score': 8.8
    }
]

@app.route('/')
def index():
    return '''
    <h1>AI Career Platform - Test Mode</h1>
    <p>Testing report generation functionality</p>
    <ul>
        <li><a href="/test-pdf">Test PDF Report Generation</a></li>
        <li><a href="/test-csv">Test CSV Report Generation</a></li>
        <li><a href="/analytics/reports/view">View Reports Interface</a></li>
        <li><a href="/health">Health Check</a></li>
    </ul>
    '''

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'AI Career Platform Test App is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test-pdf')
def test_pdf():
    try:
        from utils.report_generator import ReportGenerator
        
        # Generate test report data
        report_data = {
            'report_type': 'placement_summary',
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_placements': len(MOCK_PLACEMENT_DATA),
                'branches_covered': 2,
                'industries_covered': 2,
                'avg_salary': sum(p['salary'] for p in MOCK_PLACEMENT_DATA) / len(MOCK_PLACEMENT_DATA)
            },
            'branch_performance': [
                {
                    'student_branch': 'Computer Science Engineering',
                    'placement_count': 2,
                    'avg_salary': 550000,
                    'avg_feedback': 8.65
                },
                {
                    'student_branch': 'Information Technology',
                    'placement_count': 1,
                    'avg_salary': 450000,
                    'avg_feedback': 9.0
                }
            ]
        }
        
        generator = ReportGenerator()
        pdf_bytes = generator.generate_pdf_report(report_data)
        
        from flask import make_response
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename="test_report.pdf"'
        return response
        
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'PDF generation failed'}), 500

@app.route('/test-csv')
def test_csv():
    try:
        from utils.report_generator import ReportGenerator
        
        # Generate test report data
        report_data = {
            'report_type': 'placement_summary',
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_placements': len(MOCK_PLACEMENT_DATA),
                'branches_covered': 2,
                'industries_covered': 2,
                'avg_salary': sum(p['salary'] for p in MOCK_PLACEMENT_DATA) / len(MOCK_PLACEMENT_DATA)
            },
            'branch_performance': [
                {
                    'student_branch': 'Computer Science Engineering',
                    'placement_count': 2,
                    'avg_salary': 550000,
                    'avg_feedback': 8.65
                },
                {
                    'student_branch': 'Information Technology',
                    'placement_count': 1,
                    'avg_salary': 450000,
                    'avg_feedback': 9.0
                }
            ]
        }
        
        generator = ReportGenerator()
        csv_content = generator.generate_csv_report(report_data)
        
        from flask import make_response
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename="test_report.csv"'
        return response
        
    except Exception as e:
        return jsonify({'error': str(e), 'message': 'CSV generation failed'}), 500

# Simple reports interface for testing
@app.route('/analytics/reports/view')
def reports_view():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reports Test Interface</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .btn { padding: 10px 20px; margin: 10px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
            .btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <h1>Reports Test Interface</h1>
        <p>Test the report generation functionality:</p>
        
        <h3>Direct Downloads:</h3>
        <a href="/test-pdf" class="btn">Download PDF Report</a>
        <a href="/test-csv" class="btn">Download CSV Report</a>
        
        <h3>API Endpoints:</h3>
        <p>You can test these endpoints with tools like Postman or curl:</p>
        <ul>
            <li><code>GET /test-pdf</code> - Generate and download PDF report</li>
            <li><code>GET /test-csv</code> - Generate and download CSV report</li>
            <li><code>GET /health</code> - Health check</li>
        </ul>
        
        <h3>Test Data:</h3>
        <p>The app uses mock placement data for testing:</p>
        <ul>
            <li>3 sample placements</li>
            <li>2 branches (CSE, IT)</li>
            <li>2 industries (Technology, Finance)</li>
            <li>Salary range: ₹4.5L - ₹6L</li>
        </ul>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🚀 Starting AI Career Platform Test App...")
    print("📊 Report generation functionality test mode")
    print("🌐 Access the app at: http://localhost:5000")
    print("📄 Test PDF generation: http://localhost:5000/test-pdf")
    print("📊 Test CSV generation: http://localhost:5000/test-csv")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)