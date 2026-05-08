from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user
import cloudinary.uploader
from app.models.file import File, DownloadLog
from app import db
import uuid
from datetime import datetime, timedelta
import smtplib
import requests

api_bp = Blueprint('api', __name__)

@api_bp.route('/email/health', methods=['GET'])
def email_health():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401

    provider = (current_app.config.get('MAIL_PROVIDER') or 'smtp').lower()

    try:
        if provider == 'resend':
            api_key = current_app.config.get('RESEND_API_KEY')
            if not api_key:
                return jsonify({'ok': False, 'provider': provider, 'message': 'RESEND_API_KEY is missing'}), 400

            response = requests.get(
                'https://api.resend.com/domains',
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=10,
            )
            if response.status_code >= 400:
                return jsonify({'ok': False, 'provider': provider, 'message': f'Resend auth failed ({response.status_code})'}), 400

            return jsonify({'ok': True, 'provider': provider, 'message': 'Resend configuration is valid'}), 200

        host = current_app.config.get('MAIL_SERVER')
        port = int(current_app.config.get('MAIL_PORT') or 587)
        username = current_app.config.get('MAIL_USERNAME')
        password = current_app.config.get('MAIL_PASSWORD')
        use_tls = bool(current_app.config.get('MAIL_USE_TLS'))

        if not host or not username or not password:
            return jsonify({'ok': False, 'provider': 'smtp', 'message': 'SMTP settings are incomplete'}), 400

        server = smtplib.SMTP(host, port, timeout=15)
        try:
            server.ehlo()
            if use_tls:
                server.starttls()
                server.ehlo()
            server.login(username, password)
        finally:
            server.quit()

        return jsonify({'ok': True, 'provider': 'smtp', 'message': 'SMTP login successful'}), 200
    except Exception as e:
        return jsonify({'ok': False, 'provider': provider, 'message': f'Email health check failed: {str(e)}'}), 500

@api_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected files'}), 400

    try:
        from flask import current_app
        import traceback
        
        # Generate a single token for this batch
        batch_token = str(uuid.uuid4().hex)[:6].upper()
        results = []

        for file in files:
            # Upload to Cloudinary
            # For non-image/video files, "raw" is often better to preserve everything
            # but "auto" usually works well if use_filename=True is set.
            upload_params = {
                "resource_type": "auto",
                "folder": "cloudshare_pro"
            }
            
            if current_app.config.get('CLOUDINARY_UPLOAD_PRESET'):
                upload_params["upload_preset"] = current_app.config['CLOUDINARY_UPLOAD_PRESET']
                if not current_app.config.get('CLOUDINARY_API_SECRET'):
                    upload_params["unsigned"] = True
                else:
                    # Only signed uploads allow these parameters via API
                    upload_params["use_filename"] = True
                    upload_params["unique_filename"] = False
            else:
                # Fallback for standard signed uploads
                upload_params["use_filename"] = True
                upload_params["unique_filename"] = False
            
        # Get advanced options
        password = request.form.get('password')
        expiry_days = request.form.get('expiry_days')
        one_time_download = request.form.get('one_time_download') == '1'
        
        expiry_date = None
        if expiry_days and expiry_days != '0':
            expiry_date = datetime.utcnow() + timedelta(days=int(expiry_days))

        for file in files:
            # Upload to Cloudinary...
            # (Keeping existing Cloudinary logic)
            print(f"Uploading file {file.filename}...")
            upload_result = cloudinary.uploader.upload(file, **upload_params)
            
            # Create file record
            new_file = File(
                user_id=current_user.id if hasattr(current_user, 'id') and current_user.is_authenticated else None,
                original_filename=file.filename,
                public_id=upload_result['public_id'],
                secure_url=upload_result['secure_url'],
                thumbnail_url=upload_result.get('thumbnail_url'),
                file_size=upload_result['bytes'],
                mime_type=upload_result.get('format') or file.content_type,
                share_token=batch_token,
                password=password, # Save password
                expiry_date=expiry_date, # Save expiry
                one_time_download=one_time_download
            )
            db.session.add(new_file)
            db.session.flush()
            results.append(new_file.id)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully uploaded {len(files)} files',
            'share_url': f"/files/download/{batch_token}",
            'file_ids': results
        }), 201
        
    except Exception as e:
        print(f"UPLOAD ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/files', methods=['GET'])
def get_files():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    files = File.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': f.id,
        'filename': f.original_filename,
        'url': f.secure_url,
        'download_url': f'/files/direct-download/{f.id}',
        'download_page_url': f'/files/download/{f.share_token}',
        'share_code': f.share_token,
        'size': f.file_size,
        'mime_type': f.mime_type,
        'created_at': f.created_at.isoformat(),
        'downloads': f.download_count
    } for f in files])

