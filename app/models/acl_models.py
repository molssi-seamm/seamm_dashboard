
from app import db

from sqlalchemy.ext.declarative import declared_attr

from flask_authorize.mixins import PipedList

def generate_association_table(entity, resource):
    """

    """

    entity_tablename = entity.__tablename__
    resource_tablename = resource.__tablename__

    class PermissionsAssociationMixin:
        __tablename__ = f"{entity_tablename}_{resource_tablename}_association"

        @declared_attr
        def entity_id(cls):
            return db.Column(db.Integer, db.ForeignKey(f"{entity_tablename}.id"), primary_key=True)
        
        @declared_attr
        def resource_id(cls):
            return db.Column(db.Integer, db.ForeignKey(f"{resource_tablename}.id"), primary_key=True)
        
        @declared_attr
        def entity_relationship(cls):
            return db.relationship(f"{entity.__name__}", backref=f"{resource_tablename}")
        
        @declared_attr
        def resource_relationship(cls):
            db.relationship(f"{resource.__name__}", backref=f"{entity_tablename}")

        locals()[f"{entity_tablename[:-1]}_id"] = entity_id
        locals()[f"{resource_tablename[:-1]}_id"] = resource_id
        permissions = db.Column(PipedList)

        locals()[f"{entity_tablename[:-1]}"] = entity_relationship
        locals()[f"{resource_tablename[:-1]}"] = resource_relationship
    
    _permissions_mixin = PermissionsAssociationMixin

    # Set-up relationshps on associated tables.
    #
    #setattr(resource, f"{entity_tablename}", db.relationship("PermissionsAssociation", lazy="dynamic", back_populates=f"{resource_tablename[:-1]}"))

    return _permissions_mixin
        
    