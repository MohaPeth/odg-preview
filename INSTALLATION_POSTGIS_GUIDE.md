# 🛠️ INSTALLATION POSTGIS - GUIDE COMPLET WINDOWS

## 📋 **Guide d'Installation PostGIS pour Windows**

### **Étape 1 : Installation PostgreSQL**

#### **1.1 Téléchargement PostgreSQL**
```bash
# Télécharger PostgreSQL 15+ depuis :
# https://www.postgresql.org/download/windows/

# Ou via winget (Windows 11)
winget install PostgreSQL.PostgreSQL
```

#### **1.2 Installation Interactive**
1. **Exécuter l'installeur** téléchargé
2. **Port par défaut** : 5432 (conserver)
3. **Superuser password** : Choisir un mot de passe fort
4. **Locale** : French_France ou English_United States
5. **Installer Stack Builder** : Cocher OUI

#### **1.3 Configuration Variables d'Environnement**
```powershell
# Ajouter PostgreSQL au PATH
$env:Path += ";C:\Program Files\PostgreSQL\15\bin"

# Vérifier l'installation
psql --version
```

### **Étape 2 : Installation PostGIS**

#### **2.1 Via Stack Builder (Recommandé)**
1. **Lancer Stack Builder** depuis le menu démarrage
2. **Sélectionner** votre instance PostgreSQL
3. **Spatial Extensions** → Cocher **PostGIS**
4. **Suivre l'assistant** d'installation

#### **2.2 Via EDB Repository (Alternative)**
```powershell
# Télécharger PostGIS bundle :
# https://download.osgeo.org/postgis/windows/

# Installation silencieuse
Start-Process -FilePath "postgis-bundle-pg15-3.3.2x64.exe" -ArgumentList "/S" -Wait
```

### **Étape 3 : Création Base de Données ODG**

#### **3.1 Connexion PostgreSQL**
```powershell
# Connexion en tant que superuser
psql -U postgres -h localhost
```

#### **3.2 Création Base et Extension**
```sql
-- Création de la base de données ODG
CREATE DATABASE odg_database
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Connexion à la nouvelle base
\c odg_database

-- Activation PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS postgis_raster;

-- Vérification installation
SELECT PostGIS_version();
```

### **Étape 4 : Configuration Utilisateur ODG**

#### **4.1 Création Utilisateur Dédié**
```sql
-- Créer utilisateur pour l'application
CREATE USER odg_user WITH
    LOGIN
    NOSUPERUSER
    INHERIT
    CREATEDB
    CREATEROLE
    NOREPLICATION
    PASSWORD 'ODG_SecurePass2025!';

-- Octroyer permissions sur la base
GRANT ALL PRIVILEGES ON DATABASE odg_database TO odg_user;
GRANT ALL ON SCHEMA public TO odg_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO odg_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO odg_user;
```

#### **4.2 Test de Connexion**
```powershell
# Test connexion avec nouvel utilisateur
psql -U odg_user -d odg_database -h localhost
```

---

## 🐍 **CONFIGURATION PYTHON/FLASK**

### **Étape 5 : Installation Dépendances Python**

#### **5.1 Packages PostGIS pour Python**
```bash
# Dans votre environnement virtuel
cd c:\Users\Moha\Desktop\test\reactJs\ODG_Modules_Complete\odg-webgis-backend

# Activation de l'environnement virtuel
.\venv\Scripts\activate

# Installation des packages PostGIS
pip install psycopg2-binary==2.9.7
pip install geoalchemy2==0.14.1
pip install flask-migrate==4.0.5
pip install shapely==2.0.1
pip install geopandas==0.14.0
```

#### **5.2 Mise à Jour requirements.txt**
```txt
# Ajouter au fichier requirements.txt existant
psycopg2-binary==2.9.7
geoalchemy2==0.14.1
flask-migrate==4.0.5
shapely==2.0.1
geopandas==0.14.0
```

### **Étape 6 : Configuration Flask**

#### **6.1 Nouveau Fichier de Configuration**
```python
# Créer config.py dans odg-webgis-backend/src/
import os
from datetime import timedelta

class Config:
    # Base de données PostGIS
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://odg_user:ODG_SecurePass2025!@localhost:5432/odg_database'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }
    
    # Sécurité
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'asdf#FGSgvasgf$5$WGT'
    
    # CORS
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5173', 'http://localhost:5000']
    
    # Upload de fichiers SIG
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max pour fichiers SIG
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = {'kml', 'gpx', 'geojson', 'json', 'shp', 'csv'}

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log des requêtes SQL

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False

# Configuration par défaut
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

#### **6.2 Modification main.py**
```python
# Mise à jour de main.py
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from src.config import config
from src.models.mining_data import db
from src.routes.user import user_bp
from src.routes.webgis import webgis_bp
from src.routes.blockchain import blockchain_bp

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    app.config.from_object(config[config_name])
    
    # Initialisation des extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Enregistrement des blueprints
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(webgis_bp, url_prefix='/api/webgis')
    app.register_blueprint(blockchain_bp, url_prefix='/api/blockchain')
    
    return app

