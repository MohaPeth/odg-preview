# Routes WebGIS avec support PostGIS pour ODG Platform
from flask import jsonify, request
from flask_cors import cross_origin
from models.geospatial import MiningDepositGIS, Community
from models.substances import Substance
from models.mining_data import db
from sqlalchemy import func
from datetime import datetime
import json
import re

# Import des endpoints Phase 2
from routes.deposit_endpoints import create_deposit, get_substances_list

@cross_origin()
def get_all_layers():
    """Récupérer toutes les couches SIG disponibles"""
    try:
        # Substances disponibles
        substances = Substance.query.all()
        substance_layers = []
        
        for substance in substances:
            deposits_count = MiningDepositGIS.query.filter_by(substance_id=substance.id).count()
            substance_layers.append({
                'id': f'substance_{substance.id}',
                'name': f'{substance.name} ({substance.symbol})',
                'type': 'substance',
                'substanceId': substance.id,
                'color': substance.color_code,
                'visible': True,
                'opacity': 100,
                'count': deposits_count,
                'marketPrice': substance.market_price_eur,
                'density': substance.density
            })
        
        # Couches système
        system_layers = [
            {
                'id': 'communities',
                'name': 'Communautés locales',
                'type': 'communities',
                'color': '#6B7280',
                'visible': True,
                'opacity': 80,
                'count': Community.query.count()
            },
            {
                'id': 'infrastructure',
                'name': 'Infrastructure',
                'type': 'infrastructure',
                'color': '#374151',
                'visible': False,
                'opacity': 70,
                'count': 0
            },
            {
                'id': 'protected_areas',
                'name': 'Zones protégées',
                'type': 'protected_areas',
                'color': '#059669',
                'visible': False,
                'opacity': 60,
                'count': 0
            }
        ]
        
        return jsonify({
            'success': True,
            'layers': {
                'substances': substance_layers,
                'system': system_layers
            },
            'totalDeposits': MiningDepositGIS.query.count(),
            'totalCommunities': Community.query.count()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur récupération couches: {str(e)}'
        }), 500

@cross_origin()
def get_deposits_geojson():
    """Récupérer tous les gisements au format GeoJSON"""
    try:
        # Filtres optionnels
        substance_ids = request.args.getlist('substances')
        statuses = request.args.getlist('statuses')
        bbox = request.args.get('bbox')  # "minLng,minLat,maxLng,maxLat"
        
        # Construire la requête
        query = MiningDepositGIS.query
        
        # Filtre par substances
        if substance_ids:
            substance_ids = [int(sid) for sid in substance_ids if sid.isdigit()]
            query = query.filter(MiningDepositGIS.substance_id.in_(substance_ids))
        
        # Filtre par statuts
        if statuses:
            query = query.filter(MiningDepositGIS.status.in_(statuses))
        
        # Filtre par bounding box
        if bbox:
            try:
                min_lng, min_lat, max_lng, max_lat = map(float, bbox.split(','))
                query = query.filter(
                    func.ST_Intersects(
                        MiningDepositGIS.geom,
                        func.ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326)
                    )
                )
            except ValueError:
                pass  # Ignorer bbox invalide
        
        # Récupérer avec relations
        deposits = query.options(db.joinedload(MiningDepositGIS.substance)).all()
        
        # Construire GeoJSON
        features = []
        for deposit in deposits:
            feature = deposit.to_geojson_feature()
            if feature:
                features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features,
            "properties": {
                "totalFeatures": len(features),
                "filters": {
                    "substances": substance_ids,
                    "statuses": statuses,
                    "bbox": bbox
                }
            }
        }
        
        return jsonify({
            'success': True,
            'data': geojson
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur récupération gisements: {str(e)}'
        }), 500

@cross_origin()
def get_communities_geojson():
    """Récupérer toutes les communautés au format GeoJSON"""
    try:
        # Filtres optionnels
        min_population = request.args.get('minPopulation', type=int)
        affected_only = request.args.get('affectedOnly', 'false').lower() == 'true'
        bbox = request.args.get('bbox')
        
        # Construire la requête
        query = Community.query
        
        if min_population:
            query = query.filter(Community.population >= min_population)
        
        if affected_only:
            query = query.filter(Community.affected_by_mining == True)
        
        if bbox:
            try:
                min_lng, min_lat, max_lng, max_lat = map(float, bbox.split(','))
                query = query.filter(
                    func.ST_Intersects(
                        Community.geom,
                        func.ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326)
                    )
                )
            except ValueError:
                pass
        
        communities = query.all()
        
        # Construire GeoJSON
        features = []
        for community in communities:
            feature = community.to_geojson_feature()
            if feature:
                features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features,
            "properties": {
                "totalFeatures": len(features),
                "filters": {
                    "minPopulation": min_population,
                    "affectedOnly": affected_only,
                    "bbox": bbox
                }
            }
        }
        
        return jsonify({
            'success': True,
            'data': geojson
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur récupération communautés: {str(e)}'
        }), 500

