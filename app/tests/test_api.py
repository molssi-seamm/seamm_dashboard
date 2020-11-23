"""
Tests for the API (public user)
"""

import os
import json

import pytest


def test_get_protected_job(client):

    response = client.get("api/jobs/2")

    assert response.status_code == 401


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


def test_get_flowchart_logged_out(client):
    """
    API endpoint for api/flowcharts/{flowchart_ID}

    Get flowchart by ID
    """

    response = client.get("api/flowcharts/ABCD")
    assert response.status_code == 401


def test_get_cytoscape(client):
    """
    API endpoint for api/flowcharts/{flowchart_ID}/cytoscape when not logged in.

    Get cytoscape representation of flowchart graph.
    """

    response = client.get("api/flowcharts/ABCD/cytoscape")
    assert response.status_code == 401


def test_update_job_not_authenticated(client):
    """Check put method of api/jobs/{job_ID}"""

    response = client.put(
        "api/jobs/3",
        data=json.dumps({"status": "submitted"}),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    )

    assert response.status_code == 401


@pytest.mark.xfail
def test_add_job(client):
    """Check post method of api/jobs/"""
    # Ask Paul
    assert False


def test_delete_job(auth_client, project_directory):
    """Check delete method of api/jobs/{jobID}"""

    response = auth_client.delete("api/jobs/2")

    assert response.status_code == 401
