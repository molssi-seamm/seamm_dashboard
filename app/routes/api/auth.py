"""
Routes for REST authentication
"""

from flask import jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies

from app.models import User, UserSchema

__all__ = ['get_auth_token']

def get_auth_token(body):

    username = body.pop('username')
    password = body.pop('password')

    user = User.query.filter_by(username=username).one_or_none()

    if not user:
        return jsonify({"msg": f"User {username} not found."}), 400
    
    if user.verify_password(password):
        user_schema = UserSchema(many=False)
        access_token = create_access_token(identity=user_schema.dump(user))

        resp = jsonify({'login': True})

        set_access_cookies(resp, access_token)
        return resp, 200
    else:
        return jsonify({"msg": "Incorrect password."}), 400

