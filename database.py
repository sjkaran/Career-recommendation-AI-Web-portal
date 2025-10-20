"""
Simple database initialization
"""
import sqlite3
import os

def init_db(app):
    """Initialize database"""
    db_path = 'career_platform.db'
    
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create basic tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password TEXT,
                role TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert demo data
        demo_users = [
            (1, 'demo_student', 'student@demo.com', 'demo123', 'student'),
            (2, 'demo_employer', 'employer@demo.com', 'demo123', 'employer'),
            (3, 'demo_officer', 'officer@demo.com', 'demo123', 'placement_officer')
        ]
        
        for user in demo_users:
            cursor.execute('''
                INSERT OR REPLACE INTO users (id, username, email, password, role) 
                VALUES (?, ?, ?, ?, ?)
            ''', user)
        
        conn.commit()
        conn.close()
        print("✅ Database initialized with demo data")
    
    return app