#!/usr/bin/env python3
"""
Script de test pour le service d'import géospatial
Usage: python test_geospatial_import.py
"""

import os
import sys
import json
import tempfile
from datetime import datetime

# Ajout du chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from flask import Flask
    from src.models.geospatial_layers import GeospatialLayer, LayerUploadHistory, db
    from src.services.geospatial_import import GeospatialImportService, FileValidator
    print("✅ Imports réussis")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)

def create_test_app():
    """Crée une application Flask de test"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_import.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    db.init_app(app)
    return app

def create_test_files():
    """Crée des fichiers de test pour l'import"""
    test_files = {}
    temp_dir = tempfile.mkdtemp(prefix='odg_test_')
    
    # 1. Fichier GeoJSON de test
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [9.4536, 0.3901]  # Libreville
                },
                "properties": {
                    "name": "Libreville",
                    "type": "Capitale",
                    "population": 703940
                }
            },
            {
                "type": "Feature", 
                "geometry": {
                    "type": "Point",
                    "coordinates": [8.7817, -0.7193]  # Port-Gentil
                },
                "properties": {
                    "name": "Port-Gentil",
                    "type": "Ville portuaire",
                    "population": 136462
                }
            }
        ]
    }
    
    geojson_file = os.path.join(temp_dir, 'villes_gabon.geojson')
    with open(geojson_file, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, indent=2)
    test_files['geojson'] = geojson_file
    
    # 2. Fichier CSV de test
    csv_data = """name,latitude,longitude,type,description
Gisement Belinga,-1.1,13.2,Fer,Gisement de fer dans l'est du Gabon
Mine Moanda,-1.5,13.2,Manganèse,Mine de manganèse exploitée par COMILOG
Gisement Tchibanga,-2.8,11.0,Or,Gisement aurifère dans la Nyanga"""
    
    csv_file = os.path.join(temp_dir, 'gisements_gabon.csv')
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write(csv_data)
    test_files['csv'] = csv_file
    
    # 3. Fichier KML de test
    kml_data = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Routes Gabon</name>
    <Placemark>
      <name>Route N1</name>
      <description>Route nationale principale</description>
      <LineString>
        <coordinates>
          9.4536,0.3901,0
          9.2,0.1,0
          8.9,-0.2,0
          8.7,-0.5,0
        </coordinates>
      </LineString>
    </Placemark>
    <Placemark>
      <name>Zone Estuaire</name>
      <description>Province de l'Estuaire</description>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              9.0,0.0,0
              10.0,0.0,0
              10.0,1.0,0
              9.0,1.0,0
              9.0,0.0,0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>"""
    
    kml_file = os.path.join(temp_dir, 'routes_gabon.kml')
    with open(kml_file, 'w', encoding='utf-8') as f:
        f.write(kml_data)
    test_files['kml'] = kml_file
    
    # 4. Fichier TXT de test (coordonnées simples)
    txt_data = """# Coordonnées des aéroports du Gabon
# Format: longitude latitude nom
9.4128 0.4586 Aéroport_Léon_Mba_Libreville
8.7542 -0.7111 Aéroport_Port_Gentil
13.2044 -1.6056 Aéroport_Franceville"""
    
    txt_file = os.path.join(temp_dir, 'aeroports_gabon.txt')
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(txt_data)
    test_files['txt'] = txt_file
    
    return test_files, temp_dir

def test_file_validation():
    """Test de validation des fichiers"""
    print("\n🔍 Test de validation des fichiers...")
    
    try:
        # Test extensions supportées
        extensions = FileValidator.get_supported_extensions()
        print(f"✅ Extensions supportées: {', '.join(extensions)}")
        
        # Test validation (simulation)
        class MockFile:
            def __init__(self, filename):
                self.filename = filename
        
        # Fichier valide
        valid_file = MockFile('test.geojson')
        is_valid, message = FileValidator.validate_file_upload(valid_file)
        if is_valid:
            print("✅ Validation fichier GeoJSON: OK")
        else:
            print(f"❌ Validation échouée: {message}")
        
        # Fichier invalide
        invalid_file = MockFile('test.xyz')
        is_valid, message = FileValidator.validate_file_upload(invalid_file)
        if not is_valid:
            print("✅ Rejet fichier invalide: OK")
        else:
            print("❌ Fichier invalide accepté")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur validation: {str(e)}")
        return False

def test_geojson_import():
    """Test d'import GeoJSON"""
    print("\n📍 Test d'import GeoJSON...")
    
    app = create_test_app()
    test_files, temp_dir = create_test_files()
    
    with app.app_context():
        try:
            db.create_all()
            
            # Configuration de la couche
            layer_config = {
                'name': 'Villes du Gabon',
                'description': 'Principales villes du Gabon avec population',
                'layer_type': 'custom',
                'status': 'actif'
            }
            
            # Import
            import_service = GeospatialImportService()
            success, message, layer = import_service.import_file(
                test_files['geojson'], 
                layer_config
            )
            
            if success and layer:
                print(f"✅ Import GeoJSON réussi: {message}")
                print(f"   Couche ID: {layer.id}")
                print(f"   Nom: {layer.name}")
                print(f"   Type géométrie: {layer.geometry_type}")
                print(f"   Nombre de features: {layer.metadata.get('source_info', {}).get('feature_count', 'N/A')}")
                
                # Test conversion GeoJSON
                geojson_feature = layer.to_geojson_feature()
                if geojson_feature:
                    print("✅ Conversion GeoJSON: OK")
                
                return True
            else:
                print(f"❌ Import GeoJSON échoué: {message}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur import GeoJSON: {str(e)}")
            return False
        finally:
            import_service.cleanup()

