from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models.event import Event, EventRegistration, EventFeedback
from models.user import Student, Admin
from models.notification import Notification
from extensions import db
from datetime import datetime, timedelta
from utils.forms import EventForm, AdminRegistrationForm
from utils.email import send_event_notification_email
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            flash('Admin access required', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get statistics
    total_events = Event.query.count()
    active_events = Event.query.filter_by(is_active=True).count()
    total_students = Student.query.count()
    total_registrations = EventRegistration.query.count()
    
    # Recent events
    recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()
    
    # Upcoming events
    upcoming_events = Event.query.filter(
        Event.date >= datetime.utcnow().date(),
        Event.is_active == True
    ).order_by(Event.date).limit(5).all()
    
    # Recent registrations
    recent_registrations = EventRegistration.query.order_by(
        EventRegistration.registration_date.desc()
    ).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_events=total_events,
                         active_events=active_events,
                         total_students=total_students,
                         total_registrations=total_registrations,
                         recent_events=recent_events,
                         upcoming_events=upcoming_events,
                         recent_registrations=recent_registrations)

@admin_bp.route('/events')
@login_required
@admin_required
def events():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')  # all, active, inactive, past, upcoming
    
    query = Event.query
    
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    elif status == 'past':
        query = query.filter(Event.date < datetime.utcnow().date())
    elif status == 'upcoming':
        query = query.filter(Event.date >= datetime.utcnow().date())
    
    events = query.order_by(Event.date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/events.html',
                         events=events,
                         current_status=status)

@admin_bp.route('/events/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    form = EventForm()
    
    print(f"DEBUG: Form method: {request.method}")
    print(f"DEBUG: Form data: {request.form}")
    print(f"DEBUG: Form files: {request.files}")
    
    if form.validate_on_submit():
        print("DEBUG: Form validation passed")
        # Handle poster upload
        poster_filename = None
        if form.poster_image.data:
            filename = secure_filename(form.poster_image.data.filename)
            poster_filename = f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            poster_path = os.path.join(current_app.config['UPLOAD_FOLDER'], poster_filename)
            form.poster_image.data.save(poster_path)
        
        # Create event
        event = Event(
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
            time=form.time.data,
            location=form.location.data,
            department=form.department.data,
            category=form.category.data,
            max_participants=form.max_participants.data,
            poster_image=poster_filename,
            created_by=current_user.id
        )
        
        db.session.add(event)
        db.session.commit()
        
        # Send notifications to relevant students
        try:
            if form.notify_students.data:
                Notification.create_bulk_event_notification(
                    event.title,
                    department=event.department
                )
                flash('Event created and notifications sent!', 'success')
            else:
                flash('Event created successfully!', 'success')
        except Exception as e:
            flash('Event created but notifications failed to send', 'warning')
        
        return redirect(url_for('admin.events'))
    else:
        print(f"DEBUG: Form validation failed: {form.errors}")
        if request.method == 'POST':
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"DEBUG: {field.name} error: {error}")
        return render_template('admin/create_event.html', form=form)

@admin_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    
    if form.validate_on_submit():
        # Handle poster upload
        if form.poster_image.data:
            # Delete old poster if exists
            if event.poster_image:
                old_poster_path = os.path.join(current_app.config['UPLOAD_FOLDER'], event.poster_image)
                if os.path.exists(old_poster_path):
                    os.remove(old_poster_path)
            
            filename = secure_filename(form.poster_image.data.filename)
            poster_filename = f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            poster_path = os.path.join(current_app.config['UPLOAD_FOLDER'], poster_filename)
            form.poster_image.data.save(poster_path)
            event.poster_image = poster_filename
        
        # Update event
        event.title = form.title.data
        event.description = form.description.data
        event.date = form.date.data
        event.time = form.time.data
        event.location = form.location.data
        event.department = form.department.data
        event.category = form.category.data
        event.max_participants = form.max_participants.data
        event.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Notify registered students about the update
        if form.notify_update.data:
            registrations = event.registrations.all()
            for registration in registrations:
                Notification.create_event_notification(
                    registration.student_id,
                    event.title,
                    'event_updated'
                )
        
        flash('Event updated successfully!', 'success')
        return redirect(url_for('admin.event_details', event_id=event_id))
    
    return render_template('admin/edit_event.html', form=form, event=event)

@admin_bp.route('/events/<int:event_id>')
@login_required
@admin_required
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Get registrations with student details
    registrations = db.session.query(
        EventRegistration, Student
    ).join(Student).filter(
        EventRegistration.event_id == event_id
    ).order_by(EventRegistration.registration_date.desc()).all()
    
    # Get feedbacks
    feedbacks = event.feedbacks.order_by(EventFeedback.created_at.desc()).all()
    
    return render_template('admin/event_details.html',
                         event=event,
                         registrations=registrations,
                         feedbacks=feedbacks)

@admin_bp.route('/events/<int:event_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_event_status(event_id):
    event = Event.query.get_or_404(event_id)
    
    event.is_active = not event.is_active
    db.session.commit()
    
    status = 'activated' if event.is_active else 'deactivated'
    flash(f'Event {status} successfully!', 'success')
    
    return redirect(url_for('admin.event_details', event_id=event_id))

@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Delete poster if exists
    if event.poster_image:
        poster_path = os.path.join(current_app.config['UPLOAD_FOLDER'], event.poster_image)
        if os.path.exists(poster_path):
            os.remove(poster_path)
    
    db.session.delete(event)
    db.session.commit()
    
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('admin.events'))

