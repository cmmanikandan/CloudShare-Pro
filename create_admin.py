import os

from app import create_app, db
from app.models.user import User

def create_admin():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin_email = 'admin@cloudshare.pro'
        admin_password = os.getenv('ADMIN_PASSWORD', 'CsP@2026!Admin#7xQ')
        admin = User.query.filter_by(email=admin_email).first()
        
        if not admin:
            admin = User(
                username='System Admin',
                email=admin_email,
                role='admin',
                is_verified=True
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created successfully!")
            print(f"📧 Email: {admin_email}")
            print(f"🔑 Password: {admin_password}")
        else:
            print("ℹ️ Admin user already exists.")
            # Ensure it has admin role
            admin.role = 'admin'
            admin.is_verified = True
            admin.set_password(admin_password)
            db.session.commit()
            print("✅ Admin password rotated successfully!")
            print(f"📧 Email: {admin_email}")
            print(f"🔑 Password: {admin_password}")

if __name__ == "__main__":
    create_admin()
