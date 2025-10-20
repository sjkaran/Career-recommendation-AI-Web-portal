#!/usr/bin/env python3
"""
Complete setup script for AI Career Platform Demo
This script will initialize the database with sample data and start the application
"""
import os
import sys
import sqlite3
from datetime import datetime, date
import hashlib

def create_sample_data():
    """Create sample data for demonstration"""
    print("📊 Creating sample data for demonstration...")
    
    # Connect to database
    conn = sqlite3.connect('career_platform.db')
    cursor = conn.cursor()
    
    try:
        # Create sample users
        print("👥 Creating sample users...")
        
        # Hash password for demo (password: "demo123")
        password_hash = hashlib.sha256("demo123".encode()).hexdigest()
        
        sample_users = [
            (1, 'student@demo.com', password_hash, 'student', 'John Doe', '2024-01-01 10:00:00'),
            (2, 'employer@demo.com', password_hash, 'employer', 'Jane Smith', '2024-01-01 10:00:00'),
            (3, 'officer@demo.com', password_hash, 'placement_officer', 'Mike Johnson', '2024-01-01 10:00:00'),
            (4, 'admin@demo.com', password_hash, 'admin', 'Admin User', '2024-01-01 10:00:00'),
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO users (id, email, password_hash, role, full_name, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_users)
        
        # Create sample student profiles
        print("🎓 Creating sample student profiles...")
        
        sample_students = [
            (1, 1, '{"name": "John Doe", "email": "student@demo.com", "phone": "+91-9876543210"}',
             '{"branch": "Computer Science Engineering", "cgpa": 8.5, "graduation_year": 2024, "university": "Demo University"}',
             '["Python", "JavaScript", "React", "Node.js", "MongoDB", "Machine Learning"]',
             '{"internships": [{"company": "TechCorp", "role": "Software Intern", "duration": "3 months"}]}',
             '2024-01-01 10:00:00'),
            (2, 2, '{"name": "Alice Johnson", "email": "alice@demo.com", "phone": "+91-9876543211"}',
             '{"branch": "Information Technology", "cgpa": 9.0, "graduation_year": 2024, "university": "Demo University"}',
             '["Java", "Spring Boot", "Angular", "MySQL", "AWS", "DevOps"]',
             '{"internships": [{"company": "DataSoft", "role": "Backend Developer Intern", "duration": "6 months"}]}',
             '2024-01-01 11:00:00'),
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO student_profiles 
            (id, user_id, personal_info, academic_records, technical_skills, experience, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_students)
        
        # Create sample employers
        print("🏢 Creating sample employers...")
        
        sample_employers = [
            (1, 2, 'TechCorp Solutions', 'Technology', 'Software Development and IT Services',
             'Bangalore, India', 'https://techcorp.demo.com', '2024-01-01 10:00:00'),
            (2, 2, 'DataSoft Analytics', 'Technology', 'Data Analytics and AI Solutions',
             'Mumbai, India', 'https://datasoft.demo.com', '2024-01-01 11:00:00'),
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO employers 
            (id, user_id, company_name, industry, description, location, website, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_employers)
        
        # Create sample job postings
        print("💼 Creating sample job postings...")
        
        sample_jobs = [
            (1, 1, 'Full Stack Developer', 'TechCorp Solutions', 'Bangalore, India',
             'We are looking for a talented Full Stack Developer to join our team.',
             '["JavaScript", "React", "Node.js", "MongoDB"]', 'entry_level',
             '{"min": 400000, "max": 600000}', 'active', '2024-12-31', '2024-01-01 10:00:00'),
            (2, 1, 'Data Scientist', 'TechCorp Solutions', 'Bangalore, India',
             'Join our AI team as a Data Scientist and work on cutting-edge projects.',
             '["Python", "Machine Learning", "TensorFlow", "SQL"]', 'mid_level',
             '{"min": 800000, "max": 1200000}', 'active', '2024-12-31', '2024-01-01 11:00:00'),
            (3, 2, 'Backend Developer', 'DataSoft Analytics', 'Mumbai, India',
             'Looking for a skilled Backend Developer to build scalable systems.',
             '["Java", "Spring Boot", "MySQL", "AWS"]', 'entry_level',
             '{"min": 500000, "max": 700000}', 'active', '2024-12-31', '2024-01-01 12:00:00'),
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO job_postings 
            (id, employer_id, title, company_name, location, description, required_skills, 
             experience_level, salary_range, status, application_deadline, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_jobs)
        
        # Create sample placement analytics
        print("📈 Creating sample placement analytics...")
        
        sample_placements = [
            (1, 1, 1, '2024-03-15', 500000, 'TechCorp Solutions', 'Technology',
             'Computer Science Engineering', 'Karnataka', 8.5, '2024-03-15 10:00:00'),
            (2, 2, 3, '2024-03-20', 550000, 'DataSoft Analytics', 'Technology',
             'Information Technology', 'Maharashtra', 9.0, '2024-03-20 10:00:00'),
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO placement_analytics 
            (id, student_id, job_id, placement_date, salary, company_name, job_category,
             student_branch, student_district, feedback_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_placements)
        
        # Create sample skill demand data
        print("🎯 Creating sample skill demand data...")
        
        sample_skills = [
            (1, 'Python', 'Technology', 95.0, 150, 800000, 15.5, '2024-01-01 10:00:00'),
            (2, 'JavaScript', 'Technology', 92.0, 200, 600000, 12.3, '2024-01-01 10:00:00'),
            (3, 'React', 'Technology', 88.0, 120, 700000, 18.7, '2024-01-01 10:00:00'),
            (4, 'Machine Learning', 'Technology', 90.0, 80, 1200000, 25.2, '2024-01-01 10:00:00'),
            (5, 'Java', 'Technology', 85.0, 180, 650000, 8.9, '2024-01-01 10:00:00'),
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO skill_demand 
            (id, skill_name, industry, demand_score, job_count, avg_salary, growth_rate, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_skills)
        
        # Create sample job applications
        print("📝 Creating sample job applications...")
        
        sample_applications = [
            (1, 1, 1, 'applied', 'Strong candidate with relevant skills', '2024-02-01 10:00:00'),
            (2, 2, 3, 'interviewed', 'Excellent technical skills, good cultural fit', '2024-02-05 10:00:00'),
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO job_applications 
            (id, student_id, job_id, status, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_applications)
        
        conn.commit()
        print("✅ Sample data created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    """Main setup function"""
    print("🚀 AI Career Platform Demo Setup")
    print("=" * 50)
    
    try:
        # Import and initialize the app
        print("📦 Importing application modules...")
        from app import create_app
        from database import init_db
        
        print("🏗️  Creating Flask application...")
        app = create_app()
        
        print("🗄️  Initializing database...")
        with app.app_context():
            init_db(app)
        
        # Create sample data
        create_sample_data()
        
        print("\n" + "=" * 50)
        print("✅ Setup completed successfully!")
        print("\n🌐 Demo Credentials:")
        print("   Student: student@demo.com / demo123")
        print("   Employer: employer@demo.com / demo123") 
        print("   Placement Officer: officer@demo.com / demo123")
        print("   Admin: admin@demo.com / demo123")
        print("\n🚀 Starting the application...")
        print("   Access at: http://localhost:5000")
        print("=" * 50)
        
        # Start the application
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()