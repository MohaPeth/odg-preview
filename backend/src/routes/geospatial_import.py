"""
Routes API pour l'import de données géospatiales ODG
"""

import os
import json
import tempfile
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from werkzeug.utils import secure_filename

from src.models.geospatial_layers import GeospatialLayer, LayerUploadHistory, db
from src.services.geospatial_import import GeospatialImportService, FileValidator

geospatial_import_bp = Blueprint('geospatial_import', __name__)

@geospatial_import_bp.route('/upload', methods=['POST'])
@cross_origin()
def upload_geospatial_file():
    """
    Upload et import d'un fichier géospatial
    
    Form data:
    - file: Fichier à importer
    - name: Nom de la couche
    - description: Description (optionnel)
    - layer_type: Type de couche (deposit, infrastructure, zone, custom)
    - status: Statut (actif, en_développement, exploration, terminé)
    """
    try:
        # Vérification de la présence du fichier
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Aucun fichier fourni'
            }), 400
        
        file = request.files['file']
        
        # Validation du fichier
        is_valid, validation_message = FileValidator.validate_file_upload(file)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': validation_message
            }), 400
        
        # Récupération des paramètres
        layer_config = {
            'name': request.form.get('name', '').strip(),
            'description': request.form.get('description', '').strip(),
            'layer_type': request.form.get('layer_type', 'custom'),
            'status': request.form.get('status', 'actif')
        }
        
        # Validation des paramètres obligatoires
        if not layer_config['name']:
            return jsonify({
                'success': False,
                'error': 'Le nom de la couche est obligatoire'
            }), 400
        
        # Validation des valeurs
        valid_layer_types = ['deposit', 'infrastructure', 'zone', 'custom']
        valid_statuses = ['actif', 'en_développement', 'exploration', 'terminé']
        
        if layer_config['layer_type'] not in valid_layer_types:
            return jsonify({
                'success': False,
                'error': f'Type de couche invalide. Valeurs acceptées: {", ".join(valid_layer_types)}'
            }), 400
        
        if layer_config['status'] not in valid_statuses:
            return jsonify({
                'success': False,
                'error': f'Statut invalide. Valeurs acceptées: {", ".join(valid_statuses)}'
            }), 400
        
        # Sauvegarde temporaire du fichier
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp(prefix='odg_upload_')
        temp_file_path = os.path.join(temp_dir, filename)
        
        file.save(temp_file_path)
        
        # Import du fichier
        import_service = GeospatialImportService()
        success, message, layer = import_service.import_file(temp_file_path, layer_config)
        
        # Nettoyage
        import_service.cleanup()
        try:
            os.remove(temp_file_path)
            os.rmdir(temp_dir)
        except:
            pass
        
        if success and layer:
            return jsonify({
                'success': True,
                'message': message,
                'data': {
                    'layer': layer.to_dict(),
                    'geojson': layer.to_geojson_feature()
                }
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except Exception as e:
        current_app.logger.error(f"Erreur upload: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erreur serveur: {str(e)}'
        }), 500

@geospatial_import_bp.route('/preview', methods=['POST'])
@cross_origin()
def preview_geospatial_file():
    """Prévisualisation d'un fichier géospatial sans création de couche.
    Retourne uniquement des métadonnées pour alimenter l'aperçu côté frontend."""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Aucun fichier fourni'
            }), 400

        file = request.files['file']

        # Validation rapide du fichier (extension, présence)
        is_valid, validation_message = FileValidator.validate_file_upload(file)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': validation_message
            }), 400

        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp(prefix='odg_preview_')
        temp_file_path = os.path.join(temp_dir, filename)

        file.save(temp_file_path)

        import_service = GeospatialImportService()
        success, message, preview_data = import_service.preview_file(temp_file_path)

        # Nettoyage
        import_service.cleanup()
        try:
            os.remove(temp_file_path)
            os.rmdir(temp_dir)
        except Exception:
            pass

        if success and preview_data:
            return jsonify({
                'success': True,
                'message': message,
                'data': preview_data
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400

    except Exception as e:
        current_app.logger.error(f"Erreur preview: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erreur serveur: {str(e)}'
        }), 500

@geospatial_import_bp.route('/layers', methods=['GET'])
@cross_origin()
def get_geospatial_layers():
    """
    Récupère toutes les couches géospatiales avec filtrage
    
    Query params:
    - layer_type: Filtrer par type
    - status: Filtrer par statut
    - search: Recherche textuelle
    - page: Numéro de page (défaut: 1)
    - per_page: Éléments par page (défaut: 20)
    - include_geojson: Inclure les géométries GeoJSON (défaut: false)
    """
    try:
        # Paramètres de requête
        layer_type = request.args.get('layer_type')
        status = request.args.get('status')
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100
        include_geojson = request.args.get('include_geojson', 'false').lower() == 'true'
        
        # Construction de la requête
        query = GeospatialLayer.query.filter_by(is_visible=True)
        
        if layer_type:
            query = query.filter_by(layer_type=layer_type)
        
        if status:
            query = query.filter_by(status=status)
        
        if search:
            query = query.filter(
                db.or_(
                    GeospatialLayer.name.ilike(f'%{search}%'),
                    GeospatialLayer.description.ilike(f'%{search}%')
                )
            )
        
        # Pagination
        layers_paginated = query.order_by(GeospatialLayer.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Formatage des résultats
        layers_data = []
        for layer in layers_paginated.items:
            layer_dict = layer.to_dict()
            if include_geojson:
                layer_dict['geojson'] = layer.to_geojson_feature()
            layers_data.append(layer_dict)
        
        return jsonify({
            'success': True,
            'data': layers_data,
            'pagination': {
                'page': page,
                'pages': layers_paginated.pages,
                'per_page': per_page,
                'total': layers_paginated.total,
                'has_next': layers_paginated.has_next,
                'has_prev': layers_paginated.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur récupération couches: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erreur serveur: {str(e)}'
        }), 500

@geospatial_import_bp.route('/layers/<int:layer_id>', methods=['GET'])
@cross_origin()
def get_geospatial_layer(layer_id):
    """Récupère une couche géospatiale spécifique"""
    try:
        layer = GeospatialLayer.query.get_or_404(layer_id)
        
        return jsonify({
            'success': True,
            'data': {
                'layer': layer.to_dict(),
                'geojson': layer.to_geojson_feature()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Couche non trouvée: {str(e)}'
        }), 404

@geospatial_import_bp.route('/layers/<int:layer_id>', methods=['PUT'])
@cross_origin()
def update_geospatial_layer(layer_id):
    """
    Met à jour une couche géospatiale
    
    JSON body:
    - name: Nouveau nom
    - description: Nouvelle description
    - status: Nouveau statut
    - is_visible: Visibilité
    - style_config: Configuration des styles
    """
    try:
        layer = GeospatialLayer.query.get_or_404(layer_id)
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Données JSON requises'
            }), 400
        
        # Mise à jour des champs
        if 'name' in data:
            layer.name = data['name'].strip()
        
        if 'description' in data:
            layer.description = data['description'].strip()
        
        if 'status' in data:
            valid_statuses = ['actif', 'en_développement', 'exploration', 'terminé']
            if data['status'] in valid_statuses:
                layer.status = data['status']
        
        if 'is_visible' in data:
            layer.is_visible = bool(data['is_visible'])
        
        if 'style_config' in data:
            layer.style_config = data['style_config']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Couche mise à jour avec succès',
            'data': layer.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Erreur mise à jour: {str(e)}'
        }), 500

