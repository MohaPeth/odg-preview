from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from src.models.mining_data import db, MiningDeposit, ExploitationArea, Infrastructure
import json

webgis_bp = Blueprint('webgis', __name__)

@webgis_bp.route('/deposits', methods=['GET'])
@cross_origin()
def get_deposits():
    """Récupère tous les gisements miniers"""
    try:
        search = request.args.get('search', '')
        deposits = MiningDeposit.query
        
        if search:
            deposits = deposits.filter(
                db.or_(
                    MiningDeposit.name.ilike(f'%{search}%'),
                    MiningDeposit.type.ilike(f'%{search}%'),
                    MiningDeposit.company.ilike(f'%{search}%')
                )
            )
        
        deposits = deposits.all()
        return jsonify({
            'success': True,
            'data': [deposit.to_dict() for deposit in deposits],
            'count': len(deposits)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@webgis_bp.route('/deposits/<int:deposit_id>', methods=['GET'])
@cross_origin()
def get_deposit(deposit_id):
    """Récupère un gisement spécifique"""
    try:
        deposit = MiningDeposit.query.get_or_404(deposit_id)
        return jsonify({
            'success': True,
            'data': deposit.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@webgis_bp.route('/deposits', methods=['POST'])
@cross_origin()
def create_deposit():
    """Crée un nouveau gisement"""
    try:
        data = request.get_json()
        
        deposit = MiningDeposit(
            name=data['name'],
            type=data['type'],
            latitude=data['coordinates'][0],
            longitude=data['coordinates'][1],
            company=data['company'],
            estimated_quantity=data.get('estimatedQuantity'),
            status=data['status'],
            description=data.get('description')
        )
        
        # Mettre à jour la géométrie PostGIS
        deposit.update_geometry()
        
        db.session.add(deposit)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': deposit.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@webgis_bp.route('/exploitation-areas', methods=['GET'])
@cross_origin()
def get_exploitation_areas():
    """Récupère toutes les zones d'exploitation"""
    try:
        areas = ExploitationArea.query.all()
        return jsonify({
            'success': True,
            'data': [area.to_dict() for area in areas],
            'count': len(areas)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@webgis_bp.route('/exploitation-areas', methods=['POST'])
@cross_origin()
def create_exploitation_area():
    """Crée une nouvelle zone d'exploitation"""
    try:
        data = request.get_json()
        
        area = ExploitationArea(
            name=data['name'],
            company=data['company'],
            status=data['status'],
            coordinates=json.dumps(data['coordinates']),
            area=data.get('area'),
            extracted_volume=data.get('extractedVolume')
        )
        
        # Mettre à jour la géométrie PostGIS
        area.update_geometry()
        
        db.session.add(area)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': area.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@webgis_bp.route('/infrastructure', methods=['GET'])
@cross_origin()
def get_infrastructure():
    """Récupère toutes les infrastructures"""
    try:
        infrastructure = Infrastructure.query.all()
        return jsonify({
            'success': True,
            'data': [infra.to_dict() for infra in infrastructure],
            'count': len(infrastructure)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@webgis_bp.route('/infrastructure', methods=['POST'])
@cross_origin()
def create_infrastructure():
    """Crée une nouvelle infrastructure"""
    try:
        data = request.get_json()
        
        infra = Infrastructure(
            name=data['name'],
            type=data['type'],
            coordinates=json.dumps(data['coordinates']),
            length=data.get('length'),
            capacity=data.get('capacity'),
            status=data.get('status')
        )
        
        # Mettre à jour la géométrie PostGIS
        infra.update_geometry()
        
        db.session.add(infra)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': infra.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@webgis_bp.route('/geojson/deposits', methods=['GET'])
@cross_origin()
def get_deposits_geojson():
    """Récupère les gisements au format GeoJSON"""
    try:
        deposits = MiningDeposit.query.all()
        
        features = []
        for deposit in deposits:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [deposit.longitude, deposit.latitude]
                },
                "properties": {
                    "id": deposit.id,
                    "name": deposit.name,
                    "type": deposit.type,
                    "company": deposit.company,
                    "estimatedQuantity": deposit.estimated_quantity,
                    "status": deposit.status,
                    "description": deposit.description
                }
            }
            features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        return jsonify(geojson)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@webgis_bp.route('/geojson/exploitation-areas', methods=['GET'])
@cross_origin()
def get_exploitation_areas_geojson():
    """Récupère les zones d'exploitation au format GeoJSON"""
    try:
        areas = ExploitationArea.query.all()
        
        features = []
        for area in areas:
            coordinates = json.loads(area.coordinates) if area.coordinates else []
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates]
                },
                "properties": {
                    "id": area.id,
                    "name": area.name,
                    "company": area.company,
                    "status": area.status,
                    "area": area.area,
                    "extractedVolume": area.extracted_volume
                }
            }
            features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        return jsonify(geojson)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@webgis_bp.route('/stats', methods=['GET'])
@cross_origin()
def get_stats():
    """Récupère les statistiques générales"""
    try:
        total_deposits = MiningDeposit.query.count()
        active_deposits = MiningDeposit.query.filter_by(status='Actif').count()
        total_areas = ExploitationArea.query.count()
        active_areas = ExploitationArea.query.filter_by(status='En cours').count()
        total_infrastructure = Infrastructure.query.count()
        
        # Statistiques par type de minerai
        gold_deposits = MiningDeposit.query.filter_by(type='Or').count()
        diamond_deposits = MiningDeposit.query.filter_by(type='Diamant').count()
        
        # Statistiques par entreprise
        companies = db.session.query(MiningDeposit.company, db.func.count(MiningDeposit.id)).group_by(MiningDeposit.company).all()
        
        return jsonify({
            'success': True,
            'data': {
                'deposits': {
                    'total': total_deposits,
                    'active': active_deposits,
                    'byType': {
                        'gold': gold_deposits,
                        'diamond': diamond_deposits
                    }
                },
                'exploitationAreas': {
                    'total': total_areas,
                    'active': active_areas
                },
                'infrastructure': {
                    'total': total_infrastructure
                },
                'companies': [{'name': company[0], 'deposits': company[1]} for company in companies]
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# =======================
# Endpoints d'export des données minières
# =======================

@webgis_bp.route('/deposits/export/<format>', methods=['GET'])
@cross_origin()
def export_all_deposits(format):
    """Exporte tous les gisements dans le format spécifié (geojson, kml, csv, wkt)"""
    try:
        from flask import send_file, make_response
        from src.services.geospatial_export import GeospatialExportService
        import io
        
        deposits = MiningDeposit.query.all()
        
        if not deposits:
            return jsonify({
                'success': False,
                'error': 'Aucun gisement à exporter'
            }), 404
        
        format_lower = format.lower()
        
        # Export GeoJSON
        if format_lower == 'geojson':
            from datetime import datetime
            features = [d.to_geojson_feature() for d in deposits if d.to_geojson_feature()]
            geojson = {
                'type': 'FeatureCollection',
                'features': features,
                'metadata': {
                    'count': len(features),
                    'type': 'deposits',
                    'exported_at': datetime.utcnow().isoformat()
                }
            }
            
            output = io.BytesIO()
            output.write(json.dumps(geojson, indent=2, ensure_ascii=False).encode('utf-8'))
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/geo+json',
                as_attachment=True,
                download_name='deposits.geojson'
            )
        
        # Export CSV
        elif format_lower == 'csv':
            import csv
            output = io.StringIO()
            writer = csv.writer(output)
            
            # En-têtes
            writer.writerow(['id', 'name', 'type', 'latitude', 'longitude', 'company', 'estimated_quantity', 'status', 'description'])
            
            # Données
            for deposit in deposits:
                writer.writerow([
                    deposit.id,
                    deposit.name,
                    deposit.type,
                    deposit.latitude,
                    deposit.longitude,
                    deposit.company,
                    deposit.estimated_quantity or '',
                    deposit.status,
                    deposit.description or ''
                ])
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name='deposits.csv'
            )
        
        # Export KML/KMZ via le service
        elif format_lower in ['kml', 'kmz']:
            # Créer des GeospatialLayer temporaires pour l'export
            export_service = GeospatialExportService()
            
            # Pour simplifier, on exporte chaque deposit comme une feature
            features = [d.to_geojson_feature() for d in deposits if d.to_geojson_feature()]
            
            # Créer un KML simple
            try:
                import simplekml
                kml = simplekml.Kml()
                kml.document.name = "Gisements Miniers ODG"
                
                for deposit in deposits:
                    pnt = kml.newpoint(name=deposit.name)
                    pnt.coords = [(deposit.longitude, deposit.latitude)]
                    pnt.description = f"{deposit.type} - {deposit.company}\nStatut: {deposit.status}"
                    pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/ylw-stars.png'
                
                if format_lower == 'kml':
                    output = io.BytesIO(kml.kml().encode('utf-8'))
                    mimetype = 'application/vnd.google-earth.kml+xml'
                    filename = 'deposits.kml'
                else:  # kmz
                    output = io.BytesIO()
                    kml.savekmz(output)
                    output.seek(0)
                    mimetype = 'application/vnd.google-earth.kmz'
                    filename = 'deposits.kmz'
                
                return send_file(
                    output,
                    mimetype=mimetype,
                    as_attachment=True,
                    download_name=filename
                )
            except ImportError:
                return jsonify({
                    'success': False,
                    'error': 'Module simplekml non disponible. Installez: pip install simplekml'
                }), 500
        
        else:
            return jsonify({
                'success': False,
                'error': f'Format non supporté: {format}. Formats disponibles: geojson, kml, kmz, csv'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur export: {str(e)}'
        }), 500


@webgis_bp.route('/exploitation-areas/export/<format>', methods=['GET'])
@cross_origin()
def export_all_areas(format):
    """Exporte toutes les zones d'exploitation dans le format spécifié"""
    try:
        from flask import send_file
        import io
        
        areas = ExploitationArea.query.all()
        
        if not areas:
            return jsonify({
                'success': False,
                'error': 'Aucune zone d\'exploitation à exporter'
            }), 404
        
        format_lower = format.lower()
        
        # Export GeoJSON
        if format_lower == 'geojson':
            from datetime import datetime
            features = [a.to_geojson_feature() for a in areas if a.to_geojson_feature()]
            geojson = {
                'type': 'FeatureCollection',
                'features': features,
                'metadata': {
                    'count': len(features),
                    'type': 'exploitation_areas',
                    'exported_at': datetime.utcnow().isoformat()
                }
            }
            
            output = io.BytesIO()
            output.write(json.dumps(geojson, indent=2, ensure_ascii=False).encode('utf-8'))
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/geo+json',
                as_attachment=True,
                download_name='exploitation_areas.geojson'
            )
        
        else:
            return jsonify({
                'success': False,
                'error': f'Format non supporté: {format}. Formats disponibles: geojson, kml, csv'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur export: {str(e)}'
        }), 500


@webgis_bp.route('/infrastructure/export/<format>', methods=['GET'])
@cross_origin()
def export_all_infrastructure(format):
    """Exporte toutes les infrastructures dans le format spécifié"""
    try:
        from flask import send_file
        import io
        
        infrastructures = Infrastructure.query.all()
        
        if not infrastructures:
            return jsonify({
                'success': False,
                'error': 'Aucune infrastructure à exporter'
            }), 404
        
        format_lower = format.lower()
        
        # Export GeoJSON
        if format_lower == 'geojson':
            from datetime import datetime
            features = [i.to_geojson_feature() for i in infrastructures if i.to_geojson_feature()]
            geojson = {
                'type': 'FeatureCollection',
                'features': features,
                'metadata': {
                    'count': len(features),
                    'type': 'infrastructure',
                    'exported_at': datetime.utcnow().isoformat()
                }
            }
            
            output = io.BytesIO()
            output.write(json.dumps(geojson, indent=2, ensure_ascii=False).encode('utf-8'))
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/geo+json',
                as_attachment=True,
                download_name='infrastructure.geojson'
            )
        
        else:
            return jsonify({
                'success': False,
                'error': f'Format non supporté: {format}. Formats disponibles: geojson, kml, csv'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur export: {str(e)}'
        }), 500
