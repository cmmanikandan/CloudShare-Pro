from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.user import User
from app.models.file import File
from app import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
def index():
    if current_user.role != 'admin':
        return "Unauthorized", 403

    files = File.query.all()
    total_storage = sum((file.file_size or 0) for file in files)
    one_time_files = sum(1 for file in files if file.one_time_download)
    avg_file_size = (total_storage / len(files)) if files else 0
    
    stats = {
        'total_users': User.query.count(),
        'total_files': len(files),
        'total_downloads': db.session.query(db.func.sum(File.download_count)).scalar() or 0,
        'total_storage': total_storage,
        'avg_file_size': avg_file_size,
        'one_time_files': one_time_files
    }
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_files = File.query.order_by(File.created_at.desc()).limit(5).all()
    
    return render_template('admin.html', stats=stats, recent_users=recent_users, recent_files=recent_files)

@admin_bp.route('/users')
@login_required
def manage_users():
    if current_user.role != 'admin': return "Unauthorized", 403
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@admin_bp.route('/users/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.role != 'admin': return "Unauthorized", 403
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return "User deleted", 200

@admin_bp.route('/files')
@login_required
def manage_files():
    if current_user.role != 'admin': return "Unauthorized", 403
    files = File.query.all()
    return render_template('admin_files.html', files=files)
