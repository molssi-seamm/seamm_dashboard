from flask import render_template

from . import projects


@projects.route("/views/projects")
def project_list():
    return render_template("projects/project_list.html")


@projects.route("/views/projects/<id>/jobs")
@projects.route("/views//projects/<id>/jobs")
def project_jobs_list(id):
    return render_template("jobs/jobs_list.html")
