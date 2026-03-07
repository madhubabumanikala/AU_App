from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models.event import Event, EventRegistration
from models.user import Student
from models.notification import Notification
from extensions import db
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__)

@api_bp.route('/events/upcoming')
def upcoming_events():
    """Get upcoming events for mobile app"""
    limit = request.args.get('limit', 10, type=int)
    department = request.args.get('department')
    
    query = Event.query.filter(
        Event.is_active == True,
        Event.date >= datetime.utcnow().date()
    )
    
    if department:
        query = query.filter(Event.department == department)
    
    events = query.order_by(Event.date).limit(limit).all()
    
    return jsonify({
        'success': True,
        'events': [{
            'id': event.id,
            'title': event.title,
            'description': event.description[:200] + '...' if len(event.description) > 200 else event.description,
            'date': event.date.strftime('%Y-%m-%d'),
            'time': event.time.strftime('%H:%M'),
            'location': event.location,
            'department': event.department,
            'category': event.category,
            'max_participants': event.max_participants,
            'registered_count': event.registered_count(),
            'is_full': event.is_full,
            'poster_image': event.poster_image
        } for event in events]
    })

@api_bp.route('/events/<int:event_id>')
def event_details(event_id):
    """Get event details for mobile app"""
    event = Event.query.get_or_404(event_id)
    
    if not event.is_active:
        return jsonify({'success': False, 'error': 'Event not active'}), 404
    
    # Check if current user is registered
    is_registered = False
    if current_user.is_authenticated and isinstance(current_user, Student):
        is_registered = EventRegistration.query.filter_by(
            student_id=current_user.id,
            event_id=event_id
        ).first() is not None
    
    return jsonify({
        'success': True,
        'event': {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'date': event.date.strftime('%Y-%m-%d'),
            'time': event.time.strftime('%H:%M'),
            'location': event.location,
            'department': event.department,
            'category': event.category,
            'max_participants': event.max_participants,
            'registered_count': event.registered_count(),
            'is_full': event.is_full,
            'is_registered': is_registered,
            'poster_image': event.poster_image,
            'average_rating': round(event.average_rating, 1),
            'created_at': event.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@api_bp.route('/events/<int:event_id>/register', methods=['POST'])
@login_required
def register_event_api(event_id):
    """Register for event via API"""
    if isinstance(current_user, Admin):
        return jsonify({'success': False, 'error': 'Admins cannot register for events'}), 403
    
    event = Event.query.get_or_404(event_id)
    
    if not event.is_active:
        return jsonify({'success': False, 'error': 'Event is not active'}), 400
    
    if event.date < datetime.utcnow().date():
        return jsonify({'success': False, 'error': 'Cannot register for past events'}), 400
    
    success, message = event.register_student(current_user.id)
    
    if success:
        # Generate QR code
        from utils.qr_generator import generate_qr_code
        registration = EventRegistration.query.filter_by(
            student_id=current_user.id,
            event_id=event_id
        ).first()
        
        qr_path = generate_qr_code(registration)
        registration.qr_code_path = qr_path
        db.session.commit()
        
        # Create notification
        Notification.create_event_notification(current_user.id, event.title, 'new_event')
        
        return jsonify({
            'success': True,
            'message': message,
            'registration_id': registration.id
        })
    else:
        return jsonify({'success': False, 'error': message}), 400

@api_bp.route('/events/<int:event_id>/unregister', methods=['POST'])
@login_required
def unregister_event_api(event_id):
    """Unregister from event via API"""
    if isinstance(current_user, Admin):
        return jsonify({'success': False, 'error': 'Admins cannot unregister from events'}), 403
    
    event = Event.query.get_or_404(event_id)
    success, message = event.unregister_student(current_user.id)
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message}), 400

@api_bp.route('/student/events')
@login_required
def student_events():
    """Get student's registered events"""
    if isinstance(current_user, Admin):
        return jsonify({'success': False, 'error': 'Admin access not allowed'}), 403
    
    # Get registered events
    registrations = db.session.query(
        EventRegistration, Event
    ).join(Event).filter(
        EventRegistration.student_id == current_user.id
    ).order_by(Event.date.desc()).all()
    
    registered_events = []
    upcoming_events = []
    past_events = []
    
    for registration, event in registrations:
        event_data = {
            'id': event.id,
            'title': event.title,
            'date': event.date.strftime('%Y-%m-%d'),
            'time': event.time.strftime('%H:%M'),
            'location': event.location,
            'department': event.department,
            'category': event.category,
            'attendance_status': registration.attendance_status,
            'registration_date': registration.registration_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if event.date >= datetime.utcnow().date():
            upcoming_events.append(event_data)
        else:
            past_events.append(event_data)
        
        registered_events.append(event_data)
    
    # Get recommended events
    recommended = current_user.get_recommended_events()
    recommended_events = [{
        'id': event.id,
        'title': event.title,
        'date': event.date.strftime('%Y-%m-%d'),
        'time': event.time.strftime('%H:%M'),
        'location': event.location,
        'department': event.department,
        'category': event.category,
        'registered_count': event.registered_count(),
        'is_full': event.is_full
    } for event in recommended]
    
    return jsonify({
        'success': True,
        'registered_events': registered_events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'recommended_events': recommended_events
    })

@api_bp.route('/student/notifications')
@login_required
def student_notifications():
    """Get student notifications"""
    if isinstance(current_user, Admin):
        return jsonify({'success': False, 'error': 'Admin access not allowed'}), 403
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    notifications = current_user.notifications.order_by(
        Notification.created_at.desc()
    ).paginate(page=page, per_page=limit, error_out=False)
    
    return jsonify({
        'success': True,
        'notifications': [{
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.type,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for notification in notifications.items],
        'has_next': notifications.has_next,
        'total': notifications.total
    })

@api_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read_api(notification_id):
    """Mark notification as read via API"""
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.student_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    notification.mark_as_read()
    
    return jsonify({'success': True})

@api_bp.route('/departments')
def departments():
    """Get list of all departments"""
    departments = db.session.query(Event.department).distinct().all()
    
    return jsonify({
        'success': True,
        'departments': [dept[0] for dept in departments]
    })

@api_bp.route('/categories')
def categories():
    """Get list of all event categories"""
    categories = db.session.query(Event.category).distinct().all()
    
    return jsonify({
        'success': True,
        'categories': [cat[0] for cat in categories]
    })

@api_bp.route('/search/events')
def search_events():
    """Search events via API"""
    query = request.args.get('q', '')
    department = request.args.get('department')
    category = request.args.get('category')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    if not query:
        return jsonify({'success': False, 'error': 'Search query required'}), 400
    
    db_query = Event.query.filter(
        Event.is_active == True,
        Event.date >= datetime.utcnow().date(),
        (Event.title.contains(query) | Event.description.contains(query))
    )
    
    if department:
        db_query = db_query.filter(Event.department == department)
    
    if category:
        db_query = db_query.filter(Event.category == category)
    
    events = db_query.order_by(Event.date).paginate(
        page=page, per_page=limit, error_out=False
    )
    
    return jsonify({
        'success': True,
        'events': [{
            'id': event.id,
            'title': event.title,
            'description': event.description[:200] + '...' if len(event.description) > 200 else event.description,
            'date': event.date.strftime('%Y-%m-%d'),
            'time': event.time.strftime('%H:%M'),
            'location': event.location,
            'department': event.department,
            'category': event.category,
            'registered_count': event.registered_count(),
            'is_full': event.is_full,
            'poster_image': event.poster_image
        } for event in events.items],
        'has_next': events.has_next,
        'total': events.total
    })

@api_bp.route('/stats/dashboard')
@login_required
def dashboard_stats():
    """Get dashboard statistics"""
    if isinstance(current_user, Admin):
        # Admin stats
        total_events = Event.query.count()
        active_events = Event.query.filter_by(is_active=True).count()
        total_students = Student.query.count()
        total_registrations = EventRegistration.query.count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_events': total_events,
                'active_events': active_events,
                'total_students': total_students,
                'total_registrations': total_registrations
            }
        })
    else:
        # Student stats
        total_registered = current_user.event_registrations.count()
        upcoming_registered = len(current_user.get_upcoming_events())
        unread_notifications = current_user.notifications.filter_by(is_read=False).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_registered': total_registered,
                'upcoming_registered': upcoming_registered,
                'unread_notifications': unread_notifications
            }
        })
