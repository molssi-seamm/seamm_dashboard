"""
Table models for SEAMM datastore SQLAlchemy database.
"""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from app import db, ma

#############################
#
# SQLAlchemy Models
#
#############################

class Flowchart(db.Model):
    __tablename__ = 'flowcharts'

    id = db.Column(db.String, nullable=False, primary_key=True, unique=True)
    title = db.Column(db.String, nullable=True)
    description = db.Column(db.String(1000), nullable=True)
    flowchart_file = db.Column(db.String, nullable=False)
    flowchart_json = db.Column(db.JSON, nullable=False)
    authors = db.Column(db.String, nullable=True)
    jobs = db.relationship('Job', back_populates='flowchart', lazy=True)

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.description = kwargs['description']
        self.flowchart_file = kwargs['flowchart_file']
        self.flowchart_json = kwargs['flowchart_json']
    
    def __repr__(self):
        return F"Flowchart(id={self.id}, description={self.description}, flowchart_file={self.flowchart_file}')"


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String, nullable=False)
    flowchart_id = db.Column(db.String, db.ForeignKey("flowcharts.id"))
    submission_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    author = db.Column(db.String, nullable=True)
    name = db.Column(db.String, nullable=True)
    notes = db.Column(db.String, nullable=True)
    status = db.Column(db.String, nullable=False, default="Created")

    flowchart = db.relationship('Flowchart', back_populates='jobs')

    def __repr__(self):
        return F"Job(path={self.path}, flowchart_id={self.flowchart_id}, submission_date={self.submission_date})"

class Project(db.Model):
    __tablename__ = "projects"

    name = db.Column(db.String, nullable=False, primary_key=True)
    project_path = db.Column(db.String, nullable=False, primary_key=True)
    description = db.Column(db.String, nullable=True, unique=False)

    def __repr__(self):
        return F"Project(name={self.name}, project_path={self.project_path}, description={self.description})"


class JobProject(db.Model):
    __tablename__ = "project_jobs"

    job_path = db.Column(db.String, db.ForeignKey('jobs.path'), primary_key=True)
    project = db.Column(db.String, db.ForeignKey('projects.name'), primary_key=True)

class User(db.Model):
    __tablename__ = "users"
    username = db.Column(db.String, unique=True, nullable=False, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class UserProject(db.Model):
    __tablename__ = "user_projects"

    user = db.Column(db.String, db.ForeignKey('users.username'), primary_key=True)
    project = db.Column(db.String, db.ForeignKey('projects.name'), primary_key=True)

#############################
#
# Marshmallow
#
#############################

class JobSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = Job

class FlowchartSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = Flowchart
