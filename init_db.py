#!/usr/bin/env python3
"""
Database initialization script for AI Career Platform
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from database import init_db
    
    print("Creating Flask application...")
    app = create_app()
    
    print("Initializing database...")
    with app.app_context():
        init_db(app)
    
    print("✅ Database initialized successfully!")
    print("📁 Database file: career_platform.db")
    
except Exception as e:
    print(f"❌ Error initializing database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)