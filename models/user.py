from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Import db from extensions to avoid circular imports
from extensions import db

class User(UserMixin, db.Model):
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Student(User):
    __tablename__ = 'students'
    
    student_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.String(15))
    
    # Relationships
    event_registrations = db.relationship('EventRegistration', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    feedbacks = db.relationship('EventFeedback', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_upcoming_events(self):
        from .event import Event, EventRegistration
        return Event.query.join(EventRegistration).filter(
            EventRegistration.student_id == self.id,
            Event.date >= datetime.utcnow().date()
        ).all()
    
    def get_recommended_events(self, limit=5):
        from .event import Event
        # Simple recommendation based on department
        return Event.query.filter(
            Event.department == self.department,
            Event.date >= datetime.utcnow().date(),
            ~Event.registrations.any(student_id=self.id)
        ).order_by(Event.date).limit(limit).all()
    
    def __repr__(self):
        return f'<Student {self.student_id}>'

class Admin(User):
    __tablename__ = 'admins'
    
    username = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), default='admin')  # admin, super_admin
    department = db.Column(db.String(100))
    
    # Relationships
    created_events = db.relationship('Event', backref='creator', lazy='dynamic')
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Admin {self.username}>'
