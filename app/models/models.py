"""
Table models for SEAMM datastore SQLAlchemy database.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_authorize import PermissionsMixin, RestrictionsMixin
from flask_authorize.mixin_generator import generate_association_table

from app import db, jwt

#from .acl_models import generate_association_table

#from .authorize_patch import BasePermissionsMixin

#############################
#
# SQLAlchemy Models
#
#############################

# Authentication Mapping Tables
UserJobMixin = generate_association_table("User", "Job")
UserFlowchartMixin = generate_association_table("User", "Flowchart")
UserProjectMixin = generate_association_table("User", "Project")
GroupJobMixin = generate_association_table("Group", "Job")

class UserJobAssociation(db.Model, UserJobMixin):
    pass

class UserFlowchartAssociation(db.Model, UserFlowchartMixin):
    pass

class UserProjectAssociation(db.Model, UserProjectMixin):
    pass

class GroupJobAssociation(db.Model, GroupJobMixin):
    pass

user_group = db.Table(
    "user_group",
    db.Column("user", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("group", db.Integer, db.ForeignKey("groups.id"), primary_key=True),
)

user_role = db.Table(
    "user_role",
    db.Column("user", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("role", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
)


flowchart_project = db.Table(
    "flowchart_project",
    db.Column(
        "flowchart", db.String(32), db.ForeignKey("flowcharts.id"), primary_key=True
    ),
    db.Column("project", db.Integer, db.ForeignKey("projects.id"), primary_key=True),
)

job_project = db.Table(
    "job_project",
    db.Column("job", db.Integer, db.ForeignKey("jobs.id"), primary_key=True),
    db.Column("project", db.Integer, db.ForeignKey("projects.id"), primary_key=True),
)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String)
    added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String, default="active")

    roles = db.relationship("Role", secondary=user_role, back_populates="users")
    groups = db.relationship("Group", secondary=user_group, back_populates="users")

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    """Function for app, to return user object"""

    if identity:
        username = identity["username"]
        user = User.query.filter_by(username=username).one_or_none()

        return user
    else:
        # return None / null
        return None


class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    users = db.relationship("User", secondary=user_group, back_populates="groups")


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    users = db.relationship("User", secondary=user_role, back_populates="roles")


class Flowchart(db.Model, PermissionsMixin):
    __tablename__ = "flowcharts"

    id = db.Column(db.String(32), nullable=False, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    path = db.Column(db.String, unique=True)
    text = db.Column(db.Text, nullable=False)
    json = db.Column(db.JSON, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    jobs = db.relationship("Job", back_populates="flowchart", lazy=True)
    projects = db.relationship(
        "Project", secondary=flowchart_project, back_populates="flowcharts"
    )

    def __repr__(self):
        return f"Flowchart(id={self.id}, description={self.description}, path={self.path})"  # noqa: E501


class Job(db.Model, PermissionsMixin):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    flowchart_id = db.Column(db.String(32), db.ForeignKey("flowcharts.id"))
    title = db.Column(db.String, nullable=True)
    description = db.Column(db.Text, nullable=True)
    path = db.Column(db.String, unique=True)
    submitted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    started = db.Column(db.DateTime)
    finished = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String, nullable=False, default="imported")

    flowchart = db.relationship("Flowchart", back_populates="jobs")
    projects = db.relationship("Project", secondary=job_project, back_populates="jobs")

    def __repr__(self):
        return f"Job(path={self.path}, flowchart_id={self.flowchart}, submitted={self.submitted})"  # noqa: E501

class Project(db.Model, PermissionsMixin):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String(1000), nullable=True)
    path = db.Column(db.String, unique=True)

    flowcharts = db.relationship(
        "Flowchart", secondary=flowchart_project, back_populates="projects"
    )
    jobs = db.relationship("Job", secondary=job_project, back_populates="projects")

    def __repr__(self):
        return f"Project(name={self.name}, path={self.path}, description={self.description})"  # noqa: E501


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


class RoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        include_relationships = True
        model = Role
