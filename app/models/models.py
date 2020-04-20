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

    id = db.Column(db.String(32), nullable=False, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    owner = db.Column(db.Integer, db.ForeignKey("user.id"))
    group = db.Column(db.Integer, db.ForeignKey("group.id"))
    permissions = db.Column(db.String(9), nullable=False, default='rwxr-x---')
    path = db.Column(db.String, nullable=False)
    text = db.Column(db.Text, nullable=False)
    json = db.Column(db.JSON, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    job = db.relationship('Job', back_populates='flowchart', lazy=True)

    # def __init__(self, **kwargs):
    #     self.id = kwargs['id']
    #     self.description = kwargs['description']
    #     self.path = kwargs['path']
    
    def __repr__(self):
        return F"Flowchart(id={self.id}, description={self.description}, path={self.path}')"


class Job(db.Model):
    __tablename__ = 'job'

    id = db.Column(db.Integer, primary_key=True)
    flowchart_id = db.Column(db.String(32), db.ForeignKey("flowchart.id"))
    title = db.Column(db.String, nullable=True)
    description = db.Column(db.Text, nullable=True)
    owner = db.Column(db.Integer, db.ForeignKey("user.id"))
    group = db.Column(db.Integer, db.ForeignKey("group.id"))
    permissions = db.Column(db.String(9), nullable=False, default='rwxr-x---')
    path = db.Column(db.String, nullable=False, unique=True)
    submitted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    started = db.Column(db.DateTime)
    finished = db.Column(db.DateTime)
    status = db.Column(db.String, nullable=False, default="imported")

    flowchart = db.relationship('Flowchart', back_populates='job')

    def __repr__(self):
        return F"Job(path={self.path}, flowchart_id={self.flowchart}, submission_date={self.submitted})"

class Project(db.Model):
    __tablename__ = "project"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String(1000), nullable=True)
    path = db.Column(db.String, nullable=False, unique=True)
    owner = db.Column(db.Integer, db.ForeignKey("user.id"))
    group = db.Column(db.Integer, db.ForeignKey("group.id"))
    permissions = db.Column(db.String(9), nullable=False, default='rwxr-x---')

    def __repr__(self):
        return F"Project(name={self.name}, path={self.path}, description={self.description})"


class JobProject(db.Model):
    __tablename__ = "project_job"

    job = db.Column(db.Integer, db.ForeignKey('job.id'), primary_key=True)
    project = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String, default='active')

class UserProject(db.Model):
    __tablename__ = "user_project"

    user = db.Column(db.String, db.ForeignKey('user.id'), primary_key=True)
    project = db.Column(db.String, db.ForeignKey('project.id'), primary_key=True)

class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

class UserGroup(db.Model):
    __tablename__ = 'user_group'

    user = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    group = db.Column(db.Integer, db.ForeignKey('group.id'), primary_key=True)

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
