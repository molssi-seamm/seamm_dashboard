import os
import glob

from datetime import datetime
import logging

from app.models import Flowchart, Job, Project, JobProject
from app.models.util import process_flowchart, process_job

from app import db

logger = logging.getLogger()


def add_flowchart(flowchart_path):
    """Parse flowchart and add to data store.

    Parameters
    ----------
    flowchart_path : str
        The path to the flowchart to be added to the data store.
    """

    # Validate flowchart path
    flowchart_info = process_flowchart(flowchart_path)

    # Store the flowchart info
    flowchart = Flowchart(**flowchart_info)

    found = db.session.query(Flowchart).filter_by(id=flowchart_info['id']).all()
    if not found:
        db.session.add(flowchart)
    

def add_job(job_path, job_name):
    """Add a job to the datastore. A unique job is based on directory location.
    
    If job_path does not have a .flow file, it is skipped and not added to the datastore.

    Parameters
    ----------
    job_path : str
        The directory containing the job to be added to the datastore.
    """

    job_info = process_job(job_path)

    if job_info:
        flowchart_path = job_info.pop('flowchart_path')
        job = Job(**job_info)

        # Check if job is in DB
        found = db.session.query(Job).filter_by(path=job.path).all()

        if not found:
            add_flowchart(flowchart_path)
            db.session.add(job)
            db.session.commit()
    else:
        print("No job found in directory {}. No job added to data store".format(job_path))

def add_project(project_path, project_name):
    """
    Add a project to datastore.
    """

    project = Project(path=project_path, name=project_name)

    # Check if in DB
    found = db.session.query(Project).filter_by(name=project.name, path=project.path).all()

    if not found:
        db.session.add(project)
        db.session.commit()

def create_datastore(location):

    n_projects = 0
    n_jobs = 0
    for potential_project in os.listdir(location):
        potential_project = os.path.join(location, potential_project)

        if os.path.isdir(potential_project):
            n_projects += 1
            project_name = os.path.basename(potential_project)
            logger.debug('Adding project {}'.format(project_name))
            add_project(potential_project, project_name)
        
            for potential_job in os.listdir(potential_project):
                
                potential_job = os.path.join(potential_project, potential_job)
                job_name = os.path.basename(potential_job)
            
                if os.path.isdir(potential_job):
                    n_jobs += 1
                    job_name = os.path.basename(potential_job)
                    logger.debug('       job {}'.format(job_name))
                    add_job(potential_job, job_name)
    return (n_projects, n_jobs)
