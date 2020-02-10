"""
API calls for jobs.
"""
from datetime import datetime
from sqlalchemy import and_

from app.models import Job, JobSchema

__all__ = ['get_jobs', 'add_job', 'get_job', 'update_job', 'delete_job']

def get_jobs(createdSince=None, createdBefore=None, limit=None):
    """
    Function for API endpoint /api/jobs

    Parameters
    ----------
    createdSince: str
        Return jobs created after this date. Must be in format M-D-YYYY where M all numbers are integers.
    createdBefore: str
        Return jobs created before this date. Must be in format M-D-YYYY where M all numbers are integers.
    limit: int
        The maximum number of jobs to return.
    """
    # Handle dates
    if createdSince is not None:
        createdSince = datetime.strptime(createdSince, '%m-%d-%Y')
    else:
        # Basically all times
        createdSince = datetime.strptime('1-1-0001', '%m-%d-%Y')
    
    if createdBefore is not None:
        createdBefore = datetime.strptime(createdBefore, '%m-%d-%Y')
    else:
        # Up to now.
        createdBefore = datetime.utcnow()
    
    # If limit is not set, set limit to max.
    if limit is None:
        limit = Job.query.count()
    
    jobs = Job.query.filter(and_(Job.submission_date>createdSince, Job.submission_date<createdBefore)).limit(limit)

    jobs_schema = JobSchema(many=True)
    
    return jobs_schema.dump(jobs)

def add_job():
    return []

def get_job(id):
    job = Job.query.get(id)
    job_schema = JobSchema(many=False)
    return job_schema.dump(job)

def update_job(id):
    return []

def delete_job(id):
    pass

