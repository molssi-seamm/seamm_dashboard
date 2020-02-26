"""
Tests for the API
"""

import pytest

import os
import json
from datetime import date

def test_test(client):
    response = client.get('/')
    print(response)
    assert response.status_code == 200

@pytest.mark.parametrize('job_id, status_code', [
    (1, 201),
    (1, 409),
    ("1", 400),
])
def test_add_job(job_id, status_code, client):
    job_data = {
        "flowchart_id": "ABCD",
        "id": job_id,
        "path": "/Users/username/seamm/projects",
        "submission_date": "2016-08-29T09:12:33.001000+00:00"
        }

    response = client.post('api/jobs', json=job_data)

    assert response.status_code == status_code