from flask import render_template, flash, Markup, send_from_directory
from flask_jwt_extended import jwt_required, get_current_user

from . import main

from seamm_dashboard.routes.api.auth import refresh_expiring_jwts


@main.route("/")
@jwt_required(optional=True)
def index():
    """Homepage"""
    if get_current_user() is None:
        flash(
            Markup(
                "You are currently viewing the dashboard as a public user."
                + " <a href='login'>Log In</a> to see your jobs."
            ),
            category="public",
        )
    return render_template("index.html")


@main.route("/401")
def unauthorized():
    """Unauthorized Access"""
    return render_template("401.html")


@main.route("/views/id/<id>")
@main.route("/views//id/<id>")
def get_sample(id):
    return "<h3> this is id: " + id + "</h3>"


@main.route("/views/<path:path>")
@main.route("/views//<path:path>")
@jwt_required(optional=True)
def send_view(path):
    return render_template("views/" + path)


@main.route("/static/<path:path>")
def send_js(path):
    return send_from_directory("static", path)


@main.after_request
def main_refresh(response):
    return refresh_expiring_jwts(response)
