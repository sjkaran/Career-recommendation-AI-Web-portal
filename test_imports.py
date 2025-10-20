#!/usr/bin/env python3
"""
Test script to check imports and identify issues
"""
import sys
import traceback

def test_import(module_name, description):
    try:
        __import__(module_name)
        print(f"✅ {description}: OK")
        return True
    except Exception as e:
        print(f"❌ {description}: {e}")
        traceback.print_exc()
        return False

print("Testing imports for AI Career Platform...")
print("=" * 50)

# Test basic imports
test_import("flask", "Flask")
test_import("flask_cors", "Flask-CORS")
test_import("config", "Config module")
test_import("database", "Database module")

# Test utility imports
test_import("utils.language_service", "Language service")
test_import("utils.security_middleware", "Security middleware")
test_import("utils.privacy_manager", "Privacy manager")

# Test blueprint imports
test_import("blueprints.auth", "Auth blueprint")
test_import("blueprints.student", "Student blueprint")
test_import("blueprints.employer", "Employer blueprint")
test_import("blueprints.analytics", "Analytics blueprint")
test_import("blueprints.api", "API blueprint")
test_import("blueprints.ai_recommendations", "AI recommendations blueprint")
test_import("blueprints.gamification", "Gamification blueprint")

print("=" * 50)
print("Import testing complete!")