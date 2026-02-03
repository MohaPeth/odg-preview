# 🚀 GUIDE D'INSTALLATION DES CORRECTIFS – ODG EXPORT

## 📋 Vue d'Ensemble

Ce guide permet d'installer les correctifs critiques identifiés par le Tech Lead, notamment :
- ✅ Service d'export géospatial complet (KML, KMZ, SHP, CSV, WKT, GPX)
- ✅ Route d'export batch (plusieurs couches à la fois)
- ✅ Dépendances mises à jour

## ⚠️ PRÉREQUIS

- Python 3.11+
- PostgreSQL 15+ avec PostGIS
- Environnement virtuel activé
- Accès administrateur à la base de données

## 📦 ÉTAPE 1 : Installation des Dépendances

### 1.1 Mise à Jour requirements.txt

Le fichier `backend/requirements.txt` a été mis à jour avec les nouvelles dépendances :
- `simplekml==1.3.6` (export KML/KMZ)
- `gpxpy==1.5.0` (export GPX)
- `python-magic==0.4.27` (validation MIME)

### 1.2 Installation

```bash
cd backend
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate     # Windows

# Installation des nouvelles dépendances
pip install simplekml==1.3.6
pip install gpxpy==1.5.0
pip install python-magic==0.4.27

# OU installer toutes les dépendances
pip install -r requirements.txt
```

### 1.3 Vérification de l'Installation

```bash
python -c "import simplekml; print('simplekml OK')"
python -c "import gpxpy; print('gpxpy OK')"
python -c "import magic; print('python-magic OK')"
```

**Sortie attendue** :
```
simplekml OK
gpxpy OK
python-magic OK
```

## 🔧 ÉTAPE 2 : Vérification des Fichiers Créés

### 2.1 Service d'Export

Vérifier que le fichier existe :
```bash
ls -la backend/src/services/geospatial_export.py
```

### 2.2 Routes Mises à Jour

Vérifier que les routes ont été modifiées :
```bash
grep -n "geospatial_export" backend/src/routes/geospatial_import.py
```

**Attendu** : Plusieurs lignes avec `from src.services.geospatial_export import GeospatialExportService`

## 🧪 ÉTAPE 3 : Tests de Validation

### 3.1 Démarrage du Serveur

```bash
cd backend
python run_server.py
```

**Sortie attendue** :
```
 * Running on http://localhost:5000
 * Restarting with stat
Module simplekml disponible - Export KML activé
Module fiona disponible - Export Shapefile activé
Service d'export initialisé
```

### 3.2 Test de l'API Export

#### Test 1 : Export GeoJSON (déjà fonctionnel)

```bash
curl -X GET "http://localhost:5000/api/geospatial/layers/1/export/geojson" \
  -H "Accept: application/json" \
  -o test_geojson.json

# Vérifier le fichier
cat test_geojson.json
```

#### Test 2 : Export KML (NOUVEAU)

```bash
curl -X GET "http://localhost:5000/api/geospatial/layers/1/export/kml" \
  -H "Accept: application/vnd.google-earth.kml+xml" \
  -o test_export.kml

# Vérifier le fichier
file test_export.kml
cat test_export.kml
```

**Attendu** : Fichier KML valide avec balises XML :
```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Nom de la couche</name>
    ...
  </Document>
</kml>
```

#### Test 3 : Export KMZ (NOUVEAU)

```bash
curl -X GET "http://localhost:5000/api/geospatial/layers/1/export/kmz" \
  -o test_export.kmz

# Vérifier que c'est un ZIP
file test_export.kmz
unzip -l test_export.kmz
```

**Attendu** : Archive ZIP contenant `doc.kml`

#### Test 4 : Export Shapefile (NOUVEAU)

```bash
curl -X GET "http://localhost:5000/api/geospatial/layers/1/export/shp" \
  -o test_export_shp.zip

# Décompression
unzip test_export_shp.zip -d test_shapefile/
ls -la test_shapefile/
```

**Attendu** : Fichiers `.shp`, `.shx`, `.dbf`, `.prj`, `.cpg`

#### Test 5 : Export CSV (NOUVEAU)

```bash
curl -X GET "http://localhost:5000/api/geospatial/layers/1/export/csv" \
  -o test_export.csv

# Vérifier le contenu
cat test_export.csv
```

**Attendu** : CSV valide avec en-têtes et données

#### Test 6 : Export GPX (NOUVEAU)

```bash
curl -X GET "http://localhost:5000/api/geospatial/layers/1/export/gpx" \
  -o test_export.gpx

# Vérifier le fichier
file test_export.gpx
cat test_export.gpx
```

**Attendu** : Fichier GPX valide (uniquement pour points)

#### Test 7 : Export Batch (NOUVEAU)

```bash
curl -X POST "http://localhost:5000/api/geospatial/export-batch" \
  -H "Content-Type: application/json" \
  -d '{"layer_ids": [1, 2, 3], "format": "kml"}' \
  -o test_batch_export.zip

# Vérifier le ZIP
unzip -l test_batch_export.zip
```

