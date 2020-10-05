"""
API calls for the status
"""
import logging

from app.models import Project, Job, Flowchart

from flask_login import current_user
from sqlalchemy import and_

from app import authorize


logger = logging.getLogger('__file__')

__all__ = ['status']

def status():
    """The status of the dashboard.

    Currently always 'running', but in the future other
    values may be added.
    
    """
    #users = User.query.all()
    #user_schema = UserSchema(many=True)
    #users = user_schema.dump(users)

    try:
        username =  current_user.username
    except AttributeError:
        username =  'Anonymous User'

    if current_user.get_id():
        roles = current_user.roles
    else:
        roles = None
    
    # Get information about jobs, projects, flowcharts
    num_jobs_running = Job.query.filter(and_(Job.status == 'running', Job.authorized('read'))).count()
    num_jobs_finished = Job.query.filter(and_(Job.status == 'finished', Job.authorized('read'))).count()
    num_jobs_queued = Job.query.filter(and_(Job.status == 'running', Job.authorized('submitted'))).count()
    num_flowcharts = Flowchart.query.filter(Flowchart.authorized('read')).count()
    num_projects = Project.query.filter(Project.authorized('read')).count()

    # Build return json
    status = {
        'status' : 'running',
        'user id': current_user.get_id(),
        'username': username,
        'roles': roles,
        'jobs': {
            'running': num_jobs_running,
            'finished': num_jobs_finished,
            'queued': num_jobs_queued,
            },
        'flowcharts': num_flowcharts,
        'projects': num_projects
        
    }

    return status, 200
    
