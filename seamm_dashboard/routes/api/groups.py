"""
API endpoint for groups
"""

from flask_jwt_extended import jwt_required

from seamm_dashboard import authorize
from seamm_datastore.database.models import Group
from seamm_datastore.database.schema import GroupSchema


@jwt_required(optional=True)
@authorize.has_role("admin", "group manager")
def get_groups():

    groups = Group.query.all()

    # usernames = [ [ user.username for user in group.users ] for group in groups ]

    group_schema = GroupSchema(many=True)

    groups = group_schema.dump(groups)

    # for i, group in enumerate(groups):
    #    group["usernames"] = usernames[i]

    return groups, 200
