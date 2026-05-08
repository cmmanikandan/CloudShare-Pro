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
    
    stats = {
        'total_users': User.query.count(),
        'total_files': File.query.count(),
        'total_downloads': db.session.query(db.func.sum(File.download_count)).scalar() or 0
    }
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_files = File.query.order_by(File.created_at.desc()).limit(5).all()
    
    return render_template('admin.html', stats=stats, recent_users=recent_users, recent_files=recent_files)
