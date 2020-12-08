"""
API calls for users (creating, logging in, logging out)

"""

from flask import Response
from flask_jwt_extended import jwt_optional

from app import db, authorize
from app.models import User, UserSchema, Role, RoleSchema, Group, GroupSchema

__all__ = ["add_user", "get_users"]

def _process_user_body(request_data):
    """This function is a private internal function to process user data to get it in a format which can be added to the database.

    Takes request data in json and converts to user object. Returns 400 status if not valid.
    """

    username = request_data["username"]
    password = request_data["password"]

    if username is None or password is None:
        return Response(
            "Both username and password must be supplied to create new user", status=400
        )

    if User.query.filter_by(username=username).first() is not None:
        return Response(f"User with username '{username}'' already exists", status=400)

    user_info = {"username":username, "password": password, "roles":[], "groups":[]}

    possible_keys = ["roles", 
                    "groups", 
                    "first_name", 
                    "last_name", 
                    "email_address"]
    
    map_values = {
                    "roles": Role,
                    "roles_values": [],
                    "groups": Group,
                    "group_values": []
                }
    
    for key in possible_keys:
        try:
            if key == "roles" or key == "groups":
                model = map_values[key]
                for listed_value in request_data[key]:
                    is_model = model.query.filter_by(name=listed_value).first()
                    if not is_model:
                        return response(f"{listed_value} is not an available value for {key}.", status=400)
                    else:
                        user_info[key].append(is_model)
            else:
                user_info[key] = request_data[key]
        except KeyError as e:
            # Not a key in the body. Pass.
            pass
        
    user = User(**user_info)

    return user


@jwt_optional
@authorize.has_role("admin")
def add_user(body):
    
    get_data = _process_user_body(body)

    if isinstance(get_data, Response):
        return get_data
    
    db.session.add(get_data)
    db.session.commit()

    return get_data.id, 201

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
