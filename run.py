from app import create_app, db
from app.models.user import User
from app.models.file import File

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'File': File}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
