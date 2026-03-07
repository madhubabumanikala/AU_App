"""
Social Media Models for AU Event System
"""
from extensions import db
from datetime import datetime
from models.user import User
from sqlalchemy import or_

class Post(db.Model):
    """Social media post model"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    media_type = db.Column(db.String(20), nullable=True)  # image, video, document
    media_url = db.Column(db.String(255), nullable=True)
    media_thumbnail = db.Column(db.String(255), nullable=True)
    
    # Author information (polymorphic - can be student or admin)
    author_id = db.Column(db.Integer, nullable=False)
    author_type = db.Column(db.String(20), nullable=False)  # student, admin
    
    # Event relationship (optional - for event-related posts)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True)
    
    # Post metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_pinned = db.Column(db.Boolean, default=False)
    is_university_post = db.Column(db.Boolean, default=False)  # Admin-only university posts
    is_announcement = db.Column(db.Boolean, default=False)     # Official announcements
    
    # Privacy settings
    visibility = db.Column(db.String(20), default='public')  # public, department, private
    
    # Engagement metrics
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    shares_count = db.Column(db.Integer, default=0)
    views_count = db.Column(db.Integer, default=0)
    
    # Relationships
    likes = db.relationship('PostLike', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('PostComment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    shares = db.relationship('PostShare', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def author(self):
        """Get the author based on author_type"""
        if self.author_type == 'student':
            from models.user import Student
            return Student.query.get(self.author_id)
        elif self.author_type == 'admin':
            from models.user import Admin
            return Admin.query.get(self.author_id)
        return None
    
    @property
    def event(self):
        """Get associated event if any"""
        if self.event_id:
            from models.event import Event
            return Event.query.get(self.event_id)
        return None
    
    def is_liked_by(self, user):
        """Check if post is liked by user"""
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter_by(user_id=user.id, user_type=user.__class__.__name__.lower()).first() is not None
    
    def get_recent_comments(self, limit=3):
        """Get recent comments"""
        return self.comments.filter_by(is_active=True).order_by(PostComment.created_at.desc()).limit(limit).all()
    
    def can_edit(self, user):
        """Check if user can edit this post"""
        if not user or not user.is_authenticated:
            return False
        # Author can always edit their own posts
        if (user.id == self.author_id and 
            user.__class__.__name__.lower() == self.author_type):
            return True
        # Admins can edit any post for moderation
        return user.__class__.__name__.lower() == 'admin'
    
    def can_delete(self, user):
        """Check if user can delete this post"""
        if not user or not user.is_authenticated:
            return False
        # Author can delete their own posts
        if (user.id == self.author_id and 
            user.__class__.__name__.lower() == self.author_type):
            return True
        # Admins can delete any post for moderation
        return user.__class__.__name__.lower() == 'admin'
    
    def can_pin(self, user):
        """Check if user can pin/unpin this post"""
        if not user or not user.is_authenticated:
            return False
        # Only admins can pin posts
        return user.__class__.__name__.lower() == 'admin'
    
    def get_media_display_url(self):
        """Get URL for displaying media"""
        if self.media_url:
            if self.media_type == 'image':
                return self.media_url
            elif self.media_type == 'video' and self.media_thumbnail:
                return self.media_thumbnail
            else:
                return '/static/images/file-icon.png'
        return None
    
    def to_dict(self):
        """Convert post to dictionary"""
        return {
            'id': self.id,
            'content': self.content,
            'media_type': self.media_type,
            'media_url': self.media_url,
            'media_thumbnail': self.media_thumbnail,
            'author': {
                'id': self.author_id,
                'type': self.author_type,
                'name': f"{self.author.first_name} {self.author.last_name}" if self.author else "Unknown",
                'department': getattr(self.author, 'department', 'N/A')
            },
            'event': {
                'id': self.event.id,
                'title': self.event.title,
                'date': self.event.date.isoformat()
            } if self.event else None,
            'created_at': self.created_at.isoformat(),
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'shares_count': self.shares_count,
            'views_count': self.views_count,
            'visibility': self.visibility,
            'is_pinned': self.is_pinned
        }
    
    def __repr__(self):
        return f'<Post {self.id}: {self.content[:50]}...>'

class PostLike(db.Model):
    """Post likes model"""
    __tablename__ = 'post_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # student, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', 'user_type', name='unique_post_like'),)
    
    @property
    def user(self):
        """Get the user who liked"""
        if self.user_type == 'student':
            from models.user import Student
            return Student.query.get(self.user_id)
        elif self.user_type == 'admin':
            from models.user import Admin
            return Admin.query.get(self.user_id)
        return None
    
    def __repr__(self):
        return f'<PostLike {self.user_type} {self.user_id} -> Post {self.post_id}>'

class PostComment(db.Model):
    """Post comments model"""
    __tablename__ = 'post_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    # Author information
    author_id = db.Column(db.Integer, nullable=False)
    author_type = db.Column(db.String(20), nullable=False)  # student, admin
    
    # Comment metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Reply system (optional)
    parent_id = db.Column(db.Integer, db.ForeignKey('post_comments.id'), nullable=True)
    replies = db.relationship('PostComment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    @property
    def author(self):
        """Get the author based on author_type"""
        if self.author_type == 'student':
            from models.user import Student
            return Student.query.get(self.author_id)
        elif self.author_type == 'admin':
            from models.user import Admin
            return Admin.query.get(self.author_id)
        return None
    
    def can_edit(self, user):
        """Check if user can edit this comment"""
        if not user or not user.is_authenticated:
            return False
        return (user.id == self.author_id and user.__class__.__name__.lower() == self.author_type) or user.is_admin
    
    def can_delete(self, user):
        """Check if user can delete this comment"""
        return self.can_edit(user)
    
    def to_dict(self):
        """Convert comment to dictionary"""
        return {
            'id': self.id,
            'content': self.content,
            'author': {
                'id': self.author_id,
                'type': self.author_type,
                'name': f"{self.author.first_name} {self.author.last_name}" if self.author else "Unknown",
                'department': getattr(self.author, 'department', 'N/A')
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'parent_id': self.parent_id,
            'replies_count': self.replies.count()
        }
    
    def __repr__(self):
        return f'<PostComment {self.id}: {self.content[:50]}...>'

class PostShare(db.Model):
    """Post shares model"""
    __tablename__ = 'post_shares'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # student, admin
    share_type = db.Column(db.String(20), default='share')  # share, repost
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def user(self):
        """Get the user who shared"""
        if self.user_type == 'student':
            from models.user import Student
            return Student.query.get(self.user_id)
        elif self.user_type == 'admin':
            from models.user import Admin
            return Admin.query.get(self.user_id)
        return None
    
    def __repr__(self):
        return f'<PostShare {self.user_type} {self.user_id} -> Post {self.post_id}>'

class PostView(db.Model):
    """Post views tracking"""
    __tablename__ = 'post_views'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=True)  # nullable for anonymous views
    user_type = db.Column(db.String(20), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)  # For anonymous tracking
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    post = db.relationship('Post', backref='post_views')
    
    def __repr__(self):
        return f'<PostView Post {self.post_id} by {self.user_type} {self.user_id}>'
