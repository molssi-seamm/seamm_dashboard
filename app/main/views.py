from flask import request, render_template, flash, g, \
                render_template_string, session, \
                redirect, url_for, abort, jsonify, send_from_directory,\
                current_app
import os
import json
from . import main
import logging
import random


@main.route('/')
def index():
    """Homepage"""
    return render_template('index.html')


@main.route('/views/id/<id>')
@main.route('/views//id/<id>')
def get_sample(id):
    return "<h3> this is id: " + id + "</h3>"


@main.route('/views/<path:path>')
@main.route('/views//<path:path>')
def send_view(path):
    print('innnnnnnnn send view')
    return render_template('views/' + path)


@main.route('/views/jobs_list/')
@main.route('/views//jobs_list/')
def jobs_list():
    jobs = []
    for i in range(20):
        job = dict(id=random.randint(10000, 99999),
                   name="My Job " + str(random.randint(1, 100)),
                   description="This is description.."
            )
        jobs.append(job)

    return render_template('views/jobs_list.html', jobs=jobs)


@main.route('/views/job_details/id/<id>')
@main.route('/views//job_details/id/<id>')
def jobs_details(id):

    job = dict(id=id,
               name="My Job " + str(random.randint(1, 100)),
               description="This is description.."
        )

    # return render_template('views/jobs_details.html', job=job)
    return render_template('views/charts.html')


@main.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)
