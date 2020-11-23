"""
Patch for anonymous users in flask authorize
"""

import six

from flask_jwt_extended import get_current_user

from flask_authorize.plugin import *

# Attempt at monkey patching Authorizer.
def allowed(self, *args, **kwargs):

    # look to flask-login for current user
    user = kwargs.get('user')
    if user is None:
        # Had to change this
        user = get_current_user()

    # otherwise, use current user method
    elif isinstance(user, types.FunctionType):
        user = user()

    ###########################################################
    #  PATCH
    ###########################################################
    ## We should check the permissions for "OTHER" if we do allow
    ## anonymous actions.
    if user is None:
        if not current_app.config['AUTHORIZE_ALLOW_ANONYMOUS_ACTIONS']:
            return False
    ###########################################################
    #  END PATCH
    ###########################################################
            
    # authorize if user has relevant role
    if len(self.has_role):
        if user_has_role(user, self.has_role):
            return True
        elif not len(self.permission) and not len(self.create):
            return False

    # authorize if user has relevant group
    if len(self.in_group):
        if user_in_group(user, self.in_group):
            return True
        elif not len(self.permission) and not len(self.create):
            return False

    # authorize create privileges based on access
    if len(self.create):
        for model in self.create:
            if user_is_restricted(user, ['create'], model) or \
                not user_is_allowed(user, ['create'], model):
                return False

    # return if no additional permission check needed
    if len(self.permission) == 0:
        return True

    # check permissions on individual instances - all objects
    # must have authorization to proceed.
    operation = set(self.permission)
    for arg in args:

        if not isinstance(arg.__class__, six.class_types):
            continue

        # check role restrictions/allowances
        if user_is_restricted(user, operation, arg):
            return False

        if not user_is_allowed(user, operation, arg):
            return False

        # only check permissions for items that have set permissions
        check = current_app.config['AUTHORIZE_IGNORE_PROPERTY']
        if hasattr(arg, check) and not getattr(arg, check):
            continue
        if not hasattr(arg, 'permissions'):
            continue

        # check other permissions
        check = arg.permissions.get('other', [])
        permitted = has_permission(operation, check)

        # check user permissions
        if hasattr(arg, 'owner'):
            if arg.owner == user:
                check = arg.permissions.get('owner', [])
                permitted |= has_permission(operation, check)

        # check group permissions
        if hasattr(arg, 'group'):
            if hasattr(user, 'groups'):
                if arg.group in user.groups:
                    check = arg.permissions.get('group', [])
                    permitted |= has_permission(operation, check)

        if not permitted:
            # if we are ever not permitted, it will return False
            return False

    # If we make it through the loop without permissions denied, we
    # return True
    return True

Authorizer.allowed = allowed
