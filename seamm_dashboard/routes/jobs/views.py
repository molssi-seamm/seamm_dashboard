import json

from flask import request, render_template, flash, redirect, url_for

from flask_jwt_extended import jwt_required, get_current_user

from seamm_datastore.database.models import Project, Job
from seamm_datastore.util import parse_job_data

from seamm_dashboard import db, authorize

from . import jobs

from seamm_dashboard.routes.jobs.forms import EditJob, ImportJob


@jobs.route("/views/jobs/")
@jobs.route("/views//jobs/")
def jobs_list():
    return render_template("jobs/jobs_list.html", project=False)


@jobs.route("/views/jobs/<id>")
@jobs.route("/views//jobs/<id>")
@jwt_required(optional=True)
def job_details(id):

    from seamm_datastore.api import get_job
    from seamm_datastore.util import NotAuthorizedError

    try:
        job = get_job(db.session, id)
    except NotAuthorizedError:
        return render_template("401.html")

    edit_job = authorize.update(job)

    own_string = "You do not own this job."

    if job.owner == get_current_user():
        own_string = "You are the job owner."

    # Build the url ourselves.
    base_url = url_for("main.index")
    edit_url = base_url + f"jobs/{id}/edit"

    return render_template(
        "jobs/job_report.html",
        edit_job=edit_job,
        job=job,
        edit_url=edit_url,
        own_string=own_string,
    )


@jobs.route("/jobs/<job_id>/edit", methods=["GET", "POST"])
@jwt_required(optional=True)
def edit_job(job_id):

    job = Job.query.get(job_id)

    if not authorize.update(job):
        return render_template("401.html")

    form = EditJob()

    # Build the url ourselves.
    base_url = url_for("main.index")
    job_url = base_url + f"#jobs/{job_id}"

    if form.validate_on_submit():
        job.title = form.name.data
        job.description = form.notes.data
        db.session.commit()
        flash("Job updated successfully.", "successs")

        return redirect(job_url)

    elif request.method == "GET":
        form.name.data = job.title
        form.notes.data = job.description

    return render_template(
        "jobs/edit_job.html", title=f"Edit Job {job_id}", form=form, back_url=job_url
    )


@jobs.route("/jobs/import", methods=["GET", "POST"])
@jwt_required()
def import_job():
    # TODO - rewrite
    form = ImportJob()

    if form.validate_on_submit():
        data = json.load(form.outfile.data.stream)

        working_directory = data["working directory"]

        job_info = parse_job_data(working_directory)

        if form.title.data:
            job_info["title"] = form.title.data

        projects = data["projects"]

        project_objs = []
        for project in projects:
            query_project = Project.query.filter_by(name=project).one_or_none()

            # Create project if it doesn't exist
            if not query_project:
                query_project = Project(name=project)
                db.session.add(query_project)
                db.session.commit()

            project_objs.append(query_project)

        # TODO Add job
        # add_job(working_directory, job_info["title"], project_objs)
        flash(f"Job {job_info['id']} successfully added to database.")
        return redirect(url_for("main.index"))

    return render_template("jobs/import_job.html", form=form)
