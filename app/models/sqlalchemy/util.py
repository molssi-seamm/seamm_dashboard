"""
util.py

Utility functions.
"""

import os
import json
import glob
import hashlib

from datetime import datetime

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

    flowchart_info['path'] = os.path.abspath(flowchart_path)

    # Get the flowchart text
    with open(flowchart_path, 'r') as f:
        flowchart_info['flowchart_file'] = f.read()
    
    # Get the flowchart description
    with open(flowchart_path) as f:
        f.readline()
        f.readline()
        flowchart_info['flowchart_json'] = json.load(f)

    # Get a hash of the flowchart contents
    flowchart_info['id'] = hashlib.md5(flowchart_info['flowchart_file'].encode('utf-8')).hexdigest()

    # Get the flowchart description.
    flowchart_info['description'] = flowchart_info['flowchart_json']['nodes'][0]["attributes"]['_description']

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

    job_info = {}

    # Look for a flowchart in the job path
    flow_path = os.path.join(job_path, "*.flow")
    flowchart = glob.glob(flow_path)

    if len(flowchart) > 1:
        raise ValueError("More than one flowchart found! Cannot add job.")

    if len(flowchart) < 1:
        # If no flowchart is found - not a job - can't store. Return None
        return None

    flowchart_info = process_flowchart(flowchart[0])

    job_info['flowchart_id'] = flowchart_info['id']
    job_info['path'] = os.path.abspath(job_path)
    job_info['submission_date'] = datetime.fromtimestamp(os.path.getmtime(flowchart_info['path']))
    job_info['flowchart_path'] = flowchart_info['path']

    return job_info
