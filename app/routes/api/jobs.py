"""
API calls for jobs.
"""

import os

from datetime import datetime
from sqlalchemy import and_
from flask import Response, request
from dateutil import parser
from flask import url_for, send_file

import urllib.parse

from app import db

from app.models import Job, JobSchema

__all__ = ['get_jobs', 'get_job', 'get_job_files']

file_icons = {
    'graph': 'fas fa-chart-line',
    'csv': "fas fa-table",
    'flow': "fas fa-project-diagram",
    'other': "far fa-file-alt",
    'folder': 'far fa-folder-open'
    
}

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
    
    # If limit is not set, set limit to all jobs in DB.
    if limit is None:
        limit = Job.query.count()
    
    jobs = Job.query.filter(and_(Job.submission_date>createdSince, Job.submission_date<createdBefore)).limit(limit)

    jobs_schema = JobSchema(many=True)
    
    return jobs_schema.dump(jobs), 200

def add_job():

    # Job data is in request since not listed
    # as parameter in swagger.yml
    job_data = request.get_json(force=True)

    # Make sure this job isn't in the DB
    jobs = Job.query.get(job_data['id'])

    if jobs is not None:
        return Response(status=409)

    job_schema = JobSchema(many=False)

    job_schema.load(job_data, session=db.session)

    # Check validity
    try:
        job_schema.load(job_data)
    except:
        return Response(status=400)

    job_data['submission_date'] = parser.parse(job_data['submission_date'])
    job_to_add = Job(**job_data)

    db.session.add(job_to_add)
    db.session.commit()

    return Response(status=201)

def get_job(id):
    """
    Function for api endpoint api/jobs/{id}

    Parameters
    ----------
    id : the ID of the job to return
    """
    if not isinstance(id, int):
        return Response(status=400)

    job = Job.query.get(id)

    if job is None:
        return Response(status=404)

    job_schema = JobSchema(many=False)
    return job_schema.dump(job), 200

def get_job_files(id, file_path=None):
    """
    Function for api endpoint api/jobs/{id}/files

    Parameters
    ----------
    id : the ID of the job to return
    """

    job_info, status = get_job(id)

    if file_path is None:
        js_tree = []

        path = job_info['path']

        base_dir = os.path.split(path)[1]

        used_ids = []

        js_tree.append({
            'id': path,
            'parent': '#',
            'text': base_dir,
            'state': {
            'opened': "true",
            'selected': "true",
            },
            'icon': file_icons['folder'],
        })

        for root, dirs, files in os.walk(path):
            parent = root
            
            for name in sorted(files):

                extension = name.split('.')[-1]

                encoded_path = urllib.parse.quote(os.path.join(root, name), safe='')
                    
                js_tree.append({
                    'id': encoded_path,
                    'parent': parent,
                    'text': name,
                    'a_attr': {'href': f'api/jobs/{id}/files?file_path={encoded_path}', 'class': 'file'},
                    'icon': [file_icons[extension] if extension in file_icons.keys() else file_icons['other'] ][0],
                    
                })
                
            for name in sorted(dirs):
                js_tree.append({
                'id': os.path.join(root,name),
                'parent': parent,
                'text': name,
                'icon': file_icons['folder']
            })
        return js_tree

    else:
        unencoded_path = urllib.parse.unquote(file_path)

        return send_file(unencoded_path)
    

