# Script de migration SQLite vers PostGIS pour ODG Platform
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from src.config import Config
from src.models.mining_data import db, MiningDeposit
# Import séparé pour éviter les erreurs circulaires
from src.models.substances import Substance
from src.models.substances import create_default_substances
from src.models.geospatial import MiningDepositGIS, Community
from geoalchemy2.functions import ST_GeomFromText
import sqlite3
import os
from datetime import datetime, date
import json

def create_app():
    """Créer l'application Flask pour migration"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def migrate_sqlite_to_postgis():
    """Migration complète des données SQLite vers PostGIS"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Début de la migration SQLite vers PostGIS")
        
        # 1. Créer toutes les tables PostGIS
        print("📋 Création des tables PostGIS...")
        try:
            db.create_all()
            print("✅ Tables PostGIS créées avec succès")
        except Exception as e:
            print(f"❌ Erreur création tables: {e}")
            return False
        
        # 2. Créer les substances par défaut
        print("🧪 Création des substances par défaut...")
        try:
            create_default_substances()
            db.session.commit()
            print("✅ Substances créées avec succès")
        except Exception as e:
            print(f"❌ Erreur création substances: {e}")
            return False
        
        # 3. Migrer les données SQLite existantes
        sqlite_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')
        if os.path.exists(sqlite_path):
            print(f"📂 Migration des données SQLite depuis: {sqlite_path}")
            migrate_mining_deposits(sqlite_path)
        else:
            print("⚠️ Aucune base SQLite trouvée, création d'exemples...")
            create_sample_data()
        
        print("✅ Migration terminée avec succès!")
        return True

def migrate_mining_deposits(sqlite_path):
    """Migrer les gisements de SQLite vers PostGIS"""
    try:
        # Connexion SQLite
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        cursor = sqlite_conn.cursor()
        
        # Récupérer les gisements SQLite
        cursor.execute("SELECT * FROM mining_deposit")
        deposits = cursor.fetchall()
        
        print(f"📊 {len(deposits)} gisements trouvés dans SQLite")
        
        # Mapping des substances par nom
        substance_map = {}
        for substance in Substance.query.all():
            substance_map[substance.name.lower()] = substance.id
        
        migrated_count = 0
        for deposit in deposits:
            try:
                # Déterminer la substance (par défaut: Fer si inconnue)
                substance_id = substance_map.get('fer', 3)  # ID par défaut: Fer
                
                # Déterminer la substance par le nom
                if deposit['name']:
                    name_lower = deposit['name'].lower()
                    if 'or' in name_lower or 'gold' in name_lower:
                        substance_id = substance_map.get('or', 1)
                    elif 'diamant' in name_lower or 'diamond' in name_lower:
                        substance_id = substance_map.get('diamant', 2)
                    elif 'sable' in name_lower or 'sand' in name_lower:
                        substance_id = substance_map.get('sable', 4)
                    elif 'manganèse' in name_lower or 'manganese' in name_lower:
                        substance_id = substance_map.get('manganèse', 5)
                
                # Créer le gisement PostGIS
                new_deposit = MiningDepositGIS(
                    name=deposit['name'] or f"Gisement_{deposit['id']}",
                    description=deposit['description'],
                    geom=ST_GeomFromText(
                        f"POINT({deposit['longitude']} {deposit['latitude']})",
                        4326
                    ),
                    substance_id=substance_id,
                    company=deposit['company'] or 'Non spécifié',
                    company_contact=deposit.get('contact'),
                    estimated_quantity=deposit.get('estimated_quantity'),
                    quantity_unit='tonnes',
                    status='Exploration',
                    data_source='Migration SQLite',
                    data_quality='validated',
                    created_by='System Migration',
                    approval_status='approved',
                    approval_date=datetime.utcnow()
                )
                
                db.session.add(new_deposit)
                migrated_count += 1
                
            except Exception as e:
                print(f"⚠️ Erreur migration gisement {deposit['id']}: {e}")
                continue
        
        # Valider les changements
        db.session.commit()
        sqlite_conn.close()
        
        print(f"✅ {migrated_count} gisements migrés avec succès")
        
    except Exception as e:
        print(f"❌ Erreur migration SQLite: {e}")
        db.session.rollback()

