from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.event import Event, EventRegistration, EventFeedback
from models.user import Student, Admin
from models.notification import Notification
from extensions import db
from datetime import datetime, timedelta
from utils.qr_generator import generate_qr_code
from utils.mobile_detector import MobileDetector, mobile_template
import calendar

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Show upcoming events to non-logged-in users
    upcoming_events = Event.query.filter(
        Event.date >= datetime.utcnow().date(),
        Event.is_active == True
    ).order_by(Event.date).limit(6).all()
    
    return render_template('index.html', events=upcoming_events)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if isinstance(current_user, Admin):
        return redirect(url_for('admin.dashboard'))
    
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
    
    return render_template(mobile_template('main/dashboard_complete.html'),
                         registered_events=registered_events,
                         recommended_events=recommended_events,
                         notifications=unread_notifications,
                         upcoming_events=recent_events)

@main_bp.route('/events')
def events():
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
    
    return render_template(mobile_template('main/events_filtered.html'), 
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
                         current_search=search,
                         current_date=datetime.utcnow().date())

@main_bp.route('/events/<int:event_id>')
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    
    if not event.is_active:
        flash('This event is no longer active', 'error')
        return redirect(url_for('main.events'))
    
    # Check if current student is registered
    is_registered = False
    registration = None
    
    if current_user.is_authenticated and isinstance(current_user, Student):
        registration = EventRegistration.query.filter_by(
            student_id=current_user.id,
            event_id=event_id
        ).first()
        is_registered = registration is not None
    
    # Get event feedbacks
    feedbacks = event.feedbacks.order_by(EventFeedback.created_at.desc()).limit(10).all()
    
    return render_template('main/event_details.html',
                         event=event,
                         is_registered=is_registered,
                         registration=registration,
                         feedbacks=feedbacks)

@main_bp.route('/events/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    if isinstance(current_user, Admin):
        flash('Admins cannot register for events', 'error')
        return redirect(url_for('main.event_details', event_id=event_id))
    
    event = Event.query.get_or_404(event_id)
    
    if not event.is_active:
        flash('This event is no longer active', 'error')
        return redirect(url_for('main.event_details', event_id=event_id))
    
    if event.date < datetime.utcnow().date():
        flash('Cannot register for past events', 'error')
        return redirect(url_for('main.event_details', event_id=event_id))
    
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
        
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('main.event_details', event_id=event_id))

@main_bp.route('/events/<int:event_id>/unregister', methods=['POST'])
@login_required
def unregister_event(event_id):
    if isinstance(current_user, Admin):
        flash('Admins cannot unregister from events', 'error')
        return redirect(url_for('main.event_details', event_id=event_id))
    
    event = Event.query.get_or_404(event_id)
    
    success, message = event.unregister_student(current_user.id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('main.event_details', event_id=event_id))

@main_bp.route('/my-events')
@login_required
def my_events():
    if isinstance(current_user, Admin):
        return redirect(url_for('admin.events'))
    
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'upcoming')  # upcoming, past, all
    
    query = EventRegistration.query.filter_by(student_id=current_user.id).join(Event)
    
    if status == 'upcoming':
        query = query.filter(Event.date >= datetime.utcnow().date())
    elif status == 'past':
        query = query.filter(Event.date < datetime.utcnow().date())
    
    registrations = query.order_by(Event.date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('main/my_events.html',
                         registrations=registrations,
                         current_status=status)

@main_bp.route('/calendar')
@login_required
def calendar_view():
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # Get events for the specified month
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
    
    # Get user's personal tasks for the month
    from models.task import Task
    tasks = Task.query.filter(
        Task.date >= start_date,
        Task.date < end_date,
        Task.user_id == current_user.id,
        Task.user_type == current_user.__class__.__name__.lower(),
        Task.is_active == True
    ).all()
    
    # Create calendar data - set first day of week to Sunday (6)
    calendar.setfirstweekday(calendar.SUNDAY)
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    return render_template('main/calendar.html',
                         calendar_data=cal,
                         month_name=month_name,
                         year=year,
                         month=month,
                         events=events,
                         tasks=tasks)

@main_bp.route('/notifications')
@login_required
def notifications():
    if isinstance(current_user, Admin):
        flash('Admins do not have notifications', 'info')
        return redirect(url_for('admin.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    notifications = current_user.notifications.order_by(
        Notification.created_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('main/notifications.html', notifications=notifications)

@main_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification.mark_as_read()
    return jsonify({'success': True})

@main_bp.route('/notifications/<int:notification_id>/mark_all_read', methods=['POST'])
@login_required
def mark_all_read():
    if isinstance(current_user, Admin):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Mark all notifications as read
    current_user.notifications.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    
    return jsonify({'success': True})

@main_bp.route('/feedback/<int:event_id>', methods=['GET', 'POST'])
@login_required
def submit_feedback(event_id):
    if isinstance(current_user, Admin):
        flash('Admins cannot submit feedback', 'error')
        return redirect(url_for('main.event_details', event_id=event_id))
    
    event = Event.query.get_or_404(event_id)
    
    # Check if student attended the event
    registration = EventRegistration.query.filter_by(
        student_id=current_user.id,
        event_id=event_id
    ).first()
    
    if not registration:
        flash('You must be registered for this event to submit feedback', 'error')
        return redirect(url_for('main.event_details', event_id=event_id))
    
    # Check if feedback already exists
    existing_feedback = EventFeedback.query.filter_by(
        student_id=current_user.id,
        event_id=event_id
    ).first()
    
    if existing_feedback:
        flash('You have already submitted feedback for this event', 'info')
        return redirect(url_for('main.event_details', event_id=event_id))
    
    from utils.forms import FeedbackForm
    form = FeedbackForm()
    
    if form.validate_on_submit():
        feedback = EventFeedback(
            student_id=current_user.id,
            event_id=event_id,
            rating=form.rating.data,
            comments=form.comments.data
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('main.event_details', event_id=event_id))
    
    return render_template('main/event_details.html', event=event, form=form)
