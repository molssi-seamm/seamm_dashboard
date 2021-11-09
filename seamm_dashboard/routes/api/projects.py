"""
API calls for projects
"""

import logging

from flask import Response
from flask_jwt_extended import jwt_required
from sqlalchemy import and_

from seamm_dashboard import db, authorize
import seamm_datastore.api
from seamm_datastore.database.models import Project, Job
from seamm_datastore.database.schema import JobSchema, ProjectSchema

logger = logging.getLogger("__file__")

__all__ = ["get_projects", "add_project", "get_project", "get_project_jobs"]


@jwt_required(optional=True)
def get_projects(description=None, limit=None):

    # If limit is not set, set limit to all jobs in DB.
    if limit is None:
        limit = Project.query.count()
    if description is not None:
        projects = Project.query.filter(
            and_(Project.authorized("read"), Project.description.contains(description))
        ).limit(limit)
    else:
        projects = Project.query.filter(Project.authorized("read")).limit(limit)

    projects_schema = ProjectSchema(many=True)

    return projects_schema.dump(projects), 200


@jwt_required(optional=True)
def add_project(body):
    """Add a new project

    Parameters
    ----------
    body : dict
        The description of the project.

    Returns
    -------
    str
        The project name

    The body contains:

        name : str
            The name of the project
        description : str
            A longer description of the project.
    """

    logger.debug("Adding a project. Items in the body are:")
    for key, value in body.items():
        logger.debug("  {:15s}: {}".format(key, str(value)[:20]))

    name = body["name"]
    if "description" in body:
        description = body["description"]
    else:
        description = ""

    seamm_datastore.api.add_project(
        db.session,
        name,
        description,
    )

    return {"name": name}, 201


@jwt_required(optional=True)
def get_project(id):
    """
    Function for api endpoint api/projects/{id}

    Parameters
    ----------
    id : the ID of the project to return
    """
    project = Project.query.get(id)

    if project is None:
        return Response(status=404)

    if not authorize.read(project):
        return Response("You are not authorized to access this content.", status=401)

    project_schema = ProjectSchema(many=False)
    return project_schema.dump(project), 200


@jwt_required(optional=True)
def get_project_jobs(id):
    """
    Function for api endpoint api/projects/{id}/jobs. Get jobs associated with a
    project.

    Parameters
    ----------
    id : the ID of the project to return
    """

    project = Project.query.get(id)

    if project is None:
        return Response(status=404)

    if not authorize.read(project):
        return Response("You are not authorized to access this content.", status=401)

    jobs = []
    for job in project.jobs:
        jobs.append(Job.query.get(job.id))

    jobs_schema = JobSchema(many=True)

    return jobs_schema.dump(jobs), 200
