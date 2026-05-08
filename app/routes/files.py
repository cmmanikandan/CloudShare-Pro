from datetime import datetime

from flask import Blueprint, render_template, abort, url_for, jsonify
from app.models.file import File, DownloadLog
from app import db
from flask import request
import cloudinary.uploader

files_bp = Blueprint('files', __name__)

@files_bp.route('/validate/<token>')
def validate_share_code(token):
    exists = File.query.filter(File.share_token.ilike(token)).first() is not None
    return jsonify({'valid': exists})

@files_bp.route('/download/<token>')
def download_page(token):
    files = File.query.filter(File.share_token.ilike(token)).all()
    if not files:
        abort(404)
    
    # Use the first file for metadata like password check if needed
    file = files[0]
    
    # Detailed Analytics Logging
    user_agent = request.headers.get('User-Agent')
    ip = request.remote_addr
    
    # Simple Geolocation (Placeholder logic or free API)
    country = 'Unknown'
    try:
        import requests
        geo_resp = requests.get(f'http://ip-api.com/json/{ip}', timeout=2).json()
        if geo_resp.get('status') == 'success':
            country = geo_resp.get('country', 'Unknown')
    except:
        pass

    log = DownloadLog(
        file_id=file.id, 
        ip_address=ip,
        country=country,
        user_agent=user_agent
    )
    db.session.add(log)
    db.session.commit()

    def format_duration(delta):
        total_seconds = int(delta.total_seconds())
        if total_seconds <= 0:
            return "0 min"

        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes = remainder // 60

        parts = []
        if days:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours:
            parts.append(f"{hours} hr{'s' if hours != 1 else ''}")
        if not parts and minutes:
            parts.append(f"{minutes} min{'s' if minutes != 1 else ''}")
        return " ".join(parts[:2]) or "0 min"

    now = datetime.utcnow()
    share_url = url_for('files.download_page', token=file.share_token, _external=True)

    for item in files:
        item.share_code = item.share_token or token
        item.share_url = url_for('files.download_page', token=item.share_token or token, _external=True)

        if item.expiry_date:
            remaining = item.expiry_date - now
            if remaining.total_seconds() > 0:
                item.expiry_state = 'active'
                item.expiry_label = f"{format_duration(remaining)} remaining"
            else:
                item.expiry_state = 'expired'
                item.expiry_label = f"Expired {format_duration(abs(remaining))} ago"
        else:
            item.expiry_state = 'permanent'
            item.expiry_label = 'Permanent access'
    
    total_size = sum((item.file_size or 0) for item in files)
    return render_template(
        'download.html',
        files=files,
        share_url=share_url,
        share_code=file.share_token or token,
        total_size=total_size,
    )

@files_bp.route('/direct-download/<int:file_id>')
def direct_download(file_id):
    from flask import Response, stream_with_context
    import requests
    
    file_record = File.query.get_or_404(file_id)
    
    # Update download count
    file_record.download_count += 1
    db.session.commit()
    
    # Stream the file from Cloudinary to the user with correct headers
    req = requests.get(file_record.secure_url, stream=True)
    
    def generate():
        for chunk in req.iter_content(chunk_size=4096):
            yield chunk

    # Determine filename with extension
    filename = file_record.original_filename
    
    # Set proper Content-Disposition
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"',
        'Content-Type': file_record.mime_type or req.headers.get('Content-Type', 'application/octet-stream')
    }

    if file_record.one_time_download:
        try:
            cloudinary.uploader.destroy(file_record.public_id)
        except Exception:
            pass
        db.session.delete(file_record)
        db.session.commit()
    
    return Response(stream_with_context(generate()), headers=headers)
