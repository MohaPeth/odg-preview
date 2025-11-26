#!/usr/bin/env python3
"""
Script de test pour valider la configuration PostGIS et les modèles géospatiaux
Usage: python test_geospatial_setup.py
"""

import os
import sys
import json
from datetime import datetime

# Ajout du chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from geoalchemy2 import Geometry
    from geoalchemy2.functions import ST_GeomFromText, ST_AsGeoJSON, ST_Area, ST_Length
    from src.models.geospatial_layers import GeospatialLayer, LayerUploadHistory, db
    print("✅ Imports réussis")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Installez les dépendances manquantes:")
    print("pip install geoalchemy2 shapely")
    sys.exit(1)

def create_test_app():
    """Crée une application Flask de test"""
    app = Flask(__name__)
    
    # Configuration pour PostgreSQL/PostGIS (à adapter selon votre config)
    # Pour les tests, on peut utiliser SQLite avec SpatiaLite ou PostgreSQL
    
    # Option 1: PostgreSQL/PostGIS (recommandé)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/odg_test'
    
    # Option 2: SQLite avec SpatiaLite (pour tests rapides)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_geospatial.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    
    db.init_app(app)
    return app

def test_model_creation():
    """Test de création des modèles"""
    print("\n🧪 Test de création des modèles...")
    
    app = create_test_app()
    
    with app.app_context():
        try:
            # Création des tables
            db.create_all()
            print("✅ Tables créées avec succès")
            
            # Vérification de la structure des tables
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['geospatial_layers', 'layer_upload_history']
            for table in expected_tables:
                if table in tables:
                    print(f"✅ Table '{table}' existe")
                    
                    # Vérification des colonnes
                    columns = [col['name'] for col in inspector.get_columns(table)]
                    print(f"   Colonnes: {', '.join(columns[:5])}...")
                else:
                    print(f"❌ Table '{table}' manquante")
                    
        except Exception as e:
            print(f"❌ Erreur lors de la création des tables: {e}")
            return False
            
    return True

