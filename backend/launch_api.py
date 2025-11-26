#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Démarrage direct depuis le dossier src/
Cette version évite tous les problèmes de path
"""

import sys
import os
from pathlib import Path

# Déterminer les chemins
script_dir = Path(__file__).parent
src_dir = script_dir / 'src'

# Changer vers le dossier src AVANT d'importer
os.chdir(src_dir)

# Maintenant importer depuis src/
sys.path.insert(0, str(src_dir))

if __name__ == '__main__':
    try:
        # Import direct depuis le dossier src/
        from main_postgis import app
        
        print("🌍 ODG WebGIS API - Démarrage Direct")
        print("=" * 50)
        print("📍 Frontend: http://localhost:5173")
        print("🗄️ API: http://localhost:5000")
        print("📊 Health: http://localhost:5000/api/health")
        print("🔧 Version: http://localhost:5000/api/version")
        print("=" * 50)
        print("💡 Redémarrage automatique activé")
        print("   Modifiez les fichiers pour voir les changements")
        print("=" * 50)
        
        # Configuration optimale pour développement
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True,
            use_reloader=True,  # Reloader activé car on est dans src/
            reloader_options={'watchdog': True}  # Monitoring avancé
        )
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("\n🔧 Diagnostic:")
        print(f"   Dossier de travail: {os.getcwd()}")
        print(f"   Python path: {sys.path[:3]}...")
        print("\n💡 Solutions:")
        print("   1. pip install -r ../requirements.txt")
        print("   2. Vérifier que vous êtes dans le bon environnement")
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur")
        
    except Exception as e:
        print(f"💥 Erreur: {e}")
        import traceback
        traceback.print_exc()
