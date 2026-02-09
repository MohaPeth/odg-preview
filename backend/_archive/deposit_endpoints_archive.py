# -*- coding: utf-8 -*-
"""
ARCHIVÉ - Endpoint d'ajout de gisement (Phase 2).

Rôle initial : validation et création de gisements miniers via le modèle MiningDepositGIS
et le référentiel Substance.

Raison de l'archivage :
- Non enregistré dans main.py (jamais branché).
- Dépend de models.geospatial.MiningDepositGIS et models.substances (imports sans src.),
  modèles/chemins absents ou différents dans le dépôt actuel.
- Doublon fonctionnel avec webgis (CRUD gisements) et mining_import (import GeoJSON).

La gestion des gisements passe par : webgis (routes /api/webgis/deposits) et
mining_import (POST /api/mining/import/deposits).
Conservé pour référence uniquement.
"""

# -*- coding: utf-8 -*-
"""
Endpoint d'ajout de gisement - Phase 2
Fonctions de validation et création de gisements miniers
"""

from flask import jsonify, request
from flask_cors import cross_origin
from models.geospatial import MiningDepositGIS
from models.substances import Substance
from models.mining_data import db
from sqlalchemy import func
from datetime import datetime
import re

def validate_deposit_data(data):
    """Validation complète des données de gisement"""
    errors = []
    
    # Validation des champs obligatoires
    required_fields = ['name', 'company', 'substanceId', 'latitude', 'longitude', 'status']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Le champ '{field}' est obligatoire")
    
    # Validation du nom (longueur et caractères autorisés)
    if 'name' in data and data['name']:
        name = data['name'].strip()
        if len(name) < 3:
            errors.append("Le nom du gisement doit contenir au moins 3 caractères")
        elif len(name) > 100:
            errors.append("Le nom du gisement ne peut pas dépasser 100 caractères")
        elif not re.match(r'^[a-zA-ZÀ-ÿ0-9\s\-_\.]+$', name):
            errors.append("Le nom du gisement contient des caractères non autorisés")
    
    # Validation de l'entreprise
    if 'company' in data and data['company']:
        company = data['company'].strip()
        if len(company) < 2:
            errors.append("Le nom de l'entreprise doit contenir au moins 2 caractères")
        elif len(company) > 100:
            errors.append("Le nom de l'entreprise ne peut pas dépasser 100 caractères")
    
    # Validation de la substance
    if 'substanceId' in data:
        try:
            substance_id = int(data['substanceId'])
            substance = Substance.query.get(substance_id)
            if not substance:
                errors.append("La substance sélectionnée n'existe pas")
            elif not substance.is_active:
                errors.append("La substance sélectionnée n'est plus active")
        except (ValueError, TypeError):
            errors.append("L'ID de la substance doit être un nombre entier")
    
    # Validation des coordonnées géographiques
    if 'latitude' in data:
        try:
            lat = float(data['latitude'])
            if lat < -90 or lat > 90:
                errors.append("La latitude doit être comprise entre -90 et 90 degrés")
            # Vérification spécifique pour le Gabon (approximativement)
            elif lat < -5 or lat > 3:
                errors.append("La latitude semble être en dehors du territoire gabonais (-5° à 3°)")
        except (ValueError, TypeError):
            errors.append("La latitude doit être un nombre décimal valide")
    
    if 'longitude' in data:
        try:
            lng = float(data['longitude'])
            if lng < -180 or lng > 180:
                errors.append("La longitude doit être comprise entre -180 et 180 degrés")
            # Vérification spécifique pour le Gabon (approximativement)
            elif lng < 8 or lng > 15:
                errors.append("La longitude semble être en dehors du territoire gabonais (8° à 15°)")
        except (ValueError, TypeError):
            errors.append("La longitude doit être un nombre décimal valide")
    
    # Validation du statut
    valid_statuses = ['Exploration', 'En développement', 'Actif', 'Suspendu', 'Fermé']
    if 'status' in data and data['status'] not in valid_statuses:
        errors.append(f"Le statut doit être un de : {', '.join(valid_statuses)}")
    
    # Validation des valeurs numériques optionnelles
    if 'estimatedQuantity' in data and data['estimatedQuantity'] is not None:
        try:
            quantity = float(data['estimatedQuantity'])
            if quantity < 0:
                errors.append("La quantité estimée ne peut pas être négative")
            elif quantity > 1000000000:  # 1 milliard
                errors.append("La quantité estimée semble irréaliste (> 1 milliard)")
        except (ValueError, TypeError):
            errors.append("La quantité estimée doit être un nombre décimal")
    
    if 'estimatedValue' in data and data['estimatedValue'] is not None:
        try:
            value = float(data['estimatedValue'])
            if value < 0:
                errors.append("La valeur estimée ne peut pas être négative")
        except (ValueError, TypeError):
            errors.append("La valeur estimée doit être un nombre décimal")
    
    # Validation de la description (optionnelle mais limitée)
    if 'description' in data and data['description']:
        if len(data['description']) > 1000:
            errors.append("La description ne peut pas dépasser 1000 caractères")
    
    return errors

