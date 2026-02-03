"""
Script de nettoyage des couches de test avec données incorrectes
À exécuter après avoir corrigé le bug .tolist() pour supprimer les anciennes couches
et permettre un ré-import propre.
"""

import sys
import os

# Ajouter le dossier parent au PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app, db
from src.models.geospatial_layers import GeospatialLayer

def cleanup_layers():
    """Supprimer toutes les couches et permettre un redémarrage propre"""
    
    with app.app_context():
        print("\n" + "="*60)
        print("🧹 NETTOYAGE DES COUCHES GÉOSPATIALES")
        print("="*60 + "\n")
        
        # Lister toutes les couches actuelles
        layers = GeospatialLayer.query.all()
        
        if not layers:
            print("✅ Aucune couche trouvée - Base de données déjà propre")
            return
        
        print(f"📊 {len(layers)} couche(s) trouvée(s):\n")
        for layer in layers:
            print(f"   • ID {layer.id}: {layer.name}")
            print(f"     - Type: {layer.layer_type or '❌ NULL'}")
            print(f"     - Format: {layer.source_format or '❌ NULL'}")
            print(f"     - Géométrie: {'✅' if layer.geometry_type else '❌ NULL'}")
            print()
        
        # Demander confirmation
        response = input("⚠️  Voulez-vous SUPPRIMER toutes ces couches ? (oui/non): ")
        
        if response.lower() not in ['oui', 'o', 'yes', 'y']:
            print("\n❌ Opération annulée")
            return
        
        # Supprimer toutes les couches
        try:
            count = GeospatialLayer.query.delete()
            db.session.commit()
            
            print(f"\n✅ {count} couche(s) supprimée(s) avec succès!")
            print("\n💡 Vous pouvez maintenant ré-importer vos fichiers géospatiaux")
            print("   Les nouveaux imports utiliseront le code corrigé (.tolist() fixé)")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erreur lors de la suppression: {e}")
            raise

def list_layers_only():
    """Lister les couches sans les supprimer"""
    
    with app.app_context():
        print("\n" + "="*60)
        print("📋 LISTE DES COUCHES ACTUELLES")
        print("="*60 + "\n")
        
        layers = GeospatialLayer.query.all()
        
        if not layers:
            print("ℹ️  Aucune couche trouvée dans la base de données")
            return
        
        print(f"Total: {len(layers)} couche(s)\n")
        
        for layer in layers:
            print(f"🗺️  {layer.name} (ID: {layer.id})")
            print(f"   └─ Type: {layer.layer_type or '⚠️  Non défini'}")
            print(f"   └─ Format: {layer.source_format or '⚠️  Non défini'}")
            print(f"   └─ Géométrie: {layer.geometry_type or '⚠️  Non définie'}")
            print(f"   └─ Features: {layer.point_count or 0}")
            print(f"   └─ Statut: {layer.status}")
            print(f"   └─ Visible: {'Oui' if layer.is_visible else 'Non'}")
            print()

if __name__ == '__main__':
    print("\n🔧 ODG - Outil de maintenance des couches géospatiales\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        list_layers_only()
    else:
        cleanup_layers()
