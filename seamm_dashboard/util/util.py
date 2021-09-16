"""
util.py

Utility functions.
"""

from datetime import datetime
import glob
import hashlib
import json
import logging
from pathlib import Path
import os

from seamm_datastore.database.models import User, Group, Role
from seamm_dashboard import db, jwt

logger = logging.getLogger(__name__)

time_format = "%Y-%m-%d %H:%M:%S %Z"

@jwt.user_lookup_loader
def user_loader_callback(jwt_header, jwt_payload):
    """Function for app, to return user object"""

    if jwt_header:
        from seamm_datastore.database.models import User

        username = jwt_payload["sub"]["username"]
        user = User.query.filter_by(username=username).one_or_none()

        return user
    else:
        # return None / null
        return None

def process_flowchart(path):
    """
    Function for parsing information from flowchart
    
    Parameters
    ----------
    path: str
        The path to the flowchart.

    Returns
    -------
    flowchart_info: dict
        A json containing flowchart information to be added to the database.
    """

    import re

    with open(path) as f:
        f.readline()
        version_info = " " + f.readline().split()[-1]
        text = f.read()

    if " 1." in version_info:
        metadata_pattern = None
        flowchart_pattern = re.compile("\{.+\}", re.DOTALL)
    elif " 2." in version_info:
        # Flowchart is version 2.
        metadata_pattern = re.compile("#metadata\n(\{.+?\})\n#", re.DOTALL)
        flowchart_pattern = re.compile("#flowchart\n(\{.+\})\n#", re.DOTALL)
    else:
        # TODO Maybe raise custom exception. SEAMM Flowchart version error
        # Value Error for now
        raise ValueError
    
    # Handle the metadata
    if metadata_pattern:
        metadata = json.loads(metadata_pattern.findall(text)[0])
    else:
        metadata = {}

    metadata["flowchart_version"] = float(version_info)
    flowchart = {"json":flowchart_pattern.findall(text)[0]}

    flowchart.update(metadata)
    flowchart["id"] = hashlib.md5(
        text.encode("utf-8")
    ).hexdigest()
    flowchart["path"] = path

    return flowchart

def _read_job_data(job_data):
    """Function for reading job data from job_data.json"""

    job_info = {"description": ""}

    if "title" in job_data:
        job_info["title"] = job_data["title"]
    if "state" in job_data:
        job_info["status"] = job_data["state"]
    else:
        job_info["status"] = "unknown"
    if "start time" in job_data:
        job_info["submitted"] = datetime.strptime(job_data["start time"], time_format)
        job_info["started"] = datetime.strptime(job_data["start time"], time_format)
    if "end time" in job_data:
        job_info["finished"] = datetime.strptime(job_data["end time"], time_format)
    if "working directory" in job_data:
        job_info["path"] = job_data["working directory"]
    if "job id" in job_data:
        job_info["id"] = job_data["job id"]

    return job_info


def process_job(job_path):
    """Process path for adding job to datastore.

    Parameters
    ----------
        job_path: str
            Path to directory job is in.

    Returns
    -------
        job_info: dict
            The job information to be added to the datastore.
    """

    job_info = {"description": ""}

    # Look for a flowchart in the job path
    flow_path = os.path.join(job_path, "*.flow")
    flowchart = glob.glob(flow_path)

    if len(flowchart) > 1:
        raise ValueError("More than one flowchart found! Cannot add job.")

    if len(flowchart) < 1:
        # If no flowchart is found - not a job - can't store. Return None
        return None

    flowchart_info = process_flowchart(flowchart[0])

    # If there is a job_data.json file, extract data
    data_file = os.path.join(job_path, "job_data.json")
    if os.path.exists(data_file):
        try:
            with open(data_file, "r") as fd:
                data = json.load(fd)
            job_info = _read_job_data(data)

        except Exception as e:
            logger.warning("Encountered error reading job {}".format(job_path))
            logger.warning("Error: {}".format(e))

    job_info["flowchart_id"] = flowchart_info["id"]
    job_info["path"] = os.path.abspath(job_path)
    job_info["flowchart_path"] = flowchart_info["path"]

    return job_info


def file_owner(path):
    """Return the User object for the owner of a file or directory.

    The User is created if it does not exist.

    Parameters:
    -----------
    path : str or path
        The directory or file to check.

    Returns
    -------
    User object
    """

    item = Path(path)
    if item.exists():
        # Get the group first
        name = item.group()
        group = db.session.query(Group).filter_by(name=name).one_or_none()
        if group is None:
            group = Group(name=name)
            db.session.add(group)
            db.session.commit()

        # and now the user
        name = item.owner()
        user = db.session.query(User).filter_by(username=name).one_or_none()
        if user is None:
            admin_role = db.session.query(Role).filter_by(name="admin").one_or_none()

            if admin_role is None:
                admin_role = Role(name="admin")

            user = User(username=name, password="default", roles=[admin_role])
            user.groups.append(group)
            db.session.add(user)
            db.session.add(admin_role)
            db.session.add(group)
            db.session.commit()
        return user.id, group.id
    else:
        return None
