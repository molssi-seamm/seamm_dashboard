
from app import db

from sqlalchemy.ext.declarative import declared_attr

from flask_authorize.mixins import PipedList

def generate_association_table(entity_name, resource_name, entity_tablename=None, resource_tablename=None):

    # Make them plural by adding 's' :)
    if not entity_tablename:
        entity_tablename = entity_name.lower() + 's'
    if not resource_tablename:
        resource_tablename = resource_name.lower() + 's'

    # More names
    entity_name_lower = entity_name.lower()
    resource_name_lower = resource_name.lower()

    @declared_attr
    def entity_id(cls):
        return db.Column(db.Integer, db.ForeignKey(f"{entity_tablename}.id"), primary_key=True)
    
    @declared_attr
    def resource_id(cls):
        return db.Column(db.Integer, db.ForeignKey(f"{resource_tablename}.id"), primary_key=True)
    
    @declared_attr
    def entity_relationship(cls):
        return db.relationship(f"{entity_name}", backref=db.backref(f"special_{resource_tablename}"))
    
    @declared_attr
    def resource_relationship(cls):
        return db.relationship(f"{resource_name}", backref=db.backref(f"special_{entity_tablename}"))

    class PermissionsAssociationMixin:
        __tablename__ = f"{entity_tablename}_{resource_tablename}_association"

        locals()[f"{entity_name_lower}_id"] = entity_id
        locals()[f"{resource_name_lower}_id"] = resource_id

        locals()[f"special_{entity_tablename}"] = entity_relationship
        locals()[f"special_{resource_tablename}"] = resource_relationship

        special_permissions = db.Column(PipedList)

    return PermissionsAssociationMixin
        
    