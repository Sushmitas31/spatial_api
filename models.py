from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy()

class PointData(db.Model):
    __tablename__ = 'point_data'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    geom = db.Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    properties = db.Column(JSONB, nullable=True)  # arbitrary metadata

class PolygonData(db.Model):
    __tablename__ = 'polygon_data'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    geom = db.Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=False)
    properties = db.Column(JSONB, nullable=True)  # e.g. population density or other attributes