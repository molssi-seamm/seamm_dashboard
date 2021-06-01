"""
A patch so that we only need csrf tokens from flask-jwt-extended with specified
routes.

This allows two things:
    1. Using jwts on all routes to identify users
    2. Using csrf tokens from the JWT on API routes, while front-end views use CSRF
       tokens which are part of flask-wtforms
"""


from flask import request

from flask_jwt_extended.config import config
from flask_jwt_extended.exceptions import (
    CSRFError,
    NoAuthorizationError,
)

from flask import current_app

import flask_jwt_extended


def _decode_jwt_from_cookies(refresh):
    if refresh:
        cookie_key = config.refresh_cookie_name
        csrf_header_key = config.refresh_csrf_header_name
        csrf_field_key = config.refresh_csrf_field_name
    else:
        cookie_key = config.access_cookie_name
        csrf_header_key = config.access_csrf_header_name
        csrf_field_key = config.access_csrf_field_name

    encoded_token = request.cookies.get(cookie_key)
    if not encoded_token:
        raise NoAuthorizationError('Missing cookie "{}"'.format(cookie_key))

    if (
        config.csrf_protect
        and request.method in config.csrf_request_methods
        and current_app.config["JWT_CSRF_ACCESS_PATH"] in request.url
    ):
        csrf_value = request.headers.get(csrf_header_key, None)
        if not csrf_value and config.csrf_check_form:
            csrf_value = request.form.get(csrf_field_key, None)
        if not csrf_value:
            raise CSRFError("Missing CSRF token")
    else:
        csrf_value = None

    return encoded_token, csrf_value


flask_jwt_extended.view_decorators._decode_jwt_from_cookies = _decode_jwt_from_cookies
