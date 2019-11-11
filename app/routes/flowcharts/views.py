from flask import request, render_template, flash, g, \
                render_template_string, session, \
                redirect, url_for, abort, jsonify, send_from_directory,\
                current_app
import os
import json
from . import flowcharts
import logging
import random

#import seamm
#import subprocess

from app.routes.jobs.forms import EditJob
from app.models.sqlalchemy import Job, Flowchart


@flowcharts.route("/flowchart/edit/<flowchart_id>")
def edit_flowchart(flowchart_id):
    """This route will be for opening and editing a flowchart with SEAMM."""
    flowchart = Flowchart.query.get(flowchart_id)
    dir_path = os.path.dirname(os.path.abspath(__file__))
    temp_file = os.path.join(dir_path, '..','..', 'data','tmp','tmp.flow')
    
    with open(temp_file, 'w+') as f:
        f.write(flowchart.flowchart_file)
    
    #subprocess.run(['seamm', '{}'.format(temp_file)])
    os.remove(temp_file)
    return redirect(url_for('jobs.jobs_list'))

@flowcharts.route('/views/flowchart_details/id/<id>')
@flowcharts.route('/views//flowchart_details/id/<id>')
def flowchart_details(id):
    flowchart = Flowchart.query.get(id)

    #job = dict(id=id,
    #           name="My Job " + str(random.randint(1, 100)),
    #           description="This is description.."
    #    )

    # return render_template('views/jobs_details.html', job=job)
    return render_template('views/charts.html', flowchart=flowchart)
    