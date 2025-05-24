from flask import Blueprint, request, jsonify
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import shape, mapping

from models import db, PolygonData, PointData

polygons_bp = Blueprint('polygons', __name__, url_prefix='/polygons')

# Utility to serialize geometry to GeoJSON

def serialize_geom(record):
    geom = to_shape(record.geom)
    props = record.properties or {}
    return {
        'type': 'Feature',
        'geometry': mapping(geom),
        'properties': {
            'id': record.id,
            'name': record.name,
            **props
        }
    }

@polygons_bp.route('', methods=['POST'])
def create_polygon():
    data = request.get_json()
    shp = shape(data['geometry'])
    record = PolygonData(
        name=data['name'],
        geom=from_shape(shp, srid=4326),
        properties=data.get('properties')
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({'id': record.id}), 201

@polygons_bp.route('', methods=['GET'])
def list_polygons():
    features = [serialize_geom(p) for p in PolygonData.query.all()]
    return jsonify({'type': 'FeatureCollection', 'features': features})

@polygons_bp.route('/<int:id>', methods=['PUT'])
def update_polygon(id):
    data = request.get_json()
    rec = PolygonData.query.get_or_404(id)
    rec.name = data.get('name', rec.name)
    if 'geometry' in data:
        shp = shape(data['geometry'])
        rec.geom = from_shape(shp, srid=4326)
    if 'properties' in data:
        rec.properties = data['properties']
    db.session.commit()
    return jsonify({'message': 'updated'})

@polygons_bp.route('/<int:id>', methods=['DELETE'])
def delete_polygon(id):
    rec = PolygonData.query.get_or_404(id)
    db.session.delete(rec)
    db.session.commit()
    return jsonify({'message': 'deleted'})

@polygons_bp.route('/<int:pid>/points', methods=['GET'])
def points_in_polygon(pid):
    poly = PolygonData.query.get_or_404(pid)
    pts = PointData.query.filter(PointData.geom.ST_Within(poly.geom)).all()
    features = []
    for p in pts:
        geom = to_shape(p.geom)
        props = p.properties or {}
        features.append({
            'type': 'Feature',
            'geometry': mapping(geom),
            'properties': {
                'id': p.id,
                'name': p.name,
                **props
            }
        })
    return jsonify({'type': 'FeatureCollection', 'features': features})