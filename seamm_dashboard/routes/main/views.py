from flask import render_template, send_from_directory

from . import main


@main.route("/")
def index():
    """Homepage"""
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
def send_view(path):
    return render_template("views/" + path)


@main.route("/static/<path:path>")
def send_js(path):
    return send_from_directory("static", path)
