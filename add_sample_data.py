#!/usr/bin/env python3
"""
Add sample data to the database for demonstration
"""
import sqlite3
import hashlib
from datetime import datetime

def add_sample_data():
    """Add sample data for demonstration"""
    print("📊 Adding sample data for demonstration...")
    
    conn = sqlite3.connect('career_platform.db')
    cursor = con