from flask import render_template

from . import projects


@projects.route("/views/projects")
def project_list():
    return render_template("projects/project_list.html")
