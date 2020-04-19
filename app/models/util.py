"""
util.py

Utility functions.
"""

from datetime import datetime
import os
import json
import glob
import hashlib
import logging


logger = logging.getLogger(__name__)

time_format = '%Y-%m-%d %H:%M:%S %Z'

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
    try:
        node0 = flowchart_info['flowchart_json']['nodes'][0]
        flowchart_info['description'] = node0["attributes"]['_description']
    except KeyError:
        flowchart_info['description'] = 'No description given.'
    except Exception:
        flowchart_info['description'] = 'The flowchart may be corrupted.'

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

    # If there is a job_data.json file, extract data
    data_file = os.path.join(job_path, 'job_data.json')
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as fd:
                data = json.load(fd)
            
            if 'title' in data:
                job_info['title'] = data['title']
            if 'state' in data:
                job_info['status'] = data['state']
            else:
                job_info['status'] = 'unknown'
            if 'start time' in data:
                job_info['submitted'] = datetime.strptime(data['start time'], time_format)
                job_info['started'] = datetime.strptime(data['start time'], time_format)
            if 'end time' in data:
                job_info['finished'] = datetime.strptime(data['end time'], time_format)
        except Exception as e:
            logger.warning('Encountered error reading job {}'.format(job_path))
            logger.warning('Error: {}'.format(e))

    job_info['flowchart_id'] = flowchart_info['id']
    job_info['path'] = os.path.abspath(job_path)
    job_info['submission_date'] = datetime.fromtimestamp(os.path.getmtime(flowchart_info['path']))
    job_info['flowchart_path'] = flowchart_info['path']

    # Attempt to read job ID from file path
    dir_name = os.path.basename(job_path)
    job_id = dir_name.split('_')[1]
    job_id = float(job_id)
    job_info['id'] = job_id

    return job_info