def test_csv_import():
    """Test d'import CSV"""
    print("\n📊 Test d'import CSV...")
    
    app = create_test_app()
    test_files, temp_dir = create_test_files()
    
    with app.app_context():
        try:
            db.create_all()
            
            layer_config = {
                'name': 'Gisements Miniers Gabon',
                'description': 'Principaux gisements miniers du Gabon',
                'layer_type': 'deposit',
                'status': 'actif'
            }
            
            import_service = GeospatialImportService()
            success, message, layer = import_service.import_file(
                test_files['csv'], 
                layer_config
            )
            
            if success and layer:
                print(f"✅ Import CSV réussi: {message}")
                print(f"   Type géométrie: {layer.geometry_type}")
                print(f"   Statut: {layer.status}")
                return True
            else:
                print(f"❌ Import CSV échoué: {message}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur import CSV: {str(e)}")
            return False
        finally:
            import_service.cleanup()

def test_kml_import():
    """Test d'import KML"""
    print("\n🗺️ Test d'import KML...")
    
    app = create_test_app()
    test_files, temp_dir = create_test_files()
    
    with app.app_context():
        try:
            db.create_all()
            
            layer_config = {
                'name': 'Infrastructure Gabon',
                'description': 'Routes et zones administratives',
                'layer_type': 'infrastructure',
                'status': 'actif'
            }
            
            import_service = GeospatialImportService()
            success, message, layer = import_service.import_file(
                test_files['kml'], 
                layer_config
            )
            
            if success and layer:
                print(f"✅ Import KML réussi: {message}")
                print(f"   Type géométrie: {layer.geometry_type}")
                return True
            else:
                print(f"❌ Import KML échoué: {message}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur import KML: {str(e)}")
            return False
        finally:
            import_service.cleanup()

def test_txt_import():
    """Test d'import TXT"""
    print("\n📝 Test d'import TXT...")
    
    app = create_test_app()
    test_files, temp_dir = create_test_files()
    
    with app.app_context():
        try:
            db.create_all()
            
            layer_config = {
                'name': 'Aéroports Gabon',
                'description': 'Aéroports principaux du Gabon',
                'layer_type': 'infrastructure',
                'status': 'actif'
            }
            
            import_service = GeospatialImportService()
            success, message, layer = import_service.import_file(
                test_files['txt'], 
                layer_config
            )
            
            if success and layer:
                print(f"✅ Import TXT réussi: {message}")
                return True
            else:
                print(f"❌ Import TXT échoué: {message}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur import TXT: {str(e)}")
            return False
        finally:
            import_service.cleanup()

def test_upload_history():
    """Test de l'historique des uploads"""
    print("\n📚 Test de l'historique des uploads...")
    
    app = create_test_app()
    
    with app.app_context():
        try:
            db.create_all()
            
            # Vérification des enregistrements d'historique
            history_count = LayerUploadHistory.query.count()
            print(f"✅ Enregistrements d'historique: {history_count}")
            
            if history_count > 0:
                latest_upload = LayerUploadHistory.query.order_by(
                    LayerUploadHistory.uploaded_at.desc()
                ).first()
                
                print(f"   Dernier upload: {latest_upload.original_filename}")
                print(f"   Statut: {latest_upload.upload_status}")
                print(f"   Format: {latest_upload.file_format}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur historique: {str(e)}")
            return False

def cleanup_test_files(test_files, temp_dir):
    """Nettoyage des fichiers de test"""
    try:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("✅ Fichiers de test nettoyés")
    except Exception as e:
        print(f"⚠️ Erreur nettoyage: {str(e)}")

def main():
    """Fonction principale de test"""
    print("🚀 Tests du Service d'Import Géospatial ODG")
    print("=" * 50)
    
    success_count = 0
    total_tests = 0
    
    # Liste des tests
    tests = [
        ("Validation des fichiers", test_file_validation),
        ("Import GeoJSON", test_geojson_import),
        ("Import CSV", test_csv_import),
        ("Import KML", test_kml_import),
        ("Import TXT", test_txt_import),
        ("Historique des uploads", test_upload_history)
    ]
    
    # Création des fichiers de test
    test_files, temp_dir = create_test_files()
    print(f"📁 Fichiers de test créés dans: {temp_dir}")
    
    # Exécution des tests
    for test_name, test_func in tests:
        total_tests += 1
        print(f"\n📋 {test_name}...")
        
        try:
            if test_func():
                print(f"✅ {test_name}: SUCCÈS")
                success_count += 1
            else:
                print(f"❌ {test_name}: ÉCHEC")
        except Exception as e:
            print(f"❌ {test_name}: ERREUR - {str(e)}")
    
    # Nettoyage
    cleanup_test_files(test_files, temp_dir)
    
    # Résumé
    print("\n" + "=" * 50)
    print(f"📊 RÉSULTATS: {success_count}/{total_tests} tests réussis")
    
    if success_count == total_tests:
        print("🎉 TOUS LES TESTS SONT PASSÉS!")
        print("✅ Le service d'import géospatial est opérationnel")
    else:
        print(f"⚠️ {total_tests - success_count} test(s) ont échoué")
        print("🔧 Vérifiez les dépendances et la configuration")
    
    print("\n📋 Prochaines étapes:")
    print("1. Tester avec de vrais fichiers SIG")
    print("2. Implémenter l'interface frontend")
    print("3. Ajouter les fonctions d'export")
    print("4. Optimiser les performances pour gros fichiers")

if __name__ == "__main__":
    main()
