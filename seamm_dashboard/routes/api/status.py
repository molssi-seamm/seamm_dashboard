"""
API calls for the status
"""
import logging

from seamm_datastore.database.models import Project, Job, Flowchart
from seamm_datastore.database.schema import RoleSchema

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

    num_jobs = Job.permissions_query("read").count()
    num_jobs_running = Job.permissions_query("read").filter_by(status="running").count()
    num_jobs_finished = (
        Job.permissions_query("read").filter_by(status="finished").count()
    )
    num_jobs_queued = (
        Job.permissions_query("read").filter_by(status="submitted").count()
    )

    flowcharts = Flowchart.get()
    num_flowcharts = len(flowcharts)
    num_projects = len(Project.get())

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
