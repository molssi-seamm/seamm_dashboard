"""
API calls for projects
"""

import logging
import os
import shutil

from pathlib import Path

from flask import Response
from flask_jwt_extended import jwt_required

from seamm_dashboard import datastore, db
from seamm_datastore.database.models import Project
from seamm_datastore.database.schema import JobSchema, ProjectSchema

from seamm_datastore.util import NotAuthorizedError


logger = logging.getLogger(__name__)

__all__ = [
    "get_projects",
    "add_project",
    "get_project",
    "get_project_jobs",
    "list_projects",
    "update_project",
    "delete_project",
]


@jwt_required(optional=True)
def update_project(id, body):
    from seamm_datastore.util import NotAuthorizedError

    try:
        project = Project.get_by_id(id, permission="update")
    except NotAuthorizedError:
        return Response(status=401)

    if project is None:
        return Response(status=404)

    project.update(id, **body)

    return Response(status=201)


@jwt_required(optional=True)
def delete_project(id):
    try:
        project = Project.get_by_id(id, permission="delete")
    except NotAuthorizedError:
        return Response(status=403)

    if not project:
        return Response(status=404)

    from seamm_dashboard import datastore

    path = project.path

    # Ensure that job path is absolute
    # and that it shares a base directory
    # with the datastore
    if not os.path.isabs(path) or os.path.commonprefix([datastore, path]) != datastore:
        return Response(status=401)

    path = project.path
    project_path = Path(path)

    # Remove job files if they exist
    if project_path.exists():
        shutil.rmtree(project_path)

    # Remove job info from DB
    db.session.delete(project)
    db.session.commit()

    return Response(status=200)


@jwt_required(optional=True)
def get_projects(
    permission="read",
    description=None,
    offset=None,
    limit=None,
    sort_by="id",
    order="asc",
):

    projects = Project.get(
        permission=permission,
        description=description,
        offset=offset,
        limit=limit,
        sort_by=sort_by,
        order=order,
    )

    projects = ProjectSchema(many=True).dump(projects)

    return projects, 200


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
    logger.debug("Adding a project. Items in the body are:")
    for key, value in body.items():
        logger.debug("  {:15s}: '{}'".format(key, str(value)[:20]))
    name = body["name"]
    description = body["description"] if "description" in body else None

    # Create a directory for the project
    project_path = Path(datastore).expanduser() / "projects" / name

    project_path.mkdir(parents=True, exist_ok=True)

    project = Project.create(name=name, description=description, path=str(project_path))
    db.session.add(project)
    db.session.commit()

    return {"name": name}, 201


@jwt_required(optional=True)
def get_project(id):
    """
    Function for api endpoint api/projects/{id}

    Parameters
    ----------
    id : the ID of the project to return
    """

    try:
        id = int(id)
    except ValueError:
        return Response(status=400)

    try:
        project = Project.get_by_id(id)
    except NotAuthorizedError:
        return Response("You are not authorized to view this content.", status=401)

    if project is None:
        return Response(status=404)

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

    try:
        id = int(id)
    except ValueError:
        return Response(status=400)

    try:
        project = Project.get_by_id(id, permission="read")
    except NotAuthorizedError:
        return Response("You are not authorized to view this content.", status=401)

    if project is None:
        return Response(status=404)

    jobs_schema = JobSchema(many=True)

    return jobs_schema.dump(project.jobs), 200


@jwt_required(optional=True)
def list_projects(
    permission="read",
    description=None,
    offset=None,
    limit=None,
    sort_by="id",
    order="asc",
):

    projects = Project.get(
        permission=permission,
        description=description,
        offset=offset,
        limit=limit,
        sort_by=sort_by,
        order=order,
        only=["name"],
    )
    project_list = [x.name for x in projects]
    return project_list, 200
