#!/usr/bin/env python3
"""
Quick Admin Creation Script
Run this to create/fix admin login
"""

from app import create_app
from extensions import db
from models.user import Admin

def create_admin_user():
    app = create_app()
    
    with app.app_context():
        try:
            # Ensure tables exist
            db.create_all()
            
            # Remove existing admin if any
            existing = Admin.query.filter_by(email='admin@test.com').first()
            if existing:
                db.session.delete(existing)
                db.session.commit()
                print("Removed existing admin")
            
            # Create new admin
            admin = Admin(
                email='admin@test.com',
                username='admin',
                first_name='System',
                last_name='Admin',
                is_active=True
            )
            admin.set_password('admin123')
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Admin created successfully!")
            print("📧 Email: admin@test.com")
            print("🔐 Password: admin123")
            print("👤 Select 'Admin' as user type at login")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    create_admin_user()
