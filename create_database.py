#!/usr/bin/env python3
"""
Simple database creation script for AI Career Platform
Creates all necessary tables without requiring full app import
"""
import sqlite3
import os

def create_database():
    """Create database and all required tables"""
    print("🗄️  Creating database and tables...")
    
    # Remove existing database if it exists
    if os.path.exists('career_platform.db'):
        os.remove('career_platform.db')
        print("🗑️  Removed existing database")
    
    conn = sqlite3.connect('career_platform.db')
    cursor = conn.cursor()
    
    try:
        # Users table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('student', 'employer', 'placement_officer', 'admin')),
                full_name TEXT,
                is_active BOOLEAN DEFAULT 1,
                email_verified BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Student profiles table
        cursor.execute('''
            CREATE TABLE student_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                personal_info TEXT,
                academic_records TEXT,
                technical_skills TEXT,
                experience TEXT,
                achievements TEXT,
                preferences TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Employers table
        cursor.execute('''
            CREATE TABLE employers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                company_name TEXT NOT NULL,
                industry TEXT,
                description TEXT,
                location TEXT,
                website TEXT,
                company_size TEXT,
                founded_year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Job postings table
        cursor.execute('''
            CREATE TABLE job_postings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employer_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                company_name TEXT NOT NULL,
                location TEXT,
                description TEXT,
                required_skills TEXT,
                experience_level TEXT,
                salary_range TEXT,
                employment_type TEXT DEFAULT 'full_time',
                status TEXT DEFAULT 'active' CHECK (status IN ('active', 'closed', 'draft')),
                application_deadline DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employer_id) REFERENCES employers (id)
            )
        ''')
        
        # Job applications table
        cursor.execute('''
            CREATE TABLE job_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                status TEXT DEFAULT 'applied' CHECK (status IN ('applied', 'reviewed', 'interviewed', 'offered', 'accepted', 'rejected')),
                cover_letter TEXT,
                resume_path TEXT,
                notes TEXT,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES student_profiles (id),
                FOREIGN KEY (job_id) REFERENCES job_postings (id),
                UNIQUE(student_id, job_id)
            )
        ''')
        
        # Placement analytics table
        cursor.execute('''
            CREATE TABLE placement_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                job_id INTEGER,
                placement_date DATE,
                salary REAL,
                company_name TEXT,
                job_category TEXT,
                student_branch TEXT,
                student_district TEXT,
                feedback_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES student_profiles (id),
                FOREIGN KEY (job_id) REFERENCES job_postings (id)
            )
        ''')
        
        # Skill demand table
        cursor.execute('''
            CREATE TABLE skill_demand (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT NOT NULL,
                industry TEXT,
                demand_score REAL,
                job_count INTEGER DEFAULT 0,
                avg_salary REAL,
                growth_rate REAL DEFAULT 0.0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(skill_name, industry)
            )
        ''')
        
        # Gamification table
        cursor.execute('''
            CREATE TABLE gamification (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                points INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                badges TEXT,
                achievements TEXT,
                streak_days INTEGER DEFAULT 0,
                last_activity DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Privacy settings table
        cursor.execute('''
            CREATE TABLE privacy_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                data_processing_consent BOOLEAN DEFAULT 0,
                marketing_consent BOOLEAN DEFAULT 0,
                profile_visibility TEXT DEFAULT 'private',
                data_retention_period INTEGER DEFAULT 365,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Audit log table
        cursor.execute('''
            CREATE TABLE audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id INTEGER,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        print("✅ Database and tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    create_database()
    print("🎉 Database setup complete!")