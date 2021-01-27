"""
Patch to allow access control lists in flask-authorize

"""

from flask_authorize.mixins import *

from sqlalchemy import or_


@classmethod
def authorized(cls, check):
    """
    Query operator for permissions mixins. This operator
    can be used in SQLAlchemy query statements, and will
    automatically decorate queries with appropriate owner/group
    and permissionc checks.

    Arguments:
        check (str): Permission to authorize (i.e. read, update)

    Examples:

        Query all articles where the current user is read-authorized:

        .. code-block:: python

            Article.query.filter(Article.authorized('read')).all()


        Query by multiple parameters, including authorization:

        .. code-block:: python

            Article.query.filter(or_(
                Article.name.contains('open article'),
                Article.authorized('read')
            ))
    """
    from flask_authorize.plugin import CURRENT_USER

    current_user = CURRENT_USER()

    clauses = [
        cls.other_permissions.contains(check),
    ]
    if hasattr(current_user, "id"):
        if hasattr(cls, "owner_id"):
            clauses.append(
                and_(
                    current_user.id == cls.owner_id,
                    cls.owner_permissions.contains(check),
                )
            )
        if hasattr(cls, "group_id") and hasattr(current_user, "groups"):
            clauses.append(
                and_(
                    cls.group_id.in_([x.id for x in current_user.groups]),
                    cls.group_permissions.contains(check),
                )
            )

        # Check if user has special permissions for the resource
        if hasattr(current_user, f"special_{cls.__tablename__}"):
            self_type = type(cls)
            
            item = getattr(current_user, f"special_{cls.__tablename__}")
            permissions = item.filter(cls.id).one_or_none()

            if permissions:
                clauses.append( permissions.contains(check) )


    return or_(*clauses)


BasePermissionsMixin.authorized = authorized
