#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script pour vérifier les couches dans la base de données"""

import os
import sys
from pathlib import Path
import psycopg2
import json

# Charger les variables d'environnement
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

def check_layers():
    """Vérifie les couches dans la base de données"""
    db_url = os.getenv('DATABASE_URL')
    
    # Parser l'URL PostgreSQL
    # Format: postgresql://user:pass@host:port/dbname
    import re
    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
    if not match:
        print(f"❌ URL invalide: {db_url}")
        return
    
    user, password, host, port, dbname = match.groups()
    password = password.replace('%40', '@')  # Décoder le @
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=dbname
        )
        cursor = conn.cursor()
        
        # Compter les couches
        cursor.execute("SELECT COUNT(*) FROM geospatial_layers")
        count = cursor.fetchone()[0]
        
        print(f"\n{'='*60}")
        print(f"📊 ÉTAT DE LA BASE DE DONNÉES")
        print(f"{'='*60}\n")
        print(f"Nombre total de couches: {count}\n")
        
        if count == 0:
            print("❌ Aucune couche trouvée dans la base de données")
            conn.close()
            return
        
        # Récupérer les détails
        cursor.execute("""
            SELECT id, name, layer_type, source_format, is_visible, 
                   layer_metadata, ST_AsText(geom) as geometry
            FROM geospatial_layers 
            ORDER BY created_at DESC
        """)
        
        layers = cursor.fetchall()
        
        for i, layer in enumerate(layers, 1):
            layer_id, name, layer_type, source_format, is_visible, metadata, geometry = layer
            
            print(f"Couche #{i}: {name}")
            print(f"  - ID: {layer_id}")
            print(f"  - Type: {layer_type}")
            print(f"  - Format: {source_format}")
            print(f"  - Visible: {is_visible}")
            
            # Vérifier le GeoJSON dans les métadonnées
            has_geojson = False
            feature_count = 0
            if metadata and isinstance(metadata, dict):
                has_geojson = 'geojson' in metadata
                if has_geojson:
                    geojson_data = metadata['geojson']
                    if isinstance(geojson_data, dict):
                        if geojson_data.get('type') == 'FeatureCollection':
                            feature_count = len(geojson_data.get('features', []))
                        elif geojson_data.get('type') == 'Feature':
                            feature_count = 1
            
            print(f"  - GeoJSON: {'✅ Présent' if has_geojson else '❌ Manquant'}")
            print(f"  - Geometry PostGIS: {'✅ Présent' if geometry else '❌ Manquant'}")
            
            if has_geojson:
                print(f"  - Nombre de features: {feature_count}")
            
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == '__main__':
    check_layers()
