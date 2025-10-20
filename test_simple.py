#!/usr/bin/env python3
"""
Simple test to check if the application can start
"""
import os
import sys

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("Testing imports...")
        import flask
        print("✓ Flask imported")
        
        import sqlite3
        print("✓ SQLite3 imported")
        
        from app import create_app
        print("✓ App module imported")
        
        app = create_app()
        print("✓ App created successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_database():
    """Test database creation"""
    try:
        print("\nTesting database...")
        import sqlite3
        
        # Create a simple test database
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        ''')
        
        cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("test",))
        conn.commit()
        
        cursor.execute("SELECT * FROM test_table")
        result = cursor.fetchone()
        
        conn.close()
        os.remove('test.db')
        
        print("✓ Database operations successful")
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 AI Career Platform - Simple Test")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test database
    if not test_database():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed! The application should be ready to run.")
        print("\nTo start the application:")
        print("1. Run: python app.py")
        print("2. Open browser to: http://localhost:5000")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == '__main__':
    main()