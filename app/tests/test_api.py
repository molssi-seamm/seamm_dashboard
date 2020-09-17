"""
Tests for the API
"""

import pytest

import os
import json
from datetime import date
from dateutil import parser

from app.routes.api.jobs import *

@pytest.mark.usefixtures("authenticated_request")
@pytest.mark.parametrize("createdSince, createdBefore, limit, expected_number", [
    ("01-01-2018", None, None, 1),
    (None, "01-01-2018", None, 2),
    (None, "01-01-2015", None, 0),
    (None, None, 1, 1),
    (None, None, None, 3),
])
def test_get_jobs(createdSince, createdBefore, limit, expected_number):
    """Tests get method for api/jobs with various query strings"""

    jobs_received = get_jobs(createdBefore=createdBefore, createdSince=createdSince, limit=limit)[0]

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

    received = response.json

    for k in expected_response.keys():
        if k == "submitted":
            received[k] = parser.parse(received[k])
        assert received[k] == expected_response[k]

    assert response.status_code == 200

def test_get_job_missing(client):
    """
    API endpoint api/jobs/{job_number}

    Test 404 response for job which does not exist
    
    """
    response = client.get("api/jobs/100")

    assert response.status_code == 404

def test_flowcharts(client):
    """API endpoint for api/flowcharts"""

    response = client.get("api/flowcharts")

    assert len(response.json) == 1
    assert response.status_code == 200

def test_get_flowchart(client):
    """
    API endpoint for api/flowcharts/{flowchart_ID}

    Get flowchart by ID
    """

    response = client.get("api/flowcharts/ABCD")
    assert response.status_code == 200

def test_get_cytoscape(client):
    """
    API endpoint for api/flowcharts/{flowchart_ID}/cytoscape

    Get cytoscape representation of flowchart graph.
    """

    response = client.get("api/flowcharts/ABCD/cytoscape")
    received = response.json
    # Will be three nodes and two edges, for a length of 5.
    assert len(received) == 5
    assert response.status_code == 200

def test_update_job(client):
    """Check put method of api/jobs/{job_ID}"""

    original_info = client.get("api/jobs/1").json
    assert original_info["status"].lower() == "imported"
    
    response = client.put("api/jobs/1", data=json.dumps({"status": "submitted"}), 
        headers={'Accept': 'application/json','Content-Type': 'application/json'})
    
    assert response.status_code == 201

    new_info = client.get("api/jobs/1").json
    assert new_info["status"]  == "submitted"

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


