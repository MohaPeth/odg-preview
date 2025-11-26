#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de lancement pour ODG WebGIS API avec PostGIS
Résout les problèmes d'imports Python
"""

import sys
import os

# Ajouter le dossier src au Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

if __name__ == '__main__':
    # Importer et lancer l'application depuis src/
    # NE PAS changer le répertoire de travail pour éviter les problèmes de restart
    # os.chdir(src_dir)  # Commenté pour éviter les problèmes de redémarrage Flask
    
    try:
        from main_postgis import app
        
        print("🌍 Démarrage ODG WebGIS API avec PostGIS")
        print("📍 Frontend attendu sur: http://localhost:5173")
        print("🗄️ API disponible sur: http://localhost:5000")
        print("📊 Health check: http://localhost:5000/api/health")
        print("🔧 Version API: http://localhost:5000/api/version")
        print("📋 Endpoints: http://localhost:5000/")
        print("\n" + "=" * 50)
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True,
            use_reloader=False  # Désactiver le reloader pour éviter les problèmes de path
        )
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("🔧 Vérifiez que tous les modules sont installés:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"💥 Erreur de démarrage: {e}")
        sys.exit(1)
