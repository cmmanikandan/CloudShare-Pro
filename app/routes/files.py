from flask import Blueprint, render_template, abort
from app.models.file import File, DownloadLog
from app import db
from flask import request

files_bp = Blueprint('files', __name__)

@files_bp.route('/download/<token>')
def download_page(token):
    files = File.query.filter(File.share_token.ilike(token)).all()
    if not files:
        abort(404)
    
    # Use the first file for metadata like password check if needed
    file = files[0]
    
    # Log download (simplistic)
    log = DownloadLog(file_id=file.id, ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()
    
    return render_template('download.html', files=files)

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
    
    return Response(stream_with_context(generate()), headers=headers)
