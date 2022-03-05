"""
API calls for jobs.
"""

import os
import shutil
from datetime import datetime, timezone
import fasteners
import json
import logging
from pathlib import Path
import re
import urllib.parse
import tempfile

from flask import send_from_directory, Response, request
from flask_jwt_extended import jwt_required, get_current_user

from seamm_dashboard import db, datastore, options
from seamm_datastore.database.models import Job, Role
from seamm_datastore.database.schema import JobSchema

from seamm_datastore.util import NotAuthorizedError

logger = logging.getLogger("__file__")

__all__ = [
    "add_file_to_job",
    "get_jobs",
    "get_job",
    "get_job_files",
    "download_job_files",
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
def get_jobs(
    permission="read",
    description=None,
    title=None,
    offset=None,
    limit=None,
    sortby="id",
    order="asc",
    only="all",
):
    """
    Function for API endpoint /api/jobs
    """

    jobs = Job.get(
        permission=permission,
        description=description,
        title=title,
        offset=offset,
        limit=limit,
        sort_by=sortby,
        order=order,
        only=only,
    )

    jobs = JobSchema(many=True).dump(jobs)

    return jobs


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

    The body contains:

        flowchart : str
            The flowchart
        project : [str]
            The projects associated with this job.
        title : str
            The title of the job (<100 chars)
        description : str
            A longer description of the job.
    """

    logger.debug("Adding a job. Items in the body are:")
    for key, value in body.items():
        logger.debug("  {:15s}: {}".format(key, str(value)[:20]))
    flowchart = body["flowchart"]
    project_names = [body["project"]]
    title = body["title"]
    description = body["description"]
    if "parameters" in body:
        parameters = body["parameters"]
        if "cmdline" not in parameters:
            parameters["cmdline"] = []
    else:
        parameters = {"cmdline": []}
    # Get the unique ID for the job...
    if options["job_id_file"] is None:
        job_id_file = os.path.join(datastore, "job.id")
    else:
        job_id_file = options["job_id_file"]
    job_id = get_job_id(job_id_file)

    # Create the directory and write the flowchart to it.
    project_path = Path(datastore).expanduser() / "projects" / project_names[0]
    directory = project_path / "Job_{:06d}".format(job_id)
    logger.info("Writing job files to " + str(directory))
    directory.mkdir(parents=True, exist_ok=True)

    path = directory / "flowchart.flow"
    with path.open("w") as fd:
        fd.write(flowchart)
    flowchart_file = str(path)

    # Write the json data file for the job
    data = {
        "data_version": "1.0",
        "command line": parameters["cmdline"],
        "title": body["title"],
        "working directory": str(directory),
        "state": "submitted",
        "projects": project_names,
        "datastore": datastore,
        "job id": job_id,
        "submitted": datetime.now(timezone.utc).isoformat(),
    }
    path = directory / "job_data.json"
    with path.open("w") as fd:
        fd.write("!MolSSI job_data 1.0\n")
        json.dump(data, fd, sort_keys=True, indent=3)

    job = Job.create(
        job_id,
        path=str(directory),
        flowchart_filename=flowchart_file,
        project_names=project_names,
        title=title,
        description=description,
        parameters=parameters,
    )

    db.session.add(job)
    db.session.commit()

    job = JobSchema(many=False).dump(job)

    return job, 201


@jwt_required(optional=True)
def get_job(id):
    """
    Function for api endpoint api/jobs/{id}

    Parameters
    ----------
    id : the ID of the job to return
    """

    try:
        id = int(id)
    except ValueError:
        return Response(status=400)

    try:
        job = Job.get_by_id(id)
    except NotAuthorizedError:
        return Response("You are not authorized to view this content.", status=401)

    if job is None:
        return Response(status=404)

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
    from seamm_datastore.util import NotAuthorizedError

    try:
        job = Job.get_by_id(id, permission="update")
    except NotAuthorizedError:
        return Response(status=401)

    if job is None:
        return Response(status=404)

    jobu = job.update(id=id, **body)
    db.session.add(jobu)
    db.session.commit()

    return Response(status=204)


@jwt_required(optional=True)
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
    try:
        job = Job.get_by_id(id, permission="delete")
    except NotAuthorizedError:
        admin_role = Role.query.filter(Role.name == "admin").one()
        current = get_current_user()
        if current is None or admin_role not in current.roles:
            return Response(status=401)
        else:
            job = Job.query.get(id)

    if not job:
        return Response(status=404)

    from seamm_dashboard import datastore

    path = job.path

    # Ensure that job path is absolute
    # and that it shares a base directory
    # with the datastore
    if not os.path.isabs(path) or os.path.commonprefix([datastore, path]) != datastore:
        return Response(status=401)

    job_path = Path(path)

    # Remove job files if they exist
    if job_path.exists():
        shutil.rmtree(job_path)

    # Remove job info from DB
    db.session.delete(job)
    db.session.commit()

    return Response(status=200)


@jwt_required(optional=True)
def get_job_files(id):
    """
    Function for get method of api endpoint api/jobs/{id}/files.

    Parameters
    ----------
    id : int
        the ID of the job to return
    """
    try:
        job = Job.get_by_id(id)
    except NotAuthorizedError:
        return Response(status=401)

    js_tree = []

    path = job.path

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
        safe = parent.replace(job.path, "")[1:]

        for name in sorted(files):

            extension = name.split(".")[-1]

            encoded_path = urllib.parse.quote(os.path.join(root, name), safe="")
            safe_encode = urllib.parse.quote(os.path.join(safe, name), safe="")

            js_tree.append(
                {
                    "id": encoded_path,
                    "parent": parent,
                    "text": name,
                    "a_attr": {
                        "href": f"api/jobs/{id}/files/download?filename={safe_encode}",
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


@jwt_required(optional=True)
def download_job_files(id, filename=None):
    """
    Function for get method of api endpoint api/jobs/{id}/files/download.

    Without a query, will return zip file of job directory.
    With query, returns specified file.

    Parameters
    ----------
    id : int
        the ID of the job to return
    """

    try:
        job = Job.get_by_id(id)
    except NotAuthorizedError:
        return Response(status=401)

    path = job.path
    path, job_directory = os.path.split(path)

    if filename is None:
        # Create zip file in temporary directory and send.
        tmpdir = tempfile.mkdtemp()
        tmpzip = os.path.join(tmpdir, job_directory)
        shutil.make_archive(f"{tmpzip}", "zip", job.path)
        return send_from_directory(
            tmpdir, path=f"{job_directory}.zip", as_attachment=True
        )
    else:
        if "../" in filename:
            return Response(status=401)
        unencoded_path = urllib.parse.unquote(filename)
        return send_from_directory(job.path, path=unencoded_path, as_attachment=True)


@jwt_required(optional=True)
def add_file_to_job(body, id=None):
    """Add a new file to a job

    Parameters
    ----------
    body : dict
        The description of the file.

    Returns
    -------
    The job id (integer)
    """
    job_info, status = get_job(id)
    root = Path(job_info["path"])

    file_data = request.files["file"]
    filename = file_data.filename

    if filename[0:4] == "job:":
        filename = filename[4:]

    path = root / filename
    path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Saving file to {root / filename}")
    file_data.save(root / filename)

    return {"path": str(root / filename)}, 201
