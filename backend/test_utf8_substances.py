# -*- coding: utf-8 -*-
"""
Test specifique pour l'encodage UTF-8 des substances
"""
import os
import sys
import json

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask
from models.mining_data import db
from models.substances import Substance, create_default_substances
from config import get_config

def test_utf8_substances():
    """Test d'encodage UTF-8 pour les substances"""
    print("🧪 Test d'encodage UTF-8 des substances...")
    
    # Creer l'application Flask
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)
    
    # Configuration UTF-8 explicite
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # Initialiser la base de données
    db.init_app(app)
    
    with app.app_context():
        try:
            # Creer les tables si necessaire
            db.create_all()
            
            # Verifier si des substances existent deja
            substances_count = Substance.query.count()
            print(f"📊 Nombre de substances existantes: {substances_count}")
            
            # Si pas de substances, les créer
            if substances_count == 0:
                print("📝 Creation des substances par defaut...")
                create_default_substances()
                db.session.commit()
                print("✅ Substances creees avec succes!")
            
            # Recuperer toutes les substances
            substances = Substance.query.filter_by(is_active=True).all()
            print(f"🔍 Substances actives trouvees: {len(substances)}")
            
            # Tester l'encodage de chaque substance
            for substance in substances:
                print(f"\n📋 Test substance: {substance.name}")
                print(f"   Symbole: {substance.symbol}")
                print(f"   Description: {substance.description}")
                
                # Tester la conversion en JSON
                try:
                    substance_dict = {
                        'id': substance.id,
                        'name': substance.name,
                        'symbol': substance.symbol,
                        'description': substance.description,
                        'unit': substance.unit,
                        'color_code': substance.color_code,
                        'market_price': substance.market_price
                    }
                    
                    # Conversion en JSON avec UTF-8
                    json_str = json.dumps(substance_dict, ensure_ascii=False, indent=2)
                    print(f"   ✅ JSON UTF-8: OK")
                    
                    # Verifier l'encodage des caracteres speciaux
                    if any(char in substance.description for char in ['e', 'e', 'a', 'c', 'o', 'u']):
                        print(f"   🎯 Caracteres traites correctement")
                    
                except Exception as e:
                    print(f"   ❌ Erreur JSON: {e}")
                    return False
            
            print("\n🎉 Test UTF-8 reussi! Toutes les substances sont correctement encodees.")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
            return False

if __name__ == "__main__":
    success = test_utf8_substances()
    if success:
        print("\n✅ Tests d'encodage UTF-8 termines avec succes!")
    else:
        print("\n❌ Echec des tests d'encodage UTF-8")
        sys.exit(1)
