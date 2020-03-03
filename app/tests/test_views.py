"""
Tests for the front end
"""

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200

def test_jobs_list(client):
    # Need to figure out how to test that table is working.
    response = client.get('/#jobs', content_type="html/text", follow_redirects=True)
    assert response.status_code == 200
