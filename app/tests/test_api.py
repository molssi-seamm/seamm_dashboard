"""
Tests for the API
"""

import pytest

import os
import json
from datetime import date
from dateutil import parser

def test_home(client):
    response = client.get('/')
    print(response)
    assert response.status_code == 200

@pytest.mark.parametrize("createdSince, createdBefore, limit, expected_number", [
    ("01-01-2018", None, None, 1),
    (None, "01-01-2018", None, 1),
    (None, "01-01-2015", None, 0),
    (None, None, 1, 1),
    (None, None, None, 2),
])
def test_get_jobs(createdSince, createdBefore, limit, expected_number, client):
    query_string = "api/jobs"
    
    if createdSince is not None:
        query_string += F"?createdSince={createdSince}"
    if createdBefore is not None:
        query_string += F"?createdBefore={createdBefore}"
    if limit is not None:
        query_string += F"?limit={limit}"

    response = client.get(query_string)
    jobs_received = response.json
    assert len(jobs_received) == expected_number
    assert response.status_code == 200


def test_get_job_by_id(client):
    response = client.get("api/jobs/1")
    
    expected_response =  {
        "flowchart_id": "ABCD",
        "id": 1,
        "path": "/Users/username/seamm/projects",
        "submission_date": parser.parse("2016-08-29T09:12:33.001000+00:00").replace(tzinfo=None)
        }

    received = response.json

    for k in expected_response.keys():
        if k == "submission_date":
            received[k] = parser.parse(received[k])
        assert received[k] == expected_response[k]

    assert response.status_code == 200

def test_get_job_missing(client):
    response = client.get("api/jobs/100")

    assert response.status_code == 404

def test_flowcharts(client):

    response = client.get("api/flowcharts")

    assert len(response.json) == 1
    assert response.status_code == 200

def test_get_flowchart(client):

    response = client.get("api/flowcharts/ABCD")
    assert response.status_code == 200