def create_sample_data():
    """Créer des données d'exemple pour la Guinée"""
    
    # Gisements d'exemple en Guinée
    sample_deposits = [
        {
            'name': 'Mine d\'Or de Siguiri',
            'lat': 11.4167, 'lng': -9.1667,
            'substance': 'Or',
            'company': 'AngloGold Ashanti',
            'description': 'Grande mine d\'or à ciel ouvert dans la région de Siguiri',
            'quantity': 2500000, 'status': 'Actif'
        },
        {
            'name': 'Mine de Bauxite de Sangarédi',
            'lat': 11.1333, 'lng': -13.7333,
            'substance': 'Manganèse',
            'company': 'Compagnie des Bauxites de Guinée',
            'description': 'Exploitation de bauxite pour production d\'aluminium',
            'quantity': 15000000, 'status': 'Actif'
        },
        {
            'name': 'Gisement de Fer de Simandou',
            'lat': 8.5667, 'lng': -8.9833,
            'substance': 'Fer',
            'company': 'Rio Tinto',
            'description': 'Gisement de minerai de fer de classe mondiale',
            'quantity': 2200000000, 'status': 'En_développement'
        },
        {
            'name': 'Mine de Diamant de Banankoro',
            'lat': 9.4167, 'lng': -10.0833,
            'substance': 'Diamant',
            'company': 'Société Aurifère de Guinée',
            'description': 'Exploitation artisanale de diamants alluviaux',
            'quantity': 50000, 'status': 'Exploration'
        },
        {
            'name': 'Carrière de Sable de Conakry',
            'lat': 9.6412, 'lng': -13.5784,
            'substance': 'Sable',
            'company': 'Entreprise Locale BTP',
            'description': 'Extraction de sable pour construction',
            'quantity': 100000, 'status': 'Actif'
        }
    ]
    
    # Mapping substances
    substance_map = {}
    for substance in Substance.query.all():
        substance_map[substance.name] = substance.id
    
    for deposit_data in sample_deposits:
        try:
            deposit = MiningDepositGIS(
                name=deposit_data['name'],
                description=deposit_data['description'],
                geom=ST_GeomFromText(
                    f"POINT({deposit_data['lng']} {deposit_data['lat']})",
                    4326
                ),
                substance_id=substance_map[deposit_data['substance']],
                company=deposit_data['company'],
                estimated_quantity=deposit_data['quantity'],
                quantity_unit='tonnes',
                status=deposit_data['status'],
                data_source='Données d\'exemple',
                data_quality='draft',
                created_by='System',
                approval_status='pending',
                geological_formation='Formation guinéenne',
                confidence_level='medium',
                accessibility='moderate'
            )
            
            db.session.add(deposit)
            
        except Exception as e:
            print(f"⚠️ Erreur création exemple {deposit_data['name']}: {e}")
    
    # Communautés d'exemple
    sample_communities = [
        {
            'name': 'Siguiri', 'lat': 11.4167, 'lng': -9.1667,
            'population': 28319, 'level': 'city', 'affected': True, 'distance': 0
        },
        {
            'name': 'Sangarédi', 'lat': 11.1333, 'lng': -13.7333,
            'population': 12000, 'level': 'town', 'affected': True, 'distance': 0
        },
        {
            'name': 'Beyla', 'lat': 8.6667, 'lng': -8.6667,
            'population': 15000, 'level': 'town', 'affected': True, 'distance': 12
        },
        {
            'name': 'Kouroussa', 'lat': 10.6500, 'lng': -9.8833,
            'population': 18000, 'level': 'town', 'affected': False, 'distance': 45
        }
    ]
    
    for comm_data in sample_communities:
        try:
            community = Community(
                name=comm_data['name'],
                geom=ST_GeomFromText(
                    f"POINT({comm_data['lng']} {comm_data['lat']})",
                    4326
                ),
                population=comm_data['population'],
                administrative_level=comm_data['level'],
                affected_by_mining=comm_data['affected'],
                nearest_mine_distance=comm_data['distance'],
                has_electricity=True if comm_data['level'] == 'city' else False,
                has_water=True,
                has_school=True,
                has_health_center=True if comm_data['population'] > 15000 else False,
                road_access='paved' if comm_data['level'] == 'city' else 'unpaved',
                main_activities='agriculture, commerce',
                employment_in_mining=50 if comm_data['affected'] else 0,
                data_source='Données d\'exemple'
            )
            
            db.session.add(community)
            
        except Exception as e:
            print(f"⚠️ Erreur création communauté {comm_data['name']}: {e}")
    
    # Valider toutes les créations
    try:
        db.session.commit()
        print("✅ Données d'exemple créées avec succès")
    except Exception as e:
        print(f"❌ Erreur validation données: {e}")
        db.session.rollback()

def verify_migration():
    """Vérifier le succès de la migration"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Vérification de la migration...")
        
        # Compter les enregistrements
        substances_count = Substance.query.count()
        deposits_count = MiningDepositGIS.query.count()
        communities_count = Community.query.count()
        
        print(f"📊 Résultats de la migration:")
        print(f"   - Substances: {substances_count}")
        print(f"   - Gisements: {deposits_count}")
        print(f"   - Communautés: {communities_count}")
        
        # Tester les requêtes géospatiales
        if deposits_count > 0:
            print("🗺️ Test des fonctions géospatiales...")
            
            # Premier gisement
            first_deposit = MiningDepositGIS.query.first()
            coords = first_deposit.get_coordinates()
            print(f"   - Coordonnées du premier gisement: {coords}")
            
            # Conversion GeoJSON
            geojson = first_deposit.to_geojson_feature()
            print(f"   - GeoJSON généré: {geojson is not None}")
            
            # Recherche par substance
            or_deposits = MiningDepositGIS.get_by_substance(1)  # Or
            print(f"   - Gisements d'or: {len(or_deposits)}")
        
        print("✅ Vérification terminée")

if __name__ == "__main__":
    print("🚀 Lancement de la migration ODG SQLite → PostGIS")
    
    if migrate_sqlite_to_postgis():
        verify_migration()
        print("🎉 Migration complète réussie!")
    else:
        print("💥 Échec de la migration")
