from flask import request, render_template, flash, g, \
                render_template_string, session, \
                redirect, url_for, abort, jsonify, send_from_directory,\
                current_app
import os
import json
import logging
import random


from . import jobs

#import seamm
import subprocess

from app.routes.jobs.forms import EditJob
from app.models.sqlalchemy import Job, Flowchart


@jobs.route('/views/jobs_list/')
@jobs.route('/views//jobs_list/')
def jobs_list():
    jobs = Job.query.all()
    
    return render_template('jobs/jobs_list.html', jobs=jobs)

@jobs.route('/views/job_detail/id/<id>')
@jobs.route('/views//job_details/id/<id>')
def job_details(id):

    #job = dict(id=id,
    #           name="My Job " + str(random.randint(1, 100)),
    #           description="This is description.."
    #    )

    # return render_template('views/jobs_details.html', job=job)
    return render_template('views/charts.html')
   
@jobs.route('/views/edit_job/id/<job_id>', methods=["GET", "POST"])
@jobs.route('/views//edit_job/id/<job_id>', methods=["GET", "POST"])
def edit_job(job_id):
    job = Job.query.get(job_id)
    form = EditJob()

    if form.validate_on_submit():
        job.name = form.name.data
        job.notes = form.notes.data
        current_app.db.commit()
        flash('Job updated successfully.', 'successs')
        return redirect(url_for('jobs.jobs_list'))
    elif request.method == 'GET':
        if job.name is not None:
            form.name.data = job.name
        if job.notes is not None:
            form.notes.data = job.notes
    return render_template('jobs/edit_job.html', title='Edit Job', form=form)
