"""
Table models for SEAMM datastore SQLAlchemy database.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class Flowchart(Base):
    __tablename__ = 'flowcharts'

    id = Column(String, nullable=False, primary_key=True, unique=True)
    description = Column(String(1000), nullable=True)
    flowchart_file = Column(String(5000), nullable=False)
    jobs = relationship('Job', back_populates='flowchart', lazy=True)

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.description = kwargs['description']
        self.flowchart_file = kwargs['flowchart_file']
    
    def __repr__(self):
        return F"Flowchart(id={self.id}, description={self.description}, flowchart_file={self.flowchart_file}')"


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    flowchart_id = Column(String, ForeignKey("flowcharts.id"))
    submission_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    author = Column(String(50), nullable=True)
    name = Column(String(100), nullable=True)
    notes = Column(String(1000), nullable=True)

    flowchart = relationship('Flowchart', back_populates='jobs')

    def __init__(self, **kwargs):
        self.path = kwargs['path']
        self.flowchart_id  = kwargs['flowchart_id']
        self.submission_date = kwargs['submission_date']
        try:
            self.author = kwargs['author']
        except KeyError:
            # Allow the author project name to not be specified.
            pass

        try:
            self.author = kwargs['name']
        except KeyError:
            # Allow the author project name to not be specified.
            pass

        try:
            self.author = kwargs['notes']
        except KeyError:
            # Allow the author project name to not be specified.
            pass
    
    def __repr__(self):
        return F"Job(path={self.path}, flowchart_id={self.flowchart_id}, submission_date={self.submission_date})"

class Project(Base):
    __tablename__ = "projects"

    name = Column(String(100), nullable=False, primary_key=True)
    description = Column(String(1000), nullable=True, unique=False)

class JobProject(Base):
    __tablename__ = "project_jobs"

    job_path = Column(String, ForeignKey('jobs.path'), primary_key=True)
    project = Column(String, ForeignKey('projects.name', primary_key=True))

class User(Base):
    __tablename__ = "users"
    username = Column(String(20), unique=True, nullable=False, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(60), nullable=False)

class UserProject(Base):
    __tablename__ = "user_projects"

    user = Column(String, ForeignKey('users.username'), primary_key=True)
    project = Column(String, ForeignKey('projects.name'), primary_key=True)

    
