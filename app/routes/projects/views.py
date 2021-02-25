from flask import render_template, url_for, request, flash, redirect
from flask_jwt_extended import jwt_optional, get_current_user

from . import projects
from .forms import EditProject

from app.models import Project

from app import authorize, db


@projects.route("/views/projects")
def project_list():
    return render_template("projects/project_list.html")


@projects.route("/views/projects/<id>/jobs")
@projects.route("/views//projects/<id>/jobs")
@jwt_optional
def project_jobs_list(id):

    project = Project.query.get(id)

    own_string = "You do not own this job."

    if project.owner == get_current_user():
        own_string = "You are the job owner."

    manage_project =  authorize.manage(project)
    edit_project = authorize.update(project)

    # Build the url ourselves.
    base_url = url_for("main.index")
    edit_url = base_url + f"projects/{id}/edit"

    return render_template("jobs/jobs_list.html", project=True, manage_project=manage_project, edit_project=edit_project, edit_url=edit_url)

@projects.route("/projects/<project_id>/edit", methods=["GET", "POST"])
@jwt_optional
def edit_project(project_id):

    project = Project.query.get(project_id)

    if not authorize.update(project):
        return render_template("401.html")

    form = EditProject()

    # Build the url ourselves.
    base_url = url_for("main.index")
    project_url = base_url + f"#projects/{project_id}/jobs"

    if form.validate_on_submit():
        project.name = form.name.data
        project.description = form.notes.data
        db.session.commit()
        flash("Project updated successfully.", "successs")

        return redirect(project_url)
    
    elif request.method == "GET":
        form.name.data = project.name
        form.notes.data = project.description
            
    return render_template("jobs/edit_job.html", title=f"Edit Project {project_id}", form=form, back_url=project_url)
