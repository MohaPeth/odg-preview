# Script de test des composants PostgreSQL/PostGIS pour ODG Platform
import os
import sys
import importlib
import subprocess
import socket

def check_required_packages():
    """Vérifier les packages Python requis"""
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_migrate',
        'flask_cors',
        'geoalchemy2',
        'psycopg2'
    ]
    
    missing_packages = []
    
    print("📋 Vérification des packages Python...")
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"  ✓ {package}: installé")
        except ImportError:
            missing_packages.append(package)
            print(f"  ✗ {package}: manquant")
    
    return missing_packages

def check_postgresql():
    """Vérifier si PostgreSQL est accessible"""
    print("\n🐘 Vérification de PostgreSQL...")
    
    # Test de port
    postgres_running = False
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 5432))
        if result == 0:
            postgres_running = True
            print("  ✓ PostgreSQL est accessible sur le port 5432")
        else:
            print("  ✗ PostgreSQL n'est pas accessible sur le port 5432")
        sock.close()
    except Exception as e:
        print(f"  ✗ Erreur lors de la vérification du port PostgreSQL: {e}")
    
    # Test de commande psql
    psql_available = False
    try:
        result = subprocess.run(
            ["psql", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            psql_available = True
            version = result.stdout.strip()
            print(f"  ✓ Commande psql disponible: {version}")
        else:
            print("  ✗ Commande psql indisponible")
    except Exception:
        print("  ✗ Commande psql introuvable")
    
    return postgres_running, psql_available

def check_project_structure():
    """Vérifier la structure du projet"""
    print("\n📁 Vérification de la structure du projet...")
    
    required_files = [
        'src/__init__.py',
        'src/config.py',
        'src/main_postgis.py',
        'src/migrate_to_postgis.py',
        'src/models/__init__.py',
        'src/models/geospatial.py',
        'src/models/mining_data.py',
        'src/models/substances.py',
        'src/routes/__init__.py',
        'src/routes/webgis_postgis.py',
        'setup_postgresql.ps1'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}: trouvé")
        else:
            missing_files.append(file_path)
            print(f"  ✗ {file_path}: manquant")
    
    return missing_files

def run_diagnostics():
    """Exécuter tous les diagnostics"""
    print("🔍 DIAGNOSTICS ODG POSTGIS")
    print("==========================\n")
    
    # Vérification des packages
    missing_packages = check_required_packages()
    
    # Vérification PostgreSQL
    postgres_running, psql_available = check_postgresql()
    
    # Vérification structure projet
    missing_files = check_project_structure()
    
    # Résumé
    print("\n📊 RÉSUMÉ DES DIAGNOSTICS")
    print("==========================")
    
    all_ok = True
    
    if missing_packages:
        all_ok = False
        print("❌ Packages Python manquants:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\nInstallation recommandée:")
        print(f"pip install {' '.join(missing_packages)}")
    else:
        print("✅ Tous les packages Python sont installés")
    
    if postgres_running:
        print("✅ PostgreSQL est en fonctionnement")
    else:
        all_ok = False
        print("❌ PostgreSQL n'est pas en fonctionnement")
        if not psql_available:
            print("   - La commande psql n'est pas disponible")
        print("   - Vérifiez que le service PostgreSQL est démarré")
        print("   - net start postgresql-x64-15")
    
    if missing_files:
        all_ok = False
        print("❌ Fichiers de projet manquants:")
        for file in missing_files:
            print(f"   - {file}")
    else:
        print("✅ La structure du projet est complète")
    
    print("\n" + "=" * 50)
    if all_ok:
        print("✅ TOUT EST PRÊT! Le système est correctement configuré.")
        print("   Vous pouvez exécuter: python src/main_postgis.py")
    else:
        print("⚠️ DES PROBLÈMES ONT ÉTÉ DÉTECTÉS!")
        print("   Veuillez résoudre les problèmes avant de continuer.")
        print("   Utilisez: python fix_postgis.py")

if __name__ == "__main__":
    run_diagnostics()
