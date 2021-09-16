"""
API calls for users (creating, logging in, logging out)

"""

from flask import Response
from flask_jwt_extended import jwt_required

from seamm_dashboard import db, authorize
from seamm_datastore.database.models import User, Role, Group

from seamm_datastore.database.schema import UserSchema, RoleSchema, GroupSchema

__all__ = ["add_user", "get_users"]


def _process_user_body(request_data, original_user_data=None):
    """This function is a private internal function to process user data to get it in a
    format which can be added to the database.

    Takes request data in json and converts to user object. Returns 400 status if not
    valid.
    """

    username = request_data["username"]
    password = request_data["password"]

    if not original_user_data:
        # Check that both username and password are supplied
        if username is None or password is None:
            return Response(
                "Both username and password must be supplied to create new user",
                status=400,
            )
        # Create starting user object with the appropriate information
        user_info = {
            "username": username,
            "password": password,
            "roles": [],
            "groups": [],
        }
        user = User(**user_info)

        # Check if username exists.
        if User.query.filter_by(username=username).first() is not None:
            return Response(
                f"User with username '{username}'' already exists", status=400
            )

    else:
        user = original_user_data
        user.roles = []
        user.groups = []

        # Check if username exists. First we check if the name is in the database. If
        # the name is in the database, this may be an update, so check if the supplied
        # username is equal to the original user info.
        if (
            User.query.filter_by(username=username).first() is not None
            and user.username != username
        ):
            return Response(
                f"User with username '{username}' already exists", status=400
            )

        # After check, update username and password.
        user.username = username

        # only set the password if the password is not blank
        if password:
            user.password = password

    possible_keys = ["roles", "groups", "first_name", "last_name", "email"]

    map_values = {
        "roles": Role,
        "roles_values": [],
        "groups": Group,
        "group_values": [],
    }

    for key in possible_keys:
        try:
            if key == "roles" or key == "groups":
                model = map_values[key]
                for listed_value in request_data[key]:
                    is_model = model.query.filter_by(name=listed_value).first()
                    if not is_model:
                        return Response(
                            f"{listed_value} is not an available value for {key}.",
                            status=400,
                        )
                    else:
                        if getattr(user, key) is None:
                            setattr(user, key, [])
                        getattr(user, key).append(is_model)
            else:
                setattr(user, key, request_data[key])
        except KeyError:
            # Not a key in the body. Pass.
            pass

    return user


@jwt_required(optional=True)
@authorize.has_role("admin")
def add_user(body):

    get_data = _process_user_body(body)

    if isinstance(get_data, Response):
        return get_data

    db.session.add(get_data)
    db.session.commit()

    return get_data.id, 201


@jwt_required(optional=True)
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
        user_info["roles"] = user_roles
        user_info["groups"] = user_groups

        user_list.append(user_info)

    return user_list, 200
