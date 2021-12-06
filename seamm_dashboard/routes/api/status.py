"""
API calls for the status
"""
import logging

from seamm_dashboard import db

from seamm_datastore import api
from seamm_datastore.database.models import Project, Job, Flowchart
from seamm_datastore.database.schema import RoleSchema

from sqlalchemy import and_, func

from flask_jwt_extended import get_current_user, jwt_required

logger = logging.getLogger("__file__")

__all__ = ["status"]


@jwt_required(optional=True)
def status():
    """The status of the dashboard.

    Currently always 'running', but in the future other
    values may be added.

    """
    current_user = get_current_user()

    try:
        username = current_user.username
    except AttributeError:
        username = "Anonymous User"

    if username != "Anonymous User":
        user_id = current_user.id
        roles = current_user.roles
        role_schema = RoleSchema(many=True)
        roles = role_schema.dump(roles)

        user_roles = []
        for role in roles:
            user_roles.append(role["name"])
    else:
        user_roles = []
        user_id = None

    # Get information about jobs, projects, flowcharts
    num_jobs = api.get_jobs(count=True)
    num_jobs_running = api.get_jobs(count=True, status="running")
    num_jobs_finished = api.get_jobs(count=True, status="finished")
    num_jobs_queued = api.get_jobs(count=True, status="submitted")

    flowcharts = api.get_flowcharts()
    num_flowcharts = len(flowcharts)
    num_projects = len(api.get_projects())

    # Build return json
    status = {
        "status": "running",
        "user id": user_id,
        "username": username,
        "roles": user_roles,
        "jobs": {
            "total": num_jobs,
            "running": num_jobs_running,
            "finished": num_jobs_finished,
            "queued": num_jobs_queued,
        },
        "flowcharts": num_flowcharts,
        "projects": num_projects,
    }

    return status, 200
