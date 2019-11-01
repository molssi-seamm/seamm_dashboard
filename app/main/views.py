from flask import request, render_template, flash, g, \
                render_template_string, session, \
                redirect, url_for, abort, jsonify, send_from_directory,\
                current_app
import os
import json
import logging
import random


from . import main

#import seamm
import subprocess

from app.models.sqlalchemy.models import Job, Flowchart


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
    print(F'SEND VIEW\nSEND VIEW\nSEND VIEW\nSEND VIEW\nSEND VIEW\nSEND VIEW\n\nviews/{path}')
    return render_template('views/' + path)

@main.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)
