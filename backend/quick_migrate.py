# backend/quick_migrate.py
import os
import sys

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")
    
    # List tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("📊 Tables:", tables)