@cross_origin()
def get_deposit_details(deposit_id):
    """Récupérer les détails complets d'un gisement"""
    try:
        deposit = MiningDepositGIS.query.options(
            db.joinedload(MiningDepositGIS.substance)
        ).get_or_404(deposit_id)
        
        # Calculer les communautés proches (dans un rayon de 50km)
        coords = deposit.get_coordinates()
        nearby_communities = []
        
        if coords:
            communities = Community.query.filter(
                func.ST_DWithin(
                    Community.geom,
                    func.ST_GeomFromText(f"POINT({coords['longitude']} {coords['latitude']})", 4326),
                    50000  # 50 km en mètres
                )
            ).all()
            
            for community in communities:
                # Calculer distance exacte
                distance_result = db.session.execute(
                    db.text("""
                        SELECT ST_Distance(
                            ST_GeomFromText(:deposit_point, 4326)::geography,
                            geom::geography
                        ) / 1000 as distance_km
                        FROM communities WHERE id = :community_id
                    """),
                    {
                        "deposit_point": f"POINT({coords['longitude']} {coords['latitude']})",
                        "community_id": community.id
                    }
                ).fetchone()
                
                community_data = community.to_dict()
                if distance_result and hasattr(distance_result, 'distance_km'):
                    community_data['distanceKm'] = round(float(distance_result.distance_km), 2)
                else:
                    community_data['distanceKm'] = 0.0
                nearby_communities.append(community_data)
        
        # Gisements similaires (même substance, dans un rayon de 100km)
        similar_deposits = []
        if coords:
            similar = MiningDepositGIS.query.filter(
                MiningDepositGIS.substance_id == deposit.substance_id,
                MiningDepositGIS.id != deposit.id,
                func.ST_DWithin(
                    MiningDepositGIS.geom,
                    func.ST_GeomFromText(f"POINT({coords['longitude']} {coords['latitude']})", 4326),
                    100000  # 100 km
                )
            ).limit(5).all()
            
            for sim_deposit in similar:
                similar_deposits.append({
                    'id': sim_deposit.id,
                    'name': sim_deposit.name,
                    'company': sim_deposit.company,
                    'status': sim_deposit.status,
                    'estimatedQuantity': sim_deposit.estimated_quantity
                })
        
        result = {
            'deposit': deposit.to_dict(include_geom=True, include_relations=True),
            'nearbyCommunities': nearby_communities,
            'similarDeposits': similar_deposits,
            'analytics': {
                'totalCommunities': len(nearby_communities),
                'affectedCommunities': len([c for c in nearby_communities if c.get('affectedByMining')]),
                'totalPopulation': sum(c.get('population', 0) for c in nearby_communities),
                'averageDistance': round(
                    sum(c.get('distanceKm', 0) for c in nearby_communities) / max(len(nearby_communities), 1), 2
                )
            }
        }
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur récupération détails: {str(e)}'
        }), 500

