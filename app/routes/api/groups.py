"""
API endpoint for groups
"""

from flask_jwt_extended import jwt_optional

from app import authorize
from app.models import Group, GroupSchema

@jwt_optional
@authorize.has_role("admin", "manager")
def get_groups():

    groups = Group.query.all()

    group_schema = GroupSchema(many=True)

    groups = group_schema.dump(groups)

    return groups, 200
