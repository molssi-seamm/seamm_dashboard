import pytest

import os
import shutil
from dateutil import parser

from app import create_app, db
from app.models.util import process_flowchart
from app.models import Job, Flowchart, Project, User, Role
from app.models.import_jobs import add_project
from selenium import webdriver
import chromedriver_binary  # Adds chromedriver binary to path

from flask import make_response
from flask_jwt_extended import (
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)

from app.routes.api.auth import create_tokens


@pytest.fixture(scope="session")
def project_directory(tmpdir_factory):

    # Copy our project files to a tmpdir
    dir_path = os.path.dirname(os.path.realpath(__file__))
    real_project_path = os.path.realpath(
        os.path.join(dir_path, "..", "..", "data", "projects", "MyProject")
    )

    temp_project_path = str(tmpdir_factory.mktemp("fake_project"))

    return_path = shutil.copytree(
        real_project_path, temp_project_path, dirs_exist_ok=True
    )

    return return_path


@pytest.fixture(scope="module")
def app(project_directory):

    test_project_path = project_directory

    flask_app = create_app("testing")
    app_context = flask_app.app_context()
    app_context.push()

    # Create a sample project
    test_project = {"name": "MyProject", "path": test_project_path, "owner_id": 1}

    project = Project(**test_project)

    # Create some sample role
    admin_role = Role(name="admin")
    manager_role = Role(name="manager")

    # Create a sample user.
    test_user = User(username="sample_user", password="sample_password")
    test_admin = User(username="admin_user", password="iamadmin", roles=[admin_role])

    # Fill in some data
    job1_data = {
        "flowchart_id": "ABCD",
        "id": 1,
        "path": os.path.realpath(os.path.join(test_project_path, "Job_000001")),
        "submitted": parser.parse("2016-08-29T09:12:33.001000+00:00"),
        "projects": [project],
        "owner_id": 1,
        "status": "finished",
    }

    # Fill in some data
    job2_data = {
        "flowchart_id": "ABCD",
        "id": 2,
        "path": os.path.realpath(os.path.join(test_project_path, "Job_000002")),
        "submitted": parser.parse("2017-08-29T09:12:33.001000+00:00"),
        "projects": [project],
        "owner_id": 1,
        "status": "finished",
    }

    # More data - this job path (probably) doesn't actually exist
    job3_data = {
        "flowchart_id": "ABCD",
        "id": 3,
        "path": "/Users/username/seamm/projects",
        "submitted": parser.parse("2019-08-29T09:12:33.001000+00:00"),
        "projects": [project],
        "owner_id": 1,
        "status": "finished",
    }

    # Load a simple flowchart
    current_location = os.path.dirname(os.path.realpath(__file__))
    flowchart_data = process_flowchart(
        os.path.join(current_location, "..", "..", "data", "sample.flow")
    )

    # Make the ID easier
    flowchart_data["id"] = "ABCD"
    flowchart_data["owner_id"] = 1

    # Save the fake data to the db
    job1 = Job(**job1_data)
    job2 = Job(**job2_data)

    # Add job3 and readable for world.
    job3 = Job(**job3_data)

    job3.permissions = {"other": ["read"]}

    flowchart = Flowchart(**flowchart_data)
    db.session.add(test_user)
    db.session.add(admin_role)
    db.session.add(manager_role)
    db.session.add(test_admin)
    db.session.add(project)
    db.session.add(job1)
    db.session.add(job2)
    db.session.add(job3)
    db.session.add(flowchart)
    db.session.commit()
    yield flask_app

    # clean up
    app_context.pop()


@pytest.fixture(scope="module")
def client(app):

    my_client = app.test_client()
    yield my_client


@pytest.fixture(scope="module")
def auth_client(client):
    auth_client = client
    response = auth_client.post(
        "api/auth/token",
        json=dict(
            username="sample_user",
            password="sample_password",
        ),
        follow_redirects=True,
    )

    yield auth_client

    response = auth_client.get("api/auth/token/remove", follow_redirects=True)


@pytest.fixture(scope="module")
def admin_client(app):
    client = app.test_client()
    client.post(
        "api/auth/token",
        json=dict(
            username="admin_user",
            password="iamadmin",
        ),
        follow_redirects=True,
    )

    yield client

    client.get("api/auth/token/remove", follow_redirects=True)


@pytest.fixture
def chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    # executable_path = os.getenv('EXECUTABLE_PATH')
    driver = webdriver.Chrome(options=chrome_options)

    yield driver

    driver.close()
