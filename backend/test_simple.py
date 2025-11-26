# -*- coding: utf-8 -*-
import sys
import os
sys.path.append('src')

# Test simple pour verifier que tout fonctionne
from main_postgis import create_app

def test_server():
    print("Creation de l'application Flask...")
    app = create_app()
    print("Application creee avec succes!")
    
    with app.app_context():
        print("Context de l'application OK")
        
        # Test import des substances
        try:
            from models.substances import Substance, create_default_substances
            print("Import des substances OK")
            
            # Test creation de la base
            from models.mining_data import db
            db.create_all()
            print("Base de donnees creee")
            
            # Test creation des substances
            result = create_default_substances()
            print(f"Substances: {result}")
            
            print("✅ Tous les tests passes!")
            return True
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    test_server()