@cross_origin()
def search_locations():
    """Recherche géographique avancée"""
    try:
        query_text = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all')  # all, deposits, communities
        limit = min(request.args.get('limit', 20, type=int), 100)
        
        if not query_text:
            return jsonify({
                'success': False,
                'error': 'Paramètre de recherche requis'
            }), 400
        
        results = {
            'deposits': [],
            'communities': [],
            'substances': []
        }
        
        # Recherche dans les gisements
        if search_type in ['all', 'deposits']:
            deposits = MiningDepositGIS.query.options(
                db.joinedload(MiningDepositGIS.substance)
            ).filter(
                MiningDepositGIS.name.ilike(f'%{query_text}%') |
                MiningDepositGIS.company.ilike(f'%{query_text}%') |
                MiningDepositGIS.description.ilike(f'%{query_text}%')
            ).limit(limit).all()
            
            for deposit in deposits:
                results['deposits'].append({
                    'id': deposit.id,
                    'name': deposit.name,
                    'type': 'deposit',
                    'company': deposit.company,
                    'substance': deposit.substance.name if deposit.substance else None,
                    'substanceColor': deposit.substance.color_code if deposit.substance else None,
                    'status': deposit.status,
                    'coordinates': deposit.get_coordinates()
                })
        
        # Recherche dans les communautés
        if search_type in ['all', 'communities']:
            communities = Community.query.filter(
                Community.name.ilike(f'%{query_text}%') |
                Community.canton.ilike(f'%{query_text}%') |
                Community.department.ilike(f'%{query_text}%')
            ).limit(limit).all()
            
            for community in communities:
                results['communities'].append({
                    'id': community.id,
                    'name': community.name,
                    'type': 'community',
                    'population': community.population,
                    'administrativeLevel': community.administrative_level,
                    'affectedByMining': community.affected_by_mining,
                    'coordinates': community.get_coordinates()
                })
        
        # Recherche dans les substances
        if search_type in ['all', 'substances']:
            substances = Substance.query.filter(
                Substance.name.ilike(f'%{query_text}%') |
                Substance.symbol.ilike(f'%{query_text}%')
            ).all()
            
            for substance in substances:
                deposit_count = MiningDepositGIS.query.filter_by(substance_id=substance.id).count()
                results['substances'].append({
                    'id': substance.id,
                    'name': substance.name,
                    'type': 'substance',
                    'symbol': substance.symbol,
                    'color': substance.color_code,
                    'depositCount': deposit_count,
                    'marketPrice': substance.market_price_eur
                })
        
        total_results = len(results['deposits']) + len(results['communities']) + len(results['substances'])
        
        return jsonify({
            'success': True,
            'data': results,
            'meta': {
                'query': query_text,
                'searchType': search_type,
                'totalResults': total_results,
                'limit': limit
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur recherche: {str(e)}'
        }), 500

@cross_origin()
def get_statistics():
    """Statistiques globales de la plateforme"""
    try:
        # Statistiques générales
        total_deposits = MiningDepositGIS.query.count()
        total_communities = Community.query.count()
        total_substances = Substance.query.count()
        
        # Répartition par substance
        substance_stats = []
        for substance in Substance.query.all():
            deposit_count = MiningDepositGIS.query.filter_by(substance_id=substance.id).count()
            active_count = MiningDepositGIS.query.filter_by(
                substance_id=substance.id,
                status='Actif'
            ).count()
            
            # Valeur totale estimée
            total_value = db.session.execute(
                db.text("""
                    SELECT COALESCE(SUM(estimated_value), 0) as total
                    FROM mining_deposits_gis 
                    WHERE substance_id = :substance_id
                """),
                {"substance_id": substance.id}
            ).fetchone()
            
            substance_stats.append({
                'id': substance.id,
                'name': substance.name,
                'symbol': substance.symbol,
                'color': substance.color_code,
                'totalDeposits': deposit_count,
                'activeDeposits': active_count,
                'estimatedValue': float(total_value.total) if total_value and hasattr(total_value, 'total') and total_value.total else 0,
                'marketPrice': substance.market_price_eur
            })
        
        # Répartition par statut
        status_stats = db.session.execute(
            db.text("""
                SELECT status, COUNT(*) as count
                FROM mining_deposits_gis
                GROUP BY status
                ORDER BY count DESC
            """)
        ).fetchall()
        
        status_distribution = [
            {'status': row.status, 'count': row.count}
            for row in status_stats
        ]
        
        # Communautés affectées
        affected_communities = Community.query.filter_by(affected_by_mining=True).count()
        total_affected_population = db.session.execute(
            db.text("""
                SELECT COALESCE(SUM(population), 0) as total
                FROM communities
                WHERE affected_by_mining = true
            """)
        ).fetchone()
        
        # Top entreprises
        company_stats = db.session.execute(
            db.text("""
                SELECT company, COUNT(*) as deposit_count
                FROM mining_deposits_gis
                WHERE company IS NOT NULL
                GROUP BY company
                ORDER BY deposit_count DESC
                LIMIT 10
            """)
        ).fetchall()
        
        top_companies = [
            {'company': row.company, 'depositCount': row.deposit_count}
            for row in company_stats
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'overview': {
                    'totalDeposits': total_deposits,
                    'totalCommunities': total_communities,
                    'totalSubstances': total_substances,
                    'affectedCommunities': affected_communities,
                    'affectedPopulation': int(total_affected_population.total) if total_affected_population and hasattr(total_affected_population, 'total') and total_affected_population.total else 0
                },
                'substanceDistribution': substance_stats,
                'statusDistribution': status_distribution,
                'topCompanies': top_companies
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur récupération statistiques: {str(e)}'
        }), 500

# Routes pour enregistrer les endpoints
def register_webgis_routes(app):
    """Enregistrer toutes les routes WebGIS"""
    app.add_url_rule('/api/webgis/layers', 'get_layers', get_all_layers, methods=['GET'])
    app.add_url_rule('/api/webgis/deposits', 'get_deposits', get_deposits_geojson, methods=['GET'])
    app.add_url_rule('/api/webgis/deposits', 'create_deposit', create_deposit, methods=['POST'])
    app.add_url_rule('/api/webgis/communities', 'get_communities', get_communities_geojson, methods=['GET'])
    app.add_url_rule('/api/webgis/deposits/<int:deposit_id>', 'get_deposit_details', get_deposit_details, methods=['GET'])
    app.add_url_rule('/api/webgis/search', 'search_locations', search_locations, methods=['GET'])
    app.add_url_rule('/api/webgis/statistics', 'get_statistics', get_statistics, methods=['GET'])
    app.add_url_rule('/api/webgis/substances', 'get_substances', get_substances_list, methods=['GET'])