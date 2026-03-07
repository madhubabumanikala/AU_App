#!/usr/bin/env python3
"""
Check all module imports
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 60)
print("MODULE INTEGRATION CHECK")
print("=" * 60)

modules_to_check = [
    ('flask', 'Flask'),
    ('flask_sqlalchemy', 'SQLAlchemy'),
    ('flask_login', 'LoginManager'),
    ('werkzeug.security', 'generate_password_hash'),
    ('routes.auth', 'auth_bp'),
    ('routes.mobile', 'mobile_bp'),
    ('models.user', 'Student, Admin'),
    ('models.event', 'Event'),
    ('models.notification', 'Notification'),
    ('extensions', 'db, login_manager'),
    ('config_portable', 'PortableConfig'),
]

all_passed = True

for module_name, import_name in modules_to_check:
    try:
        exec(f"from {module_name} import {import_name}")
        print(f"SUCCESS: {module_name} imported successfully")
    except ImportError as e:
        print(f"FAILED: {module_name} import failed: {e}")
        all_passed = False
    except Exception as e:
        print(f"ERROR: {module_name} error: {e}")
        all_passed = False

print("=" * 60)
if all_passed:
    print("SUCCESS: ALL MODULES INTEGRATED SUCCESSFULLY")
    print("Mobile app should work!")
else:
    print("FAILED: SOME MODULES FAILED TO IMPORT")
    print("Check virtual environment and dependencies")

print("=" * 60)
