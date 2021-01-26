
from app import db

from sqlalchemy.ext.declarative import declared_attr

from flask_authorize.mixins import PipedList

def generate_association_table(table_name, entity, resource):
    """

    """

    entity_tablename = entity.__tablename__
    resource_tablename = resource.__tablename__

    class PermissionsAssociation(db.Model):
        __tablename__ = table_name

        locals()[f"{entity_tablename[:-1]}_id"] = db.Column(db.Integer, db.ForeignKey(f"{entity_tablename}.id"), primary_key=True)
        locals()[f"{resource_tablename[:-1]}_id"] = db.Column(db.Integer, db.ForeignKey(f"{resource_tablename}.id"), primary_key=True)
        permissions = db.Column(PipedList)

        
        locals()[f"{entity_tablename[:-1]}"] = db.relationship(f"{entity.__name__}", back_populates=f"{resource_tablename}")
        locals()[f"{resource_tablename[:-1]}"] = db.relationship(f"{resource.__name__}", back_populates=f"{entity_tablename}")
    
    _permissions_association = PermissionsAssociation

    # Set-up relationshps on associated tables.
    setattr(entity, f"{resource_tablename}", db.relationship("PermissionsAssociation", lazy="dynamic", back_populates=f"{entity_tablename[:-1]}"))
    setattr(resource, f"{entity_tablename}", db.relationship("PermissionsAssociation", lazy="dynamic", back_populates=f"{resource_tablename[:-1]}"))

    return _permissions_association
        
    