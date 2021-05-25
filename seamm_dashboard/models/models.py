"""
Table models for SEAMM datastore SQLAlchemy database.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Related, Nested

from flask import current_app

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text, JSON
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base

# Patched flask authorize
from seamm_dashboard.flask_authorize_patch import (
    AccessControlPermissionsMixin,
    generate_association_table,
)

# Create declarative base
Base = declarative_base()

#############################
#
# SQLAlchemy Models
#
#############################

# Authentication Mapping Tables for Access Control
UserJobMixin = generate_association_table("User", "Job")
UserFlowchartMixin = generate_association_table("User", "Flowchart")
UserProjectMixin = generate_association_table("User", "Project")
GroupJobMixin = generate_association_table("Group", "Job")
GroupProjectMixin = generate_association_table("Group", "Project")
GroupFlowchartMixin = generate_association_table("Group", "Flowchart")


class UserJobAssociation(Base, UserJobMixin):
    pass


class UserFlowchartAssociation(Base, UserFlowchartMixin):
    pass


class UserProjectAssociation(Base, UserProjectMixin):
    def __setattr__(self, name, value):
        """
        Change behavior of set attribute so that when a user gets permissions for a
        project, they get updated permissions for all jobs and flowcharts within the
        project.
        """

        if name == "permissions":
            # See if there is an asociation between the group and project
            project = Project.query.filter_by(id=self.resource_id).one()

            if project.jobs:
                for job in project.jobs:
                    assoc = UserJobAssociation.query.filter_by(
                        entity_id=self.entity_id, resource_id=job.id
                    ).one_or_none()

                    if assoc:
                        assoc.permissions = value
                    else:
                        assoc = UserJobAssociation(
                            entity_id=self.entity_id,
                            resource_id=job.id,
                            permissions=value,
                        )

                    current_app.db.add(assoc)
                    current_app.db.commit()

            if project.flowcharts:
                for flowchart in project.flowcharts:
                    assoc = UserFlowchartAssociation.query.filter_by(
                        entity_id=self.entity_id, resource_id=flowchart.id
                    ).one_or_none()
                    if assoc:
                        assoc.permissions = value
                    else:
                        assoc = UserFlowchartAssociation(
                            entity_id=self.entity_id,
                            resource_id=flowchart.id,
                            permissions=value,
                        )

                    current_app.db.add(assoc)
                    current_app.db.commit()

        super().__setattr__(name, value)


class GroupJobAssociation(Base, GroupJobMixin):
    pass


class GroupProjectAssociation(Base, GroupProjectMixin):
    def __setattr__(self, name, value):
        """
        Change behavior of set attribute so that when a group gets permissions for a
        project, they get updated permissions for all jobs and flowcharts within the
        project.
        """

        if name == "permissions":
            # See if there is an asociation between the group and project
            project = Project.query.filter_by(id=self.resource_id).one()

            if project.jobs:
                for job in project.jobs:
                    assoc = GroupJobAssociation.query.filter_by(
                        entity_id=self.entity_id, resource_id=job.id
                    ).one_or_none()
                    if assoc:
                        assoc.permissions = value
                    else:
                        assoc = GroupJobAssociation(
                            entity_id=self.entity_id,
                            resource_id=job.id,
                            permissions=value,
                        )

                    current_app.db.add(assoc)
                    current_app.db.commit()

            if project.flowcharts:
                for flowchart in project.flowcharts:
                    assoc = GroupFlowchartAssociation.query.filter_by(
                        entity_id=self.entity_id, resource_id=flowchart.id
                    ).one_or_none()
                    if assoc:
                        assoc.permissions = value
                    else:
                        assoc = GroupFlowchartAssociation(
                            entity_id=self.entity_id,
                            resource_id=flowchart.id,
                            permissions=value,
                        )

                    current_app.db.add(assoc)
                    current_app.db.commit()

        super().__setattr__(name, value)


class GroupFlowchartAssociation(Base, GroupFlowchartMixin):
    pass


user_group = Table(
    "user_group",
    Base.metadata,
    Column("user", Integer, ForeignKey("users.id"), primary_key=True),
    Column("group", Integer, ForeignKey("groups.id"), primary_key=True),
)

user_role = Table(
    "user_role",
    Base.metadata,
    Column("user", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role", Integer, ForeignKey("roles.id"), primary_key=True),
)


flowchart_project = Table(
    "flowchart_project",
    Base.metadata,
    Column("flowchart", String(32), ForeignKey("flowcharts.id"), primary_key=True),
    Column("project", Integer, ForeignKey("projects.id"), primary_key=True),
)

job_project = Table(
    "job_project",
    Base.metadata,
    Column("job", Integer, ForeignKey("jobs.id"), primary_key=True),
    Column("project", Integer, ForeignKey("projects.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password_hash = Column(String)
    added = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String, default="active")

    roles = relationship("Role", secondary=user_role, back_populates="users")
    groups = relationship("Group", secondary=user_group, back_populates="users")

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", secondary=user_group, back_populates="groups")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", secondary=user_role, back_populates="roles")


class Flowchart(Base, AccessControlPermissionsMixin):
    __tablename__ = "flowcharts"

    id = Column(String(32), nullable=False, primary_key=True)
    title = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    path = Column(String, unique=True)
    text = Column(Text, nullable=False)
    json = Column(JSON, nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.utcnow)

    jobs = relationship("Job", back_populates="flowchart", lazy=True)
    projects = relationship(
        "Project", secondary=flowchart_project, back_populates="flowcharts"
    )

    def __repr__(self):
        return f"Flowchart(id={self.id}, description={self.description}, path={self.path})"  # noqa: E501


class Job(Base, AccessControlPermissionsMixin):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    flowchart_id = Column(String(32), ForeignKey("flowcharts.id"))
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    path = Column(String, unique=True)
    submitted = Column(DateTime, nullable=False, default=datetime.utcnow)
    started = Column(DateTime)
    finished = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="imported")

    flowchart = relationship("Flowchart", back_populates="jobs")
    projects = relationship("Project", secondary=job_project, back_populates="jobs")

    def __repr__(self):
        return f"Job(path={self.path}, flowchart_id={self.flowchart}, submitted={self.submitted})"  # noqa: E501


class Project(Base, AccessControlPermissionsMixin):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String(1000), nullable=True)
    path = Column(String, unique=True)

    flowcharts = relationship(
        "Flowchart", secondary=flowchart_project, back_populates="projects"
    )
    jobs = relationship("Job", secondary=job_project, back_populates="projects")

    def __repr__(self):
        return f"Project(name={self.name}, path={self.path}, description={self.description})"  # noqa: E501

    def set_permissions(self, permissions):
        super().set_permissions(permissions)

        for job in self.jobs:
            job.set_permissions(permissions)
            current_app.db.add(job)
            current_app.db.commit()

        for flowchart in self.flowcharts:
            flowchart.set_permissions(permissions)
            current_app.db.add(flowchart)
            current_app.db.commit()


#############################
#
# Marshmallow
#
#############################


class FlowchartSchema(SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        include_relationships = True
        model = Flowchart
        exclude = (
            "json",
            "text",
            "owner_permissions",
            "group_permissions",
            "other_permissions",
        )

    owner = Related("username")
    group = Related("name")


class ProjectSchema(SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        include_relationships = True
        model = Project
        exclude = ("owner_permissions", "group_permissions", "other_permissions")

    owner = Related("username")
    group = Related("name")


class JobSchema(SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        include_relationships = True
        model = Job
        exclude = (
            "flowchart",
            "owner_permissions",
            "group_permissions",
            "other_permissions",
        )

    owner = Related("username")
    group = Related("name")
    projects = Nested(
        ProjectSchema(
            only=(
                "name",
                "id",
            ),
            many=True,
        )
    )


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        include_relationships = True
        model = User
        exclude = ("password_hash",)


class GroupSchema(SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        include_relationships = True
        model = Group

    users = Nested(
        UserSchema(
            only=(
                "username",
                "id",
            ),
            many=True,
        )
    )


class RoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        include_relationships = True
        model = Role
