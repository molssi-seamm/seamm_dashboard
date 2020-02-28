import pytest

import os
import json

from app import create_app, db
from dateutil import parser

from app.models import Job, Flowchart

@pytest.fixture(scope="session")
def app():
    flask_app = create_app('testing')
    app_context = flask_app.app_context()
    app_context.push()

    # Fill in some data
    job1_data = {
        "flowchart_id": "ABCD",
        "id": 1,
        "path": "/Users/username/seamm/projects",
        "submission_date": parser.parse("2016-08-29T09:12:33.001000+00:00")
        }

    job2_data = {
        "flowchart_id": "ABCD",
        "id": 2,
        "path": "/Users/username/seamm/projects",
        "submission_date": parser.parse("2019-08-29T09:12:33.001000+00:00")
        }
    
    # Just nonsense values
    flowchart_data = {
        "id": "ABCD",
        "flowchart_file": "",
        "flowchart_json": json.dumps({'sample': 2}),
        "description": "Sort of a sample."
    }

    job1 = Job(**job1_data)
    job2 = Job(**job2_data)
    flowchart = Flowchart(**flowchart_data)
    db.session.add(job1)
    db.session.add(job2)
    db.session.add(flowchart)
    db.session.commit()

    yield flask_app

    # clean up
    app_context.pop()


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()