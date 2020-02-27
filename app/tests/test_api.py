"""
Tests for the API
"""

import pytest

import os
import json
from datetime import date

def test_home(client):
    response = client.get('/')
    print(response)
    assert response.status_code == 200

def test_get_jobs(client):
    response = client.get('api/jobs')
    jobs_received = response.json
    assert response.status_code == 200
