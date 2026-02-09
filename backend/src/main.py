import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Charger le .env AVANT tout le reste
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)
print(f"📄 Chargement des variables depuis {env_path}")
print(f"✅ DATABASE_URL chargée: {os.getenv('DATABASE_URL', 'NON DÉFINIE')[:50]}...")

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from src.models.mining_data import db
from src.auth import get_current_user_from_token
from src.limiter import limiter
from src.models.geospatial_layers import GeospatialLayer, LayerUploadHistory
from src.routes.health import health_bp
from src.routes.user import user_bp
from src.routes.webgis import webgis_bp
from src.routes.blockchain import blockchain_bp
from src.routes.geospatial_import import geospatial_import_bp
from src.routes.operators import operators_bp
from src.routes.blockchain_integration import blockchain_integration_bp
from src.routes.dashboard import dashboard_bp
from src.routes.mining_import import mining_import_bp

# Import de la configuration
try:
    from config_production import get_config, setup_logging, validate_production_config
    Config = get_config()
except ImportError:
    # Fallback vers configuration simple si config_production n'existe pas
    class Config:
        SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}")
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
        CORS_ORIGINS = ['*']

# Validation des dépendances blockchain
def check_blockchain_dependencies():
    """Vérifie si les dépendances blockchain sont disponibles"""
    try:
        import web3
        from eth_account import Account
        return True
    except ImportError:
        return False

BLOCKCHAIN_AVAILABLE = check_blockchain_dependencies()

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Configuration
    app.config.from_object(Config)
    app.config['BLOCKCHAIN_AVAILABLE'] = BLOCKCHAIN_AVAILABLE
    
    # Validation pour la production
    if os.getenv('FLASK_ENV') == 'production':
        try:
            validate_production_config()
        except ValueError as e:
            print(f"❌ Erreur de configuration production : {e}")
            sys.exit(1)
    
    # Configuration CORS
    cors_origins = getattr(Config, 'CORS_ORIGINS', ['*'])
    CORS(app, origins=cors_origins)
    
    # Enregistrement des blueprints
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(webgis_bp, url_prefix='/api/webgis')
    
    # Toujours enregistrer les blueprints blockchain (ils géreront le mode dégradé en interne)
    app.register_blueprint(blockchain_bp, url_prefix='/api/blockchain')
    app.register_blueprint(blockchain_integration_bp, url_prefix='/api/blockchain-integration')
    
    if BLOCKCHAIN_AVAILABLE:
        print("✅ Modules blockchain activés")
    else:
        print("⚠️  Modules blockchain en mode dégradé (dépendances web3 manquantes)")
    
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(geospatial_import_bp, url_prefix='/api/geospatial')
    app.register_blueprint(operators_bp, url_prefix='/api/operators')
    app.register_blueprint(mining_import_bp, url_prefix='/api/mining')
    
    # Initialisation de la base de données
    db.init_app(app)

    # Rate limiting (appel après db.init_app pour avoir le contexte)
    limiter.init_app(app)

    # Protection JWT : toutes les routes /api/* sauf login et health exigent un token valide
    @app.before_request
    def require_auth_for_api():
        path = request.path
        if not path.startswith('/api/'):
            return None
        if request.method == 'POST' and path.rstrip('/') == '/api/auth/login':
            return None
        if request.method == 'GET' and path.rstrip('/') == '/api/health':
            return None
        user = get_current_user_from_token()
        if user is None:
            return jsonify({'error': 'Authentification requise ou token invalide/expiré'}), 401
        from flask import g
        g.current_user = user
        return None

    # Configuration des logs pour la production
    if hasattr(Config, 'LOG_LEVEL'):
        setup_logging(app)
    
    return app

# Créer l'application
app = create_app()

