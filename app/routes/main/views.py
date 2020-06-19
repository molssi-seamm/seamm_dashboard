from flask import render_template, send_from_directory

from . import main

from app.models import Job, Flowchart, Project


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
    jobs = Job.query.all()
    flowcharts = Flowchart.query.all()
    projects = Project.query.all()
    return render_template('views/' + path, jobs=jobs, flowcharts=flowcharts, projects=projects)

@main.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)
