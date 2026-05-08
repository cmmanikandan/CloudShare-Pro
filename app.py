from app import create_app, db
from app.models.user import User
from app.models.file import File
import os

app = create_app()

# For Vercel/Production: ensure tables exist if using SQLite (though a hosted DB is recommended)
# Note: create_all() is safe to call even if tables already exist.
with app.app_context():
    if os.environ.get('VERCEL'):
        db.create_all()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'File': File}

if __name__ == '__main__':
    app.run(debug=True)
