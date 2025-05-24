from flask import Blueprint, request, jsonify
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import Point, mapping

from models import db, PointData

points_bp = Blueprint('points', __name__, url_prefix='/points')

# Utility to serialize geometry to GeoJSON

def serialize_geom(record):
    shape = to_shape(record.geom)
    props = record.properties or {}
    return {
        'type': 'Feature',
        'geometry': mapping(shape),
        'properties': {
            'id': record.id,
            'name': record.name,
            **props
        }
    }

@points_bp.route('', methods=['POST'])
def create_point():
    data = request.get_json()
    pt = Point(data['longitude'], data['latitude'])
    record = PointData(
        name=data['name'],
        geom=from_shape(pt, srid=4326),
        properties=data.get('properties')
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({'id': record.id}), 201

@points_bp.route('', methods=['GET'])
def list_points():
    # Optional bounding-box filter
    minx = request.args.get('min_lon', type=float)
    miny = request.args.get('min_lat', type=float)
    maxx = request.args.get('max_lon', type=float)
    maxy = request.args.get('max_lat', type=float)

    query = PointData.query
    if None not in (minx, miny, maxx, maxy):
        envelope = f'SRID=4326;POLYGON(({minx} {miny}, {minx} {maxy}, {maxx} {maxy}, {maxx} {miny}, {minx} {miny}))'
        query = query.filter(PointData.geom.ST_Within(envelope))

    features = [serialize_geom(p) for p in query.all()]
    return jsonify({'type': 'FeatureCollection', 'features': features})

@points_bp.route('/<int:id>', methods=['PUT'])
def update_point(id):
    data = request.get_json()
    rec = PointData.query.get_or_404(id)
    rec.name = data.get('name', rec.name)
    if 'latitude' in data and 'longitude' in data:
        pt = Point(data['longitude'], data['latitude'])
        rec.geom = from_shape(pt, srid=4326)
    if 'properties' in data:
        rec.properties = data['properties']
    db.session.commit()
    return jsonify({'message': 'updated'})

@points_bp.route('/<int:id>', methods=['DELETE'])
def delete_point(id):
    rec = PointData.query.get_or_404(id)
    db.session.delete(rec)
    db.session.commit()
    return jsonify({'message': 'deleted'})