"""
Routes for REST authentication
"""

from flask import jsonify, request, Response
from flask_jwt_extended import (create_access_token, create_refresh_token, 
                                set_access_cookies, set_refresh_cookies,
                                jwt_refresh_token_required)

from app.models import User, UserSchema

__all__ = ['get_auth_token', 'refresh_auth_token']

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
    Write docstring TODO
    """

    username = body.pop('username')
    password = body.pop('password')

    user = User.query.filter_by(username=username).one_or_none()

    if not user:
        return jsonify({"msg": f"User {username} not found."}), 400
    
    if user.verify_password(password):
        access_token, refresh_token = create_tokens(user)
        
        resp = Response({'login': True})
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp, 200
    else:
        return jsonify({"msg": "Incorrect password."}), 400


@jwt_refresh_token_required
def refresh_auth_token():
    """
    Route for refreshing the access token.
    """

    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    # Set the JWT access cookie in the response
    resp = Response({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200

