import pytest

import os
import shutil
from dateutil import parser

from app import create_app, db
from app.models.util import process_flowchart
from app.models import Job, Flowchart, Project
from app.models.import_jobs import add_project
from selenium import webdriver
import chromedriver_binary  # Adds chromedriver binary to path

@pytest.fixture(scope="session")
def project_directory(tmpdir_factory):

    # Copy our project files to a tmpdir
    dir_path = os.path.dirname(os.path.realpath(__file__))
    real_project_path = os.path.realpath(os.path.join(dir_path, "..", "..", "data", "projects", "MyProject"))

    temp_project_path = str(tmpdir_factory.mktemp('fake_project'))
    
    return_path = shutil.copytree(real_project_path, temp_project_path, dirs_exist_ok=True)    
    
    return return_path

@pytest.fixture(scope="session")
def app(project_directory):

    test_project_path = project_directory

    flask_app = create_app('testing')
    app_context = flask_app.app_context()
    app_context.push()

    test_project = {
    'name': 'MyProject',
    'path': test_project_path,
    }
    
    project = Project(**test_project)

    # Fill in some data
    job1_data = {
        "flowchart_id": "ABCD",
        "id": 1,
        "path": os.path.realpath(os.path.join(test_project_path, "Job_000001")),
        "submitted": parser.parse("2016-08-29T09:12:33.001000+00:00"),
        "projects": [project]
        }

    # Fill in some data
    job2_data = {
        "flowchart_id": "ABCD",
        "id": 2,
        "path": os.path.realpath(os.path.join(test_project_path, "Job_000002")),
        "submitted": parser.parse("2017-08-29T09:12:33.001000+00:00"),
        "projects": [project]
        }

    # More data - this job path (probably) doesn't actually exist
    job3_data = {
        "flowchart_id": "ABCD",
        "id": 3,
        "path": "/Users/username/seamm/projects",
        "submitted": parser.parse("2019-08-29T09:12:33.001000+00:00"),
        "projects": [project]
        }

    # Load a simple flowchart
    current_location = os.path.dirname(os.path.realpath(__file__))
    flowchart_data = process_flowchart(os.path.join(current_location, "..", "..", "data", "sample.flow"))

    # Make the ID easier
    flowchart_data['id'] = 'ABCD'

    # Save the fake data to the db
    job1 = Job(**job1_data)
    job2 = Job(**job2_data)
    job3 = Job(**job3_data)
    flowchart = Flowchart(**flowchart_data)
    db.session.add(project)
    db.session.add(job1)
    db.session.add(job2)
    db.session.add(job3)
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
    # executable_path = os.getenv('EXECUTABLE_PATH')
    driver = webdriver.Chrome(options=chrome_options)
    
    yield driver

    driver.close()