# Initialisation de la base de données avec des données de test
def init_database():
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"❌ Erreur lors de la création des tables: {e}")
            raise
        
        # Vérifier si des données existent déjà
        from src.models.mining_data import MiningDeposit, ExploitationArea, Infrastructure, BlockchainTransaction, Operator
        from src.models.user import User
        from datetime import datetime
        import json
        
        # Créer des utilisateurs de test si aucun n'existe
        if User.query.count() == 0:
            # Créer un opérateur de test
            operator = Operator(
                name="Opérateur Test",
                slug="operateur-test",
                country="Gabon",
                status="Actif",
                description="Opérateur de test pour le dashboard ODG",
                commodities_json='[{"code": "AU", "label": "Or"}]',
                permits_count=1
            )
            db.session.add(operator)
            db.session.flush()  # Pour obtenir l'ID de l'opérateur
            
            # Créer les utilisateurs de test
            test_users = [
                User(username='admin', email='admin@odg.ga', role='admin', status='active'),
                User(username='operator', email='operator@odg.ga', role='operator', status='active', operator_id=operator.id),
                User(username='partner', email='partner@odg.ga', role='partner', status='active')
            ]
            for user in test_users:
                db.session.add(user)
            
            print("✅ Utilisateurs de test créés (admin@odg.ga, operator@odg.ga, partner@odg.ga)")
        
        if MiningDeposit.query.count() == 0:
            # Données de test pour les gisements
            deposits = [
                MiningDeposit(
                    name="Gisement Minkebe",
                    type="Or",
                    latitude=-0.5,
                    longitude=12.0,
                    company="ODG",
                    estimated_quantity="755 Km²",
                    status="Actif",
                    description="Gisement aurifère dans la province de Woleu-Ntem"
                ),
                MiningDeposit(
                    name="Gisement Myaning",
                    type="Or",
                    latitude=-1.2,
                    longitude=10.8,
                    company="ODG",
                    estimated_quantity="150 Km²",
                    status="En développement",
                    description="Gisement aurifère à 70 Km de Lambaréné"
                ),
                MiningDeposit(
                    name="Gisement Eteke",
                    type="Or",
                    latitude=-2.1,
                    longitude=11.5,
                    company="ODG",
                    estimated_quantity="765 Km²",
                    status="Exploration",
                    description="Gisement dans le sud-est du Gabon, province de la Ngounié"
                )
            ]
            
            for deposit in deposits:
                db.session.add(deposit)
            
            # Données de test pour les zones d'exploitation
            areas = [
                ExploitationArea(
                    name="Zone AFM",
                    company="AFM",
                    status="En cours",
                    coordinates=json.dumps([[-0.4, 11.9], [-0.6, 11.9], [-0.6, 12.1], [-0.4, 12.1]]),
                    area="50 Km²",
                    extracted_volume="1,200 tonnes"
                ),
                ExploitationArea(
                    name="Zone BDM",
                    company="BDM",
                    status="Terminé",
                    coordinates=json.dumps([[-1.1, 10.7], [-1.3, 10.7], [-1.3, 10.9], [-1.1, 10.9]]),
                    area="30 Km²",
                    extracted_volume="800 tonnes"
                )
            ]
            
            for area in areas:
                db.session.add(area)
            
            # Données de test pour l'infrastructure
            infrastructure = [
                Infrastructure(
                    name="Route Libreville-Lambaréné",
                    type="Route",
                    coordinates=json.dumps([[0.4, 9.4], [-0.7, 10.2], [-1.2, 10.8]]),
                    length="250 km",
                    capacity="",
                    status="Bon état"
                )
            ]
            
            for infra in infrastructure:
                db.session.add(infra)
            
            # Données de test pour les transactions blockchain
            transactions = [
                BlockchainTransaction(
                    transaction_hash="0x1234567890abcdef1234567890abcdef12345678",
                    block_number=1234567,
                    from_address="0xabcdef1234567890abcdef1234567890abcdef12",
                    to_address="0x1234567890abcdef1234567890abcdef12345678",
                    material_type="Or",
                    quantity=10.5,
                    unit="kg",
                    timestamp=datetime.utcnow(),
                    status="confirmed",
                    metadata_json=json.dumps({
                        "origin": "Mine Minkebe",
                        "destination": "Raffinerie Libreville",
                        "operator": "ODG",
                        "quality": {"purity": "99.5%"},
                        "environmental_impact": {"co2": "2.1 tonnes"}
                    })
                ),
                BlockchainTransaction(
                    transaction_hash="0xfedcba0987654321fedcba0987654321fedcba09",
                    block_number=1234568,
                    from_address="0x1234567890abcdef1234567890abcdef12345678",
                    to_address="0x9876543210fedcba9876543210fedcba98765432",
                    material_type="Or",
                    quantity=5.2,
                    unit="kg",
                    timestamp=datetime.utcnow(),
                    status="pending",
                    metadata_json=json.dumps({
                        "origin": "Mine Myaning",
                        "destination": "Export Terminal",
                        "operator": "ODG",
                        "quality": {"purity": "98.8%"}
                    })
                )
            ]
            
            for tx in transactions:
                db.session.add(tx)
            
            # Données de test pour les couches géospatiales
            if GeospatialLayer.query.count() == 0:
                try:
                    from geoalchemy2.functions import ST_GeomFromText
                    
                    geospatial_layers = [
                        GeospatialLayer(
                            name="Points d'Intérêt Libreville",
                            description="Points d'intérêt touristiques et administratifs de Libreville",
                            layer_type="custom",
                            geometry_type="POINT",
                            source_format="CSV",
                            status="actif",
                            geom=ST_GeomFromText('POINT(9.4536 0.3901)', 4326),
                            layer_metadata={
                                "properties": {"ville": "Libreville", "type": "capitale"},
                                "source_info": {"date_creation": "2025-11-17", "precision": "GPS"}
                            }
                        ),
                        GeospatialLayer(
                            name="Route Nationale N1",
                            description="Route principale Libreville - Lambaréné - Franceville",
                            layer_type="infrastructure",
                            geometry_type="LINESTRING",
                            source_format="KML",
                            status="actif",
                            geom=ST_GeomFromText('LINESTRING(9.4536 0.3901, 9.2 0.1, 8.9 -0.2, 8.7 -0.5)', 4326),
                            layer_metadata={
                                "properties": {"route": "N1", "longueur_km": "450"},
                                "source_info": {"ministere": "Travaux Publics", "annee": "2024"}
                            }
                        ),
                        GeospatialLayer(
                            name="Parc National de la Lopé",
                            description="Zone protégée du Parc National de la Lopé",
                            layer_type="zone",
                            geometry_type="POLYGON",
                            source_format="SHP",
                            status="actif",
                            geom=ST_GeomFromText('POLYGON((11.0 -0.5, 11.5 -0.5, 11.5 0.0, 11.0 0.0, 11.0 -0.5))', 4326),
                            layer_metadata={
                                "properties": {"superficie_km2": "4970", "statut": "Parc National"},
                                "source_info": {"organisme": "ANPN", "classification": "UNESCO"}
                            }
                        )
                    ]
                    
                    for layer in geospatial_layers:
                        layer.set_default_style_by_type()
                        db.session.add(layer)
                    
                    print("Couches géospatiales de test ajoutées")
                    
                except Exception as e:
                    print(f"Attention: Impossible d'ajouter les couches géospatiales de test: {e}")
                    print("Cela est normal si PostGIS n'est pas configuré. Les couches géospatiales nécessitent PostgreSQL/PostGIS.")
            
            db.session.commit()
            print("Base de données initialisée avec des données de test")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # Ne pas intercepter les routes API
    if path.startswith('api/'):
        return "API route not found", 404
    
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    init_database()
    app.run(host='0.0.0.0', port=5000, debug=True)

