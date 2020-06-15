"""
Table models for SEAMM datastore SQLAlchemy database.
"""

from datetime import datetime
from app import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

#############################
#
# SQLAlchemy Models
#
#############################

user_group = db.Table(
    'user_group',
    db.Column('user', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column(
        'group', db.Integer, db.ForeignKey('group.id'), primary_key=True
    )
)

flowchart_project = db.Table(
    'flowchart_project',
    db.Column(
        'flowchart',
        db.String(32),
        db.ForeignKey('flowchart.id'),
        primary_key=True
    ),
    db.Column(
        'project', db.Integer, db.ForeignKey('project.id'), primary_key=True
    )
)

job_project = db.Table(
    'job_project',
    db.Column('job', db.Integer, db.ForeignKey('job.id'), primary_key=True),
    db.Column(
        'project', db.Integer, db.ForeignKey('project.id'), primary_key=True
    )
)

user_project = db.Table(
    'user_project',
    db.Column('user', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column(
        'project', db.Integer, db.ForeignKey('project.id'), primary_key=True
    )
)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String)
    added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String, default='active')

    groups = db.relationship(
        'Group', secondary=user_group, back_populates='users'
    )
    projects = db.relationship(
        'Project', secondary=user_project, back_populates='users'
    )


class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    users = db.relationship(
        'User', secondary=user_group, back_populates='groups'
    )


class Flowchart(db.Model):
    __tablename__ = 'flowchart'

    id = db.Column(db.String(32), nullable=False, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    group = db.Column(db.Integer, db.ForeignKey('group.id'))
    path = db.Column(db.String, unique=True)
    text = db.Column(db.Text, nullable=False)
    json = db.Column(db.JSON, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    owner_r = db.Column(db.Boolean, nullable=False, default=True)
    owner_w = db.Column(db.Boolean, nullable=False, default=True)
    owner_x = db.Column(db.Boolean, nullable=False, default=True)
    group_r = db.Column(db.Boolean, nullable=False, default=True)
    group_w = db.Column(db.Boolean, nullable=False, default=False)
    group_x = db.Column(db.Boolean, nullable=False, default=True)
    world_r = db.Column(db.Boolean, nullable=False, default=False)
    world_w = db.Column(db.Boolean, nullable=False, default=False)
    world_x = db.Column(db.Boolean, nullable=False, default=False)

    jobs = db.relationship('Job', back_populates='flowchart', lazy=True)
    projects = db.relationship(
        'Project', secondary=flowchart_project, back_populates='flowcharts'
    )

    def __repr__(self):
        return F'Flowchart(id={self.id}, description={self.description}, path={self.path})'  # noqa: E501


class Job(db.Model):
    __tablename__ = 'job'

    id = db.Column(db.Integer, primary_key=True)
    flowchart_id = db.Column(db.String(32), db.ForeignKey('flowchart.id'))
    title = db.Column(db.String, nullable=True)
    description = db.Column(db.Text, nullable=True)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    group = db.Column(db.Integer, db.ForeignKey('group.id'))
    path = db.Column(db.String, unique=True)
    submitted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    started = db.Column(db.DateTime)
    finished = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String, nullable=False, default='imported')
    owner_r = db.Column(db.Boolean, nullable=False, default=True)
    owner_w = db.Column(db.Boolean, nullable=False, default=True)
    owner_x = db.Column(db.Boolean, nullable=False, default=True)
    group_r = db.Column(db.Boolean, nullable=False, default=True)
    group_w = db.Column(db.Boolean, nullable=False, default=False)
    group_x = db.Column(db.Boolean, nullable=False, default=True)
    world_r = db.Column(db.Boolean, nullable=False, default=False)
    world_w = db.Column(db.Boolean, nullable=False, default=False)
    world_x = db.Column(db.Boolean, nullable=False, default=False)

    flowchart = db.relationship('Flowchart', back_populates='jobs')
    projects = db.relationship(
        'Project', secondary=job_project, back_populates='jobs'
    )

    def __repr__(self):
        return F'Job(path={self.path}, flowchart_id={self.flowchart}, submitted={self.submitted})'  # noqa: E501


class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String(1000), nullable=True)
    path = db.Column(db.String, unique=True)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    group = db.Column(db.Integer, db.ForeignKey('group.id'))
    owner_r = db.Column(db.Boolean, nullable=False, default=True)
    owner_w = db.Column(db.Boolean, nullable=False, default=True)
    owner_x = db.Column(db.Boolean, nullable=False, default=True)
    group_r = db.Column(db.Boolean, nullable=False, default=True)
    group_w = db.Column(db.Boolean, nullable=False, default=False)
    group_x = db.Column(db.Boolean, nullable=False, default=True)
    world_r = db.Column(db.Boolean, nullable=False, default=False)
    world_w = db.Column(db.Boolean, nullable=False, default=False)
    world_x = db.Column(db.Boolean, nullable=False, default=False)

    flowcharts = db.relationship(
        'Flowchart', secondary=flowchart_project, back_populates='projects'
    )
    jobs = db.relationship(
        'Job', secondary=job_project, back_populates='projects'
    )
    users = db.relationship(
        'User', secondary=user_project, back_populates='projects'
    )

    def __repr__(self):
        return F'Project(name={self.name}, path={self.path}, description={self.description})'  # noqa: E501


#############################
#
# Marshmallow
#
#############################


class JobSchema(SQLAlchemyAutoSchema):

    class Meta:
        include_fk = True
        include_relationships = True
        model = Job


class FlowchartSchema(SQLAlchemyAutoSchema):

    class Meta:
        include_fk = True
        include_relationships = True
        model = Flowchart


class ProjectSchema(SQLAlchemyAutoSchema):

    class Meta:
        include_fk = True
        include_relationships = True
        model = Project


class UserSchema(SQLAlchemyAutoSchema):

    class Meta:
        include_fk = True
        include_relationships = True
        model = User


class GroupSchema(SQLAlchemyAutoSchema):

    class Meta:
        include_fk = True
        include_relationships = True
        model = Group
