"""
Tests for the API (admin user)
"""


import os
import json

import pytest


@pytest.mark.skip
@pytest.mark.xfail
def test_delete_job(admin_client, project_directory):
    """Check delete method of api/jobs/{jobID}

    This is currently XFAIL. With jobs being a primary key in association tables,
    this is more complicated to delete
    """

    csrf_token = admin_client[1]
    admin_client = admin_client[0]

    csrf_headers = {"X-CSRF-TOKEN": csrf_token}

    expected_path = os.path.join(project_directory, "Job_000002")

    assert os.path.exists(expected_path)

    response = admin_client.delete("api/jobs/2", headers=csrf_headers)

    assert response.status_code == 200

    assert not os.path.exists(expected_path)


def test_get_users(admin_client):
    """Check get method of api/users on admin client"""

    admin_client = admin_client[0]

    response = admin_client.get("api/users")

    names = []
    for r in response.json:
        names.append(r["username"])

    assert response.status_code == 200

    assert len(response.json) == 5, names


def test_add_user(admin_client):
    """Check post method of api/users on admin client."""
    csrf_token = admin_client[1]
    admin_client = admin_client[0]

    csrf_headers = {"X-CSRF-TOKEN": csrf_token}

    new_user = {
        "username": "waffles",
        "password": "waffles!",
        "roles": ["group manager"],
    }

    response = admin_client.post(
        "api/users",
        data=json.dumps(new_user),
        content_type="application/json",
        headers=csrf_headers,
    )

    assert response.status_code == 201, response.data
