from datetime import datetime

# Import db from extensions to avoid circular imports
from extensions import db

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='info')  # info, warning, success, error
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @classmethod
    def create_event_notification(cls, student_id, event_title, message_type='new_event'):
        if message_type == 'new_event':
            title = "New Event Posted"
            message = f"A new event '{event_title}' has been posted. Check it out!"
        elif message_type == 'event_reminder':
            title = "Event Reminder"
            message = f"Reminder: Event '{event_title}' is coming up soon!"
        elif message_type == 'event_updated':
            title = "Event Updated"
            message = f"The event '{event_title}' has been updated. Please check the details."
        else:
            title = "Event Notification"
            message = f"Update regarding event '{event_title}'"
        
        notification = cls(
            student_id=student_id,
            title=title,
            message=message,
            type='info'
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    @classmethod
    def create_bulk_event_notification(cls, event_title, department=None, student_ids=None):
        notifications = []
        
        if student_ids:
            # Send to specific students
            for student_id in student_ids:
                notification = cls.create_event_notification(student_id, event_title, 'new_event')
                notifications.append(notification)
        elif department:
            # Send to all students in a department
            from .user import Student
            students = Student.query.filter_by(department=department).all()
            for student in students:
                notification = cls.create_event_notification(student.id, event_title, 'new_event')
                notifications.append(notification)
        
        return notifications
    
    def mark_as_read(self):
        self.is_read = True
        db.session.commit()
    
    def __repr__(self):
        return f'<Notification {self.title}>'
