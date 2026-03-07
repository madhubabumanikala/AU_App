from datetime import datetime

# Import db from extensions to avoid circular imports
from extensions import db

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)  # technical, cultural, workshop, seminar
    max_participants = db.Column(db.Integer)
    poster_image = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    registrations = db.relationship('EventRegistration', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    feedbacks = db.relationship('EventFeedback', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def registered_count(self):
        return self.registrations.count()
    
    @property
    def available_slots(self):
        if self.max_participants is None:
            return None
        return self.max_participants - self.registered_count()
    
    @property
    def is_full(self):
        if self.max_participants is None:
            return False
        return self.registered_count() >= self.max_participants
    
    @property
    def is_upcoming(self):
        return self.date >= datetime.utcnow().date()
    
    @property
    def average_rating(self):
        feedbacks = self.feedbacks.filter(EventFeedback.rating.isnot(None)).all()
        if not feedbacks:
            return 0
        return sum(feedback.rating for feedback in feedbacks) / len(feedbacks)
    
    def register_student(self, student_id):
        if self.is_full:
            return False, "Event is full"
        
        existing_registration = self.registrations.filter_by(student_id=student_id).first()
        if existing_registration:
            return False, "Already registered"
        
        registration = EventRegistration(student_id=student_id, event_id=self.id)
        db.session.add(registration)
        db.session.commit()
        return True, "Registration successful"
    
    def unregister_student(self, student_id):
        registration = self.registrations.filter_by(student_id=student_id).first()
        if registration:
            db.session.delete(registration)
            db.session.commit()
            return True, "Unregistration successful"
        return False, "Not registered"
    
    def get_attendees(self):
        return self.registrations.filter_by(attendance_status=True).all()
    
    def __repr__(self):
        return f'<Event {self.title}>'

class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    attendance_status = db.Column(db.Boolean, default=False)
    qr_code_path = db.Column(db.String(255))
    
    # Unique constraint to prevent duplicate registrations
    __table_args__ = (db.UniqueConstraint('student_id', 'event_id', name='unique_student_event_registration'),)
    
    def __repr__(self):
        return f'<EventRegistration Student:{self.student_id} Event:{self.event_id}>'

class EventFeedback(db.Model):
    __tablename__ = 'event_feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    rating = db.Column(db.Integer)  # 1-5 stars
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate feedbacks
    __table_args__ = (db.UniqueConstraint('student_id', 'event_id', name='unique_student_event_feedback'),)
    
    def __repr__(self):
        return f'<EventFeedback Student:{self.student_id} Event:{self.event_id} Rating:{self.rating}>'
