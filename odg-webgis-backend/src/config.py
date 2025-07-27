# Configuration Flask pour PostGIS - ODG Platform
import os
from datetime import timedelta

class Config:
    """Configuration de base"""
    
    # Base de données PostGIS
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://odg_user:ODG_SecurePass2025!@localhost:5432/odg_database'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,        # Vérifier les connexions
        'pool_recycle': 300,          # Recycler après 5 min
        'pool_timeout': 20,           # Timeout connexion
        'max_overflow': 0,            # Pas de connexions supplémentaires
        'pool_size': 10               # Taille du pool
    }
    
    # Sécurité
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'asdf#FGSgvasgf$5$WGT_PostGIS_2025'
    
    # CORS - Autoriser les domaines de développement
    CORS_ORIGINS = [
        'http://localhost:3000',      # React dev server
        'http://localhost:5173',      # Vite dev server
        'http://localhost:5000',      # Flask server
        'http://127.0.0.1:5000',      # Flask alternative
        'http://127.0.0.1:5173'       # Vite alternative
    ]
    
    # Upload de fichiers SIG
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max pour fichiers SIG
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads', 'sig')
    ALLOWED_EXTENSIONS = {'kml', 'gpx', 'geojson', 'json', 'shp', 'csv', 'zip'}
    
    # Configuration SIG
    DEFAULT_SRID = 4326              # WGS84 - Système de référence mondial
    SPATIAL_INDEX_TYPE = 'GIST'      # Type d'index spatial PostGIS
    
    # Pagination par défaut
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

class DevelopmentConfig(Config):
    """Configuration développement"""
    DEBUG = True
    SQLALCHEMY_ECHO = True          # Afficher les requêtes SQL
    TESTING = False
    
    # Logs détaillés en développement
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Configuration production"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    TESTING = False
    
    # Sécurité renforcée en production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Logs optimisés
    LOG_LEVEL = 'INFO'

class TestingConfig(Config):
    """Configuration tests"""
    TESTING = True
    DEBUG = True
    
    # Base de données de test en mémoire
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Désactiver CSRF pour les tests
    WTF_CSRF_ENABLED = False

# Mapping des environnements
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(env_name=None):
    """Récupérer la configuration selon l'environnement"""
    if env_name is None:
        env_name = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(env_name, config['default'])
