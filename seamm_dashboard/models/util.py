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

from . import User, Group, Role
from seamm_dashboard import db

logger = logging.getLogger(__name__)

time_format = "%Y-%m-%d %H:%M:%S %Z"


def process_flowchart(flowchart_path):
    """Read in flowchart from file and process for addition to SEAMM datastore.

    Parameters
    ----------
        flowchart_path: str
            The location of the flowchart

    Returns
    -------
        flowchart_info: dict
            Dictionary of flowchart information.
    """
    flowchart_info = {}

    flowchart_info["path"] = os.path.abspath(flowchart_path)

    # Get the flowchart text
    with open(flowchart_path, "r") as f:
        flowchart_info["text"] = f.read()

    # Get the flowchart description
    with open(flowchart_path) as f:
        f.readline()
        f.readline()
        flowchart_info["json"] = json.load(f)

    # Get a hash of the flowchart contents
    flowchart_info["id"] = hashlib.md5(
        flowchart_info["text"].encode("utf-8")
    ).hexdigest()

    # Get the flowchart description.
    try:
        node0 = flowchart_info["json"]["nodes"][0]
        flowchart_info["description"] = node0["attributes"]["_description"]
    except KeyError:
        flowchart_info["description"] = "No description given."
    except Exception:
        flowchart_info["description"] = "The flowchart may be corrupted."

    return flowchart_info


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

            if "title" in data:
                job_info["title"] = data["title"]
            if "state" in data:
                job_info["status"] = data["state"]
            else:
                job_info["status"] = "unknown"
            if "start time" in data:
                job_info["submitted"] = datetime.strptime(
                    data["start time"], time_format
                )
                job_info["started"] = datetime.strptime(data["start time"], time_format)
            if "end time" in data:
                job_info["finished"] = datetime.strptime(data["end time"], time_format)
        except Exception as e:
            logger.warning("Encountered error reading job {}".format(job_path))
            logger.warning("Error: {}".format(e))

    job_info["flowchart_id"] = flowchart_info["id"]
    job_info["path"] = os.path.abspath(job_path)
    job_info["flowchart_path"] = flowchart_info["path"]

    # Attempt to read job ID from file path
    dir_name = os.path.basename(job_path)
    job_id = dir_name.split("_")[1].lstrip("0")
    job_info["id"] = int(job_id)

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
