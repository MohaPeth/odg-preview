#!/usr/bin/env python3
"""
Point d'entrée WSGI pour la production ODG Géospatial
Compatible avec Gunicorn, uWSGI, et autres serveurs WSGI
"""

import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Définir l'environnement de production
os.environ.setdefault('FLASK_ENV', 'production')

# Importer l'application
from src.main import app

# Configuration pour Gunicorn
application = app

if __name__ == "__main__":
    # Pour les tests locaux
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    print(f"🚀 Démarrage ODG Géospatial sur le port {port}")
    print(f"🔧 Mode debug: {debug}")
    print(f"🌍 Environnement: {os.getenv('FLASK_ENV', 'development')}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
