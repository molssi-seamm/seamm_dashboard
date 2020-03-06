from flask import request, render_template, flash, g, \
                render_template_string, session, \
                redirect, url_for, abort, jsonify, send_from_directory,\
                current_app
import json
from . import flowcharts
import logging
import random

#import seamm
#import subprocess

from app.routes.jobs.forms import EditJob
from app.models import Job, Flowchart

@flowcharts.route("/views/flowcharts")
def flowchart_list():
    return render_template("flowcharts/flowchart_list.html")

@flowcharts.route('/views/flowcharts/<id>')
@flowcharts.route('/views/flowcharts/<id>/<flowchart_keys>')
def flowchart_details(id):
    return render_template('flowcharts/render_flowchart.html')