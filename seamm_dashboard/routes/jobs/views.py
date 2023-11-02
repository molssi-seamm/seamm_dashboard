import json
from pathlib import Path
import shlex

import requests

from flask import request, render_template, flash, redirect, url_for
from flask_jwt_extended import jwt_required, get_current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import (
    BooleanField,
    FloatField,
    IntegerField,
    MultipleFileField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Regexp

from seamm_datastore.database.models import Job, Project, UserProjectAssociation
from seamm_dashboard import db, authorize
from seamm_dashboard.routes.jobs.forms import EditJob, ImportJob, GetFlowchart
from seamm_dashboard.routes.api.auth import refresh_expiring_jwts
import seamm_dashboard.util as util
from . import jobs

flowchart_text = None
types = {
    "str": StringField,
    "int": IntegerField,
    "float": FloatField,
    "bool": BooleanField,
    "file": FileField,
}


@jobs.route("/views/jobs/")
@jobs.route("/views//jobs/")
@jwt_required(optional=True)
def jobs_list():
    return render_template("jobs/jobs_list.html", project=False)


@jobs.route("/views/jobs/<id>")
@jobs.route("/views//jobs/<id>")
@jobs.route("/views/jobs/<id>?filename=<filename>")
@jwt_required(optional=True)
def job_details(id, filename=None):

    from seamm_datastore.util import NotAuthorizedError

    try:
        job = Job.get_by_id(id)
    except NotAuthorizedError:
        return render_template("401.html")

    edit_job = authorize.update(job)

    own_string = "You do not own this job."

    if job.owner == get_current_user():
        own_string = "You are the job owner."

    # Build the url ourselves.
    base_url = url_for("main.index")
    edit_url = base_url + f"jobs/{id}/edit"
    submit_url = base_url + f"jobs/{id}/resubmit"

    # Figure out if we can use cdn for plotly
    plotly_location = "https://cdn.plot.ly/plotly-2.9.0.min.js"

    try:
        found_plotly = requests.get(f"{plotly_location}").status_code == 200
    except:
        # if the request doesn't work for some reason, just use the packaged plotly.
        found_plotly = False

    if not found_plotly:
        plotly_location = url_for(
            "static", filename="node_modules/plotly.js-dist-min/plotly.min.js"
        )

    return render_template(
        "jobs/job_report.html",
        edit_job=edit_job,
        job=job,
        edit_url=edit_url,
        submit_url=submit_url,
        own_string=own_string,
        plotly=plotly_location,
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

        job_info = Job.parse_job_data(working_directory)

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


@jobs.route("/jobs/submit", methods=["GET", "POST"])
@jwt_required()
def submit_job():
    """Handle the dialogs for submitting a job by uploading a flowchart.
    
    Steps:
        1. Get the file
        2. Read the file to setup the dialog with the correct parameters
    """
    global flowchart_text
    form = GetFlowchart()

    if form.validate_on_submit():
        data = form.outfile.data.stream.read().decode()

        lines = data.splitlines()

        # Check the definition of the file
        if len(lines[0]) > 2 and lines[0][0:2] != "#!":
            header = lines[0]
        else:
            header = lines[1]
        fields = header.split()
        if len(fields) < 3 or fields[0] != "!MolSSI" or fields[1] != "flowchart":
            flash(f"The file is not a flowchart: {header}")
        else:
            flowchart_text = data
            return redirect(url_for("jobs.job_parameters"))

    return render_template("jobs/submit_job.html", form=form)


@jobs.route("/jobs/parameters", methods=["GET", "POST"])
@jwt_required()
def job_parameters(template_job=None):
    """Handle the dialogs for submitting a job by uploading a flowchart.

    This is step 2: setting up the page to get the parameters
    
    Steps:
        1. Get the file
        2. Read the file to setup the dialog with the correct parameters
    """
    global flowchart_text
    lines = flowchart_text.splitlines()

    # Find the definition of the file
    if len(lines[0]) > 2 and lines[0][0:2] != "#!":
        header = lines[0]
    else:
        header = lines[1]
    fields = header.split()
    if len(fields) < 3 or fields[0] != "!MolSSI" or fields[1] != "flowchart":
        flash(f"The file is not a flowchart: {header}")
        form = GetFlowchart()
        return render_template("jobs/submit_job.html", form=form)
    else:
        sections = {}
        section = ""
        saved = []
        for line in lines:
            if len(line) > 1 and line[0] == "#":
                if section != "":
                    sections[section] = "\n".join(saved)
                saved = []
                section = line[1:].split()[0]
            elif section != "":
                saved.append(line)
        if section != "" and len(saved) > 0:
            sections[section] = "\n".join(saved)
        if "flowchart" not in sections:
            flash("There was no flowchart in the file!")
            form = GetFlowchart()
            return render_template("jobs/submit_job.html", form=form)
        else:
            # Get info on the user and allowed projects, etc.
            projects = Project.get(
                permission="update",
                description=None,
                offset=None,
                limit=None,
                sort_by="name",
                order="asc",
            )
            project_names = sorted([x.name for x in projects])

            # Create an empty Form class
            class JP(FlaskForm):
                pass

            flowchart = json.loads(sections["flowchart"])

            # Find the control parameters, if any in the flowchart.
            # TODO: This doesn't check if the step is connected

            widgets = {}
            for step in flowchart["nodes"]:
                if step["class"] == "ControlParameters":
                    # Insert the correct input into the form
                    variables = step["attributes"]["parameters"]["variables"]["value"]
                    count = 0
                    for name, value in variables.items():
                        count += 1
                        _type = value["type"]
                        choices = value["choices"]
                        if isinstance(choices, str):
                            choices = json.loads(choices)
                        if len(choices) == 0:
                            choices = None

                        if _type == "str" and choices is not None:
                            if "or more" in value["nargs"]:
                                val = SelectMultipleField(name, choices=choices)
                            else:
                                val = SelectField(name, choices=choices)
                        elif _type == "file":
                            if "or more" in value["nargs"]:
                                val = MultipleFileField(name)
                            else:
                                val = FileField(name)
                        else:
                            val = types[_type](name)

                        widget = f"w{count}"
                        setattr(JP, widget, val)

                        widgets[widget] = {
                            "default": value["default"],
                            "description": value["help"],
                            "name": name,
                            **value,
                        }

            # And the final inputs for the job itself.
            setattr(JP, "project", SelectMultipleField("Project", choices=project_names))
            setattr(JP, "title", StringField("Job Title"))
            setattr(JP, "description", TextAreaField("Description"))
            setattr(JP, "submit", SubmitField("Submit Just This Job"))
            setattr(JP, "submit_more", SubmitField("Submit More Jobs..."))

            form = JP()

    if request.method == "GET":
        values = {}
        if template_job is not None:
            tmp = template_job.parameters
            if "control parameters" in tmp:
                values = tmp["control parameters"]

        for key, tmp in widgets.items():
            name = tmp["name"]
            if name in values:
                form[key].data = values[name]
            else:
                form[key].data = tmp["default"]

            if tmp["help"] != "":
                form[key].description = tmp["help"]

            if tmp["default"] != "":
                form[key].default = value["default"]

        if "metadata" in sections:
            data = json.loads(sections["metadata"])
            form.title.render_kw = {
                "size": "100",
                "maxlength": 100,
                "placeholder": "A short (< 100 chars) description of this job",
            }
            if template_job is not None and template_job.title != "":
                form.title.data = template_job.title
            elif data["title"] != "":
                form.title.data = data["title"]

            form.description.render_kw = {
                "rows": 8,
                "placeholder": "A longer description of this job",
            }
            if template_job is not None and template_job.description != "":
                form.description.data = template_job.description
            elif data["description"] != "":
                form.description.data = data["description"]
        if len(project_names) > 0:
            form.project.data = project_names[0]
    elif form.validate_on_submit():
        result = form.data

        # Prepare the command line arguments, transforming and remembering files
        files = {}
        control_parameters = {}
        if len(widgets) == 0:
            cmdline = []
        else:
            # Build the command line
            optional = []
            required = []
            for key, values in widgets.items():
                name = values["name"]
                if values["optional"] == "Yes":
                    if values["type"] == "bool":
                        control_parameters[name] = result[key]
                        if result[key] == "Yes":
                            optional.append(f"--{name}")
                    elif values["type"] == "file":
                        if values["nargs"] == "a single value":
                            file_storage = form[key].data
                            filename = file_storage.filename
                            if filename in files:
                                c = 2
                                tmp_name = f"{c}__{filename}"
                                while tmp_name in files:
                                    c += 1
                                    tmp_name = f"{c}__{filename}"
                                filename = tmp_name
                            files[filename] = file_storage
                            optional.append(f"--{name}")
                            optional.append(f"job:data/{filename}")
                        else:
                            first = True
                            for _file in form[key].data:
                                file_storage = _file
                                filename = file_storage.filename
                                if filename == "":
                                    continue
                                if filename in files:
                                    c = 2
                                    tmp_name = f"{c}__{filename}"
                                    while tmp_name in files:
                                        c += 1
                                        tmp_name = f"{c}__{filename}"
                                    filename = tmp_name
                                files[filename] = file_storage
                                if first:
                                    optional.append(f"--{name}")
                                    first = False
                                optional.append(f"job:data/{filename}")
                    else:
                        control_parameters[name] = result[key]
                        optional.append(f"--{name}")
                        if values["nargs"] == "a single value":
                            optional.append(result[key])
                        else:
                            optional.extend(shlex.split(result[key]))
                else:
                    if values["type"] == "file":
                        if values["nargs"] == "a single value":
                            file_storage = form[key].data
                            filename = file_storage.filename
                            if filename in files:
                                c = 2
                                tmp_name = f"{c}__{filename}"
                                while tmp_name in files:
                                    c += 1
                                    tmp_name = f"{c}__{filename}"
                                filename = tmp_name
                            files[filename] = file_storage
                            required.append(f"job:data/{filename}")
                        else:
                            for _file in form[key].data:
                                file_storage = _file
                                filename = file_storage.filename
                                if filename == "":
                                    continue
                                if filename in files:
                                    c = 2
                                    tmp_name = f"{c}__{filename}"
                                    while tmp_name in files:
                                        c += 1
                                        tmp_name = f"{c}__{filename}"
                                    filename = tmp_name
                                files[filename] = file_storage
                                required.append(f"job:data/{filename}")
                    else:
                        control_parameters[name] = result[key]
                        if values["nargs"] == "a single value":
                            required.append(result[key])
                        else:
                            required.extend(shlex.split(result[key]))

            if len(required) > 0:
                optional.append("--")
                cmdline = optional + required
            else:
                cmdline = optional

        # Submit the job ... how do we do this?
        job = util.setup_job(
            flowchart_text,
            result["project"],
            result["title"],
            result["description"],
            {"cmdline": cmdline, "control parameters": control_parameters},
        )
        job_id = job.id

        # Save any files transferred with the job
        if len(files) > 0:
            path = Path(job.path) / "data"
            path.mkdir(exist_ok=True)
            for filename, file_storage in files.items():
                file_storage.save(path / filename)
                file_storage.close()

        # Let the user know the job was actually submitted.
        flash(f"Submitted as job {job_id}.")

        # If just submitting one job go to its page
        if result["submit"]:
            base_url = url_for("main.index")
            job_url = base_url + f"#jobs/{job_id}"
            return redirect(job_url)

    return render_template("jobs/job_parameters.html", form=form)


@jobs.route("/jobs/<id>/resubmit", methods=["GET", "POST"])
@jwt_required()
def resubmit_job(id=None):
    """Handle the dialogs for submitting a job by uploading a flowchart.

    This is step 2: setting up the page to get the parameters
    
    Steps:
        1. Get the file
        2. Read the file to setup the dialog with the correct parameters
    """
    global flowchart_text

    # Get the flowchart   TODO permissions???
    job = Job.get_by_id(id)

    # The flowchart
    path = Path(job.path) / "flowchart.flow"
    try:
        text = path.read_text()
    except Exception:
        flash("An error occured reading the flowchart!")
        base_url = url_for("main.index")
        job_url = base_url + f"#jobs/{job.id}"
        return redirect(job_url)

    flowchart_text = text

    return job_parameters(template_job=job)

@jobs.after_request
def job_refresh(response):
    return refresh_expiring_jwts(response)
