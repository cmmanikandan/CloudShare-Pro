from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from app import db
from app.models.user import User
from werkzeug.security import check_password_hash

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    if not current_user.is_authenticated:
        return render_template('login.html')
    return render_template('dashboard.html')

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action', 'preferences')

        if action == 'profile':
            username = (request.form.get('username') or '').strip()
            email = (request.form.get('email') or '').strip().lower()
            current_password = request.form.get('current_password') or ''
            new_password = request.form.get('new_password') or ''

            if len(username) < 2:
                flash('Please enter a valid username.', 'error')
                return redirect(url_for('main.settings'))

            if '@' not in email or '.' not in email:
                flash('Please enter a valid email address.', 'error')
                return redirect(url_for('main.settings'))

            existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
            if existing_user:
                flash('That email is already in use.', 'error')
                return redirect(url_for('main.settings'))

            current_user.username = username
            current_user.email = email

            if new_password:
                if not current_password or not current_user.check_password(current_password):
                    flash('Current password is required to change your password.', 'error')
                    return redirect(url_for('main.settings'))

                if len(new_password) < 8:
                    flash('New password must be at least 8 characters long.', 'error')
                    return redirect(url_for('main.settings'))

                current_user.set_password(new_password)

            db.session.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('main.settings'))

        current_user.email_notifications = 'email_notifications' in request.form
        current_user.telegram_notifications = 'telegram_notifications' in request.form
        db.session.commit()
        flash('Settings saved successfully.', 'success')
        return redirect(url_for('main.settings'))

    return render_template('settings.html')

@main_bp.route('/features')
def features():
    return render_template('features.html')

@main_bp.route('/pricing')
def pricing():
    # Pricing removed — service is fully free. Redirect to features.
    return redirect(url_for('main.features'))

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')