@geospatial_import_bp.route('/layers/<int:layer_id>', methods=['DELETE'])
@cross_origin()
def delete_geospatial_layer(layer_id):
    """Supprime une couche géospatiale"""
    try:
        layer = GeospatialLayer.query.get_or_404(layer_id)
        
        # Suppression logique (marquer comme invisible)
        layer.is_visible = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Couche supprimée avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Erreur suppression: {str(e)}'
        }), 500

@geospatial_import_bp.route('/layers/<int:layer_id>/export/<format>', methods=['GET'])
@cross_origin()
def export_geospatial_layer(layer_id, format):
    """
    Exporte une couche géospatiale
    
    Formats supportés: geojson, kml, csv
    """
    try:
        layer = GeospatialLayer.query.get_or_404(layer_id)
        
        if format.lower() == 'geojson':
            geojson = layer.to_geojson_feature()
            return jsonify(geojson)
        
        elif format.lower() == 'kml':
            # TODO: Implémenter l'export KML
            return jsonify({
                'success': False,
                'error': 'Export KML non encore implémenté'
            }), 501
        
        elif format.lower() == 'csv':
            # TODO: Implémenter l'export CSV
            return jsonify({
                'success': False,
                'error': 'Export CSV non encore implémenté'
            }), 501
        
        else:
            return jsonify({
                'success': False,
                'error': f'Format non supporté: {format}'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur export: {str(e)}'
        }), 500

