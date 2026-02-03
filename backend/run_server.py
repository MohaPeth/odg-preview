#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de lancement du serveur ODG avec chargement des variables d'environnement
"""

import os
import sys
from pathlib import Path

# Charger les variables d'environnement depuis .env
def load_env_file():
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        print(f"📄 Chargement des variables depuis {env_path}")
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ Variables d'environnement chargées")
    else:
        print("⚠️  Fichier .env non trouvé, utilisation des valeurs par défaut")

# Charger l'environnement
load_env_file()

# Forcer le mode développement
os.environ['FLASK_ENV'] = 'development'

# Ajouter le dossier src au path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / 'src'))

if __name__ == '__main__':
    try:
        # Importer l'application
        from src.main import app, init_database
        
        print("\n" + "="*60)
        print("🌍 ODG WebGIS API - Démarrage")
        print("="*60)
        print(f"🗄️  Base de données: {os.environ.get('DATABASE_URL', 'Non configurée')}")
        print(f"🔧 Mode: {os.environ.get('FLASK_ENV', 'development')}")
        print(f"🌐 API: http://localhost:5000")
        print(f"📊 Frontend attendu: http://localhost:5173")
        print("="*60)
        
        # Initialiser la base de données
        print("\n🔄 Initialisation de la base de données...")
        init_database()
        print("✅ Base de données initialisée\n")
        
        print("🚀 Serveur démarré - Appuyez sur CTRL+C pour arrêter")
        print("="*60 + "\n")
        
        # Lancer le serveur
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False
        )
        
    except ImportError as e:
        print(f"\n❌ Erreur d'import: {e}")
        print("\n🔧 Solutions:")
        print("   1. Vérifier que les dépendances sont installées: pip install -r requirements.txt")
        print("   2. Activer l'environnement virtuel si nécessaire")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Serveur arrêté par l'utilisateur")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n💥 Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
