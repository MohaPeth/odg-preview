# -*- coding: utf-8 -*-
# Application Flask principale avec support PostGIS pour ODG Platform
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config, get_config
from models.mining_data import db
from models.substances import Substance
from models.geospatial import MiningDepositGIS, Community
from routes.webgis_postgis import register_webgis_routes
import os
import sys
import logging

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(Config)
    
    # Configuration UTF-8
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # CORS pour le frontend React
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialisation des extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Configuration du logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # Routes de base
    @app.route('/')
    def index():
        """Page d'accueil de l'API"""
        return jsonify({
            'message': 'ODG WebGIS API avec PostGIS',
            'version': '1.0.0',
            'status': 'active',
            'features': [
                'Gestion géospatiale avec PostGIS',
                'API GeoJSON pour cartographie',
                'Filtres multi-substances',
                'Analyse spatiale avancée',
                'Support communautés locales'
            ],
            'endpoints': {
                'layers': '/api/webgis/layers',
                'deposits': '/api/webgis/deposits',
                'communities': '/api/webgis/communities',
                'search': '/api/webgis/search',
                'statistics': '/api/webgis/statistics'
            }
        })
    
    @app.route('/api/health')
    def health_check():
        """Vérification santé de l'API et de la base de données"""
        try:
            # Test connexion base de données
            db.session.execute(db.text('SELECT 1'))
            
            # Test PostGIS
            postgis_version = db.session.execute(
                db.text('SELECT PostGIS_Version()')
            ).fetchone()
            
            # Statistiques rapides
            deposits_count = MiningDepositGIS.query.count()
            substances_count = Substance.query.count()
            communities_count = Community.query.count()
            
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'postgis_version': postgis_version[0] if postgis_version else 'Unknown',
                'data': {
                    'deposits': deposits_count,
                    'substances': substances_count,
                    'communities': communities_count
                },
                'timestamp': db.func.now()
            })
            
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'database': 'disconnected'
            }), 500
    
    @app.route('/api/version')
    def version():
        """Informations de version et configuration"""
        try:
            import flask
            flask_version = getattr(flask, '__version__', 'Unknown')
        except:
            flask_version = 'Unknown'
            
        return jsonify({
            'api_version': '1.0.0',
            'flask_version': flask_version,
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'database_uri': app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else 'localhost',
            'debug_mode': app.debug,
            'environment': os.environ.get('FLASK_ENV', 'production')
        })
    
    # Enregistrer les routes WebGIS
    register_webgis_routes(app)
    
    # Gestionnaires d'erreurs
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint non trouvé',
            'code': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur',
            'code': 500
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'Requête invalide',
            'code': 400
        }), 400
    
    # Commandes CLI pour la migration
    @app.cli.command('init-db')
    def init_db_command():
        """Initialiser la base de données PostGIS"""
        print("🔄 Initialisation de la base de données PostGIS...")
        
        # Créer toutes les tables
        db.create_all()
        print("✅ Tables créées")
        
        # Créer les substances par défaut
        from models.substances import create_default_substances
        result = create_default_substances()
        if result.get('success', False):
            print("✅ Substances par défaut créées")
        else:
            print(f"⚠️ Avertissement: {result.get('message')}")
        
        print("🎉 Base de données initialisée avec succès!")
    
    @app.cli.command('migrate-data')
    def migrate_data_command():
        """Migrer les données SQLite vers PostGIS"""
        from migrate_to_postgis import migrate_sqlite_to_postgis, verify_migration
        
        print("🚀 Démarrage de la migration...")
        if migrate_sqlite_to_postgis():
            verify_migration()
            print("🎉 Migration terminée avec succès!")
        else:
            print("💥 Échec de la migration")
    
    @app.cli.command('create-sample-data')
    def create_sample_data_command():
        """Créer des données d'exemple"""
        from migrate_to_postgis import create_sample_data
        
        print("🔄 Création des données d'exemple...")
        create_sample_data()
        print("✅ Données d'exemple créées!")
    
    return app

# Point d'entrée pour le développement
app = create_app()

if __name__ == '__main__':
    print("🌍 Démarrage ODG WebGIS API avec PostGIS")
    print("📍 Frontend attendu sur: http://localhost:5173")
    print("🗄️ API disponible sur: http://localhost:5000")
    print("📊 Health check: http://localhost:5000/api/health")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
