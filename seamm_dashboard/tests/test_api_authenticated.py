"""
Tests for the API (logged in user)
"""

import os
import json

import pytest

from datetime import datetime


@pytest.mark.parametrize(
    "limit, expected_number",
    [
        (None, 3),
        (2, 2),
    ],
)
def test_get_jobs(limit, expected_number, auth_client):
    """Tests get method for api/jobs with various query strings"""

    auth_client = auth_client[0]

    query_string = "api/jobs"

    if limit is not None:
        query_string += f"?limit={limit}"

    response = auth_client.get(query_string)
    jobs_received = response.json

    assert len(jobs_received) == expected_number, jobs_received


def test_get_job_by_id(auth_client):
    """API endpoint api/jobs/{jobID}"""
    auth_client = auth_client[0]

    response = auth_client.get("api/jobs/3")

    sub_time = datetime.fromisoformat("2016-08-29T09:12:00.000000+00:00").astimezone()
    sub_time = sub_time.strftime(format="%Y-%m-%d %H:%M")
    expected_response = {
        "flowchart_id": "ABCD",
        "id": 3,
        "path": "/Users/username/seamm/projects",
        "submitted": sub_time,
    }

    received = response.json

    for k in expected_response.keys():
        if k == "submitted":
            assert received[k] == expected_response[k]

    assert response.status_code == 200


def test_flowcharts_logged_in(auth_client):

    auth_client = auth_client[0]

    response = auth_client.get("api/flowcharts")

    assert len(response.json) == 1, "The response is" + str(response)
    assert response.status_code == 200


def test_get_flowchart_logged_in(auth_client):
    """
    Test for api/flowcharts/{flowchart_ID} when logged in and owner of flowchart
    """

    auth_client = auth_client[0]

    response = auth_client.get("api/flowcharts/100")

    assert response.status_code == 200


def test_get_cytoscape_logged_in(auth_client):
    """
    Test for api/flowcharts/{flowchart_ID}/cytoscape
    """
    auth_client = auth_client[0]

    response = auth_client.get("api/flowcharts/100/cytoscape")
    assert response.status_code == 201


def test_update_job(auth_client):
    """Check put method of api/jobs/{job_ID}"""

    csrf_token = auth_client[1]
    auth_client = auth_client[0]

    original_info = auth_client.get("api/jobs/1").json
    assert original_info["status"].lower() == "finished"
    response = auth_client.put(
        "api/jobs/1",
        data=json.dumps({"status": "submitted"}),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-CSRF-TOKEN": csrf_token,
        },
    )

    assert response.status_code == 201

    new_info = auth_client.get("api/jobs/1").json

    assert new_info["status"] == "submitted"


def test_update_project(auth_client):
    """Check put method of api/jobs/{job_ID}"""

    csrf_token = auth_client[1]
    auth_client = auth_client[0]
    original_info = auth_client.get("api/projects/1").json
    assert original_info["description"] is None

    response = auth_client.put(
        "api/projects/1",
        data=json.dumps({"description": "testing update"}),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-CSRF-TOKEN": csrf_token,
        },
    )

    assert response.status_code == 201

    new_info = auth_client.get("api/projects/1").json
    assert new_info["description"] == "testing update"


def test_add_job(auth_client):
    """Check post method of api/jobs/"""
    csrf_token = auth_client[1]
    auth_client = auth_client[0]
    flowchart_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "sample.flow"
    )

    with open(flowchart_file) as f:
        flowchart = f.read()

    job_info = {
        "id": 1000,
        "flowchart": flowchart,
        "project": "MyProject",
        "description": "This is the description.",
        "title": "Title",
    }

    response = auth_client.post(
        "api/jobs",
        data=json.dumps(job_info),
        content_type="application/json",
        headers={"X-CSRF-TOKEN": csrf_token},
    )

    assert response.status_code == 201
    assert response.json["id"] == 12


def test_add_job_parameters(auth_client):
    """Check post method of api/jobs/"""
    csrf_token = auth_client[1]
    auth_client = auth_client[0]
    flowchart_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "sample.flow"
    )

    with open(flowchart_file) as f:
        flowchart = f.read()

    job_info = {
        "id": 1000,
        "flowchart": flowchart,
        "project": "MyProject",
        "description": "This is the description.",
        "title": "Title",
        "parameters": ["job:data/Users_psaxe_SEAMM_data_anatase.cif"],
    }

    response = auth_client.post(
        "api/jobs",
        data=json.dumps(job_info),
        content_type="application/json",
        headers={"X-CSRF-TOKEN": csrf_token},
    )

    assert response.status_code == 201
    assert response.json["parameters"] == [
        "job:data/Users_psaxe_SEAMM_data_anatase.cif"
    ]


def test_add_project(auth_client):
    csrf_token = auth_client[1]
    auth_client = auth_client[0]

    project = {"name": "added_project"}

    response = auth_client.post(
        "api/projects",
        data=json.dumps(project),
        content_type="application/json",
        headers={"X-CSRF-TOKEN": csrf_token},
    )

    assert response.status_code == 201

    from seamm_dashboard import datastore

    assert os.path.exists(os.path.join(datastore, "projects", "added_project"))


def test_get_users(auth_client):
    """Check get method of api/users on authenticated client"""

    auth_client = auth_client[0]

    response = auth_client.get("api/users")

    assert response.status_code == 401


def test_get_projects(auth_client):
    """Check get method of api/projects on authenticated client"""

    auth_client = auth_client[0]

    response = auth_client.get("api/projects")

    assert response.status_code == 200

    assert len(response.json) == 2


def test_get_project(auth_client):
    """Check get method of api/projects on authenticated client"""

    auth_client = auth_client[0]

    response = auth_client.get("api/projects/100")

    assert response.status_code == 200


def test_get_project_jobs(auth_client):
    """Check get method of api/projects on authenticated client"""

    auth_client = auth_client[0]

    response = auth_client.get("api/projects/100/jobs")

    assert response.status_code == 200


def test_get_project_jobs_404(auth_client):
    """Check get method of api/projects on authenticated client"""

    auth_client = auth_client[0]

    response = auth_client.get("api/projects/1000/jobs")

    assert response.status_code == 404
