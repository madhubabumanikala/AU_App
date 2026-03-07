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
