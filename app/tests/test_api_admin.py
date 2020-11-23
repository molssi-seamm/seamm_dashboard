"""
Tests for the API (admin user)
"""


import os


def test_delete_job(admin_client, project_directory):
    """Check delete method of api/jobs/{jobID}"""

    expected_path = os.path.join(project_directory, "Job_000002")

    assert os.path.exists(expected_path)

    response = admin_client.delete("api/jobs/2")

    assert response.status_code == 200

    assert not os.path.exists(expected_path)
