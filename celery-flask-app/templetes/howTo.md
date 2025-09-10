How to Run on Windows
Install dependencies:

bash
pip install -r requirements.txt
Initialize the database:

bash
python -c "
from app import create_app
from models import db
app = create_app()
with app.app_context():
    db.create_all()
print('Database initialized')
"
Start the Celery worker (Windows compatible):

bash
celery -A celery_worker.celery worker --loglevel=info --pool=solo
Start the Flask application:

bash
python app.py
Open your browser and go to:

text
http://localhost:5000
Windows-Specific Notes
Worker Pool: Using --pool=solo instead of the default prefork pool for Windows compatibility

File Paths: Using absolute paths for SQLite databases to avoid path issues

Directory Creation: Ensuring the instance directory exists before creating databases

Eventlet: Added eventlet as a dependency which can be used as an alternative pool for better performance

The application should now run smoothly on Windows! The key change is using the solo pool for Celery workers, which is compatible with Windows.