@api_bp.route('/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    file = File.query.filter_by(id=file_id, user_id=current_user.id).first()
    if not file:
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Optional: Delete from Cloudinary as well
        cloudinary.uploader.destroy(file.public_id)
        
        db.session.delete(file)
        db.session.commit()
        return jsonify({'message': 'File deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/files/<int:file_id>/rename', methods=['PATCH'])
def rename_file(file_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401

    file = File.query.filter_by(id=file_id, user_id=current_user.id).first()
    if not file:
        return jsonify({'error': 'File not found'}), 404

    data = request.get_json(silent=True) or {}
    new_name = (data.get('filename') or '').strip()

    if len(new_name) < 2:
        return jsonify({'error': 'Please enter a valid file name'}), 400

    file.original_filename = new_name
    db.session.commit()
    return jsonify({'message': 'File renamed successfully', 'filename': file.original_filename}), 200

@api_bp.route('/share/email', methods=['POST'])
def share_via_email():
    data = request.json
    file_ids = data.get('file_ids')
    recipient = data.get('recipient')
    message = data.get('message')
    
    if not file_ids or not recipient:
        return jsonify({'error': 'Missing file_ids or recipient'}), 400
    
    files = File.query.filter(File.id.in_(file_ids)).all()
    if not files:
        return jsonify({'error': 'Files not found'}), 404
    
    from app.services.email_service import send_share_email
    from app.models.user import EmailShare
    share_url = f"{request.host_url}files/download/{files[0].share_token}"
    
    try:
        send_share_email(recipient, files, share_url, password=files[0].password, message=message)

        # Log the share
        for f in files:
            share_log = EmailShare(file_id=f.id, recipient_email=recipient)
            db.session.add(share_log)
        db.session.commit()

        return jsonify({'message': 'Email sent successfully'}), 200
    except Exception as e:
        # Provide a clear error message to the client
        return jsonify({'error': 'Failed to send email: ' + str(e)}), 500
@api_bp.route('/analytics', methods=['GET'])
def get_analytics():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get all files for the user
    user_files = File.query.filter_by(user_id=current_user.id).all()
    file_ids = [f.id for f in user_files]
    
    # Aggregated Stats
    total_downloads = sum(f.download_count for f in user_files)
    
    # Country Stats
    from sqlalchemy import func
    country_stats = db.session.query(
        DownloadLog.country, func.count(DownloadLog.id)
    ).filter(DownloadLog.file_id.in_(file_ids)).group_by(DownloadLog.country).all()
    
    # Browser Stats
    browser_stats = db.session.query(
        DownloadLog.user_agent, func.count(DownloadLog.id)
    ).filter(DownloadLog.file_id.in_(file_ids)).group_by(DownloadLog.user_agent).all()

    # Last 7 days download trend
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=6)
    daily_rows = db.session.query(
        func.date(DownloadLog.downloaded_at), func.count(DownloadLog.id)
    ).filter(
        DownloadLog.file_id.in_(file_ids),
        func.date(DownloadLog.downloaded_at) >= start_date.isoformat(),
        func.date(DownloadLog.downloaded_at) <= end_date.isoformat()
    ).group_by(func.date(DownloadLog.downloaded_at)).all()

    daily_map = {row_date: count for row_date, count in daily_rows}
    daily_downloads = []
    for offset in range(7):
        day = start_date + timedelta(days=offset)
        daily_downloads.append({
            'date': day.isoformat(),
            'label': day.strftime('%a'),
            'count': daily_map.get(day.isoformat(), 0)
        })
    
    return jsonify({
        'total_downloads': total_downloads,
        'country_stats': [{'country': c, 'count': count} for c, count in country_stats],
        'browser_stats': [{'ua': ua, 'count': count} for ua, count in browser_stats],
        'daily_downloads': daily_downloads
    })
