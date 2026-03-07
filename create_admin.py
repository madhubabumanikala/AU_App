#!/usr/bin/env python3
"""
Add Dummy Admin Credentials to Database
"""

from app import create_app
from extensions import db
from models.user import Admin

def add_dummy_admin():
    """Add multiple dummy admin accounts for testing"""
    app = create_app()
    
    with app.app_context():
        try:
            # Ensure tables exist
            db.create_all()
            print("Database tables created/verified")
            
            # Define dummy admin accounts
            dummy_admins = [
                {
                    'email': 'admin@au.edu.in',
                    'username': 'admin',
                    'first_name': 'System',
                    'last_name': 'Administrator',
                    'password': 'admin123'
                },
                {
                    'email': 'dean@au.edu.in', 
                    'username': 'dean',
                    'first_name': 'Academic',
                    'last_name': 'Dean',
                    'password': 'dean123'
                },
                {
                    'email': 'registrar@au.edu.in',
                    'username': 'registrar', 
                    'first_name': 'University',
                    'last_name': 'Registrar',
                    'password': 'registrar123'
                }
            ]
            
            created_count = 0
            
            for admin_data in dummy_admins:
                # Check if admin already exists
                existing = Admin.query.filter_by(email=admin_data['email']).first()
                if existing:
                    print(f"⚠️  Admin already exists: {admin_data['email']}")
                    continue
                
                # Create new admin
                admin = Admin(
                    email=admin_data['email'],
                    username=admin_data['username'],
                    first_name=admin_data['first_name'],
                    last_name=admin_data['last_name'],
                    role='admin',
                    is_active=True
                )
                admin.set_password(admin_data['password'])
                
                db.session.add(admin)
                created_count += 1
                
                print(f"✅ Created admin: {admin_data['email']} / {admin_data['password']}")
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n🎉 Successfully added {created_count} dummy admin accounts!")
            
            # Show all admin accounts
            print("\n📋 All Admin Accounts:")
            all_admins = Admin.query.all()
            for admin in all_admins:
                print(f"   • {admin.email} ({admin.username}) - Active: {admin.is_active}")
            
            print("\n🔑 Login Credentials:")
            for admin_data in dummy_admins:
                print(f"   📧 {admin_data['email']} / 🔐 {admin_data['password']}")
            
            print("\n💡 Use any of these credentials to login as admin")
            print("   Select 'Admin' as user type at login page")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating admins: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

def verify_admin_accounts():
    """Verify all admin accounts can authenticate"""
    app = create_app()
    
    with app.app_context():
        print("\n🔍 Verifying admin accounts...")
        
        test_credentials = [
            ('admin@au.edu.in', 'admin123'),
            ('dean@au.edu.in', 'dean123'),
            ('registrar@au.edu.in', 'registrar123')
        ]
        
        for email, password in test_credentials:
            admin = Admin.query.filter_by(email=email).first()
            if admin:
                if admin.check_password(password) and admin.is_active:
                    print(f"   ✅ {email} - Authentication OK")
                else:
                    print(f"   ❌ {email} - Authentication FAILED")
            else:
                print(f"   ⚠️  {email} - Admin not found")

if __name__ == '__main__':
    print("=" * 60)
    print("ADDING DUMMY ADMIN CREDENTIALS")
    print("=" * 60)
    
    success = add_dummy_admin()
    
    if success:
        verify_admin_accounts()
        print("\n✅ Dummy admin setup complete!")
        print("Go to login page and use any of the admin credentials shown above.")
    else:
        print("\n❌ Failed to setup dummy admins")
