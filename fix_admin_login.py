#!/usr/bin/env python3
"""
Fix Admin Login Issue - Create admin user and test login
"""

def fix_admin_login():
    print("Fixing Admin Login Issue...")
    
    try:
        from app import create_app
        from extensions import db
        from models.user import Admin
        
        app = create_app()
        
        with app.app_context():
            # Drop and recreate tables to ensure consistency
            print("1. Recreating database tables...")
            db.create_all()
            
            # Check for existing admin
            existing_admin = Admin.query.filter_by(email='admin@au.edu.in').first()
            if existing_admin:
                print("   - Removing existing admin")
                db.session.delete(existing_admin)
                db.session.commit()
            
            # Create fresh admin user
            print("2. Creating new admin user...")
            admin = Admin(
                email='admin@au.edu.in',
                username='admin',
                first_name='System',
                last_name='Admin',
                is_active=True
            )
            admin.set_password('admin123')
            
            db.session.add(admin)
            db.session.commit()
            
            print(f"   ✅ Created admin user:")
            print(f"   - Email: admin@au.edu.in")
            print(f"   - Username: admin")
            print(f"   - Password: admin123")
            print(f"   - ID: {admin.id}")
            
            # Test the admin user
            print("3. Testing admin authentication...")
            
            test_admin = Admin.query.filter_by(email='admin@au.edu.in').first()
            if test_admin and test_admin.check_password('admin123') and test_admin.is_active:
                print("   ✅ Admin authentication test passed")
                
                # Test class name (used in permissions)
                class_name = test_admin.__class__.__name__
                print(f"   - Class name: '{class_name}'")
                print(f"   - Class name lower: '{class_name.lower()}'")
                
                return True
            else:
                print("   ❌ Admin authentication test failed")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_admin_permissions():
    print("\n4. Testing admin permission checks...")
    try:
        from app import create_app
        from models.user import Admin
        
        app = create_app()
        with app.app_context():
            admin = Admin.query.filter_by(email='admin@au.edu.in').first()
            if admin:
                # Test the permission checks we added
                is_admin_check = admin.__class__.__name__.lower() == 'admin'
                print(f"   - Admin permission check: {is_admin_check}")
                
                if is_admin_check:
                    print("   ✅ Admin permission checks working")
                    return True
                else:
                    print("   ❌ Admin permission checks failing")
                    return False
            else:
                print("   ❌ Admin user not found")
                return False
                
    except Exception as e:
        print(f"   ❌ Permission test error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("ADMIN LOGIN FIX")
    print("=" * 50)
    
    success1 = fix_admin_login()
    success2 = test_admin_permissions()
    
    print("\n" + "=" * 50)
    print("FIX RESULTS")
    print("=" * 50)
    
    if success1 and success2:
        print("✅ Admin login should now work!")
        print("\nLogin credentials:")
        print("📧 Email: admin@au.edu.in")
        print("🔐 Password: admin123") 
        print("👤 User Type: Admin")
        print("\nGo to login page and try these credentials.")
    else:
        print("❌ Admin login fix failed")
        print("Check the error messages above for details.")