app = create_app()

# Route pour servir le frontend
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
    with app.app_context():
        # Créer les tables si elles n'existent pas
        db.create_all()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
```

---

## 🗃️ **NOUVEAUX MODÈLES POSTGIS**

### **Étape 7 : Création des Nouveaux Modèles**

#### **7.1 Modèle Substances**
```python
# src/models/substances.py
from src.models.mining_data import db
from datetime import datetime

class Substance(db.Model):
    __tablename__ = 'substances'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    color_code = db.Column(db.String(7), nullable=False)  # Code couleur hex
    market_price = db.Column(db.Float)  # Prix actuel par unité
    price_currency = db.Column(db.String(3), default='EUR')
    unit = db.Column(db.String(20), default='kg')
    density = db.Column(db.Float)  # Densité pour calculs de volume
    description = db.Column(db.Text)
    
    # Métadonnées système
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'symbol': self.symbol,
            'colorCode': self.color_code,
            'marketPrice': self.market_price,
            'priceCurrency': self.price_currency,
            'unit': self.unit,
            'density': self.density,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
```

#### **7.2 Gisements PostGIS**
```python
# src/models/geospatial.py
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_X, ST_Y, ST_AsGeoJSON
from src.models.mining_data import db
from src.models.substances import Substance
from datetime import datetime
import json

