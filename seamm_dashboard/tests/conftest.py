import pytest

import os
import shutil
from datetime import datetime

from seamm_dashboard import create_app, db
from seamm_datastore.util import parse_flowchart

from seamm_datastore.database.models import (
    Job,
    Flowchart,
    Project,
    User,
    Role,
    UserProjectAssociation,
)
from selenium import webdriver

# Adds chromedriver binary to path:
import chromedriver_binary  # noqa: F401


def _get_cookie_from_response(response, cookie_name):
    """
    Function grabbed from testing suite of flask-jwt-extended.
    """
    cookie_headers = response.headers.getlist("Set-Cookie")

    for header in cookie_headers:
        attributes = header.split(";")
        if cookie_name in attributes[0]:
            cookie = {}
            for attr in attributes:
                split = attr.split("=")
                cookie[split[0].strip().lower()] = split[1] if len(split) > 1 else True
            return cookie
    return None


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
    test_project = {
        "name": "MyProject",
        "path": test_project_path,
        "owner_id": 3,
        "id": 100,
    }

    project = Project(**test_project)

    # Create some sample roles
    admin_role = Role.query.filter_by(name="admin").one_or_none()
    manager_role = Role.query.filter_by(name="group manager").one_or_none()
    user_role = Role.query.filter_by(name="user").one_or_none()

    # Create a sample user.
    test_user = User(
        username="sample_user", password="sample_password", roles=[user_role]
    )
    test_admin = User(username="admin_user", password="iamadmin", roles=[admin_role])

    # Fill in some data
    sub_time = datetime.fromisoformat("2016-08-29T09:12:33.001000+00:00")
    # "submitted": parser.parse("2016-08-29T09:12:33.001000+00:00"),
    job1_data = {
        "flowchart_id": 100,
        "id": 1,
        "path": os.path.realpath(os.path.join(test_project_path, "Job_000001")),
        "submitted": sub_time,
        "projects": [project],
        "owner_id": 3,
        "status": "finished",
    }

    # Fill in some data
    job2_data = {
        "flowchart_id": 100,
        "id": 2,
        "path": os.path.realpath(os.path.join(test_project_path, "Job_000002")),
        "submitted": sub_time,
        "projects": [project],
        "owner_id": 3,
        "status": "finished",
    }

    # More data - this job path (probably) doesn't actually exist
    job3_data = {
        "flowchart_id": 100,
        "id": 3,
        "path": "/Users/username/seamm/projects",
        "submitted": sub_time,
        "projects": [project],
        "owner_id": 3,
        "status": "finished",
    }

    # Load a simple flowchart
    current_location = os.path.dirname(os.path.realpath(__file__))
    flowchart_data = parse_flowchart(
        os.path.join(current_location, "..", "..", "data", "sample.flow")
    )
    # Make the ID easier
    flowchart_data[0]["id"] = 100
    flowchart_data[0]["owner_id"] = 3
    flowchart_data[0]["json"] = flowchart_data[1]

    # Save the fake data to the db
    job1 = Job(**job1_data)
    job2 = Job(**job2_data)

    # Add job3 and readable for world.
    job3 = Job(**job3_data)
    job3.permissions = {"other": ["read"]}

    # Add visitor and give read access to a project
    visitor = User(username="visitor", password="visitor", id=10)
    a = UserProjectAssociation(
        permissions=["read"], resource_id=project.id, entity_id=visitor.id
    )
    a.job = job1
    visitor.special_projects.append(a)
    db.session.add(a)
    db.session.add(visitor)

    flowchart = Flowchart(**flowchart_data[0])
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

    csrf_token = _get_cookie_from_response(response, "csrf_access_token")[
        "csrf_access_token"
    ]

    yield auth_client, csrf_token

    auth_client.get("api/auth/token/remove", follow_redirects=True)


@pytest.fixture(scope="module")
def visitor_client(client):
    visitor_client = client
    response = visitor_client.post(
        "api/auth/token",
        json=dict(
            username="visitor",
            password="visitor",
        ),
        follow_redirects=True,
    )

    csrf_token = _get_cookie_from_response(response, "csrf_access_token")[
        "csrf_access_token"
    ]

    yield visitor_client, csrf_token

    visitor_client.get("api/auth/token/remove", follow_redirects=True)


@pytest.fixture(scope="module")
def admin_client(app):
    client = app.test_client()
    response = client.post(
        "api/auth/token",
        json=dict(
            username="admin_user",
            password="iamadmin",
        ),
        follow_redirects=True,
    )

    csrf_token = _get_cookie_from_response(response, "csrf_access_token")[
        "csrf_access_token"
    ]

    yield client, csrf_token

    client.get("api/auth/token/remove", follow_redirects=True)


@pytest.fixture
def chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    # executable_path = os.getenv('EXECUTABLE_PATH')
    driver = webdriver.Chrome(options=chrome_options)

    yield driver

    driver.close()
