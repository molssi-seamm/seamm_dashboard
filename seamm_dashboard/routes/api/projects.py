"""
API calls for projects
"""

import logging

from flask import Response
from flask_jwt_extended import jwt_required

from seamm_dashboard import db, authorize
import seamm_datastore.api
from seamm_datastore.database.models import Project, Job
from seamm_datastore.database.schema import JobSchema, ProjectSchema

logger = logging.getLogger(__name__)

__all__ = [
    "get_projects",
    "add_project",
    "get_project",
    "get_project_jobs",
    "list_projects",
]


@jwt_required(optional=True)
def get_projects(action="read", description=None, limit=None):

    logger.info(f"get_projects {action=} {description=} {limit=}")
    result = seamm_datastore.api.get_projects(action=action, as_json=True)
    logger.info(f"returning {len(result)} projects")
    logger.debug(f"{result=}")

    return result, 200


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
        owner : str
            The owner of the project. If not present defaults to the current logged in
             user.
    """
    from flask_jwt_extended import current_user

    logger.debug("Adding a project. Items in the body are:")
    for key, value in body.items():
        logger.debug("  {:15s}: '{}'".format(key, str(value)[:20]))

    name = body["name"]
    description = body["description"] if "description" in body else None
    owner = body["owner"] if "owner" in body else None

    seamm_datastore.api.add_project(
        db.session,
        name,
        owner=owner,
        description=description,
        current_user=current_user,
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


@jwt_required(optional=True)
def list_projects(action="read", limit=None, offset=None):
    """
    Function for api endpoint api/projects/list

    Parameters
    ----------
    limit : int = None
        How many project names to return
    offset : into = None
        The first project name to return, in the full list

    Returns
    -------

    """
    projects = seamm_datastore.api.list_projects(limit=limit, offset=offset)
    return projects, 200
