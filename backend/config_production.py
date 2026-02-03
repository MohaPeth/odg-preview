"""
Configuration de production pour ODG Géospatial
Gère les variables d'environnement et la configuration sécurisée
"""

import os
from urllib.parse import urlparse

class ProductionConfig:
    """Configuration pour l'environnement de production"""
    
    # Sécurité - validation faite dans validate_production_config()
    SECRET_KEY = os.getenv('SECRET_KEY', '')
    
    # Base de données - validation faite dans validate_production_config()
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }
    
    # Upload de fichiers
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_FILE_SIZE', 100 * 1024 * 1024))  # 100MB par défaut
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/odg_uploads')
    
    # CORS - Domaines autorisés - validation faite dans validate_production_config()
    cors_env = os.getenv('CORS_ORIGINS', '')
    CORS_ORIGINS = [origin.strip() for origin in cors_env.split(',') if origin.strip()] if cors_env else []
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/var/log/odg/app.log')
    
    # Géospatial
    DEFAULT_SRID = 4326  # WGS84
    MAX_FEATURES_PER_LAYER = int(os.getenv('MAX_FEATURES_PER_LAYER', 10000))
    SUPPORTED_FORMATS = ['KML', 'KMZ', 'SHP', 'GEOJSON', 'CSV', 'TXT', 'TIFF']
    
    # Performance
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 300))  # 5 minutes
    
    # Monitoring
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'true').lower() == 'true'
    METRICS_PORT = int(os.getenv('METRICS_PORT', 9090))

class DevelopmentConfig:
    """Configuration pour l'environnement de développement"""
    
    # Utiliser .env même en développement
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-UNSAFE-change-me')
    DEBUG = True
    
    # Base de données : PostgreSQL si DATABASE_URL définie, sinon SQLite
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///odg_dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload de fichiers
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))  # 50MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
    
    # CORS - Lire depuis .env si disponible, sinon permissif
    cors_env = os.getenv('CORS_ORIGINS', '')
    CORS_ORIGINS = [origin.strip() for origin in cors_env.split(',') if origin.strip()] if cors_env else ['*']
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    
    # Géospatial
    DEFAULT_SRID = 4326
    MAX_FEATURES_PER_LAYER = 1000
    SUPPORTED_FORMATS = ['KML', 'KMZ', 'SHP', 'GEOJSON', 'CSV', 'TXT', 'TIFF']

def get_config():
    """Retourne la configuration appropriée selon l'environnement"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig
    else:
        return DevelopmentConfig

# Validation de la configuration de production
def validate_production_config():
    """Valide que toutes les variables requises sont définies pour la production"""
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'CORS_ORIGINS'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == '':
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Variables d'environnement manquantes pour la production : {missing_vars}")
    
    # Validation de l'URL de base de données
    db_url = os.getenv('DATABASE_URL')
    parsed = urlparse(db_url)
    
    if parsed.scheme not in ['postgresql', 'postgres']:
        raise ValueError("DATABASE_URL doit utiliser PostgreSQL en production")
    
    # Validation CORS (pas de wildcard en production)
    cors_origins = os.getenv('CORS_ORIGINS', '')
    if '*' in cors_origins:
        raise ValueError("CORS_ORIGINS ne doit pas contenir de wildcard (*) en production")
    
    return True

# Configuration des logs pour la production
def setup_logging(app):
    """Configure le logging pour la production"""
    import logging
    from logging.handlers import RotatingFileHandler
    
    if not app.debug:
        # Créer le dossier de logs s'il n'existe pas
        log_dir = os.path.dirname(app.config.get('LOG_FILE', '/var/log/odg/app.log'))
        os.makedirs(log_dir, exist_ok=True)
        
        # Handler pour fichier avec rotation
        file_handler = RotatingFileHandler(
            app.config.get('LOG_FILE', '/var/log/odg/app.log'),
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
        app.logger.info('ODG Géospatial startup')

# Exemple de fichier .env pour la production
ENV_TEMPLATE = """
# Configuration de production ODG Géospatial
# Copiez ce fichier vers .env et remplissez les valeurs

# Base de données PostgreSQL + PostGIS
DATABASE_URL=postgresql://username:password@localhost:5432/odg_production

# Sécurité
SECRET_KEY=your-very-secret-key-here-change-this

# Upload de fichiers
MAX_FILE_SIZE=104857600
UPLOAD_FOLDER=/var/odg/uploads

# CORS - Domaines autorisés (séparés par des virgules)
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/odg/app.log

# Performance
MAX_FEATURES_PER_LAYER=10000
CACHE_TYPE=redis
CACHE_TIMEOUT=300

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090

# Environnement
FLASK_ENV=production
"""

if __name__ == "__main__":
    # Créer un fichier .env d'exemple
    env_file = os.path.join(os.path.dirname(__file__), '.env.example')
    with open(env_file, 'w') as f:
        f.write(ENV_TEMPLATE)
    
    print(f"✅ Fichier d'exemple créé : {env_file}")
    print("📋 Copiez-le vers .env et remplissez les valeurs pour la production")
