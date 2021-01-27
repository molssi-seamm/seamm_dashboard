
from app import db

from sqlalchemy.ext.declarative import declared_attr

from flask_authorize.mixins import PipedList

def generate_association_table(entity_name, resource_name):

    entity_tablename = entity_name.lower() + 's'
    resource_tablename = resource_name.lower() + 's'

    @declared_attr
    def entity_id(cls):
        return db.Column(db.Integer, db.ForeignKey(f"{entity_tablename}.id"), primary_key=True)
    
    @declared_attr
    def resource_id(cls):
        return db.Column(db.Integer, db.ForeignKey(f"{resource_tablename}.id"), primary_key=True)
    
    @declared_attr
    def entity_relationship(cls):
        return db.relationship(f"{entity_name}", backref=f"{resource_tablename}")
    
    @declared_attr
    def resource_relationship(cls):
        db.relationship(f"{resource_name}", backref=f"{entity_tablename}")

    class PermissionsAssociationMixin:
        __tablename__ = f"{entity_tablename}_{resource_tablename}_association"

        locals()[f"{entity_tablename[:-1]}_id"] = entity_id
        locals()[f"{resource_tablename[:-1]}_id"] = resource_id

        locals()[f"{entity_tablename[:-1]}"] = entity_relationship
        locals()[f"{resource_tablename[:-1]}"] = resource_relationship

        permissions = db.Column(PipedList)
    
    _permissions_mixin = PermissionsAssociationMixin

    return _permissions_mixin
        
    