from flask import Blueprint, request, jsonify
from flask_login import current_user
import cloudinary.uploader
from app.models.file import File, DownloadLog
from app import db
import uuid
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__)

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
                expiry_date=expiry_date # Save expiry
            )
            db.session.add(new_file)
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
        return jsonify({'error': str(e)}), 500
