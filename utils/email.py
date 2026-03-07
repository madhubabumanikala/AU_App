from flask_mail import Message
from flask import current_app, render_template
from extensions import mail
from threading import Thread

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")

def send_email(subject, recipients, html_body, text_body=None):
    """Send email using Flask-Mail"""
    msg = Message(
        subject,
        sender=current_app.config['MAIL_USERNAME'],
        recipients=recipients
    )
    
    if text_body:
        msg.body = text_body
    msg.html = html_body
    
    # Send email asynchronously
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_welcome_email(student):
    """Send welcome email to newly registered student"""
    subject = "Welcome to AU Event Information System"
    
    html_body = render_template(
        'email/welcome.html',
        student=student
    )
    
    text_body = f"""
    Dear {student.full_name},
    
    Welcome to the Andhra University Event Information System!
    
    Your account has been successfully created with the following details:
    - Student ID: {student.student_id}
    - Email: {student.email}
    - Department: {student.department}
    
    You can now:
    - Browse upcoming events
    - Register for events
    - Receive notifications about new events
    - Submit feedback for attended events
    
    Login to your account at: http://localhost:5000/auth/login
    
    Best regards,
    AU Event Management Team
    """
    
    send_email(subject, [student.email], html_body, text_body)

def send_event_notification_email(student, event, notification_type='new_event'):
    """Send event notification email to student"""
    if notification_type == 'new_event':
        subject = f"New Event: {event.title}"
        template = 'email/new_event.html'
    elif notification_type == 'event_reminder':
        subject = f"Event Reminder: {event.title}"
        template = 'email/event_reminder.html'
    elif notification_type == 'event_updated':
        subject = f"Event Updated: {event.title}"
        template = 'email/event_updated.html'
    else:
        subject = f"Event Notification: {event.title}"
        template = 'email/event_notification.html'
    
    html_body = render_template(
        template,
        student=student,
        event=event
    )
    
    text_body = f"""
    Dear {student.full_name},
    
    {subject}
    
    Event Details:
    - Title: {event.title}
    - Date: {event.date.strftime('%Y-%m-%d')}
    - Time: {event.time.strftime('%H:%M')}
    - Location: {event.location}
    - Department: {event.department}
    - Category: {event.category}
    
    {event.description[:200]}{'...' if len(event.description) > 200 else ''}
    
    Visit the event portal for more details and to register: http://localhost:5000/events/{event.id}
    
    Best regards,
    AU Event Management Team
    """
    
    send_email(subject, [student.email], html_body, text_body)

def send_event_cancellation_email(student, event):
    """Send event cancellation notification"""
    subject = f"Event Cancelled: {event.title}"
    
    html_body = render_template(
        'email/event_cancelled.html',
        student=student,
        event=event
    )
    
    text_body = f"""
    Dear {student.full_name},
    
    We regret to inform you that the following event has been cancelled:
    
    Event Details:
    - Title: {event.title}
    - Scheduled Date: {event.date.strftime('%Y-%m-%d')}
    - Scheduled Time: {event.time.strftime('%H:%M')}
    - Location: {event.location}
    
    We apologize for any inconvenience caused. Please check the portal for other upcoming events.
    
    Best regards,
    AU Event Management Team
    """
    
    send_email(subject, [student.email], html_body, text_body)

def send_registration_confirmation_email(student, event):
    """Send registration confirmation email"""
    subject = f"Registration Confirmed: {event.title}"
    
    html_body = render_template(
        'email/registration_confirmed.html',
        student=student,
        event=event
    )
    
    text_body = f"""
    Dear {student.full_name},
    
    Your registration for the following event has been confirmed:
    
    Event Details:
    - Title: {event.title}
    - Date: {event.date.strftime('%Y-%m-%d')}
    - Time: {event.time.strftime('%H:%M')}
    - Location: {event.location}
    - Department: {event.department}
    
    Please arrive at the venue 15 minutes before the event start time.
    Don't forget to bring your QR code for attendance tracking.
    
    Best regards,
    AU Event Management Team
    """
    
    send_email(subject, [student.email], html_body, text_body)

def send_password_reset_email(user, reset_token):
    """Send password reset email"""
    subject = "Password Reset Request - AU Event System"
    
    html_body = render_template(
        'email/password_reset.html',
        user=user,
        reset_token=reset_token
    )
    
    text_body = f"""
    Dear {user.full_name},
    
    You have requested to reset your password for the AU Event Information System.
    
    Click the following link to reset your password:
    http://localhost:5000/auth/reset_password/{reset_token}
    
    This link will expire in 1 hour.
    
    If you did not request this password reset, please ignore this email.
    
    Best regards,
    AU Event Management Team
    """
    
    send_email(subject, [user.email], html_body, text_body)
