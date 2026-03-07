#!/usr/bin/env python3
"""
Mobile AU Event System - SIMPLE WORKING VERSION
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 60)
print("AU EVENT SYSTEM - MOBILE VERSION")
print("=" * 60)
print("Starting mobile app...")
print(f"Project Root: {PROJECT_ROOT}")
print(f"Database: {PROJECT_ROOT}/au_events.db")
print("=" * 60)

# Simple Flask app setup
from flask import Flask, render_template, redirect, url_for, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'au-events-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{PROJECT_ROOT}/au_events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database and login setup
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# Simple user model
class User:
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    return User(id=1, email='admin@au-events.com', password='admin123')

# Simple routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('mobile_login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email == 'admin@au-events.com' and password == 'admin123':
            user = User(id=1, email='admin@au-events.com', password='admin123')
            login_user(user)
            return redirect(url_for('dashboard'))
        elif email == 'student@test.com' and password == 'password123':
            user = User(id=2, email='student@test.com', password='password123')
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials", 401
    
    return render_template('mobile_login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('mobile_dashboard.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Create database tables
with app.app_context():
    db.create_all()
    
print("Mobile app ready!")
print("Open browser to: http://localhost:5000")
print("Login: admin@au-events.com / admin123")
print("=" * 60)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
