"""
API calls for jobs.
"""

import os
import shutil
from datetime import datetime
import fasteners
import hashlib
import json
import logging
from pathlib import Path
import re
import urllib.parse

from marshmallow import ValidationError
from sqlalchemy import and_
from flask import send_from_directory, Response
from flask_jwt_extended import jwt_required

from seamm_dashboard import db, datastore, authorize, options
from seamm_dashboard.models import User, Project, Job, JobSchema, Flowchart
from seamm_dashboard.models import FlowchartSchema

logger = logging.getLogger("__file__")

__all__ = [
    "get_jobs",
    "get_job",
    "get_job_files",
    "add_job",
    "update_job",
    "delete_job",
]

file_icons = {
    "graph": "fas fa-chart-line",
    "csv": "fas fa-table",
    "flow": "fas fa-project-diagram",
    "other": "far fa-file-alt",
    "folder": "far fa-folder-open",
    "pdb": "fas fa-cubes",
    "mmcif": "fas fa-cubes",
    "cif": "fas fa-cubes",
}


@jwt_required(optional=True)
def get_jobs(createdSince=None, createdBefore=None, limit=None):
    """
    Function for API endpoint /api/jobs

    Parameters
    ----------
    createdSince: str
        Return jobs created after this date. Must be in format M-D-YYYY where M all
        numbers are integers.
    createdBefore:str
        Return jobs created before this date. Must be in format M-D-YYYY where M all
        numbers are integers.
    limit: int
        The maximum number of jobs to return.

    """

    # Handle dates
    if createdSince is not None:
        createdSince = datetime.strptime(createdSince, "%m-%d-%Y")
    else:
        # Basically all times
        createdSince = datetime.strptime("1-1-0001", "%m-%d-%Y")

    if createdBefore is not None:
        createdBefore = datetime.strptime(createdBefore, "%m-%d-%Y")
    else:
        # Up to now.
        createdBefore = datetime.utcnow()

    # If limit is not set, set limit to all jobs in DB.
    if limit is None:
        limit = Job.query.count()

    jobs = Job.query.filter(
        and_(Job.submitted > createdSince, Job.submitted < createdBefore),
        Job.authorized("read"),
    ).limit(limit)

    jobs_schema = JobSchema(many=True)

    return jobs_schema.dump(jobs), 200


def get_job_id(filename):
    """Get the next job id from the given file.

    This uses the fasteners module to provide locking so that
    only one job at a time can access the file, so that the job
    ids are unique and monotonically increasing.
    """

    filename = os.path.expanduser(filename)

    lock_file = filename + ".lock"
    lock = fasteners.InterProcessLock(lock_file)
    locked = lock.acquire(blocking=True, timeout=5)

    if locked:
        if not os.path.isfile(filename):
            job_id = 1
            with open(filename, "w") as fd:
                fd.write("!MolSSI job_id 1.0\n")
                fd.write("1\n")
            lock.release()
        else:
            with open(filename, "r+") as fd:
                line = fd.readline()
                pos = fd.tell()
                if line == "":
                    lock.release()
                    raise EOFError("job_id file '{}' is empty".format(filename))
                line = line.strip()
                match = re.fullmatch(r"!MolSSI job_id ([0-9]+(?:\.[0-9]+)*)", line)
                if match is None:
                    lock.release()
                    raise RuntimeError(
                        "The job_id file has an incorrect header: {}".format(line)
                    )
                line = fd.readline()
                if line == "":
                    lock.release()
                    raise EOFError("job_id file '{}' is truncated".format(filename))
                try:
                    job_id = int(line)
                except TypeError:
                    raise TypeError(
                        "The job_id in file '{}' is not an integer: {}".format(
                            filename, line
                        )
                    )
                job_id += 1
                fd.seek(pos)
                fd.write("{:d}\n".format(job_id))
    else:
        raise RuntimeError("Could not lock the job_id file '{}'".format(filename))

    return job_id


