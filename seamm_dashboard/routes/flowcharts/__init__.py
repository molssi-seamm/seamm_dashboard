from flask import Blueprint

flowcharts = Blueprint("flowcharts", __name__)

from . import views  # noqa: F401, E402
