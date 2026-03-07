#!/usr/bin/env python3
"""
AU Event System - Static System Test
Tests basic system components without running the server
"""

def test_imports():
    """Test if all critical modules can be imported"""
    print("🔍 Testing Python imports...")
    
    errors = []
    
    # Test Flask and extensions
    try:
        from flask import Flask
        print("  ✅ Flask")
    except ImportError as e:
        errors.append(f"Flask: {e}")
    
    try:
        from flask_sqlalchemy import SQLAlchemy
        print("  ✅ Flask-SQLAlchemy")
    except ImportError as e:
        errors.append(f"Flask-SQLAlchemy: {e}")
    
    try:
        from flask_login import LoginManager
        print("  ✅ Flask-Login")
    except ImportError as e:
        errors.append(f"Flask-Login: {e}")
    
    try:
        from flask_socketio import SocketIO
        print("  ✅ Flask-SocketIO")
    except ImportError as e:
        errors.append(f"Flask-SocketIO: {e}")
    
    # Test our modules
    try:
        from extensions import db, login_manager, socketio
        print("  ✅ Extensions")
    except ImportError as e:
        errors.append(f"Extensions: {e}")
    
    try:
        from models.user import User, Student, Admin
        print("  ✅ User models")
    except ImportError as e:
        errors.append(f"User models: {e}")
    
    try:
        from models.event import Event, EventRegistration
        print("  ✅ Event models")
    except ImportError as e:
        errors.append(f"Event models: {e}")
    
    try:
        from models.social import Post, PostLike, PostComment
        print("  ✅ Social models")
    except ImportError as e:
        errors.append(f"Social models: {e}")
    
    try:
        from routes.auth import auth_bp
        print("  ✅ Auth routes")
    except ImportError as e:
        errors.append(f"Auth routes: {e}")
    
    try:
        from routes.main import main_bp
        print("  ✅ Main routes")
    except ImportError as e:
        errors.append(f"Main routes: {e}")
    
    try:
        from routes.social import social_bp
        print("  ✅ Social routes")
    except ImportError as e:
        errors.append(f"Social routes: {e}")
    
    try:
        from utils.mobile_detector import MobileDetector
        print("  ✅ Mobile detector")
    except ImportError as e:
        errors.append(f"Mobile detector: {e}")
    
    try:
        from utils.media_handler import MediaHandler
        print("  ✅ Media handler")
    except ImportError as e:
        errors.append(f"Media handler: {e}")
    
    return errors

def test_templates():
    """Test if critical templates exist"""
    print("\n🔍 Testing templates...")
    
    import os
    missing = []
    
    templates_to_check = [
        'templates/base.html',
        'templates/index.html',
        'templates/social/feed.html',
        'templates/social/create_post.html',
        'templates/social/post_details.html',
        'templates/social/mobile_feed.html',
        'templates/social/mobile_create_post.html',
        'templates/auth/mobile_login.html',
        'templates/auth/mobile_register.html',
        'templates/main/mobile_dashboard_complete.html',
        'templates/main/mobile_events.html'
    ]
    
    for template in templates_to_check:
        if os.path.exists(template):
            print(f"  ✅ {template}")
        else:
            print(f"  ❌ {template}")
            missing.append(template)
    
    return missing

def test_static_files():
    """Test if critical static files exist"""
    print("\n🔍 Testing static files...")
    
    import os
    missing = []
    
    static_files_to_check = [
        'static/manifest.json',
        'static/js/service-worker.js',
        'static/css/mobile.css',
        'static/js/mobile-app.js',
        'static/images/icon-192.svg',
        'static/images/icon-512.svg'
    ]
    
    for static_file in static_files_to_check:
        if os.path.exists(static_file):
            print(f"  ✅ {static_file}")
        else:
            print(f"  ❌ {static_file}")
            missing.append(static_file)
    
    return missing

def test_app_creation():
    """Test if the Flask app can be created"""
    print("\n🔍 Testing app creation...")
    
    try:
        from app import create_app
        app = create_app()
        print("  ✅ Flask app created successfully")
        
        # Test routes are registered
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        
        critical_routes = [
            '/',
            '/auth/login',
            '/auth/student/register',
            '/social/feed',
            '/social/create',
            '/api/posts/recent'
        ]
        
        missing_routes = []
        for route in critical_routes:
            if any(route in rule for rule in rules):
                print(f"  ✅ Route: {route}")
            else:
                print(f"  ❌ Route: {route}")
                missing_routes.append(route)
        
        return True, missing_routes
        
    except Exception as e:
        print(f"  ❌ App creation failed: {e}")
        return False, [str(e)]

def test_database_models():
    """Test if database models are properly defined"""
    print("\n🔍 Testing database models...")
    
    try:
        from app import create_app
        from extensions import db
        from models.user import Student, Admin
        from models.event import Event
        from models.social import Post, PostLike, PostComment
        
        app = create_app()
        
        with app.app_context():
            # Check if tables can be created
            db.create_all()
            print("  ✅ Database tables created successfully")
            
            # Test basic model instantiation
            try:
                student = Student()
                admin = Admin()
                event = Event()
                post = Post()
                print("  ✅ Model classes instantiated successfully")
                return True
            except Exception as e:
                print(f"  ❌ Model instantiation failed: {e}")
                return False
                
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False

def main():
    """Run all system tests"""
    print("=" * 60)
    print("AU EVENT SYSTEM - STATIC SYSTEM TEST")
    print("=" * 60)
    
    # Test imports
    import_errors = test_imports()
    
    # Test templates
    missing_templates = test_templates()
    
    # Test static files
    missing_static = test_static_files()
    
    # Test app creation
    app_created, missing_routes = test_app_creation()
    
    # Test database models
    db_test_passed = test_database_models()
    
    # Summary
    print("\n" + "=" * 60)
    print("SYSTEM TEST SUMMARY")
    print("=" * 60)
    
    total_issues = len(import_errors) + len(missing_templates) + len(missing_static) + len(missing_routes)
    
    if import_errors:
        print(f"❌ Import Errors ({len(import_errors)}):")
        for error in import_errors:
            print(f"   - {error}")
    
    if missing_templates:
        print(f"❌ Missing Templates ({len(missing_templates)}):")
        for template in missing_templates:
            print(f"   - {template}")
    
    if missing_static:
        print(f"❌ Missing Static Files ({len(missing_static)}):")
        for static_file in missing_static:
            print(f"   - {static_file}")
    
    if missing_routes:
        print(f"❌ Missing/Broken Routes ({len(missing_routes)}):")
        for route in missing_routes:
            print(f"   - {route}")
    
    if not app_created:
        print("❌ Flask app creation failed")
        total_issues += 1
    
    if not db_test_passed:
        print("❌ Database model test failed")
        total_issues += 1
    
    print(f"\n📊 OVERALL STATUS:")
    if total_issues == 0:
        print("✅ ALL TESTS PASSED - System is ready!")
        return 0
    else:
        print(f"❌ {total_issues} ISSUES FOUND - System needs fixes")
        return 1

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)
