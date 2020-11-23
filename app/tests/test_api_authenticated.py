"""
Tests for the API (logged in user)
"""

import json

import pytest

from dateutil import parser


@pytest.mark.parametrize(
    "createdSince, createdBefore, limit, expected_number",
    [
        ("01-01-2018", None, None, 1),
        (None, "01-01-2018", None, 2),
        (None, "01-01-2015", None, 0),
        (None, None, 1, 1),
        (None, None, None, 3),
    ],
)
def test_get_jobs(createdSince, createdBefore, limit, expected_number, auth_client):
    """Tests get method for api/jobs with various query strings"""

    query_string = "api/jobs"

    if createdSince is not None:
        query_string += f"?createdSince={createdSince}"
    if createdBefore is not None:
        query_string += f"?createdBefore={createdBefore}"
    if limit is not None:
        query_string += f"?limit={limit}"

    response = auth_client.get(query_string)
    jobs_received = response.json

    assert len(jobs_received) == expected_number


def test_get_job_by_id(client):
    """API endpoint api/jobs/{jobID}"""

    response = client.get("api/jobs/3")

    expected_response = {
        "flowchart_id": "ABCD",
        "id": 3,
        "path": "/Users/username/seamm/projects",
        "submitted": parser.parse("2019-08-29T09:12:33.001000+00:00").replace(
            tzinfo=None
        ),
    }

    received = response.json

    for k in expected_response.keys():
        if k == "submitted":
            received[k] = parser.parse(received[k])

            assert received[k] == expected_response[k]

    assert response.status_code == 200


def test_flowcharts_logged_in(auth_client):

    response = auth_client.get("api/flowcharts")

    assert len(response.json) == 1, "The response is" + str(response)
    assert response.status_code == 200


def test_get_flowchart_logged_in(auth_client):
    """
    Test for api/flowcharts/{flowchart_ID} when logged in and owner of flowchart
    """

    response = auth_client.get("api/flowcharts/ABCD")

    assert response.status_code == 200


def test_get_cytoscape_logged_in(auth_client):
    """
    Test for api/flowcharts/{flowchart_ID}/cytoscape
    """

    response = auth_client.get("api/flowcharts/ABCD/cytoscape")
    assert response.status_code == 201


def test_update_job(auth_client):
    """Check put method of api/jobs/{job_ID}"""

    original_info = auth_client.get("api/jobs/1").json
    assert original_info["status"].lower() == "finished"

    response = auth_client.put(
        "api/jobs/1",
        data=json.dumps({"status": "submitted"}),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    )

    assert response.status_code == 201

    new_info = auth_client.get("api/jobs/1").json
    assert new_info["status"] == "submitted"
