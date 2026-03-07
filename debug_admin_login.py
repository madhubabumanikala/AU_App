#!/usr/bin/env python3
"""
Debug Admin Login Issue
"""

def debug_admin_login():
    print("Debugging Admin Login Issue...")
    
    try:
        from app import create_app
        from extensions import db
        from models.user import Admin, Student
        from werkzeug.security import generate_password_hash
        
        app = create_app()
        
        with app.app_context():
            # Create tables if they don't exist
            db.create_all()
            
            print("1. Checking database tables...")
            
            # Check if admin table exists and has data
            try:
                admin_count = Admin.query.count()
                print(f"   ✅ Admin table exists with {admin_count} records")
            except Exception as e:
                print(f"   ❌ Admin table issue: {e}")
                return False
            
            # Check if there are any admins
            print("2. Checking existing admins...")
            admins = Admin.query.all()
            for admin in admins:
                print(f"   - Admin: {admin.username} ({admin.email}) - Active: {admin.is_active}")
            
            # Create test admin if none exist
            if admin_count == 0:
                print("3. Creating test admin...")
                test_admin = Admin(
                    email='admin@au.edu.in',
                    username='admin',
                    first_name='Test',
                    last_name='Admin',
                    is_active=True
                )
                test_admin.set_password('admin123')
                
                try:
                    db.session.add(test_admin)
                    db.session.commit()
                    print(f"   ✅ Created test admin: admin@au.edu.in / admin123")
                except Exception as e:
                    print(f"   ❌ Error creating admin: {e}")
                    db.session.rollback()
                    return False
            
            # Test admin login logic
            print("4. Testing admin authentication...")
            test_email = 'admin@au.edu.in'
            test_password = 'admin123'
            
            admin = Admin.query.filter_by(email=test_email).first()
            if admin:
                print(f"   - Found admin: {admin.username}")
                print(f"   - Is active: {admin.is_active}")
                print(f"   - Has password: {bool(admin.password_hash)}")
                
                # Test password check
                if admin.check_password(test_password):
                    print("   ✅ Password check passed")
                else:
                    print("   ❌ Password check failed")
                    
                # Check class name
                class_name = admin.__class__.__name__
                print(f"   - Class name: {class_name}")
                print(f"   - Class name lower: {class_name.lower()}")
                
            else:
                print("   ❌ Admin not found with test email")
            
            # Test User model inheritance
            print("5. Testing User model inheritance...")
            from models.user import User
            print(f"   - User is abstract: {getattr(User, '__abstract__', False)}")
            print(f"   - Admin inherits from User: {issubclass(Admin, User)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_login_form():
    print("\nChecking Login Form...")
    try:
        from utils.forms import LoginForm
        form = LoginForm()
        print("   ✅ LoginForm imports successfully")
        
        # Check form fields
        print(f"   - Has email field: {hasattr(form, 'email')}")
        print(f"   - Has password field: {hasattr(form, 'password')}")
        print(f"   - Has user_type field: {hasattr(form, 'user_type')}")
        print(f"   - Has remember_me field: {hasattr(form, 'remember_me')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ LoginForm error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("ADMIN LOGIN DEBUG")
    print("=" * 60)
    
    success1 = debug_admin_login()
    success2 = check_login_form()
    
    print("\n" + "=" * 60)
    print("DEBUG RESULTS")
    print("=" * 60)
    
    if success1 and success2:
        print("✅ Admin system appears functional")
        print("\nTry logging in with:")
        print("Email: admin@au.edu.in")
        print("Password: admin123")
        print("User Type: Admin")
    else:
        print("❌ Issues found in admin system")
    
    print("\nIf login still fails:")
    print("- Check browser console for JavaScript errors")
    print("- Verify database connection")
    print("- Check Flask session configuration")
