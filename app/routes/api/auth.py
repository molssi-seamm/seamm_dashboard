"""
Routes for REST authentication
"""

from flask import jsonify, request
from flask_jwt_extended import create_access_token

from app.models import User, UserSchema

__all__ = ['get_auth_token']

def get_auth_token():

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    user = User.query.filter_by(username=username).one_or_none()

    if not user:
        return jsonify({"msg": f"User {username} not found."}), 400
    
    if user.verify_password(password):
        user_schema = UserSchema(many=False)
        access_token = create_access_token(identity=user_schema.dump(user))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Incorrect password."}), 400