@jwt_required(optional=True)
def add_job(body):
    """Add a new job to the queue.

    Parameters
    ----------
    body : dict
        The description of the job.

    Returns
    -------
    The job id (integer)
    """

    logger.debug("Adding a job. Items in the body are:")
    for key, value in body.items():
        logger.debug("  {:15s}: {}".format(key, str(value)[:20]))

    # Get the project
    project_name = body.pop("project")
    project = db.session.query(Project).filter_by(name=project_name).one_or_none()
    if project is None:
        return "There is no project '{}'".format(project_name), 403

    logger.debug("  project = {}".format(project.id))

    # Get the user...
    username = body.pop("username")
    user = db.session.query(User).filter_by(username=username).one_or_none()
    if user is None:
        return "User '{}' is not registered".format(username), 403
    user_id = user.id
    group_id = user.groups[0].id
    body["owner"] = user_id
    body["group"] = group_id

    logger.debug("  user {} is {}:{}".format(username, user_id, group_id))

    # Get the flowchart and put it in place
    flowchart_text = body.pop("flowchart")
    flowchart_data = {
        "id": hashlib.md5(flowchart_text.encode("utf-8")).hexdigest(),
        "owner_id": user_id,
        "group_id": group_id,
        "description": "No description given.",
    }

    # Validate and deserialize the flowchart data
    flowchart_schema = FlowchartSchema(many=False)
    try:
        flowchart_schema.load(flowchart_data, session=db.session)
    except ValidationError as err:
        logger.error("ValidationError (flowchart): {}".format(err.messages))
        logger.info("   valid data: {}".format(err.valid_data))
        return err.messages, 422

    # See if it already in the db, if not, add it
    flowchart_is_new = False
    flowchart = (
        db.session.query(Flowchart).filter_by(id=flowchart_data["id"]).one_or_none()
    )
    if flowchart:
        if project not in flowchart.projects:
            flowchart.projects.append(project)
            db.session.commit()

    else:
        flowchart = Flowchart(
            **flowchart_data,
            text=flowchart_text,
            json="\n".join(flowchart_text.splitlines()[2:]),
        )
        flowchart.projects.append(project)
        db.session.add(flowchart)
        db.session.commit()
        flowchart_is_new = True

    # Validate and deserialize the job data
    body["status"] = "Submitted"
    body["flowchart_id"] = flowchart.id

    job_schema = JobSchema(many=False)
    try:
        job_schema.load(body, session=db.session)
    except ValidationError as err:
        logger.error("ValidationError (job): {}".format(err.messages))
        logger.info("   valid data: {}".format(err.valid_data))
        return err.messages, 422

    # Need objects, not ids?
    # body["flowchart_id"] = flowchart
    body["owner"] = user
    body["group"] = user.groups[0]

    job = Job(**body)

    # Get the unique ID for the job...

    if options["job_id_file"] is None:
        job_id_file = os.path.join(datastore, "job.id")
    else:
        job_id_file = options["job_id_file"]
    job.id = get_job_id(job_id_file)

    # And the path
    project_path = Path(datastore).expanduser() / "projects" / project_name
    directory = project_path / "Job_{:06d}".format(job.id)
    print("Writing job files to " + str(directory))
    directory.mkdir(parents=True, exist_ok=True)
    job.path = str(directory)

    # Finally add the job to the database.
    db.session.add(job)
    job.projects.append(project)

    db.session.commit()

    path = directory / "flowchart.flow"
    with path.open("w") as fd:
        fd.write(flowchart_text)
    if flowchart_is_new:
        flowchart.path = str(path)

    db.session.commit()

    # Write the json data file for the job
    data = {
        "command line": "",
        "title": body["title"],
        "working directory": str(directory),
        "state": "Submitted",
        "projects": [project_name],
        "datastore": datastore,
        "job id": job.id,
    }
    path = directory / "job_data.json"
    with path.open("w") as fd:
        json.dump(data, fd, sort_keys=True, indent=3)

    return {"id": job.id}, 201, {"location": format("/jobs/{}".format(job.id))}


