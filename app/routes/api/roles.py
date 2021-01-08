"""
API endpoint for groups
"""

from flask_jwt_extended import jwt_optional

from app import authorize
from app.models import Role, RoleSchema

@jwt_optional
@authorize.has_role("admin", "manager")
def get_roles():

    roles = Role.query.all()

    role_schema = RoleSchema(many=True)

    roles = role_schema.dump(roles)

    return roles, 200
