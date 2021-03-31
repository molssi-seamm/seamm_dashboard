from flask import Blueprint

jobs = Blueprint("jobs", __name__)

from . import views  # noqa: F401, E402
