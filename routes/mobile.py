from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required, LoginManager
from models.event import Event, EventRegistration, EventFeedback
from models.user import Student, Admin
from models.notification import Notification
from extensions import db
from datetime import datetime, timedelta
from utils.qr_generator import generate_qr_code
import calendar

mobile_bp = Blueprint('mobile', __name__)

@mobile_bp.route('/')
def index():
    """Mobile app home page"""
    if current_user.is_authenticated:
        return redirect('/mobile/dashboard')
    else:
        return redirect('/mobile/login')

@mobile_bp.route('/home')
def home():
    """Mobile app home page (alternative)"""
    if current_user.is_authenticated:
        return redirect('/mobile/dashboard')
    else:
        return render_template('mobile_login.html')

@mobile_bp.route('/login')
def login():
    """Mobile login page"""
    return render_template('mobile_login.html')

@mobile_bp.route('/dashboard')
@login_required
def dashboard():
    """Mobile dashboard"""
    try:
        if isinstance(current_user, Admin):
            return redirect('/admin/dashboard')
        
        # Get student's registered events
        registered_events = current_user.get_upcoming_events()
        
        # Get recommended events
        recommended_events = current_user.get_recommended_events()
        
        # Get unread notifications
        unread_notifications = current_user.notifications.filter_by(is_read=False).order_by(
            Notification.created_at.desc()
        ).limit(5).all()
        
        # Get recent events
        recent_events = Event.query.filter(
            Event.date >= datetime.utcnow().date(),
            Event.is_active == True
        ).order_by(Event.date).limit(10).all()
        
        return render_template('mobile_dashboard.html',
                         registered_events=registered_events,
                         recommended_events=recommended_events,
                         notifications=unread_notifications,
                         upcoming_events=recent_events)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect('/mobile/dashboard')

@mobile_bp.route('/events')
def events():
    """Mobile events listing"""
    try:
        page = request.args.get('page', 1, type=int)
        department = request.args.get('department')
        category = request.args.get('category')
        search = request.args.get('search')
        
        query = Event.query.filter(Event.is_active == True, Event.date >= datetime.utcnow().date())
        
        if department:
            query = query.filter(Event.department == department)
        
        if category:
            query = query.filter(Event.category == category)
        
        if search:
            query = query.filter(Event.title.contains(search) | Event.description.contains(search))
        
        events = query.order_by(Event.date).paginate(
            page=page, per_page=10, error_out=False
        )
        
        # Get all departments and categories for filters
        departments = db.session.query(Event.department).distinct().all()
        categories = db.session.query(Event.category).distinct().all()
        
        return render_template('mobile_events.html', 
                             events=events,
                             page=page,
                             pages=events.pages,
                             has_prev=events.has_prev,
                             has_next=events.has_next,
                             prev_num=events.prev_num,
                             next_num=events.next_num,
                             departments=[d[0] for d in departments],
                             categories=[c[0] for c in categories],
                             current_department=department,
                             current_category=category,
                             current_search=search)
    except Exception as e:
        flash(f'Error loading events: {str(e)}', 'error')
        return redirect(url_for('mobile.dashboard'))

