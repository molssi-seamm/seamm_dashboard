"""
Routes for REST authentication
"""

from datetime import timedelta

from flask import jsonify, Response, make_response, request, redirect, url_for
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
    jwt_required,
    get_jwt_identity,
    unset_jwt_cookies,
)

from seamm_datastore.database.models import User
from seamm_datastore.database.schema import UserSchema

from seamm_dashboard import jwt

__all__ = ["get_auth_token", "refresh_auth_token", "remove_auth_token"]


def create_tokens(user):
    """
    Create a token for a given user object. Not an api endpoint
    """

    # Access tokens expire after an hour.
    # Refresh tokens expire after a day.
    exp_time = timedelta(hours=1)
    exp2_time = timedelta(days=1)

    user_schema = UserSchema(many=False)
    user = user_schema.dump(user)
    access_token = create_access_token(identity=user, expires_delta=exp_time)
    refresh_token = create_refresh_token(identity=user, expires_delta=exp2_time)

    return access_token, refresh_token


def get_auth_token(body):
    """
    Endpoint for api/auth/token
    """

    username = body.pop("username")
    password = body.pop("password")

    user = User.query.filter_by(username=username).one_or_none()

    if not user:
        return jsonify({"msg": f"User {username} not found."}), 400

    if user.verify_password(password):

        access_token, refresh_token = create_tokens(user)

        resp = Response({"login": True})
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp, 200
    else:
        return jsonify({"msg": "Incorrect password."}), 400


def remove_auth_token():
    resp = make_response({"logout": True})
    unset_jwt_cookies(resp)
    return resp, 200


@jwt_required(refresh=True)
def refresh_auth_token():
    """
    Route for refreshing the access token.
    """

    exp_time = timedelta(hours=1)

    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(
        identity=current_user, expires_delta=exp_time, fresh=False
    )

    # Set the JWT access cookie in the response
    resp = Response({"refresh": True})
    set_access_cookies(resp, access_token)
    return resp, 200


@jwt.unauthorized_loader
def needed_token_callback(_):
    if "api" in request.url:
        return (
            jsonify(
                {
                    "status": 401,
                    "sub_status": 42,
                    "msg": "You are missing a token, please login.",
                }
            ),
            401,
        )

    else:
        return redirect(url_for("auth.login"))


@jwt.expired_token_loader
def my_expired_token_callback(expired_token):

    token_type = expired_token["type"]
    return (
        jsonify(
            {
                "status": 401,
                "sub_status": 42,
                "msg": "The {} token has expired".format(token_type),
            }
        ),
        401,
    )
