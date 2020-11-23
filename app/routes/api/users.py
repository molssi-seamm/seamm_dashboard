"""
API calls for users (creating, logging in, logging out)

"""

from flask import Response

from app import db
from app.models import User, UserSchema

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


def get_users():
    users = User.query.all()
    users = UserSchema(many=True).dump(users)

    return users
