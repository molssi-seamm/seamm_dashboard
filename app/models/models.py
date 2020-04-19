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
    __tablename__ = 'flowchart'

    id = db.Column(db.String, nullable=False, primary_key=True, unique=True)
    title = db.Column(db.String, nullable=True)
    description = db.Column(db.String(1000), nullable=True)
    owner = db.Column(db.Integer, db.ForeignKey("user.username"))
    group = db.Column(db.Integer, db.ForeignKey("group.name"))
    permissions = db.Column(db.String(9), nullable=False, default='rwxr-x---')
    flowchart_file = db.Column(db.String, nullable=False)
    flowchart_json = db.Column(db.JSON, nullable=False)
    authors = db.Column(db.String, nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    job = db.relationship('Job', back_populates='flowchart', lazy=True)

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.description = kwargs['description']
        self.flowchart_file = kwargs['flowchart_file']
        self.flowchart_json = kwargs['flowchart_json']
    
    def __repr__(self):
        return F"Flowchart(id={self.id}, description={self.description}, flowchart_file={self.flowchart_file}')"


class Job(db.Model):
    __tablename__ = 'job'

    id = db.Column(db.Integer, primary_key=True)
    flowchart_id = db.Column(db.String, db.ForeignKey("flowchart.id"))
    title = db.Column(db.String, nullable=True)
    description = db.Column(db.String(1000), nullable=True)
    owner = db.Column(db.Integer, db.ForeignKey("user.username"))
    group = db.Column(db.Integer, db.ForeignKey("group.name"))
    permissions = db.Column(db.String(9), nullable=False, default='rwxr-x---')
    path = db.Column(db.String, nullable=False, unique=True)
    submission_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    submitted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    started = db.Column(db.DateTime)
    finished = db.Column(db.DateTime)
    status = db.Column(db.String, nullable=False, default="Created")

    author = db.Column(db.String, nullable=True)
    name = db.Column(db.String, nullable=True)
    notes = db.Column(db.String, nullable=True)

    flowchart = db.relationship('Flowchart', back_populates='job')

    def __repr__(self):
        return F"Job(path={self.path}, flowchart_id={self.flowchart_id}, submission_date={self.submitted})"

class Project(db.Model):
    __tablename__ = "project"

    name = db.Column(db.String, nullable=False, primary_key=True)
    description = db.Column(db.String(1000), nullable=True)
    owner = db.Column(db.Integer, db.ForeignKey("user.username"))
    group = db.Column(db.Integer, db.ForeignKey("group.name"))
    permissions = db.Column(db.String(9), nullable=False, default='rwxr-x---')
    project_path = db.Column(db.String, nullable=False, primary_key=True)

    def __repr__(self):
        return F"Project(name={self.name}, project_path={self.project_path}, description={self.description})"


class JobProject(db.Model):
    __tablename__ = "project_job"

    job_path = db.Column(db.String, db.ForeignKey('job.path'), primary_key=True)
    project = db.Column(db.String, db.ForeignKey('project.name'), primary_key=True)

class User(db.Model):
    __tablename__ = "user"
    username = db.Column(db.String, primary_key=True, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String, default='active')

class UserProject(db.Model):
    __tablename__ = "user_project"

    user = db.Column(db.String, db.ForeignKey('user.username'), primary_key=True)
    project = db.Column(db.String, db.ForeignKey('project.name'), primary_key=True)

class Group(db.Model):
    __tablename__ = 'group'
    name = db.Column(db.String(16), primary_key=True, nullable=False)

class UserGroup(db.Model):
    __tablename__ = 'user_group'
    user = db.Column(db.String(16), db.ForeignKey('user.username'), primary_key=True)
    group = db.Column(db.String(16), db.ForeignKey('group.name'), primary_key=True)

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
