#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de lancement amélioré pour ODG WebGIS API avec PostGIS
Version sans changement de répertoire de travail
"""

import sys
import os

# Ajouter le dossier src au Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

if __name__ == '__main__':
    try:
        from main_postgis import app
        
        print("🌍 Démarrage ODG WebGIS API avec PostGIS")
        print("📍 Frontend attendu sur: http://localhost:5173")
        print("🗄️ API disponible sur: http://localhost:5000")
        print("📊 Health check: http://localhost:5000/api/health")
        print("🔧 Version API: http://localhost:5000/api/version")
        print("📋 Endpoints: http://localhost:5000/")
        print("\n🔄 Mode développement (sans auto-reload)")
        print("   Pour redémarrer : Ctrl+C puis relancer")
        print("=" * 50)
        
        # Lancement sans reloader pour éviter les problèmes de path
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True,
            use_reloader=False  # Pas de reloader automatique
        )
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("🔧 Solutions possibles:")
        print("   1. Installer les dépendances: pip install -r requirements.txt")
        print("   2. Vérifier la structure du projet")
        print("   3. Utiliser l'environnement virtuel: .venv\\Scripts\\activate")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté par l'utilisateur")
        
    except Exception as e:
        print(f"💥 Erreur de démarrage: {e}")
        print("🔍 Vérifiez la configuration de la base de données")
        sys.exit(1)