@mobile_bp.route('/events/<int:event_id>')
def event_details(event_id):
    """Mobile event details"""
    try:
        event = Event.query.get_or_404(event_id)
        
        if not event.is_active:
            return jsonify({'error': 'Event not found'}), 404
        
        # Check if current student is registered
        is_registered = False
        registration = None
        
        if current_user.is_authenticated and isinstance(current_user, Student):
            registration = EventRegistration.query.filter_by(
                student_id=current_user.id,
                event_id=event_id
            ).first()
            is_registered = registration is not None
        
        # Return JSON for mobile app
        return jsonify({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'date': event.date.isoformat(),
            'time': event.time.strftime('%I:%M %p') if event.time else None,
            'location': event.location,
            'department': event.department,
            'category': event.category,
            'max_participants': event.max_participants,
            'is_registered': is_registered
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mobile_bp.route('/events/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    """Mobile event registration"""
    try:
        if isinstance(current_user, Admin):
            return jsonify({'error': 'Admins cannot register for events'}), 403
        
        event = Event.query.get_or_404(event_id)
        
        if not event.is_active:
            return jsonify({'error': 'Event not found'}), 404
        
        if event.date < datetime.utcnow().date():
            return jsonify({'error': 'Cannot register for past events'}), 400
        
        success, message = event.register_student(current_user.id)
        
        if success:
            # Generate QR code for registration
            registration = EventRegistration.query.filter_by(
                student_id=current_user.id,
                event_id=event_id
            ).first()
            
            qr_path = generate_qr_code(registration)
            registration.qr_code_path = qr_path
            db.session.commit()
            
            # Create notification
            Notification.create_event_notification(current_user.id, event.title, 'new_event')
            
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@mobile_bp.route('/my-events')
@login_required
def my_events():
    """Mobile my events"""
    try:
        if isinstance(current_user, Admin):
            return redirect(url_for('admin.events'))
        
        page = request.args.get('page', 1, type=int)
        status = request.args.get('status', 'upcoming')
        
        query = current_user.event_registrations.join(Event)
        
        if status == 'upcoming':
            query = query.filter(Event.date >= datetime.utcnow().date())
        elif status == 'past':
            query = query.filter(Event.date < datetime.utcnow().date())
        
        registrations = query.order_by(Event.date.desc()).paginate(
            page=page, per_page=10, error_out=False
        )
        
        # Convert to mobile-friendly format
        events_data = []
        for reg in registrations.items:
            events_data.append({
                'id': reg.event.id,
                'title': reg.event.title,
                'date': reg.event.date.strftime('%d %b %Y'),
                'time': reg.event.time.strftime('%I:%M %p') if reg.event.time else 'All Day',
                'location': reg.event.location,
                'category': reg.event.category,
                'status': 'Upcoming' if reg.event.date >= datetime.utcnow().date() else 'Past'
            })
        
        return jsonify({
            'events': events_data,
            'page': page,
            'pages': registrations.pages,
            'has_prev': registrations.has_prev,
            'has_next': registrations.has_next,
            'current_status': status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mobile_bp.route('/calendar')
@login_required
def calendar_view():
    """Mobile calendar view"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        # Get events for specified month
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month + 1, 1).date()
        
        events = Event.query.filter(
            Event.date >= start_date,
            Event.date < end_date,
            Event.is_active == True
        ).all()
        
        # Create calendar data
        cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]
        
        return jsonify({
            'calendar_data': cal,
            'month_name': month_name,
            'year': year,
            'month': month,
            'events': [
                {
                    'id': event.id,
                    'title': event.title,
                    'date': event.day,
                    'time': event.time.strftime('%I:%M %p') if event.time else None
                }
                for event in events
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mobile_bp.route('/notifications')
@login_required
def notifications():
    """Mobile notifications"""
    try:
        if isinstance(current_user, Admin):
            return jsonify({'error': 'Admins do not have notifications'}), 403
        
        page = request.args.get('page', 1, type=int)
        notifications = current_user.notifications.order_by(
            Notification.created_at.desc()
        ).paginate(page=page, per_page=20, error_out=False)
        
        # Convert to mobile-friendly format
        notifications_data = []
        for notification in notifications.items:
            notifications_data.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'created_at': notification.created_at.strftime('%d %b %Y, %I:%M %p'),
                'is_read': notification.is_read
            })
        
        return jsonify({
            'notifications': notifications_data,
            'page': page,
            'pages': notifications.pages,
            'has_prev': notifications.has_prev,
            'has_next': notifications.has_next
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mobile_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mobile mark notification as read"""
    try:
        notification = Notification.query.get_or_404(notification_id)
        
        if notification.student_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        notification.mark_as_read()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
