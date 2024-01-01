"""Utility functions to simplify life.
"""

from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import re

import fasteners

from seamm_dashboard import db, datastore, options
from seamm_datastore.database.models import Job

logger = logging.getLogger("__file__")


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


def safe_filename(filename):
    # Make a single filename for a file transferred for a job
    if filename[0] == "~":
        path = Path(filename).expanduser()
    else:
        path = Path(filename)
    if path.anchor == "":
        result = "_".join(path.parts)
    else:
        result = "_".join(path.parts[1:])
    return "job:data/" + result


def setup_job(flowchart, project_names, title, description, parameters):
    """Add a new job to the queue.

    Parameters
    ----------
    flowchart : str
        The flowchart
    project_names : [str]
        The projects associated with this job.
    title : str
        The title of the job (<100 chars)
    description : str
        A longer description of the job.
    parameters : {str: ....}
        The parameters, including command line, for the job.

    Returns
    -------
    The job object
    """

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
        "title": title,
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

    return job
