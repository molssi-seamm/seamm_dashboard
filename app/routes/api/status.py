"""
API calls for the status
"""
import logging

from app.models import User, UserSchema

from flask_login import current_user
from flask import session

from app import authorize


logger = logging.getLogger('__file__')

__all__ = ['status']

def status():
    """The status of the dashboard.

    Currently always 'running', but in the future other
    values may be added.
    
    """
    users = User.query.all()

    user_schema = UserSchema(many=True)

    users = user_schema.dump(users)

    try:
        username =  current_user.username
    except AttributeError:
        username =  'Anonymous User'

    if current_user.get_id():
        roles = current_user.roles
    else:
        roles = None

    status = {
        'status' : 'running',
        'user id': current_user.get_id(),
        'username': username,
        'roles': roles,
        'users': users,
        
    }

    return status, 200
    
