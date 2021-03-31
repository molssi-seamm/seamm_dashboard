"""
import_jobs.py

Functions to import jobs into the database
"""
import logging
import os
import sqlite3

from . import Flowchart, Job, Project
from .util import process_flowchart, process_job, file_owner

from seamm_dashboard import db

logger = logging.getLogger(__name__)


def import_jobs(location):
    """Import all the projects and jobs at <location>.

    <location> should be the path to the 'projects' directory in a datastore.
    All subdirectories will be added as projects, and the jobs within them
    added also.

    Parameters
    ----------
    location : str or path
        The projects directory in a datastore.

    Returns
    -------
    (n_projects, n_jobs) : int, integer
        The number of projects and jobs added to the database.
    """
    n_projects = 0
    n_added_projects = 0
    n_jobs = 0
    n_added_jobs = 0
    for potential_project in os.listdir(location):
        potential_project = os.path.join(location, potential_project)

        if os.path.isdir(potential_project):
            n_projects += 1
            project_name = os.path.basename(potential_project)
            logger.debug("Adding project {}".format(project_name))
            project, added = add_project(potential_project, project_name)
            if added:
                n_added_projects += 1

            for potential_job in os.listdir(potential_project):

                potential_job = os.path.join(potential_project, potential_job)

                if os.path.isdir(potential_job):
                    job_name = os.path.basename(potential_job)
                    logger.debug("       job {}".format(job_name))
                    try:
                        job, added = add_job(potential_job, job_name, project)
                    except sqlite3.IntegrityError as e:
                        logger.warning("Adding job {} failed: {}".format(job_name, e))
                    if job is None:
                        logger.debug("         was not a job!")
                    else:
                        n_jobs += 1
                        if added:
                            n_added_jobs += 1

    return (n_projects, n_added_projects, n_jobs, n_added_jobs)


def add_flowchart(flowchart_path, project):
    """Parse flowchart and add to data store if nedded.

    Analyze a flowchart and add to the database if it doesn't already exist. In
    either case return the Flowchart object.

    Parameters
    ----------
    flowchart_path : str
        The path to the flowchart to be added to the data store.
    project : Project
        The project object the flowchart belongs to.

    Returns
    -------
    Flowchart object.
    """

    # Analyze the flowchart given the path
    flowchart_info = process_flowchart(flowchart_path)

    flowchart = (
        db.session.query(Flowchart).filter_by(id=flowchart_info["id"]).one_or_none()
    )

    if flowchart is None:
        user, group = file_owner(flowchart_path)
        flowchart = Flowchart(owner_id=user, group_id=group, **flowchart_info)
        flowchart.projects.append(project)
        db.session.add(flowchart)
        db.session.commit()
    elif project not in flowchart.projects:
        flowchart.projects.append(project)
        db.session.commit()

    return flowchart


def add_job(job_path, job_name, project):
    """Add a job to the datastore. A unique job is based on directory location.

    If job_path does not have a .flow file, it is skipped and not added to the
    datastore.

    Parameters
    ----------
    job_path : str
        The directory containing the job to be added to the datastore.
    job_name : str
        The text name of the job, usually 'Job_xxxxxx'
    project : models.Project
        The Project object in the database
    """

    job_info = process_job(job_path)

    if job_info:
        flowchart_path = job_info.pop("flowchart_path")

        # Check if job is in DB
        found = db.session.query(Job).filter_by(path=job_info["path"]).one_or_none()

        if found is None:
            user, group = file_owner(job_path)
            job = Job(owner_id=user, group_id=group, **job_info)
            job.projects.append(project)

            add_flowchart(flowchart_path, project)

            db.session.add(job)
            db.session.commit()
            return job, True
        else:
            return found, False
    else:
        print(
            "No job found in directory {}. No job added to data store".format(job_path)
        )
        return None, False


def add_project(project_path, project_name):
    """
    Add a project to datastore.
    """

    # Check if in DB
    found = (
        db.session.query(Project)
        .filter_by(name=project_name, path=project_path)
        .one_or_none()
    )

    if found is None:
        user, group = file_owner(project_path)
        project = Project(
            path=project_path, name=project_name, owner_id=user, group_id=group
        )
        db.session.add(project)
        db.session.commit()
        return project, True
    else:
        return found, False
