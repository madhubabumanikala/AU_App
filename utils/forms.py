from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, IntegerField, DateField, TimeField, BooleanField, FileField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional, ValidationError
from models.user import Student, Admin
import re

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    user_type = RadioField('Login as', choices=[('student', 'Student'), ('admin', 'Admin')], default='student')
    remember_me = BooleanField('Remember me')

class StudentRegistrationForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired(), Length(min=10, max=20)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    department = SelectField('Department', choices=[
        ('Computer Science', 'Computer Science'),
        ('Electronics & Communication', 'Electronics & Communication'),
        ('Electrical Engineering', 'Electrical Engineering'),
        ('Mechanical Engineering', 'Mechanical Engineering'),
        ('Civil Engineering', 'Civil Engineering'),
        ('Chemical Engineering', 'Chemical Engineering'),
        ('Business Administration', 'Business Administration'),
        ('Physics', 'Physics'),
        ('Chemistry', 'Chemistry'),
        ('Mathematics', 'Mathematics'),
        ('English', 'English'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1, max=5)])
    phone_number = StringField('Phone Number', validators=[Optional(), Length(max=15)])
    
    def validate_student_id(self, field):
        # Validate Andhra University student ID format
        pattern = r'^AU\d{8}[A-Z]{2}\d{3}$'
        if not re.match(pattern, field.data):
            raise ValidationError('Invalid student ID format. Example: AU20240001CS001')
        
        if Student.query.filter_by(student_id=field.data).first():
            raise ValidationError('Student ID already registered')
    
    def validate_email(self, field):
        if Student.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[Optional(), Length(max=15)])

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=20)])
    date = DateField('Event Date', validators=[DataRequired()])
    time = TimeField('Event Time', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])
    department = SelectField('Department', choices=[
        ('Computer Science', 'Computer Science'),
        ('Electronics & Communication', 'Electronics & Communication'),
        ('Electrical Engineering', 'Electrical Engineering'),
        ('Mechanical Engineering', 'Mechanical Engineering'),
        ('Civil Engineering', 'Civil Engineering'),
        ('Chemical Engineering', 'Chemical Engineering'),
        ('Business Administration', 'Business Administration'),
        ('Physics', 'Physics'),
        ('Chemistry', 'Chemistry'),
        ('Mathematics', 'Mathematics'),
        ('English', 'English'),
        ('All Departments', 'All Departments')
    ], validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('technical', 'Technical'),
        ('cultural', 'Cultural'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('sports', 'Sports'),
        ('placement', 'Placement Drive'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    max_participants = IntegerField('Maximum Participants', validators=[Optional(), NumberRange(min=1)])
    poster_image = FileField('Event Poster', validators=[Optional()])
    notify_students = BooleanField('Notify students about this event')
    notify_update = BooleanField('Notify registered students about updates')

class FeedbackForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        (5, '5 - Excellent'),
        (4, '4 - Very Good'),
        (3, '3 - Good'),
        (2, '2 - Fair'),
        (1, '1 - Poor')
    ], validators=[DataRequired()])
    comments = TextAreaField('Comments', validators=[Optional(), Length(max=500)])

class AdminRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin')
    ], validators=[DataRequired()])
    department = SelectField('Department', choices=[
        ('Computer Science', 'Computer Science'),
        ('Electronics & Communication', 'Electronics & Communication'),
        ('Electrical Engineering', 'Electrical Engineering'),
        ('Mechanical Engineering', 'Mechanical Engineering'),
        ('Civil Engineering', 'Civil Engineering'),
        ('Chemical Engineering', 'Chemical Engineering'),
        ('Business Administration', 'Business Administration'),
        ('Physics', 'Physics'),
        ('Chemistry', 'Chemistry'),
        ('Mathematics', 'Mathematics'),
        ('English', 'English'),
        ('Administration', 'Administration')
    ], validators=[DataRequired()])
    
    def validate_username(self, field):
        if Admin.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken')
    
    def validate_email(self, field):
        if Admin.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])

class EventFilterForm(FlaskForm):
    department = SelectField('Department', choices=[('', 'All Departments')], validators=[Optional()])
    category = SelectField('Category', choices=[('', 'All Categories')], validators=[Optional()])