@admin_bp.route('/students')
@login_required
@admin_required
def students():
    page = request.args.get('page', 1, type=int)
    department = request.args.get('department')
    search = request.args.get('search')
    
    query = Student.query
    
    if department:
        query = query.filter(Student.department == department)
    
    if search:
        query = query.filter(
            (Student.first_name.contains(search) | 
             Student.last_name.contains(search) |
             Student.student_id.contains(search) |
             Student.email.contains(search))
        )
    
    students = query.order_by(Student.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get all departments for filter
    departments = db.session.query(Student.department).distinct().all()
    
    return render_template('admin/students.html',
                         students=students,
                         departments=[d[0] for d in departments],
                         current_department=department,
                         current_search=search)

@admin_bp.route('/students/<int:student_id>')
@login_required
@admin_required
def student_details(student_id):
    student = Student.query.get_or_404(student_id)
    
    # Get student's event registrations
    registrations = db.session.query(
        EventRegistration, Event
    ).join(Event).filter(
        EventRegistration.student_id == student_id
    ).order_by(Event.date.desc()).all()
    
    # Get student's feedbacks
    feedbacks = student.feedbacks.order_by(EventFeedback.created_at.desc()).all()
    
    return render_template('admin/student_details.html',
                         student=student,
                         registrations=registrations,
                         feedbacks=feedbacks)

@admin_bp.route('/attendance/<int:event_id>')
@login_required
@admin_required
def attendance(event_id):
    event = Event.query.get_or_404(event_id)
    
    registrations = db.session.query(
        EventRegistration, Student
    ).join(Student).filter(
        EventRegistration.event_id == event_id
    ).order_by(Student.first_name, Student.last_name).all()
    
    return render_template('admin/attendance.html',
                         event=event,
                         registrations=registrations)

@admin_bp.route('/attendance/<int:event_id>/mark', methods=['POST'])
@login_required
@admin_required
def mark_attendance(event_id):
    event = Event.query.get_or_404(event_id)
    registration_id = request.form.get('registration_id')
    attendance_status = request.form.get('attendance_status') == 'true'
    
    registration = EventRegistration.query.get_or_404(registration_id)
    
    if registration.event_id != event_id:
        return jsonify({'error': 'Invalid registration'}), 400
    
    registration.attendance_status = attendance_status
    db.session.commit()
    
    return jsonify({'success': True})

@admin_bp.route('/stats')
@login_required
@admin_required
def stats():
    # Event statistics
    total_events = Event.query.count()
    active_events = Event.query.filter_by(is_active=True).count()
    past_events = Event.query.filter(Event.date < datetime.utcnow().date()).count()
    
    # Student statistics
    total_students = Student.query.count()
    active_students = Student.query.filter_by(is_active=True).count()
    
    # Registration statistics
    total_registrations = EventRegistration.query.count()
    this_month_registrations = EventRegistration.query.filter(
        EventRegistration.registration_date >= datetime.utcnow().replace(day=1)
    ).count()
    
    # Department-wise statistics
    dept_stats = db.session.query(
        Student.department,
        db.func.count(Student.id).label('student_count')
    ).group_by(Student.department).all()
    
    # Event category statistics
    category_stats = db.session.query(
        Event.category,
        db.func.count(Event.id).label('event_count')
    ).filter(Event.is_active == True).group_by(Event.category).all()
    
    # Most popular events
    popular_events = db.session.query(
        Event.title,
        db.func.count(EventRegistration.id).label('registration_count')
    ).join(EventRegistration).group_by(Event.id).order_by(
        db.func.count(EventRegistration.id).desc()
    ).limit(5).all()
    
    return render_template('admin/stats.html',
                         total_events=total_events,
                         active_events=active_events,
                         past_events=past_events,
                         total_students=total_students,
                         active_students=active_students,
                         total_registrations=total_registrations,
                         this_month_registrations=this_month_registrations,
                         dept_stats=dept_stats,
                         category_stats=category_stats,
                         popular_events=popular_events)

@admin_bp.route('/register', methods=['GET', 'POST'])
@login_required
@admin_required
def register_admin():
    # Only super_admin can register new admins
    if current_user.role != 'super_admin':
        flash('Only super admin can register new admins', 'error')
        return redirect(url_for('admin.dashboard'))
    
    form = AdminRegistrationForm()
    
    if form.validate_on_submit():
        # Check if email already exists
        if Admin.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'error')
            return render_template('admin/register.html', form=form)
        
        # Check if username already exists
        if Admin.query.filter_by(username=form.username.data).first():
            flash('Username already taken', 'error')
            return render_template('admin/register.html', form=form)
        
        # Create new admin
        admin = Admin(
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            role=form.role.data,
            department=form.department.data
        )
        admin.set_password(form.password.data)
        
        db.session.add(admin)
        db.session.commit()
        
        flash(f'Admin {admin.username} registered successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/register.html', form=form)
