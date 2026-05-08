from flask import render_template, current_app
from flask_mail import Message
from app import mail
import threading
import requests

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

    def send_via_resend():
        api_key = app.config.get('RESEND_API_KEY')
        sender = app.config.get('RESEND_FROM') or app.config.get('MAIL_DEFAULT_SENDER')
        if not api_key:
            raise RuntimeError('RESEND_API_KEY is not configured')

        recipients = [recipient] if isinstance(recipient, str) else recipient
        payload = {
            'from': sender,
            'to': recipients,
            'subject': subject,
            'html': msg.html,
        }
        response = requests.post(
            'https://api.resend.com/emails',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=15,
        )
        if response.status_code >= 400:
            raise RuntimeError(f'Resend error: {response.status_code} {response.text}')
        return True

    # Attempt to send synchronously so the caller receives immediate feedback on failure.
    try:
        provider = (app.config.get('MAIL_PROVIDER') or 'smtp').lower()
        if provider == 'resend':
            send_via_resend()
        else:
            mail.send(msg)
        return True
    except Exception as e:
        # Fallback: try asynchronous send so we still attempt delivery in background, but report the error upstream
        try:
            if (app.config.get('MAIL_PROVIDER') or 'smtp').lower() == 'resend':
                # If Resend fails, fall back to SMTP path.
                thread = threading.Thread(target=send_async_email, args=(app, msg))
            else:
                thread = threading.Thread(target=send_async_email, args=(app, msg))
            thread.start()
        except Exception:
            pass
        # Re-raise so callers (API) can return an error to the client
        raise
