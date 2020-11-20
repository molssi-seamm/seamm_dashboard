"""
Tests for the API
"""

import pytest

import os
import json
from datetime import date
from dateutil import parser

from flask import jsonify

from app.routes.api.jobs import *
from app.routes.api.flowcharts import *

@pytest.mark.parametrize("createdSince, createdBefore, limit, expected_number", [
    ("01-01-2018", None, None, 1),
    (None, "01-01-2018", None, 2),
    (None, "01-01-2015", None, 0),
    (None, None, 1, 1),
    (None, None, None, 3),
])
def test_get_jobs(createdSince, createdBefore, limit, expected_number, auth_client):
    """Tests get method for api/jobs with various query strings"""

    query_string = "api/jobs"
    
    if createdSince is not None:
        query_string += F"?createdSince={createdSince}"
    if createdBefore is not None:
        query_string += F"?createdBefore={createdBefore}"
    if limit is not None:
        query_string += F"?limit={limit}"

    response = auth_client.get(query_string)
    jobs_received = response.json

    assert len(jobs_received) == expected_number

def test_get_job_by_id(client):
    """API endpoint api/jobs/{jobID}"""

    response = client.get("api/jobs/3")
    
    expected_response =  {
        "flowchart_id": "ABCD",
        "id": 3,
        "path": "/Users/username/seamm/projects",
        "submitted": parser.parse("2019-08-29T09:12:33.001000+00:00").replace(tzinfo=None)
        }

    received = response.data

    assert False, response.data

    for k in expected_response.keys():
        if k == "submitted":
            received[k] = parser.parse(received[k])
          
            assert received[k] == expected_response[k]  

    assert response.status_code == 200

def test_get_protected_job(client):

    resp = client.get("api/auth/token/remove")
    response = client.get("api/jobs/2")
    dbstatus = client.get("api/status")

    assert response.status_code == 401, dbstatus.json['username']

def test_get_job_missing(client):
    """
    API endpoint api/jobs/{job_number}

    Test 404 response for job which does not exist
    
    """
    response = client.get("api/jobs/100")

    assert response.status_code == 404

def test_flowcharts_logged_out(client):
    """API endpoint for api/flowcharts"""

    response = client.get("api/flowcharts")

    assert len(response.json) == 0
    assert response.status_code == 200

def test_flowcharts_logged_in(auth_client):

    response = auth_client.get('api/flowcharts')

    assert len(response[0]) == 1,'The response is'+ str(response)
    assert response[1] == 200

def test_get_flowchart_logged_out(client):
    """
    API endpoint for api/flowcharts/{flowchart_ID}

    Get flowchart by ID
    """

    response = client.get("api/flowcharts/ABCD")
    assert response.status_code == 401

@pytest.mark.usefixtures("authenticated_request")
def test_get_flowchart_logged_in():
    """
    Test for api/flowcharts/{flowchart_ID} when logged in and owner of flowchart
    """

    response = get_flowchart('ABCD')

    assert response[1] == 200

def test_get_cytoscape(client):
    """
    API endpoint for api/flowcharts/{flowchart_ID}/cytoscape when not logged in.

    Get cytoscape representation of flowchart graph.
    """

    response = client.get("api/flowcharts/ABCD/cytoscape")
    assert response.status_code == 401

@pytest.mark.usefixtures("authenticated_request")
def test_get_cytoscape_logged_in():
    """
    Test for api/flowcharts/{flowchart_ID}/cytoscape
    """

    response = get_cytoscape("ABCD")
    assert response[1] == 201

@pytest.mark.usefixtures("authenticated_request")
def test_update_job():
    """Check put method of api/jobs/{job_ID}"""

    original_info = get_job(1)[0]
    assert original_info["status"].lower() == "finished"
    
    response = update_job(1, {"status": "submitted"})
    
    assert response.status_code == 201

    new_info = get_job(1)[0]
    assert new_info["status"]  == "submitted"

def test_update_job_not_authenticated(client):
    """Check put method of api/jobs/{job_ID}"""
    
    response = client.put("api/jobs/3", data=json.dumps({"status": "submitted"}), 
        headers={'Accept': 'application/json','Content-Type': 'application/json'})
    
    assert response.status_code == 401

@pytest.mark.xfail
def test_add_job(client):
    """Check post method of api/jobs/"""
    # Ask Paul
    assert False

@pytest.mark.usefixtures("admin_request")
def test_delete_job(project_directory):
    """Check delete method of api/jobs/{jobID}"""

    expected_path = os.path.join(project_directory, "Job_000002")

    assert os.path.exists(expected_path)

    response = delete_job(2)
    
    assert response.status_code == 200

    assert not os.path.exists(expected_path)