@geospatial_import_bp.route('/upload-history', methods=['GET'])
@cross_origin()
def get_upload_history():
    """Récupère l'historique des uploads"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        history_paginated = LayerUploadHistory.query.order_by(
            LayerUploadHistory.uploaded_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        history_data = [record.to_dict() for record in history_paginated.items]
        
        return jsonify({
            'success': True,
            'data': history_data,
            'pagination': {
                'page': page,
                'pages': history_paginated.pages,
                'per_page': per_page,
                'total': history_paginated.total
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur récupération historique: {str(e)}'
        }), 500

@geospatial_import_bp.route('/supported-formats', methods=['GET'])
@cross_origin()
def get_supported_formats():
    """Retourne les formats de fichiers supportés"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'formats': GeospatialImportService.SUPPORTED_FORMATS,
                'extensions': FileValidator.get_supported_extensions(),
                'max_file_size_mb': GeospatialImportService.MAX_FILE_SIZE / (1024 * 1024),
                'max_features': GeospatialImportService.MAX_FEATURES
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur: {str(e)}'
        }), 500

@geospatial_import_bp.route('/statistics', methods=['GET'])
@cross_origin()
def get_geospatial_statistics():
    """Retourne les statistiques des couches géospatiales"""
    try:
        # Statistiques générales
        total_layers = GeospatialLayer.query.filter_by(is_visible=True).count()
        
        # Par type de couche
        stats_by_type = db.session.query(
            GeospatialLayer.layer_type,
            db.func.count(GeospatialLayer.id).label('count'),
            db.func.sum(GeospatialLayer.area_km2).label('total_area'),
            db.func.sum(GeospatialLayer.length_km).label('total_length')
        ).filter_by(is_visible=True).group_by(GeospatialLayer.layer_type).all()
        
        # Par statut
        stats_by_status = db.session.query(
            GeospatialLayer.status,
            db.func.count(GeospatialLayer.id).label('count')
        ).filter_by(is_visible=True).group_by(GeospatialLayer.status).all()
        
        # Par format source
        stats_by_format = db.session.query(
            GeospatialLayer.source_format,
            db.func.count(GeospatialLayer.id).label('count')
        ).filter_by(is_visible=True).group_by(GeospatialLayer.source_format).all()
        
        return jsonify({
            'success': True,
            'data': {
                'total_layers': total_layers,
                'by_type': [{'type': row.layer_type, 'count': row.count, 
                           'total_area_km2': float(row.total_area or 0),
                           'total_length_km': float(row.total_length or 0)} 
                          for row in stats_by_type],
                'by_status': [{'status': row.status, 'count': row.count} 
                            for row in stats_by_status],
                'by_format': [{'format': row.source_format, 'count': row.count} 
                            for row in stats_by_format]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur statistiques: {str(e)}'
        }), 500
