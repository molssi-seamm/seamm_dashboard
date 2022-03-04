from flask import render_template
from flask_jwt_extended import jwt_required

from . import flowcharts

from seamm_dashboard.routes.api.auth import refresh_expiring_jwts


@flowcharts.route("/views/flowcharts")
@jwt_required(optional=True)
def flowchart_list():
    return render_template("flowcharts/flowchart_list.html")


@flowcharts.route("/views/flowcharts/<id>")
@flowcharts.route("/views/flowcharts/<id>/<flowchart_keys>")
@jwt_required(optional=True)
def flowchart_details(id):
    return render_template("flowcharts/render_flowchart.html")


@flowcharts.after_request
def job_refresh(response):
    return refresh_expiring_jwts(response)