class MiningDepositGIS(db.Model):
    __tablename__ = 'mining_deposits_gis'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    
    # Géométrie PostGIS (Point avec projection WGS84)
    geom = db.Column(Geometry('POINT', srid=4326), nullable=False)
    
    # Relation avec substance
    substance_id = db.Column(db.Integer, db.ForeignKey('substances.id'), nullable=False)
    substance = db.relationship('Substance', backref='deposits')
    
    # Informations de base
    company = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Données géologiques
    estimated_quantity = db.Column(db.Float)  # Quantité numérique
    quantity_unit = db.Column(db.String(20), default='tonnes')
    quality_grade = db.Column(db.Float)  # Teneur ou qualité (%)
    confidence_level = db.Column(db.String(20), default='medium')  # low, medium, high
    
    # Profondeur
    depth_min = db.Column(db.Float)  # Profondeur minimum (mètres)
    depth_max = db.Column(db.Float)  # Profondeur maximum (mètres)
    
    # Informations temporelles
    discovery_date = db.Column(db.Date)
    last_survey = db.Column(db.Date)
    
    # Statut et permis
    status = db.Column(db.String(50), nullable=False, default='Exploration')  # Exploration, Actif, Fermé
    exploitation_permit = db.Column(db.String(50))
    permit_expiry = db.Column(db.Date)
    
    # Données administratives
    data_source = db.Column(db.String(100))  # Source des données
    created_by = db.Column(db.String(100))
    approved_by = db.Column(db.String(100))
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    
    # Métadonnées système
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_geom=True):
        result = {
            'id': self.id,
            'name': self.name,
            'substance': self.substance.to_dict() if self.substance else None,
            'company': self.company,
            'description': self.description,
            'estimatedQuantity': self.estimated_quantity,
            'quantityUnit': self.quantity_unit,
            'qualityGrade': self.quality_grade,
            'confidenceLevel': self.confidence_level,
            'depthMin': self.depth_min,
            'depthMax': self.depth_max,
            'discoveryDate': self.discovery_date.isoformat() if self.discovery_date else None,
            'lastSurvey': self.last_survey.isoformat() if self.last_survey else None,
            'status': self.status,
            'exploitationPermit': self.exploitation_permit,
            'permitExpiry': self.permit_expiry.isoformat() if self.permit_expiry else None,
            'dataSource': self.data_source,
            'approvalStatus': self.approval_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_geom and self.geom:
            # Extraction des coordonnées à partir de la géométrie PostGIS
            geom_json = db.session.scalar(ST_AsGeoJSON(self.geom))
            if geom_json:
                geom_data = json.loads(geom_json)
                result['coordinates'] = geom_data['coordinates']  # [longitude, latitude]
                result['latitude'] = geom_data['coordinates'][1]
                result['longitude'] = geom_data['coordinates'][0]
        
        return result
```

### **Étape 8 : Migration des Données**

#### **8.1 Script de Migration**
```python
# src/migrations/migrate_to_postgis.py
from src.models.mining_data import MiningDeposit as OldMiningDeposit
from src.models.geospatial import MiningDepositGIS
from src.models.substances import Substance
from src.models.mining_data import db
from geoalchemy2.functions import ST_GeomFromText

def migrate_substances():
    """Créer les substances de base"""
    substances_data = [
        {
            'name': 'Or',
            'symbol': 'Au',
            'color_code': '#FFD700',
            'market_price': 65000.0,
            'unit': 'kg',
            'density': 19.3,
            'description': 'Métal précieux, conducteur électrique'
        },
        {
            'name': 'Diamant',
            'symbol': 'C',
            'color_code': '#87CEEB',
            'market_price': 55000.0,
            'unit': 'carats',
            'density': 3.5,
            'description': 'Pierre précieuse, matériau le plus dur'
        },
        {
            'name': 'Fer',
            'symbol': 'Fe',
            'color_code': '#8B0000',
            'market_price': 120.0,
            'unit': 'tonnes',
            'density': 7.8,
            'description': 'Métal ferreux, base de la sidérurgie'
        },
        {
            'name': 'Sable',
            'symbol': 'Si',
            'color_code': '#F5F5DC',
            'market_price': 25.0,
            'unit': 'tonnes',
            'density': 1.6,
            'description': 'Silice, construction et industrie'
        }
    ]
    
    for data in substances_data:
        if not Substance.query.filter_by(name=data['name']).first():
            substance = Substance(**data)
            db.session.add(substance)
    
    db.session.commit()
    print("✅ Substances créées avec succès")

def migrate_mining_deposits():
    """Migrer les gisements vers PostGIS"""
    old_deposits = OldMiningDeposit.query.all()
    
    for old_deposit in old_deposits:
        # Trouver la substance correspondante
        substance = Substance.query.filter_by(name=old_deposit.type).first()
        if not substance:
            # Créer substance si elle n'existe pas
            substance = Substance(
                name=old_deposit.type,
                symbol=old_deposit.type[:2].upper(),
                color_code='#CCCCCC',  # Couleur par défaut
                unit='kg'
            )
            db.session.add(substance)
            db.session.commit()
        
        # Créer le nouveau gisement PostGIS
        new_deposit = MiningDepositGIS(
            name=old_deposit.name,
            geom=ST_GeomFromText(f'POINT({old_deposit.longitude} {old_deposit.latitude})', 4326),
            substance_id=substance.id,
            company=old_deposit.company,
            description=old_deposit.description,
            estimated_quantity=float(old_deposit.estimated_quantity.split()[0]) if old_deposit.estimated_quantity else None,
            status=old_deposit.status,
            approval_status='approved',  # Les données existantes sont considérées comme approuvées
            data_source='Migration from SQLite'
        )
        
        db.session.add(new_deposit)
    
    db.session.commit()
    print(f"✅ {len(old_deposits)} gisements migrés vers PostGIS")

def run_migration():
    """Exécuter la migration complète"""
    print("🚀 Début de la migration vers PostGIS...")
    
    # Créer les tables
    db.create_all()
    
    # Migrer les données
    migrate_substances()
    migrate_mining_deposits()
    
    print("🎉 Migration terminée avec succès !")

if __name__ == '__main__':
    run_migration()
```

---

## 🚀 **DÉMARRAGE IMMÉDIAT**

### **Prochaines Étapes Cette Semaine**

1. **Installer PostgreSQL + PostGIS** (voir guide ci-dessus)
2. **Configurer l'environnement Python** avec nouvelles dépendances
3. **Tester la connexion** à la base PostGIS
4. **Exécuter la migration** des données existantes

### **Commands à Exécuter**

```powershell
# 1. Aller dans le répertoire backend
cd c:\Users\Moha\Desktop\test\reactJs\ODG_Modules_Complete\odg-webgis-backend

# 2. Activer l'environnement virtuel
.\venv\Scripts\activate

# 3. Installer les nouvelles dépendances
pip install psycopg2-binary geoalchemy2 flask-migrate shapely geopandas

# 4. Initialiser Flask-Migrate
flask db init

# 5. Créer la première migration
flask db migrate -m "Initial PostGIS migration"

# 6. Appliquer la migration
flask db upgrade
```

Voulez-vous que je vous aide avec l'installation de PostgreSQL sur Windows ou préférez-vous commencer par une autre étape ?
