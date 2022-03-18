"""
Routes for REST authentication
"""

from datetime import timedelta, datetime, timezone

from flask import jsonify, Response, make_response, request, redirect, url_for
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
    get_jwt_identity,
    unset_jwt_cookies,
    get_jwt,
)

from seamm_datastore.database.models import User
from seamm_datastore.database.schema import UserSchema

from seamm_dashboard import jwt

__all__ = ["get_auth_token", "remove_auth_token", "refresh_expiring_jwts"]


def refresh_expiring_jwts(response):
    """This will automatically refresh tokens that are within 30 minutes of expiring"""

    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(seconds=0))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response

    return response


def create_tokens(user):
    """
    Create a token for a given user object. Not an api endpoint
    """

    user_schema = UserSchema(many=False)
    user = user_schema.dump(user)
    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)

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
def my_expired_token_callback(jwt_header, expired_token):
    user_agent = request.environ.get("HTTP_USER_AGENT", [])

    # If we are in a browser we want to redirect to the log out page
    # If we are not in a browser, we will return a json telling them that
    # the current token is expired.

    # This check should catch all Mozilla compatible browsers.
    # Ref: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent/Firefox
    browser = any(["Mozilla" in user_agent])

    if browser:
        return redirect(url_for("auth.logout", expired=True))

    token_type = expired_token["type"]
    return (
        jsonify(
            {
                "status": 401,
                "sub_status": 42,
                "msg": "The {} token has expired.".format(token_type)
                + "If you are in a browser and seeing this message, "
                + "please clear your browser cookies.",
            }
        ),
        401,
    )
