import types
import six

from sqlalchemy import Column, ForeignKey, Integer, or_
from sqlalchemy.orm import relationship, backref

from sqlalchemy.ext.declarative import declared_attr

from flask_authorize.mixins import PipedList, PermissionsMixin

from flask_authorize.plugin import (
    Authorizer,
    user_is_restricted,
    user_is_allowed,
    has_permission,
    user_has_role,
    user_in_group,
)

from flask import current_app

__all__ = ["generate_association_table", "AccessControlPermissionsMixin"]


def generate_association_table(
    entity_name, resource_name, entity_tablename=None, resource_tablename=None
):

    # Make them plural by adding 's' :)
    if not entity_tablename:
        entity_tablename = entity_name.lower() + "s"
    if not resource_tablename:
        resource_tablename = resource_name.lower() + "s"

    @declared_attr
    def left_id(cls):
        return Column(Integer, ForeignKey(f"{entity_tablename}.id"), primary_key=True)

    @declared_attr
    def right_id(cls):
        return Column(Integer, ForeignKey(f"{resource_tablename}.id"), primary_key=True)

    @declared_attr
    def entity_relationship(cls):
        return relationship(
            f"{entity_name}",
            backref=backref(f"special_{resource_tablename}", lazy="dynamic"),
        )

    @declared_attr
    def resource_relationship(cls):
        return relationship(
            f"{resource_name}",
            backref=backref(f"special_{entity_tablename}", lazy="dynamic"),
        )

    class PermissionsAssociationMixin:
        __tablename__ = f"{entity_tablename}_{resource_tablename}_association"

        entity_id = left_id
        resource_id = right_id

        locals()[f"{entity_tablename}"] = entity_relationship
        locals()[f"{resource_tablename}"] = resource_relationship

        permissions = Column(PipedList)

    return PermissionsAssociationMixin


class AccessControlPermissionsMixin(PermissionsMixin):
    @classmethod
    def authorized(cls, check):
        from flask_authorize.plugin import CURRENT_USER

        current_user = CURRENT_USER()

        ret = super().authorized(check)

        clauses = []

        # Check user for special permissions
        if hasattr(current_user, f"special_{cls.__tablename__}"):
            clauses.append(
                cls.id.in_(
                    [
                        x.resource_id
                        for x in getattr(current_user, f"special_{cls.__tablename__}")
                        if check in x.permissions
                    ]
                )
            )

        # Check if user is part of a group that has special access
        if current_user and hasattr(cls, "special_groups"):
            group_list = [
                x.special_groups.all()
                for x in cls.query.all()
                if x.special_groups.all()
            ]
            overlapping_groups = [
                y.resource_id
                for x in group_list
                for y in x
                if y.entity_id in [n.id for n in current_user.groups]
                if check in y.permissions
            ]
            clauses.append(cls.id.in_(overlapping_groups))

        return or_(ret, or_(*clauses))


def allowed(self, *args, **kwargs):
    from flask_authorize.plugin import CURRENT_USER

    # look to flask-login for current user
    user = kwargs.get("user")
    if user is None:
        user = CURRENT_USER()

    # otherwise, use current user method
    elif isinstance(user, types.FunctionType):
        user = user()

    # don't allow anything for anonymous users
    if user is None:
        if not current_app.config["AUTHORIZE_ALLOW_ANONYMOUS_ACTIONS"]:
            return False

    # authorize if user has relevant role
    if len(self.has_role):
        if user_has_role(user, self.has_role):
            return True
        elif not len(self.permission) and not len(self.create):
            return False

    # authorize if user has relevant group
    if len(self.in_group):
        if user_in_group(user, self.in_group):
            return True
        elif not len(self.permission) and not len(self.create):
            return False

    # authorize create privileges based on access
    if len(self.create):
        for model in self.create:
            if user_is_restricted(user, ["create"], model) or not user_is_allowed(
                user, ["create"], model
            ):
                return False

    # return if no additional permission check needed
    if len(self.permission) == 0:
        return True

    # check permissions on individual instances - all objects
    # must have authorization to proceed.
    operation = set(self.permission)
    for arg in args:

        if not isinstance(arg.__class__, six.class_types):
            continue

        # check role restrictions/allowances
        if user_is_restricted(user, operation, arg):
            return False

        if not user_is_allowed(user, operation, arg):
            return False

        # only check permissions for items that have set permissions
        check = current_app.config["AUTHORIZE_IGNORE_PROPERTY"]
        if hasattr(arg, check) and not getattr(arg, check):
            continue
        if not hasattr(arg, "permissions"):
            continue

        # check other permissions
        check = arg.permissions.get("other", [])
        permitted = has_permission(operation, check)

        # check user permissions
        if hasattr(arg, "owner"):
            if arg.owner == user:
                check = arg.permissions.get("owner", [])
                permitted |= has_permission(operation, check)

        # check group permissions
        if hasattr(arg, "group"):
            if hasattr(user, "groups"):
                if arg.group in user.groups:
                    check = arg.permissions.get("group", [])
                    permitted |= has_permission(operation, check)

        # check special permissions
        # should probably figure this out instead of cheating.
        operation = list(operation)[0]

        if hasattr(arg, "special_users") and CURRENT_USER():
            for assoc in arg.special_users.all():
                if CURRENT_USER().id == assoc.entity_id:
                    permitted |= operation in assoc.permissions

        if hasattr(arg, "special_groups") and CURRENT_USER():
            for group in arg.special_groups.all():
                if group.entity_id in [x.id for x in CURRENT_USER().groups]:
                    permitted |= operation in group.permissions

        if not permitted:
            return False

    return True


Authorizer.allowed = allowed