@jwt_required(optional=True)
def get_job(id):
    """
    Function for api endpoint api/jobs/{id}

    Parameters
    ----------
    id : the ID of the job to return
    """
    if not isinstance(id, int):
        return Response(status=400)

    job = Job.query.get(id)

    if job is None:
        return Response(status=404)

    if not authorize.read(job):
        return Response("You are not authorized to view this content.", status=401)

    job_schema = JobSchema(many=False)
    return job_schema.dump(job), 200


@jwt_required(optional=True)
def update_job(id, body):
    """
    Function to update jobs - endpoint api/jobs/{id}

    Parameters
    ----------
    id : int
        The ID of the job to update

    body : json
        The job information to update.
    """
    job = Job.query.get(id)

    if not job:
        return Response(status=404)

    if not authorize.update(job):
        return Response(status=401)

    for key, value in body.items():
        if key == "submitted" or key == "finished" or key == "started":
            if value:
                # This assumes the timestamp is in format from javascript Date.now()
                # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/now
                # Number of milliseconds since January 1, 1970
                value = datetime.fromtimestamp(value / 1000)
            else:
                value = None
        setattr(job, key, value)

    db.session.commit()

    return Response(status=201)


@jwt_required(optional=True)
@authorize.has_role("admin")
def delete_job(id):
    """
    Function for delete method of api endpoint api/jobs/{id}

    This api route removes the job from the DB and deletes the associated job files
    from disk

    Parameters
    ----------
    id : int
        The ID of the job to delete

    Returns
    -------
    status : int
        Response code for operation. 200 = successful, 404 = job not found.
    """
    job = Job.query.get(id)
    print("deleting job")

    if not job:
        return Response(status=404)
    else:
        path = job.path
        job_path = Path(path)

        # Remove job files if they exist
        if job_path.exists():
            shutil.rmtree(job_path)

        # Remove job info from DB
        db.session.delete(job)
        db.session.commit()

        return Response(status=200)


@jwt_required(optional=True)
def get_job_files(id, file_path=None):
    """
    Function for get method of api endpoint api/jobs/{id}/files. If the file_path
    parameter is used, this endpoint will send the file which is indicated by the path.

    Parameters
    ----------
    id : int
        the ID of the job to return

    file_path : string
        The encoded file path for the file to return.
    """

    job_info, status = get_job(id)

    if file_path is None:
        js_tree = []

        path = job_info["path"]

        base_dir = os.path.split(path)[1]

        js_tree.append(
            {
                "id": path,
                "parent": "#",
                "text": base_dir,
                "state": {
                    "opened": "true",
                    "selected": "true",
                },
                "icon": file_icons["folder"],
            }
        )

        for root, dirs, files in os.walk(path):
            parent = root

            for name in sorted(files):

                extension = name.split(".")[-1]

                encoded_path = urllib.parse.quote(os.path.join(root, name), safe="")

                js_tree.append(
                    {
                        "id": encoded_path,
                        "parent": parent,
                        "text": name,
                        "a_attr": {
                            "href": f"api/jobs/{id}/files?file_path={encoded_path}",
                            "class": "file",
                        },
                        "icon": [
                            file_icons[extension]
                            if extension in file_icons.keys()
                            else file_icons["other"]
                        ][0],
                    }
                )

            for name in sorted(dirs):
                js_tree.append(
                    {
                        "id": os.path.join(root, name),
                        "parent": parent,
                        "text": name,
                        "icon": file_icons["folder"],
                    }
                )
        return js_tree

    else:
        unencoded_path = urllib.parse.unquote(file_path)
        directory, file_name = os.path.split(unencoded_path)
        return send_from_directory(directory, path=file_name, as_attachment=True)
