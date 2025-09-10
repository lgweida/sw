from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, Job
from tasks import long_running_task, quick_task
from celery_worker import celery
import uuid
import os

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'dev-key-please-change-in-production'
    
    # Use absolute path for SQLite database (Windows compatibility)
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.join(base_dir, 'instance')
    
    # Create instance directory if it doesn't exist
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "app.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Routes
    @app.route('/')
    def index():
        jobs = Job.query.order_by(Job.created_at.desc()).all()
        return render_template('index.html', jobs=jobs)
    
    @app.route('/job', methods=['POST'])
    def create_job():
        job_name = request.form.get('name', f'Job-{uuid.uuid4().hex[:8]}')
        duration = int(request.form.get('duration', 10))
        
        # Create job record in database
        task = long_running_task.apply_async(args=[job_name, duration])
        
        job = Job(
            task_id=task.id,
            name=job_name,
            status='pending'
        )
        db.session.add(job)
        db.session.commit()
        
        return redirect(url_for('index'))
    
    @app.route('/quick-job', methods=['POST'])
    def create_quick_job():
        job_name = request.form.get('name', f'QuickJob-{uuid.uuid4().hex[:8]}')
        
        # Create job record in database
        task = quick_task.apply_async(args=[job_name])
        
        job = Job(
            task_id=task.id,
            name=job_name,
            status='pending'
        )
        db.session.add(job)
        db.session.commit()
        
        return redirect(url_for('index'))
    
    @app.route('/job/<task_id>')
    def get_job_status(task_id):
        job = Job.query.filter_by(task_id=task_id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Get task result from Celery if needed
        task = long_running_task.AsyncResult(task_id)
        
        response = job.to_dict()
        if task.state == 'PENDING':
            response['celery_status'] = 'Pending'
        elif task.state != 'FAILURE':
            response['celery_status'] = task.state
            if task.state == 'SUCCESS':
                response['result'] = task.result
        else:
            # Something went wrong
            response['celery_status'] = task.state
            response['result'] = str(task.info)  # Exception info
        
        return jsonify(response)
    
    @app.route('/jobs')
    def get_jobs():
        jobs = Job.query.order_by(Job.created_at.desc()).all()
        return jsonify([job.to_dict() for job in jobs])
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
