"""
API calls for projects
"""

from flask import Response
from flask_jwt_extended import jwt_required
from sqlalchemy import and_

from seamm_dashboard.models import Project, ProjectSchema, Job, JobSchema
from seamm_dashboard import authorize

__all__ = ["get_projects", "get_project", "get_project_jobs"]


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