def test_geospatial_operations():
    """Test des opérations géospatiales"""
    print("\n🗺️ Test des opérations géospatiales...")
    
    app = create_test_app()
    
    with app.app_context():
        try:
            # Test 1: Création d'un point
            print("Test 1: Création d'un point (Libreville)")
            point_layer = GeospatialLayer(
                name="Test Point Libreville",
                description="Point de test pour Libreville, Gabon",
                layer_type="custom",
                geometry_type="POINT",
                source_format="CSV",
                status="actif"
            )
            
            # Ajout de la géométrie (Libreville: 0.3901° N, 9.4536° E)
            point_wkt = "POINT(9.4536 0.3901)"
            point_layer.geom = ST_GeomFromText(point_wkt, 4326)
            
            db.session.add(point_layer)
            db.session.commit()
            print("✅ Point créé avec ID:", point_layer.id)
            
            # Test 2: Création d'une ligne
            print("Test 2: Création d'une ligne (Route)")
            line_layer = GeospatialLayer(
                name="Test Route Libreville-Lambaréné",
                description="Route de test entre Libreville et Lambaréné",
                layer_type="infrastructure",
                geometry_type="LINESTRING",
                source_format="KML",
                status="actif"
            )
            
            # Route approximative Libreville -> Lambaréné
            line_wkt = "LINESTRING(9.4536 0.3901, 9.2 0.1, 8.9 -0.2, 8.7 -0.5, 8.6 -0.7)"
            line_layer.geom = ST_GeomFromText(line_wkt, 4326)
            
            db.session.add(line_layer)
            db.session.commit()
            print("✅ Ligne créée avec ID:", line_layer.id)
            
            # Test 3: Création d'un polygone
            print("Test 3: Création d'un polygone (Zone)")
            polygon_layer = GeospatialLayer(
                name="Test Zone Estuaire du Gabon",
                description="Zone de test dans l'estuaire du Gabon",
                layer_type="zone",
                geometry_type="POLYGON",
                source_format="SHP",
                status="actif"
            )
            
            # Polygone approximatif de l'estuaire
            polygon_wkt = "POLYGON((9.0 0.0, 10.0 0.0, 10.0 1.0, 9.5 1.2, 9.0 1.0, 9.0 0.0))"
            polygon_layer.geom = ST_GeomFromText(polygon_wkt, 4326)
            
            db.session.add(polygon_layer)
            db.session.commit()
            print("✅ Polygone créé avec ID:", polygon_layer.id)
            
            # Test 4: Calcul des statistiques
            print("Test 4: Calcul des statistiques géométriques")
            
            # Mise à jour des statistiques pour le polygone
            polygon_layer.update_statistics()
            db.session.commit()
            
            print(f"   Superficie du polygone: {polygon_layer.area_km2} km²")
            
            # Longueur de la ligne
            line_layer.update_statistics()
            db.session.commit()
            
            print(f"   Longueur de la route: {line_layer.length_km} km")
            
            # Test 5: Conversion en GeoJSON
            print("Test 5: Conversion en GeoJSON")
            
            geojson_feature = point_layer.to_geojson_feature()
            if geojson_feature:
                print("✅ Conversion GeoJSON réussie")
                print(f"   Type: {geojson_feature['geometry']['type']}")
                print(f"   Coordonnées: {geojson_feature['geometry']['coordinates']}")
            else:
                print("❌ Échec de la conversion GeoJSON")
                
        except Exception as e:
            print(f"❌ Erreur lors des opérations géospatiales: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    return True

def test_model_methods():
    """Test des méthodes du modèle"""
    print("\n🔧 Test des méthodes du modèle...")
    
    app = create_test_app()
    
    with app.app_context():
        try:
            # Test des méthodes de recherche
            print("Test des méthodes de recherche:")
            
            # Recherche par statut
            active_layers = GeospatialLayer.get_by_status('actif')
            print(f"✅ Couches actives trouvées: {len(active_layers)}")
            
            # Recherche par type
            custom_layers = GeospatialLayer.get_by_layer_type('custom')
            print(f"✅ Couches personnalisées trouvées: {len(custom_layers)}")
            
            # Recherche par nom
            search_results = GeospatialLayer.search_by_name('Test')
            print(f"✅ Résultats de recherche 'Test': {len(search_results)}")
            
            # Test de la méthode to_dict()
            if active_layers:
                layer_dict = active_layers[0].to_dict()
                print("✅ Conversion to_dict() réussie")
                print(f"   Clés: {list(layer_dict.keys())[:5]}...")
                
            # Test des styles par défaut
            test_layer = GeospatialLayer(
                name="Test Style",
                layer_type="deposit",
                geometry_type="POINT",
                source_format="CSV",
                status="actif"
            )
            test_layer.set_default_style_by_type()
            print("✅ Style par défaut appliqué")
            print(f"   Couleur: {test_layer.style_config.get('color')}")
            
        except Exception as e:
            print(f"❌ Erreur lors du test des méthodes: {e}")
            return False
            
    return True

def test_upload_history():
    """Test du modèle d'historique des uploads"""
    print("\n📁 Test de l'historique des uploads...")
    
    app = create_test_app()
    
    with app.app_context():
        try:
            # Création d'un enregistrement d'historique
            upload_record = LayerUploadHistory(
                original_filename="test_data.kml",
                file_size_bytes=1024000,
                file_format="KML",
                upload_status="success",
                features_count=150,
                processing_time_seconds=2.5,
                file_metadata={
                    "crs": "EPSG:4326",
                    "driver": "KML",
                    "features": 150
                }
            )
            
            db.session.add(upload_record)
            db.session.commit()
            
            print("✅ Enregistrement d'historique créé avec ID:", upload_record.id)
            
            # Test de la conversion en dictionnaire
            history_dict = upload_record.to_dict()
            print("✅ Conversion historique to_dict() réussie")
            print(f"   Statut: {history_dict['uploadStatus']}")
            print(f"   Nombre de features: {history_dict['featuresCount']}")
            
        except Exception as e:
            print(f"❌ Erreur lors du test de l'historique: {e}")
            return False
            
    return True

def cleanup_test_data():
    """Nettoyage des données de test"""
    print("\n🧹 Nettoyage des données de test...")
    
    app = create_test_app()
    
    with app.app_context():
        try:
            # Suppression des données de test
            GeospatialLayer.query.filter(GeospatialLayer.name.like('Test%')).delete()
            LayerUploadHistory.query.delete()
            db.session.commit()
            print("✅ Données de test supprimées")
            
        except Exception as e:
            print(f"❌ Erreur lors du nettoyage: {e}")

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests PostGIS pour ODG")
    print("=" * 50)
    
    success = True
    
    # Tests séquentiels
    tests = [
        ("Création des modèles", test_model_creation),
        ("Opérations géospatiales", test_geospatial_operations),
        ("Méthodes du modèle", test_model_methods),
        ("Historique des uploads", test_upload_history)
    ]
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}...")
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name}: SUCCÈS")
            else:
                print(f"❌ {test_name}: ÉCHEC")
                success = False
        except Exception as e:
            print(f"❌ {test_name}: ERREUR - {e}")
            success = False
    
    # Nettoyage
    cleanup_test_data()
    
    # Résumé final
    print("\n" + "=" * 50)
    if success:
        print("🎉 TOUS LES TESTS SONT PASSÉS!")
        print("✅ Le système géospatial est prêt pour l'implémentation")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez la configuration PostGIS et les dépendances")
    
    print("\n📋 Prochaines étapes:")
    print("1. Vérifier la configuration PostgreSQL/PostGIS")
    print("2. Installer les dépendances: pip install geoalchemy2 shapely fiona")
    print("3. Exécuter la migration SQL: create_geospatial_tables.sql")
    print("4. Passer à la Phase 1.2: Service d'import de fichiers")

if __name__ == "__main__":
    main()
