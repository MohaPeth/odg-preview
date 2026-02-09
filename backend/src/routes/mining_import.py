"""
Routes pour l'import de données minières depuis des fichiers GeoJSON/CSV
Sans dépendance à GeoPandas
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
import logging
from datetime import datetime

from src.models.mining_data import MiningDeposit, ExploitationArea, Infrastructure, db

logger = logging.getLogger(__name__)
mining_import_bp = Blueprint('mining_import', __name__)

ALLOWED_EXTENSIONS = {'json', 'geojson', 'csv'}


def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _deposit_data_to_model_kwargs(deposit_data):
    """
    Mappe les clés GeoJSON (substance, operator, estimated_reserves, etc.)
    vers les attributs du modèle MiningDeposit (type, company, estimated_quantity).
    """
    status_raw = (deposit_data.get('status') or 'exploration').strip()
    status_map = {
        'exploration': 'Exploration',
        'en développement': 'En développement',
        'en developpement': 'En développement',
        'actif': 'Actif',
        'suspendu': 'Suspendu',
        'fermé': 'Fermé',
        'ferme': 'Fermé',
    }
    status = status_map.get(status_raw.lower(), status_raw if status_raw else 'Exploration')
    if status not in ('Actif', 'En développement', 'Exploration', 'Suspendu', 'Fermé'):
        status = 'Exploration'

    return {
        'name': deposit_data.get('name') or 'Dépôt',
        'type': deposit_data.get('deposit_type') or deposit_data.get('substance') or 'Inconnu',
        'latitude': deposit_data['latitude'],
        'longitude': deposit_data['longitude'],
        'company': deposit_data.get('operator') or 'Non spécifié',
        'estimated_quantity': deposit_data.get('estimated_reserves'),
        'status': status,
        'description': deposit_data.get('description'),
    }


@mining_import_bp.route('/import/deposits', methods=['POST'])
def import_deposits():
    """
    Importer des dépôts miniers depuis un fichier GeoJSON ou CSV
    
    Format GeoJSON attendu :
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "name": "Nom du gisement",
                    "substance": "Or",
                    "status": "exploration",
                    "estimated_reserves": "1000 tonnes",
                    ...
                }
            }
        ]
    }
    """
    try:
        # Vérifier qu'un fichier a été envoyé
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Nom de fichier vide'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': f'Format non supporté. Formats acceptés : {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Lire le contenu du fichier
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        
        if file_extension in ['json', 'geojson']:
            # Parsing GeoJSON
            geojson_data = json.load(file)
            deposits = _parse_geojson_deposits(geojson_data)
        elif file_extension == 'csv':
            # Parsing CSV
            return jsonify({
                'success': False,
                'message': 'Import CSV non encore implémenté'
            }), 501
        else:
            return jsonify({'success': False, 'message': 'Format non reconnu'}), 400
        
        if not deposits:
            return jsonify({
                'success': False,
                'message': 'Aucun dépôt valide trouvé dans le fichier'
            }), 400
        
        # Sauvegarder les dépôts en base de données
        imported_count = 0
        errors = []
        
        for deposit_data in deposits:
            try:
                kwargs = _deposit_data_to_model_kwargs(deposit_data)
                existing = MiningDeposit.query.filter_by(name=kwargs['name']).first()

                if existing:
                    for key, value in kwargs.items():
                        if hasattr(existing, key) and key != 'id':
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                else:
                    deposit = MiningDeposit(**kwargs)
                    db.session.add(deposit)

                imported_count += 1

            except Exception as e:
                logger.error(f"Erreur import dépôt {deposit_data.get('name', 'N/A')}: {str(e)}")
                errors.append(f"{deposit_data.get('name', 'N/A')}: {str(e)}")
        
        # Commit en base
        try:
            db.session.commit()
            
            message = f"{imported_count} dépôt(s) importé(s) avec succès"
            if errors:
                message += f". {len(errors)} erreur(s) rencontrée(s)"
            
            return jsonify({
                'success': True,
                'message': message,
                'imported_count': imported_count,
                'errors': errors
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur commit import: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erreur lors de la sauvegarde: {str(e)}'
            }), 500
    
    except json.JSONDecodeError as e:
        return jsonify({
            'success': False,
            'message': f'Fichier JSON invalide: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Erreur import deposits: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erreur inattendue: {str(e)}'
        }), 500


def _parse_geojson_deposits(geojson_data):
    """
    Parse un GeoJSON et extrait les dépôts miniers
    
    Returns:
        List[dict]: Liste de dictionnaires avec les données des dépôts
    """
    deposits = []
    
    # Vérifier le type
    if geojson_data.get('type') == 'FeatureCollection':
        features = geojson_data.get('features', [])
    elif geojson_data.get('type') == 'Feature':
        features = [geojson_data]
    else:
        logger.warning(f"Type GeoJSON non reconnu: {geojson_data.get('type')}")
        return deposits
    
    # Parser chaque feature
    for i, feature in enumerate(features):
        try:
            geometry = feature.get('geometry')
            properties = feature.get('properties', {})
            
            if not geometry or not geometry.get('type'):
                logger.warning(f"Feature {i} sans géométrie valide")
                continue
            
            # Vérifier que c'est un Point
            if geometry['type'] != 'Point':
                logger.warning(f"Feature {i} n'est pas un Point, ignoré")
                continue
            
            # Extraire les coordonnées
            coordinates = geometry.get('coordinates')
            if not coordinates or len(coordinates) < 2:
                logger.warning(f"Feature {i} avec coordonnées invalides")
                continue
            
            longitude = float(coordinates[0])
            latitude = float(coordinates[1])
            
            # Créer le dictionnaire deposit
            deposit_data = {
                'name': properties.get('name', f'Dépôt {i+1}'),
                'substance': properties.get('substance', 'Non spécifié'),
                'deposit_type': properties.get('deposit_type', properties.get('type', 'Inconnu')),
                'status': properties.get('status', 'exploration'),
                'latitude': latitude,
                'longitude': longitude,
                'estimated_reserves': properties.get('estimated_reserves'),
                'exploration_date': properties.get('exploration_date'),
                'operator': properties.get('operator'),
                'permit_number': properties.get('permit_number'),
                'description': properties.get('description'),
                'created_at': properties.get('created_at', datetime.utcnow().isoformat()),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            deposits.append(deposit_data)
            
        except (ValueError, KeyError, TypeError) as e:
            logger.warning(f"Erreur parsing feature {i}: {str(e)}")
            continue
    
    return deposits


@mining_import_bp.route('/import/exploitation-areas', methods=['POST'])
def import_exploitation_areas():
    """
    Importer des zones d'exploitation depuis un fichier GeoJSON
    
    Format attendu : Polygon ou MultiPolygon avec properties similaires aux deposits
    """
    return jsonify({
        'success': False,
        'message': 'Import des zones d\'exploitation non encore implémenté'
    }), 501


@mining_import_bp.route('/import/infrastructure', methods=['POST'])
def import_infrastructure():
    """
    Importer des infrastructures depuis un fichier GeoJSON
    
    Format attendu : LineString ou MultiLineString
    """
    return jsonify({
        'success': False,
        'message': 'Import des infrastructures non encore implémenté'
    }), 501
