from flask import request, render_template, flash, redirect, url_for

from app import db

from . import jobs

from app.routes.jobs.forms import EditJob
from app.models import Job

@jobs.route('/views/jobs/')
@jobs.route('/views//jobs/')
def jobs_list():    
    return render_template('jobs/jobs_list.html')

@jobs.route('/views/jobs/<id>')
@jobs.route('/views//jobs/<id>')
def job_details(id):
    return render_template('jobs/job_report.html')
   
@jobs.route('/views/jobs/<job_id>/edit', methods=["GET", "POST"])
@jobs.route('/views//jobs/<job_id>/edit', methods=["GET", "POST"])
def edit_job(job_id):
    job = Job.query.get(job_id)
    form = EditJob()

    if form.validate_on_submit():
        job.name = form.name.data
        job.notes = form.notes.data
        db.session.commit()
        flash('Job updated successfully.', 'successs')
        return redirect(url_for('jobs.jobs_list'))
    elif request.method == 'GET':
        if job.name is not None:
            form.name.data = job.name
        if job.notes is not None:
            form.notes.data = job.notes
    return render_template('jobs/edit_job.html', title='Edit Job', form=form)