**Attendu** : Archive ZIP contenant plusieurs fichiers KML

### 3.3 Tests depuis le Frontend

#### Test avec curl simulant le frontend

```bash
# Test avec headers complets
curl -X GET "http://localhost:5000/api/geospatial/layers/1/export/kml" \
  -H "Origin: http://localhost:5173" \
  -H "Accept: */*" \
  -v \
  -o test_frontend.kml
```

**Vérifier** :
- Status Code : `200 OK`
- Header `Content-Type` : `application/vnd.google-earth.kml+xml`
- Header `Content-Disposition` : `attachment; filename=...`
- Header `Access-Control-Allow-Origin` : `*` ou `http://localhost:5173`

## 🔍 ÉTAPE 4 : Validation PostGIS

### 4.1 Vérification des Couches

```sql
-- Connexion à la base
psql -d odg_mining -U odg_user

-- Lister les couches disponibles
SELECT 
    id, 
    name, 
    layer_type, 
    geometry_type, 
    status,
    ST_IsValid(geom) as geom_valid,
    ST_SRID(geom) as srid
FROM geospatial_layers
WHERE is_visible = true
LIMIT 10;
```

**Attendu** : Liste des couches avec `geom_valid = true` et `srid = 4326`

### 4.2 Test de Conversion PostGIS → WKT

```sql
-- Test export WKT direct depuis PostGIS
SELECT 
    id,
    name,
    ST_AsText(geom) as wkt,
    ST_GeometryType(geom) as geom_type
FROM geospatial_layers
WHERE id = 1;
```

**Attendu** : Géométrie WKT valide (ex: `POINT(9.4536 0.3901)`)

## 📊 ÉTAPE 5 : Tests d'Intégration

### 5.1 Script Python de Test Complet

Créer `backend/test_export_complete.py` :

```python
#!/usr/bin/env python3
"""
Script de test complet du système d'export ODG
"""

import requests
import os
import zipfile
from pathlib import Path

BASE_URL = "http://localhost:5000/api/geospatial"
TEST_LAYER_ID = 1
OUTPUT_DIR = "test_exports"

# Création du dossier de sortie
Path(OUTPUT_DIR).mkdir(exist_ok=True)

def test_export(format, layer_id=TEST_LAYER_ID):
    """Test d'export d'une couche"""
    print(f"\n🧪 Test export {format.upper()}...")
    
    url = f"{BASE_URL}/layers/{layer_id}/export/{format}"
    response = requests.get(url)
    
    if response.status_code == 200:
        # Extraction du nom de fichier
        disposition = response.headers.get('Content-Disposition', '')
        filename = disposition.split('filename=')[-1].strip('"') if 'filename=' in disposition else f"test.{format}"
        
        # Sauvegarde
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"   ✅ Export réussi: {filepath} ({len(response.content)} bytes)")
        
        # Validation spécifique par format
        if format in ['shp', 'kmz']:
            # Vérifier que c'est un ZIP valide
            if zipfile.is_zipfile(filepath):
                with zipfile.ZipFile(filepath, 'r') as zf:
                    print(f"   📦 Archive contient: {', '.join(zf.namelist())}")
            else:
                print(f"   ⚠️  Fichier n'est pas un ZIP valide")
        
        return True
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        print(f"   📄 Réponse: {response.text}")
        return False

def test_batch_export(layer_ids, format):
    """Test d'export batch"""
    print(f"\n🧪 Test export batch {format.upper()} ({len(layer_ids)} couches)...")
    
    url = f"{BASE_URL}/export-batch"
    payload = {
        "layer_ids": layer_ids,
        "format": format
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        filename = f"batch_export_{len(layer_ids)}_layers.zip"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"   ✅ Export batch réussi: {filepath} ({len(response.content)} bytes)")
        
        # Lister le contenu du ZIP
        if zipfile.is_zipfile(filepath):
            with zipfile.ZipFile(filepath, 'r') as zf:
                print(f"   📦 Archive contient {len(zf.namelist())} fichiers")
                for name in zf.namelist()[:5]:  # Afficher les 5 premiers
                    print(f"      - {name}")
        
        return True
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        print(f"   📄 Réponse: {response.text}")
        return False

def main():
    print("=" * 60)
    print("🚀 TEST COMPLET DU SYSTÈME D'EXPORT ODG")
    print("=" * 60)
    
    # Tests individuels par format
    formats = ['geojson', 'kml', 'kmz', 'shp', 'csv', 'wkt', 'gpx']
    results = {}
    
    for fmt in formats:
        results[fmt] = test_export(fmt)
    
    # Test batch
    results['batch'] = test_batch_export([1, 2, 3], 'kml')
    
    # Rapport final
    print("\n" + "=" * 60)
    print("📊 RAPPORT FINAL")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {test.upper()}")
    
    print("\n" + "=" * 60)
    print(f"🎯 Résultats: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
    print("=" * 60)
    
    if passed == total:
        print("\n✨ TOUS LES TESTS SONT PASSÉS ! Système d'export opérationnel.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests ont échoué. Vérifier les logs ci-dessus.")
        return 1

if __name__ == "__main__":
    exit(main())
```

