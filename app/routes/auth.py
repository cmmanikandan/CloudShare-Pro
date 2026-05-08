from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)
import re

def valid_email(email):
    return bool(re.match(r'^\S+@\S+\.\S+$', email))

def strong_password(pw):
    # At least 8 chars, one uppercase, one lowercase, one digit, one special
    if not pw or len(pw) < 8:
        return False
    if not re.search(r'[A-Z]', pw):
        return False
    if not re.search(r'[a-z]', pw):
        return False
    if not re.search(r'\d', pw):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pw):
        return False
    return True

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip()
        password = request.form.get('password')
        # Basic server-side validation
        if not valid_email(email):
            return render_template('login.html', login_error='Please enter a valid email address.', email=email)
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            return render_template('login.html', login_error='Invalid email or password.', email=email)
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        # Server-side validation
        if not username or len(username.strip()) < 2:
            flash('Please provide a valid name', 'error')
            return redirect(url_for('auth.register'))
        if not valid_email(email):
            flash('Please enter a valid email address', 'error')
            return redirect(url_for('auth.register'))
        if not strong_password(password):
            flash('Password must be at least 8 chars and include uppercase, lowercase, number and special character', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('auth.register'))
            
        user = User(username=username, email=email)
        user.set_password(password)
        
        # Generate Verification Code
        import random
        user.verification_code = str(random.randint(100000, 999999))
        user.is_verified = False
        
        db.session.add(user)
        db.session.commit()
        
        # Send Verification Email (Logic would go here or in a background task)
        # For now, we'll flash it so the user can see it
        flash(f'Please verify your account. Your code is: {user.verification_code}', 'info')
        
        return redirect(url_for('auth.verify', email=email))
        
    return render_template('register.html')

@auth_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    email = request.args.get('email')
    if request.method == 'POST':
        code = request.form.get('code')
        user = User.query.filter_by(email=email).first()
        
        if user and user.verification_code == code:
            user.is_verified = True
            user.verification_code = None
            db.session.commit()
            login_user(user)
            flash('Account verified successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid verification code', 'error')
            
    return render_template('verify.html', email=email)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# --- Google OAuth Routes ---
from app import oauth

@auth_bp.route('/login/google')
def google_login():
    redirect_uri = url_for('auth.google_authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/authorize')
def google_authorize():
    token = oauth.google.authorize_access_token()
    resp = oauth.google.get('https://www.googleapis.com/oauth2/v3/userinfo')
    user_info = resp.json()
    
    email = user_info.get('email')
    username = user_info.get('name', email.split('@')[0])
    
    # Check if user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        # Create new user
        user = User(username=username, email=email, is_verified=True) # Google users are pre-verified
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    return redirect(url_for('main.dashboard'))
