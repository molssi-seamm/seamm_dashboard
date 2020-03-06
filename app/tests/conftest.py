import pytest

import os
import json

from app import create_app, db
from dateutil import parser

from app.models.util import process_flowchart

from app.models import Job, Flowchart

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

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
    
    # Load a simple flowchart
    current_location = os.path.dirname(os.path.realpath(__file__))
    flowchart_data = process_flowchart(os.path.join(current_location, "..", "..", "data", "sample.flow"))

    # Make the ID easier
    flowchart_data['id'] = 'ABCD'

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


@pytest.fixture
def chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    if os.getenv('CHROME_BETA'):
        chrome_options.binary_location = os.getenv('CHROME_BETA')

    driver = webdriver.Chrome(chrome_options=chrome_options)
    
    yield driver

    driver.close()



