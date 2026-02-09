#!/usr/bin/env python3
"""
Script d'initialisation de la base de données de production ODG
Applique les migrations PostGIS et initialise les tables géospatiales
"""

import os
import sys
import logging
from datetime import datetime

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from sqlalchemy import text
from src.models.mining_data import db
from src.models.geospatial_layers import GeospatialLayer, LayerUploadHistory


def _execute_sql(sql, params=None):
    """Exécute du SQL brut (compatible SQLAlchemy 2.0)."""
    with db.engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        conn.commit()
        return result

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Créer l'application Flask pour l'initialisation"""
    app = Flask(__name__)
    
    # Configuration de la base de données
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ Variable d'environnement DATABASE_URL non définie")
        logger.info("Exemple: export DATABASE_URL='postgresql://user:password@localhost:5432/odg_production'")
        sys.exit(1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'temp-init-key')
    
    # Initialiser la base de données
    db.init_app(app)
    
    return app

def check_postgis_extensions(app):
    """Vérifier et installer les extensions PostGIS"""
    logger.info("🔍 Vérification des extensions PostGIS...")
    
    with app.app_context():
        try:
            # Vérifier si PostGIS est disponible
            result = _execute_sql("SELECT PostGIS_Version();")
            version = result.fetchone()[0]
            logger.info(f"✅ PostGIS détecté : {version}")
            return True
        except Exception as e:
            logger.error(f"❌ PostGIS non disponible : {e}")
            logger.info("💡 Installez PostGIS avec : CREATE EXTENSION postgis;")
            return False

def apply_migrations(app):
    """Appliquer les migrations SQL"""
    logger.info("📋 Application des migrations...")
    
    migration_file = os.path.join(
        os.path.dirname(__file__), 
        'src', 'migrations', 'create_geospatial_tables.sql'
    )
    
    if not os.path.exists(migration_file):
        logger.error(f"❌ Fichier de migration non trouvé : {migration_file}")
        return False
    
    with app.app_context():
        try:
            with open(migration_file, 'r', encoding='utf-8') as f:
                migration_sql = f.read()
            
            # Diviser le SQL en commandes individuelles
            commands = [cmd.strip() for cmd in migration_sql.split(';') if cmd.strip()]
            
            for i, command in enumerate(commands, 1):
                if command:
                    logger.info(f"📝 Exécution commande {i}/{len(commands)}")
                    _execute_sql(command)
            
            logger.info("✅ Migrations appliquées avec succès")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'application des migrations : {e}")
            return False

def create_tables(app):
    """Créer les tables SQLAlchemy"""
    logger.info("🏗️ Création des tables SQLAlchemy...")
    
    with app.app_context():
        try:
            db.create_all()
            logger.info("✅ Tables SQLAlchemy créées")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création des tables : {e}")
            return False

def verify_installation(app):
    """Vérifier l'installation"""
    logger.info("🔍 Vérification de l'installation...")
    
    with app.app_context():
        try:
            # Vérifier les tables principales
            tables_to_check = [
                'geospatial_layers',
                'layer_upload_history'
            ]
            
            for table in tables_to_check:
                result = _execute_sql("""
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_name = :tname
                """, {"tname": table})
                count = result.fetchone()[0]
                
                if count > 0:
                    logger.info(f"✅ Table '{table}' créée")
                else:
                    logger.error(f"❌ Table '{table}' manquante")
                    return False
            
            # Vérifier les fonctions PostGIS
            result = _execute_sql("SELECT ST_AsText(ST_Point(0, 0));")
            point = result.fetchone()[0]
            logger.info(f"✅ Fonctions PostGIS opérationnelles : {point}")
            
            # Compter les enregistrements existants
            layer_count = db.session.query(GeospatialLayer).count()
            history_count = db.session.query(LayerUploadHistory).count()
            
            logger.info(f"📊 Couches géospatiales : {layer_count}")
            logger.info(f"📊 Historique uploads : {history_count}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la vérification : {e}")
            return False

def create_sample_data(app):
    """Créer des données d'exemple (optionnel)"""
    logger.info("📝 Création de données d'exemple...")
    
    with app.app_context():
        try:
            # Vérifier si des données existent déjà
            existing_count = db.session.query(GeospatialLayer).count()
            if existing_count > 0:
                logger.info(f"ℹ️ {existing_count} couches existantes, pas de données d'exemple ajoutées")
                return True
            
            # Créer une couche d'exemple
            from geoalchemy2.functions import ST_GeomFromText

            sample_layer = GeospatialLayer(
                name="Zone Test ODG",
                description="Couche de test créée lors de l'initialisation",
                layer_type="custom",
                geometry_type="POINT",
                source_format="SYSTEM",
                status="actif",
                is_visible=True,
                layer_metadata={
                    "created_by": "init_script",
                    "purpose": "test_installation"
                }
            )
            # Géométrie simple (point à Libreville)
            sample_layer.geom = ST_GeomFromText('POINT(9.4536 0.3901)', 4326)
            
            db.session.add(sample_layer)
            db.session.commit()
            
            logger.info("✅ Données d'exemple créées")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création des données d'exemple : {e}")
            return False

def main():
    """Fonction principale d'initialisation"""
    logger.info("🚀 Initialisation de la base de données ODG Géospatial")
    logger.info("=" * 60)
    
    # Créer l'application
    app = create_app()
    
    # Étapes d'initialisation
    steps = [
        ("Vérification PostGIS", lambda: check_postgis_extensions(app)),
        ("Application migrations", lambda: apply_migrations(app)),
        ("Création tables SQLAlchemy", lambda: create_tables(app)),
        ("Vérification installation", lambda: verify_installation(app)),
        ("Données d'exemple", lambda: create_sample_data(app))
    ]
    
    success_count = 0
    
    for step_name, step_func in steps:
        logger.info(f"\n📋 {step_name}...")
        try:
            if step_func():
                success_count += 1
                logger.info(f"✅ {step_name} : SUCCÈS")
            else:
                logger.error(f"❌ {step_name} : ÉCHEC")
        except Exception as e:
            logger.error(f"❌ {step_name} : ERREUR - {e}")
    
    # Résumé
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 RÉSUMÉ : {success_count}/{len(steps)} étapes réussies")
    
    if success_count == len(steps):
        logger.info("🎉 INITIALISATION TERMINÉE AVEC SUCCÈS !")
        logger.info("✅ La base de données est prête pour la production")
        return 0
    else:
        logger.error("❌ INITIALISATION INCOMPLÈTE")
        logger.error("🔧 Vérifiez les erreurs ci-dessus et relancez le script")
        return 1

if __name__ == "__main__":
    # Vérifier les prérequis
    required_env_vars = ['DATABASE_URL']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Variables d'environnement manquantes : {missing_vars}")
        logger.info("\n📋 Configuration requise :")
        logger.info("export DATABASE_URL='postgresql://user:password@localhost:5432/odg_production'")
        logger.info("export SECRET_KEY='your-secret-key-here'")
        sys.exit(1)
    
    # Lancer l'initialisation
    exit_code = main()
    sys.exit(exit_code)
