"""
Tests for a visitor
"""


def test_get_jobs(visitor_client):
    """API endpoint api/jobs"""
    auth_client = visitor_client[0]
    response = auth_client.get("api/jobs")

    # Two because there is one public job, and one job they have been added to,
    assert len(response.json) == 3, response.json[0]["id"]
    assert response.status_code == 200
