from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.event import Event, EventRegistration, EventFeedback
from models.user import Student
from extensions import db
from datetime import datetime
from utils.forms import EventForm
import os

events_bp = Blueprint('events', __name__)

@events_bp.route('/')
def index():
    return redirect(url_for('main.events'))

@events_bp.route('/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if not query:
        return redirect(url_for('main.events'))
    
    events = Event.query.filter(
        Event.is_active == True,
        Event.date >= datetime.utcnow().date(),
        (Event.title.contains(query) | Event.description.contains(query))
    ).order_by(Event.date).paginate(page=page, per_page=10, error_out=False)
    
    return render_template('events/search_results.html',
                         events=events,
                         query=query)

@events_bp.route('/api/upcoming')
def api_upcoming():
    """API endpoint to get upcoming events for AJAX calls"""
    limit = request.args.get('limit', 5, type=int)
    
    events = Event.query.filter(
        Event.is_active == True,
        Event.date >= datetime.utcnow().date()
    ).order_by(Event.date).limit(limit).all()
    
    event_data = []
    for event in events:
        event_data.append({
            'id': event.id,
            'title': event.title,
            'date': event.date.strftime('%Y-%m-%d'),
            'time': event.time.strftime('%H:%M'),
            'location': event.location,
            'department': event.department,
            'category': event.category,
            'registered_count': event.registered_count(),
            'max_participants': event.max_participants
        })
    
    return jsonify({'events': event_data})

@events_bp.route('/api/calendar/<int:year>/<int:month>')
def api_calendar_events(year, month):
    """API endpoint to get events for calendar view"""
    from datetime import date
    
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    events = Event.query.filter(
        Event.date >= start_date,
        Event.date < end_date,
        Event.is_active == True
    ).all()
    
    calendar_data = []
    for event in events:
        calendar_data.append({
            'id': event.id,
            'title': event.title,
            'date': event.date.strftime('%Y-%m-%d'),
            'time': event.time.strftime('%H:%M'),
            'location': event.location,
            'category': event.category,
            'url': url_for('main.event_details', event_id=event.id)
        })
    
    return jsonify({'events': calendar_data})

@events_bp.route('/download/<int:event_id>/qr/<int:registration_id>')
@login_required
def download_qr(event_id, registration_id):
    """Download QR code for event registration"""
    if isinstance(current_user, Admin):
        flash('Admins cannot download student QR codes', 'error')
        return redirect(url_for('main.event_details', event_id=event_id))
    
    registration = EventRegistration.query.get_or_404(registration_id)
    
    if registration.student_id != current_user.id or registration.event_id != event_id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('main.event_details', event_id=event_id))
    
    if not registration.qr_code_path:
        flash('QR code not available', 'error')
        return redirect(url_for('main.event_details', event_id=event_id))
    
    return redirect(url_for('static', filename=registration.qr_code_path.replace('static/', '')))

@events_bp.route('/stats')
@login_required
def event_stats():
    """Show event statistics"""
    if isinstance(current_user, Admin):
        return redirect(url_for('admin.stats'))
    
    # Student statistics
    total_registered = current_user.event_registrations.count()
    upcoming_registered = current_user.get_upcoming_events().__len__()
    
    # Department-wise event counts
    dept_events = db.session.query(
        Event.department,
        db.func.count(Event.id).label('count')
    ).filter(
        Event.date >= datetime.utcnow().date(),
        Event.is_active == True
    ).group_by(Event.department).all()
    
    # Category-wise event counts
    category_events = db.session.query(
        Event.category,
        db.func.count(Event.id).label('count')
    ).filter(
        Event.date >= datetime.utcnow().date(),
        Event.is_active == True
    ).group_by(Event.category).all()
    
    return render_template('events/stats.html',
                         total_registered=total_registered,
                         upcoming_registered=upcoming_registered,
                         dept_events=dept_events,
                         category_events=category_events)

@events_bp.route('/export/ical/<int:event_id>')
def export_ical(event_id):
    """Export event as iCal file"""
    event = Event.query.get_or_404(event_id)
    
    if not event.is_active:
        flash('Event not available', 'error')
        return redirect(url_for('main.event_details', event_id=event_id))
    
    # Create iCal content
    ical_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AU Event System//AU Event Calendar//EN
BEGIN:VEVENT
UID:{event.id}@au-event-system.com
DTSTART:{event.date.strftime('%Y%m%d')}T{event.time.strftime('%H%M%S')}
DTEND:{event.date.strftime('%Y%m%d')}T{(datetime.combine(event.date, event.time) + timedelta(hours=2)).strftime('%H%M%S')}
SUMMARY:{event.title}
DESCRIPTION:{event.description.replace('\\n', '\\n')}
LOCATION:{event.location}
END:VEVENT
END:VCALENDAR"""
    
    from flask import Response
    response = Response(ical_content, mimetype='text/calendar')
    response.headers['Content-Disposition'] = f'attachment; filename={event.title.replace(" ", "_")}.ics'
    
    return response
