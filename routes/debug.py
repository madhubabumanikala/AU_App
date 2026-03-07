"""
Debug Routes for Mobile Detection Testing
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from utils.mobile_detector import MobileDetector, mobile_template

debug_bp = Blueprint('debug', __name__, url_prefix='/debug')

@debug_bp.route('/mobile-test')
def mobile_test():
    """Debug route to test mobile detection"""
    user_agent = request.headers.get('User-Agent', '')
    is_mobile = MobileDetector.is_mobile()
    device_type = MobileDetector.get_device_type()
    template_name = mobile_template('main/dashboard_complete.html')
    
    debug_info = {
        'user_agent': user_agent,
        'is_mobile': is_mobile,
        'device_type': device_type,
        'template_suggested': template_name,
        'query_params': dict(request.args),
        'headers': dict(request.headers),
        'css_classes': MobileDetector.get_css_classes(),
        'viewport_meta': MobileDetector.get_viewport_meta()
    }
    
    return jsonify(debug_info)

@debug_bp.route('/force-mobile')
@login_required
def force_mobile():
    """Force mobile view for testing"""
    if isinstance(current_user, Admin):
        return redirect(url_for('admin.dashboard'))
    
    # Get student's registered events
    registered_events = current_user.get_upcoming_events()
    
    # Get recommended events
    recommended_events = current_user.get_recommended_events()
    
    # Get unread notifications
    from models.notification import Notification
    unread_notifications = current_user.notifications.filter_by(is_read=False).order_by(
        Notification.created_at.desc()
    ).limit(5).all()
    
    # Get recent events
    from models.event import Event
    from datetime import datetime
    recent_events = Event.query.filter(
        Event.date >= datetime.utcnow().date(),
        Event.is_active == True
    ).order_by(Event.date).limit(10).all()
    
    # Force mobile template
    return render_template('main/mobile_dashboard_complete.html',
                         registered_events=registered_events,
                         recommended_events=recommended_events,
                         notifications=unread_notifications,
                         upcoming_events=recent_events)

@debug_bp.route('/template-check')
def template_check():
    """Check which templates exist"""
    import os
    from flask import current_app
    
    template_folder = current_app.template_folder
    templates_found = []
    
    # Check for dashboard templates
    templates_to_check = [
        'main/dashboard_complete.html',
        'main/mobile_dashboard_complete.html',
        'social/feed.html',
        'social/mobile_feed.html',
        'auth/login.html',
        'auth/mobile_login.html'
    ]
    
    for template in templates_to_check:
        template_path = os.path.join(template_folder, template)
        exists = os.path.exists(template_path)
        templates_found.append({
            'template': template,
            'path': template_path,
            'exists': exists,
            'size': os.path.getsize(template_path) if exists else 0
        })
    
    return jsonify({
        'template_folder': template_folder,
        'templates': templates_found,
        'mobile_detection': {
            'is_mobile': MobileDetector.is_mobile(),
            'device_type': MobileDetector.get_device_type(),
            'suggested_template': mobile_template('main/dashboard_complete.html')
        }
    })

@debug_bp.route('/create-admin')
def create_admin():
    """Emergency admin creation route"""
    from extensions import db
    from models.user import Admin
    
    try:
        # Ensure tables exist
        db.create_all()
        
        # Check if admin already exists
        existing_admin = Admin.query.filter_by(email='admin@test.com').first()
        if existing_admin:
            return f"""
            <h2>Admin Already Exists</h2>
            <p><strong>Email:</strong> {existing_admin.email}</p>
            <p><strong>Active:</strong> {existing_admin.is_active}</p>
            <p><strong>Username:</strong> {existing_admin.username}</p>
            <p>Try logging in with: admin@test.com / admin123</p>
            <p><a href="/auth/login">Go to Login</a></p>
            """
        
        # Create admin user
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
        
        return f"""
        <h2>✅ Admin Created Successfully!</h2>
        <p><strong>Email:</strong> admin@test.com</p>
        <p><strong>Password:</strong> admin123</p>
        <p><strong>Username:</strong> admin</p>
        <p><strong>User Type:</strong> Select 'Admin' at login</p>
        <p><a href="/auth/login" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Go to Login</a></p>
        """
        
    except Exception as e:
        db.session.rollback()
        return f"""
        <h2>❌ Error Creating Admin</h2>
        <p>{str(e)}</p>
        <p>Check your database configuration and try again.</p>
        """

@debug_bp.route('/create-student')
def create_student():
    """Emergency student creation route"""
    from extensions import db
    from models.user import Student
    
    try:
        # Ensure tables exist
        db.create_all()
        
        # Check if student already exists
        existing_student = Student.query.filter_by(email='student@test.com').first()
        if existing_student:
            return f"""
            <h2>Student Already Exists</h2>
            <p><strong>Email:</strong> {existing_student.email}</p>
            <p><strong>Student ID:</strong> {existing_student.student_id}</p>
            <p><strong>Active:</strong> {existing_student.is_active}</p>
            <p>Try logging in with: student@test.com / student123</p>
            <p><a href="/auth/login">Go to Login</a></p>
            """
        
        # Create student user
        student = Student(
            email='student@test.com',
            student_id='AU20240001CS001',
            first_name='Test',
            last_name='Student', 
            department='Computer Science',
            year=3,
            is_active=True
        )
        student.set_password('student123')
        
        db.session.add(student)
        db.session.commit()
        
        return f"""
        <h2>✅ Student Created Successfully!</h2>
        <p><strong>Email:</strong> student@test.com</p>
        <p><strong>Password:</strong> student123</p>
        <p><strong>Student ID:</strong> AU20240001CS001</p>
        <p><strong>User Type:</strong> Select 'Student' at login</p>
        <p><a href="/auth/login" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Go to Login</a></p>
        """
        
    except Exception as e:
        db.session.rollback()
        return f"""
        <h2>❌ Error Creating Student</h2>
        <p>{str(e)}</p>
        <p>Check your database configuration and try again.</p>
        """

@debug_bp.route('/debug-auth')
def debug_auth():
    """Debug authentication system"""
    from extensions import db
    from models.user import Student, Admin
    
    try:
        db.create_all()
        
        # Count users
        student_count = Student.query.count()
        admin_count = Admin.query.count()
        
        # Get sample users
        sample_student = Student.query.first()
        sample_admin = Admin.query.first()
        
        debug_info = f"""
        <h2>🔍 Authentication Debug Info</h2>
        
        <h3>Database Status</h3>
        <p><strong>Students:</strong> {student_count}</p>
        <p><strong>Admins:</strong> {admin_count}</p>
        
        <h3>Sample Users</h3>
        """
        
        if sample_student:
            debug_info += f"""
            <p><strong>Sample Student:</strong></p>
            <ul>
                <li>Email: {sample_student.email}</li>
                <li>Student ID: {sample_student.student_id}</li>
                <li>Active: {sample_student.is_active}</li>
                <li>Has Password: {bool(sample_student.password_hash)}</li>
            </ul>
            """
        else:
            debug_info += "<p>No students found</p>"
            
        if sample_admin:
            debug_info += f"""
            <p><strong>Sample Admin:</strong></p>
            <ul>
                <li>Email: {sample_admin.email}</li>
                <li>Username: {sample_admin.username}</li>
                <li>Active: {sample_admin.is_active}</li>
                <li>Has Password: {bool(sample_admin.password_hash)}</li>
            </ul>
            """
        else:
            debug_info += "<p>No admins found</p>"
        
        debug_info += f"""
        <h3>Quick Actions</h3>
        <p><a href="/create-admin" style="background: #dc3545; color: white; padding: 8px 16px; text-decoration: none; border-radius: 3px; margin-right: 10px;">Create Admin</a></p>
        <p><a href="/create-student" style="background: #28a745; color: white; padding: 8px 16px; text-decoration: none; border-radius: 3px; margin-right: 10px;">Create Student</a></p>
        <p><a href="/auth/login" style="background: #007bff; color: white; padding: 8px 16px; text-decoration: none; border-radius: 3px;">Go to Login</a></p>
        """
        
        return debug_info
        
    except Exception as e:
        return f"""
        <h2>❌ Debug Error</h2>
        <p>{str(e)}</p>
        """
