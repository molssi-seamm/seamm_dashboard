"""
API calls for users (creating, logging in, logging out)

"""

from flask import Response
from flask_jwt_extended import jwt_optional

from app import db, authorize
from app.models import User, UserSchema, Role, RoleSchema, Group, GroupSchema

__all__ = ["add_user", "get_users"]


def add_user(body):
    username = body["username"]
    password = body["password"]

    if username is None or password is None:
        return Response(
            "Both username and password must be supplied to create new user", status=400
        )

    if User.query.filter_by(username=username).first() is not None:
        return Response(f"User with username '{username}'' already exists", status=400)

    user = User(username=username, password=password)

    db.session.add(user)
    db.session.commit()

    return user.id, 201

@jwt_optional
@authorize.has_role("admin")
def get_users():
    users = User.query.all()

    user_list = []
    for current_user in users:
        roles = current_user.roles
        role_schema = RoleSchema(many=True)
        roles = role_schema.dump(roles)

        user_roles = []
        for role in roles:
            user_roles.append(role["name"])

        groups = current_user.groups
        group_schema = GroupSchema(many=True)
        groups = group_schema.dump(groups)

        user_groups = []
        for group in groups:
            user_groups.append(group["name"])

        user_info = UserSchema(many=False).dump(current_user)
        user_info['roles'] = user_roles
        user_info['groups'] = user_groups
    
        user_list.append(user_info)
        

    return user_list, 200
