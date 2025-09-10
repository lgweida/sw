from celery_worker import celery
from models import db, Job
from flask import current_app
import time
import random

@celery.task(bind=True)
def long_running_task(self, job_name, duration=10):
    """A sample long-running task that simulates processing"""
    task_id = self.request.id
    
    # Update job status to started
    with current_app.app_context():
        job = Job.query.filter_by(task_id=task_id).first()
        if job:
            job.status = 'started'
            db.session.commit()
    
    # Simulate work
    for i in range(duration):
        time.sleep(1)
        self.update_state(
            state='PROGRESS',
            meta={'current': i + 1, 'total': duration, 'status': f'Processing {job_name}'}
        )
    
    # Generate a result
    result = f"Completed {job_name} after {duration} seconds. Result: {random.randint(1000, 9999)}"
    
    # Update job status to completed
    with current_app.app_context():
        job = Job.query.filter_by(task_id=task_id).first()
        if job:
            job.status = 'completed'
            job.result = result
            job.completed_at = db.func.current_timestamp()
            db.session.commit()
    
    return result

@celery.task
def quick_task(job_name):
    """A quick task that returns immediately"""
    result = f"Quick task '{job_name}' completed instantly!"
    
    # Update job status in database
    with current_app.app_context():
        job = Job.query.filter_by(name=job_name).first()
        if job:
            job.status = 'completed'
            job.result = result
            job.completed_at = db.func.current_timestamp()
            db.session.commit()
    
    return result