def check_duplicate_deposit(name, latitude, longitude, substance_id):
    """Vérifier s'il existe déjà un gisement similaire"""
    # Vérification par nom exact
    existing_name = MiningDepositGIS.query.filter_by(name=name.strip()).first()
    if existing_name:
        return f"Un gisement avec le nom '{name}' existe déjà"
    
    # Vérification par proximité géographique (rayon de 1km)
    try:
        nearby_deposits = db.session.execute(
            db.text("""
                SELECT id, name, ST_Distance(
                    ST_GeomFromText(:point, 4326)::geography,
                    geom::geography
                ) / 1000 as distance_km
                FROM mining_deposits_gis 
                WHERE substance_id = :substance_id
                AND ST_DWithin(
                    ST_GeomFromText(:point, 4326)::geography,
                    geom::geography,
                    1000
                )
            """),
            {
                "point": f"POINT({longitude} {latitude})",
                "substance_id": substance_id
            }
        ).fetchall()
        
        if nearby_deposits:
            closest = nearby_deposits[0]
            return f"Un gisement similaire '{closest.name}' existe déjà à {closest.distance_km:.2f} km de cette localisation"
    
    except Exception as e:
        # Si erreur de géométrie, on continue sans vérification de proximité
        print(f"Erreur vérification proximité: {e}")
    
    return None

@cross_origin()
def create_deposit():
    """Créer un nouveau gisement minier - Phase 2"""
    try:
        # Récupération des données JSON
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Le contenu doit être en format JSON'
            }), 400
        
        data = request.get_json()
        
        # Validation des données
        validation_errors = validate_deposit_data(data)
        if validation_errors:
            return jsonify({
                'success': False,
                'error': 'Données invalides',
                'details': validation_errors
            }), 400
        
        # Vérification des doublons
        duplicate_check = check_duplicate_deposit(
            data['name'],
            float(data['latitude']),
            float(data['longitude']),
            int(data['substanceId'])
        )
        if duplicate_check:
            return jsonify({
                'success': False,
                'error': 'Gisement en doublon',
                'details': [duplicate_check]
            }), 409  # Conflict
        
        # Création de l'objet géospatial PostGIS
        point_wkt = f"POINT({data['longitude']} {data['latitude']})"
        
        # Récupération de la substance pour validation finale
        substance = Substance.query.get(int(data['substanceId']))
        if not substance:
            return jsonify({
                'success': False,
                'error': 'Substance introuvable'
            }), 404
        
        # Création du nouveau gisement avec les bons noms de paramètres
        new_deposit = MiningDepositGIS()
        new_deposit.name = data['name'].strip()
        new_deposit.description = data.get('description', '').strip() if data.get('description') else None
        new_deposit.geom = func.ST_GeomFromText(point_wkt, 4326)
        new_deposit.substance_id = int(data['substanceId'])
        new_deposit.company = data['company'].strip()
        new_deposit.status = data['status']
        new_deposit.estimated_quantity = float(data['estimatedQuantity']) if data.get('estimatedQuantity') else None
        new_deposit.quantity_unit = substance.unit
        new_deposit.estimated_value = float(data['estimatedValue']) if data.get('estimatedValue') else None
        
        # Métadonnées de création
        new_deposit.created_by = data.get('createdBy', 'web_interface')
        new_deposit.data_source = 'ODG WebGIS Interface'
        new_deposit.data_quality = 'draft'
        new_deposit.approval_status = 'pending'
        new_deposit.coordinate_precision = 10.0
        new_deposit.survey_method = 'GPS'
        new_deposit.created_at = datetime.utcnow()
        new_deposit.updated_at = datetime.utcnow()
        
        # Sauvegarde en base de données
        db.session.add(new_deposit)
        db.session.commit()
        
        # Actualiser l'objet pour récupérer l'ID généré et les relations
        db.session.refresh(new_deposit)
        
        # Récupération du gisement créé avec ses relations
        created_deposit = MiningDepositGIS.query.options(
            db.joinedload(MiningDepositGIS.substance)
        ).get(new_deposit.id)
        
        # Vérification de sécurité
        if not created_deposit:
            return jsonify({
                'success': False,
                'error': 'Erreur lors de la récupération du gisement créé'
            }), 500
        
        # Réponse de succès
        response_data = {
            'success': True,
            'message': 'Gisement créé avec succès',
            'deposit': created_deposit.to_dict(include_geom=True, include_relations=True),
            'geojson': created_deposit.to_geojson_feature(),
            'metadata': {
                'id': created_deposit.id,
                'approvalStatus': created_deposit.approval_status,
                'dataQuality': created_deposit.data_quality,
                'createdAt': created_deposit.created_at.isoformat() if created_deposit.created_at else None
            }
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        # Rollback en cas d'erreur
        db.session.rollback()
        
        # Log de l'erreur
        print(f"Erreur création gisement: {str(e)}")
        
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur',
            'details': [f'Erreur lors de la création: {str(e)}']
        }), 500

@cross_origin()
def get_substances_list():
    """Récupérer la liste des substances actives pour le formulaire"""
    try:
        substances = Substance.query.filter_by(is_active=True).order_by(Substance.name).all()
        
        substances_data = []
        for substance in substances:
            # S'assurer que toutes les chaînes sont en UTF-8
            substance_dict = {
                'id': substance.id,
                'name': str(substance.name or '').encode('utf-8', errors='replace').decode('utf-8'),
                'symbol': str(substance.symbol or '').encode('utf-8', errors='replace').decode('utf-8'),
                'colorCode': substance.color_code,
                'unit': str(substance.unit or '').encode('utf-8', errors='replace').decode('utf-8'),
                'marketPrice': substance.market_price,
                'description': str(substance.description or '').encode('utf-8', errors='replace').decode('utf-8')
            }
            substances_data.append(substance_dict)
        
        response = jsonify({
            'success': True,
            'substances': substances_data,
            'count': len(substances_data)
        })
        
        # S'assurer que la réponse est en UTF-8
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
        
    except Exception as e:
        error_response = jsonify({
            'success': False,
            'error': f'Erreur récupération substances: {str(e)}'
        })
        error_response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return error_response, 500
