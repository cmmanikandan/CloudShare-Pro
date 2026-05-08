from datetime import datetime
from app import db

class File(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    original_filename = db.Column(db.String(255), nullable=False)
    public_id = db.Column(db.String(255), unique=True, nullable=False)
    secure_url = db.Column(db.String(512), nullable=False)
    thumbnail_url = db.Column(db.String(512))
    file_size = db.Column(db.BigInteger) # In bytes
    mime_type = db.Column(db.String(100))
    visibility = db.Column(db.String(20), default='public') # 'public', 'private'
    password = db.Column(db.String(128), nullable=True) # Hashed password for access
    expiry_date = db.Column(db.DateTime, nullable=True)
    one_time_download = db.Column(db.Boolean, default=False)
    download_count = db.Column(db.Integer, default=0)
    share_token = db.Column(db.String(100), unique=False) # Token for sharing (can be shared by multiple files)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    logs = db.relationship('DownloadLog', backref='file', lazy='dynamic')

    def __repr__(self):
        return f'<File {self.original_filename}>'

class DownloadLog(db.Model):
    __tablename__ = 'download_logs'
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    ip_address = db.Column(db.String(45))
    country = db.Column(db.String(100), default='Unknown')
    user_agent = db.Column(db.String(255))
    downloaded_at = db.Column(db.DateTime, default=datetime.utcnow)