### 5.2 Exécution du Script de Test

```bash
cd backend
python test_export_complete.py
```

**Sortie attendue** :
```
============================================================
🚀 TEST COMPLET DU SYSTÈME D'EXPORT ODG
============================================================

🧪 Test export GEOJSON...
   ✅ Export réussi: test_exports/layer_1.geojson (1234 bytes)

🧪 Test export KML...
   ✅ Export réussi: test_exports/layer_1.kml (2345 bytes)

🧪 Test export KMZ...
   ✅ Export réussi: test_exports/layer_1.kmz (1567 bytes)
   📦 Archive contient: doc.kml

[...]

============================================================
📊 RAPPORT FINAL
============================================================
  ✅ PASS - GEOJSON
  ✅ PASS - KML
  ✅ PASS - KMZ
  ✅ PASS - SHP
  ✅ PASS - CSV
  ✅ PASS - WKT
  ✅ PASS - GPX
  ✅ PASS - BATCH

============================================================
🎯 Résultats: 8/8 tests réussis (100.0%)
============================================================

✨ TOUS LES TESTS SONT PASSÉS ! Système d'export opérationnel.
```

## ✅ ÉTAPE 6 : Validation dans Google Earth

### 6.1 Test KML dans Google Earth

1. Exporter une couche en KML :
```bash
curl -X GET "http://localhost:5000/api/geospatial/layers/1/export/kml" -o test_google_earth.kml
```

2. Ouvrir Google Earth Pro ou Google Earth Web

3. Importer le fichier `test_google_earth.kml`

**Vérifications** :
- ✅ La couche apparaît dans la liste des lieux
- ✅ Les géométries sont affichées sur la carte
- ✅ Les popups contiennent les métadonnées
- ✅ Les couleurs correspondent aux styles définis

### 6.2 Test Shapefile dans QGIS

1. Exporter en Shapefile :
```bash
curl -X GET "http://localhost:5000/api/geospatial/layers/1/export/shp" -o test_qgis.zip
unzip test_qgis.zip -d test_qgis/
```

2. Ouvrir QGIS Desktop

3. Menu : `Layer` → `Add Layer` → `Add Vector Layer`

4. Sélectionner le fichier `.shp`

**Vérifications** :
- ✅ La couche s'affiche correctement
- ✅ La table d'attributs contient toutes les données
- ✅ Le CRS est bien WGS84 (EPSG:4326)
- ✅ Les géométries sont valides (pas d'erreurs)

## 🚨 DÉPANNAGE

### Problème : "Module simplekml non disponible"

**Solution** :
```bash
pip install --upgrade simplekml==1.3.6
python -c "import simplekml; print('OK')"
```

### Problème : "Export KML retourne 501"

**Causes possibles** :
1. Module simplekml non installé
2. Géométrie invalide dans la couche
3. Erreur dans le modèle GeospatialLayer

**Vérifications** :
```bash
# Logs du serveur
tail -f backend/logs/app.log

# Test direct
python -c "from src.services.geospatial_export import GeospatialExportService; print('Import OK')"
```

### Problème : "Export Shapefile échoue"

**Solution** :
```bash
# Vérifier fiona
pip install --upgrade fiona geopandas

# Test direct
python -c "import fiona; print(fiona.__version__)"
```

### Problème : Fichier téléchargé est corrompu

**Causes** :
- Encodage incorrect (UTF-8 vs Latin1)
- Headers HTTP manquants
- Fichier temporaire non nettoyé

**Solution** :
Vérifier les headers dans la réponse :
```bash
curl -I "http://localhost:5000/api/geospatial/layers/1/export/kml"
```

**Attendu** :
```
HTTP/1.1 200 OK
Content-Type: application/vnd.google-earth.kml+xml
Content-Disposition: attachment; filename=layer_1.kml
Content-Length: 2345
```

## 📈 PROCHAINES ÉTAPES

Une fois tous les tests validés :

1. **Documentation API** : Mettre à jour la documentation avec les nouveaux endpoints
2. **Frontend** : Implémenter les boutons d'export dans le dashboard
3. **Tests E2E** : Ajouter des tests Cypress pour les exports
4. **Monitoring** : Logger tous les exports pour audit
5. **Performance** : Implémenter le cache Redis pour exports fréquents

## 📞 SUPPORT

En cas de problème :
1. Consulter les logs : `backend/logs/app.log`
2. Vérifier les dépendances : `pip list | grep -E "(simplekml|gpxpy|fiona)"`
3. Tester la connexion PostGIS : `psql -d odg_mining -c "SELECT PostGIS_version();"`
4. Consulter le rapport d'analyse : `TECH_LEAD_ANALYSIS_COMPLETE.md`

---

**Version** : 1.0  
**Date** : 14 janvier 2026  
**Auteur** : Tech Lead ODG
