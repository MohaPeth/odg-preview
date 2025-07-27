import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.mining_data import db
from src.routes.user import user_bp
from src.routes.webgis import webgis_bp
from src.routes.blockchain import blockchain_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Configuration CORS pour permettre les requêtes cross-origin
CORS(app)

# Enregistrement des blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(webgis_bp, url_prefix='/api/webgis')
app.register_blueprint(blockchain_bp, url_prefix='/api/blockchain')

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialisation de la base de données avec des données de test
def init_database():
    with app.app_context():
        db.create_all()
        
        # Vérifier si des données existent déjà
        from src.models.mining_data import MiningDeposit, ExploitationArea, Infrastructure, BlockchainTransaction
        from datetime import datetime
        import json
        
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
            
            db.session.commit()
            print("Base de données initialisée avec des données de test")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
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

