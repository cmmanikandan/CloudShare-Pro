from flask import render_template, current_app
from flask_mail import Message
from app import mail
import threading

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"EMAIL ERROR: {str(e)}")

def send_share_email(recipient, files, share_url, password=None, message=None):
    """
    Sends a professional share email to one or more recipients.
    """
    app = current_app._get_current_object()
    
    subject = f"Files Shared With You - CloudShare Pro"
    if len(files) == 1:
        subject = f"File Shared: {files[0].original_filename} - CloudShare Pro"

    # Calculate total size
    total_size = sum(f.file_size for f in files)
    size_mb = round(total_size / (1024 * 1024), 2)

    msg = Message(
        subject=subject,
        recipients=[recipient] if isinstance(recipient, str) else recipient,
        sender=app.config.get('MAIL_DEFAULT_SENDER')
    )

    msg.html = render_template(
        'emails/share_files.html',
        files=files,
        share_url=share_url,
        total_size_mb=size_mb,
        password=password,
        custom_message=message,
        expiry_date=files[0].expiry_date
    )

    # Send asynchronously
    thread = threading.Thread(target=send_async_email, args=(app, msg))
    thread.start()
    return True
