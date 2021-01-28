"""
Tests for a visitor
"""

def test_get_job_by_id(visitor_client):
    """API endpoint api/jobs/{jobID}"""
    auth_client = visitor_client[0]

    response = auth_client.get("api/jobs/1")

    assert response.status_code == 200