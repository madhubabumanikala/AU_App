"""
Personal Task Model for Calendar
"""
from datetime import datetime
from extensions import db

class Task(db.Model):
    """Personal task/reminder model for users"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False, index=True)
    time = db.Column(db.Time, nullable=True)
    
    # User information (polymorphic - can be student or admin)
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # student, admin
    
    # Task properties
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    status = db.Column(db.String(20), default='pending')   # pending, completed, cancelled
    color = db.Column(db.String(7), default='#007bff')     # Hex color for display
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    @property
    def user(self):
        """Get the task owner based on user_type"""
        if self.user_type == 'student':
            from models.user import Student
            return Student.query.get(self.user_id)
        elif self.user_type == 'admin':
            from models.user import Admin
            return Admin.query.get(self.user_id)
        return None
    
    @property
    def is_completed(self):
        """Check if task is completed"""
        return self.status == 'completed'
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.status == 'completed':
            return False
        
        task_datetime = datetime.combine(self.date, self.time or datetime.min.time())
        return task_datetime < datetime.now()
    
    @property
    def priority_color(self):
        """Get color based on priority"""
        colors = {
            'low': '#28a745',      # Green
            'medium': '#ffc107',   # Yellow
            'high': '#dc3545'      # Red
        }
        return colors.get(self.priority, '#007bff')
    
    @property
    def display_time(self):
        """Get formatted time for display"""
        if self.time:
            return self.time.strftime('%I:%M %p')
        return 'All Day'
    
    def mark_completed(self):
        """Mark task as completed"""
        self.status = 'completed'
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def mark_pending(self):
        """Mark task as pending"""
        self.status = 'pending'
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def can_edit(self, user):
        """Check if user can edit this task"""
        if not user or not user.is_authenticated:
            return False
        return (user.id == self.user_id and 
                user.__class__.__name__.lower() == self.user_type)
    
    def to_dict(self):
        """Convert task to dictionary for JSON responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date': self.date.isoformat(),
            'time': self.time.isoformat() if self.time else None,
            'display_time': self.display_time,
            'priority': self.priority,
            'status': self.status,
            'color': self.color or self.priority_color,
            'is_completed': self.is_completed,
            'is_overdue': self.is_overdue,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Task {self.id}: {self.title} on {self.date}>'
