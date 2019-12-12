"""
Table models for SEAMM datastore SQLAlchemy database.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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
    author = Column(String, nullable=True)
    name = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    flowchart = relationship('Flowchart', back_populates='jobs')

    def __repr__(self):
        return F"Job(path={self.path}, flowchart_id={self.flowchart_id}, submission_date={self.submission_date})"

class Project(Base):
    __tablename__ = "projects"

    name = Column(String, nullable=False, primary_key=True)
    project_path = Column(String, nullable=False, primary_key=True)
    description = Column(String, nullable=True, unique=False)

    def __repr__(self):
        return F"Project(name={self.name}, project_path={self.project_path}, description={self.description})"


class JobProject(Base):
    __tablename__ = "project_jobs"

    job_path = Column(String, ForeignKey('jobs.path'), primary_key=True)
    project = Column(String, ForeignKey('projects.name'), primary_key=True)

class User(Base):
    __tablename__ = "users"
    username = Column(String, unique=True, nullable=False, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(60), nullable=False)

class UserProject(Base):
    __tablename__ = "user_projects"

    user = Column(String, ForeignKey('users.username'), primary_key=True)
    project = Column(String, ForeignKey('projects.name'), primary_key=True)

    
