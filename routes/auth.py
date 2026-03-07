from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models.user import Student, Admin
from extensions import db
from utils.forms import LoginForm, StudentRegistrationForm
from utils.mobile_detector import MobileDetector, mobile_template
import re

auth_bp = Blueprint('auth', __name__)

def validate_student_id(student_id):
    """Validate Andhra University student ID format"""
    pattern = r'^AU\d{8}[A-Z]{2}\d{3}$'  # Example: AU20240001CS001
    return re.match(pattern, student_id) is not None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if isinstance(current_user, Admin):
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    # Initialize user_type variable
    user_type = None
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user_type = form.user_type.data
        
        if user_type == 'student':
            user = Student.query.filter_by(email=email).first()
        else:
            user = Admin.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.first_name}!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if isinstance(current_user, Admin):
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('main.dashboard'))
        else:
            if user:
                flash('Invalid email or password', 'error')
            else:
                flash('Invalid email or password', 'error')
    
    return render_template(mobile_template('auth/login.html'), form=form)

@auth_bp.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = StudentRegistrationForm()
    if form.validate_on_submit():
        # Check if student ID already exists
        if Student.query.filter_by(student_id=form.student_id.data).first():
            flash('Student ID already registered', 'error')
            return render_template('auth/student_register.html', form=form)
        
        # Check if email already exists
        if Student.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'error')
            return render_template('auth/student_register.html', form=form)
        
        # Validate student ID format
        if not validate_student_id(form.student_id.data):
            flash('Invalid student ID format', 'error')
            return render_template('auth/student_register.html', form=form)
        
        # Create new student
        student = Student(
            student_id=form.student_id.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            department=form.department.data,
            year=form.year.data,
            phone_number=form.phone_number.data
        )
        student.set_password(form.password.data)
        
        db.session.add(student)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template(mobile_template('auth/student_register.html'), form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    from sqlalchemy import text
    return render_template('auth/profile.html', text=text)

@auth_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    from utils.forms import EditProfileForm
    
    form = EditProfileForm()
    
    if form.validate_on_submit():
        # Update user profile
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.phone_number = form.phone_number.data
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    # Pre-populate form with current user data
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.email.data = current_user.email
    form.phone_number.data = current_user.phone_number
    
    return render_template('auth/edit_profile.html', form=form)
