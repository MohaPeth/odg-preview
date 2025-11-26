# Script de correction des imports et des classes pour ODG Platform
import os
import sys
from importlib import import_module, reload
import inspect

def ensure_dir(directory):
    """S'assurer qu'un répertoire existe"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def fix_postgis_setup():
    """Corriger la configuration PostGIS"""
    print("🔧 Correction de la configuration PostGIS...")
    
    # 1. Vérifier les dépendances Python
    try:
        import flask_migrate
        import geoalchemy2
        import psycopg2
        print("✅ Toutes les dépendances sont installées")
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("💡 Exécutez: pip install psycopg2-binary geoalchemy2 flask-migrate")
        return False
    
    # 2. Ajouter __init__.py manquants
    print("\n📁 Vérification des fichiers __init__.py...")
    dirs_to_check = [
        'src',
        'src/models',
        'src/routes',
        'src/static',
        'database'
    ]
    
    for directory in dirs_to_check:
        if not os.path.exists(directory):
            ensure_dir(directory)
            print(f"  📂 Créé: {directory}")
        
        init_file = os.path.join(directory, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# Fichier généré par le script de correction\n')
            print(f"  📄 Créé: {init_file}")
    
    # 3. Corriger la classe Config si nécessaire
    print("\n🔄 Vérification du fichier config.py...")
    config_path = os.path.join('src', 'config.py')
    if not os.path.exists(config_path):
        print("❌ Fichier config.py manquant!")
        return False
    
    # 4. Vérifier si le dossier database existe
    db_path = os.path.join('database')
    if not os.path.exists(db_path):
        ensure_dir(db_path)
        print(f"  📂 Créé dossier database manquant")
    
    print("✅ Configuration corrigée")
    return True

def run():
    """Exécuter les corrections"""
    print("\n🚀 SCRIPT DE CORRECTION ODG PLATFORM")
    print("===================================")
    
    if fix_postgis_setup():
        print("\n✨ Corrections terminées avec succès!")
        print("\n📋 PROCHAINES ÉTAPES:")
        print("1. Exécuter la configuration PostgreSQL:")
        print("   powershell -ExecutionPolicy Bypass -File setup_postgresql.ps1")
        print("\n2. Migrer les données:")
        print("   python src/migrate_to_postgis.py")
        print("\n3. Démarrer l'API PostGIS:")
        print("   python src/main_postgis.py")
    else:
        print("\n❌ Échec des corrections")

if __name__ == "__main__":
    run()
