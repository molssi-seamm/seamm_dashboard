import pytest

import os

from app import create_app, db

"""
https://flask.palletsprojects.com/en/1.1.x/testing/
"""

@pytest.fixture(scope="session")
def app():
    flask_app = create_app('testing')
    app_context = flask_app.app_context()
    app_context.push()

    yield flask_app

    # clean up
    app_context.pop()


@pytest.fixture(scope='module')
def client(app):
    return app.test_client()