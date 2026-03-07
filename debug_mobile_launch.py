#!/usr/bin/env python3
"""
Debug mobile app launch
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 60)
print("MOBILE APP LAUNCH DEBUG")
print("=" * 60)

# Test 1: Check basic imports
try:
    from flask import Flask
    from flask_login import LoginManager, current_user
    print("SUCCESS: Basic Flask imports work")
except Exception as e:
    print(f"ERROR: Basic Flask imports failed: {e}")
    sys.exit(1)

# Test 2: Check mobile routes import
try:
    from routes.mobile import mobile_bp
    print("SUCCESS: Mobile routes imported")
except Exception as e:
    print(f"ERROR: Mobile routes import failed: {e}")
    sys.exit(1)

# Test 3: Check config import
try:
    from config_portable import PortableConfig
    config = PortableConfig()
    print("SUCCESS: Portable config works")
    print(f"Database URI: {config.SQLALCHEMY_DATABASE_URI}")
except Exception as e:
    print(f"ERROR: Portable config failed: {e}")
    sys.exit(1)

# Test 4: Check extensions import
try:
    from extensions import db, login_manager
    print("SUCCESS: Extensions imported")
except Exception as e:
    print(f"ERROR: Extensions import failed: {e}")
    sys.exit(1)

# Test 5: Check Flask app creation
try:
    app = Flask(__name__)
    app.config.from_object(config)
    print("SUCCESS: Flask app created")
except Exception as e:
    print(f"ERROR: Flask app creation failed: {e}")
    sys.exit(1)

# Test 6: Check blueprint registration
try:
    app.register_blueprint(mobile_bp)
    print("SUCCESS: Mobile blueprint registered")
except Exception as e:
    print(f"ERROR: Blueprint registration failed: {e}")
    sys.exit(1)

# Test 7: Check database initialization
try:
    with app.app_context():
        print("Testing database initialization...")
        
        # Test basic database connection without importing models
        try:
            # Test if we can execute raw SQL
            result = db.engine.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = result.fetchone()[0]
            print(f"SUCCESS: Database connection works (Tables: {table_count})")
            
            # Now try to create tables
            db.create_all()
            print("SUCCESS: Database initialization works")
        except Exception as e:
            print(f"ERROR: Database initialization failed: {e}")
            sys.exit(1)
except Exception as e:
    print(f"ERROR: Database context failed: {e}")
    sys.exit(1)

# Test 8: Check current_user
try:
    print(f"Current user type: {type(current_user)}")
    print(f"Current user is_authenticated: {current_user.is_authenticated}")
except Exception as e:
    print(f"ERROR: Current user check failed: {e}")
    sys.exit(1)

print("=" * 60)
print("ALL TESTS PASSED!")
print("Mobile app should work now.")
print("Run: python run_mobile_fixed.py")
print("=" * 60)
