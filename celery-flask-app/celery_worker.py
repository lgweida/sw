from celery import Celery
import os

# Configure Celery to use SQLite as both broker and backend
def make_celery():
    # Use SQLite as message broker (for development only)
    # Using absolute path for better Windows compatibility
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.join(base_dir, 'instance')
    
    # Create instance directory if it doesn't exist
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    broker_url = f'sqla+sqlite:///{os.path.join(instance_path, "celery.db")}'
    backend_url = f'db+sqlite:///{os.path.join(instance_path, "celery_results.db")}'
    
    celery = Celery(
        'tasks',
        broker=broker_url,
        backend=backend_url,
        include=['tasks']
    )
    
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_send_sent_event=True,
        # Use SQLite as result backend
        result_backend=backend_url,
        # For development with SQLite
        task_always_eager=False,  # Set to True for synchronous execution (debugging)
        broker_pool_limit=None,   # Important for SQLite
        # Windows-specific settings
        worker_pool='solo',       # Use solo pool for Windows compatibility
    )
    
    return celery

# Initialize Celery
celery = make_celery()
