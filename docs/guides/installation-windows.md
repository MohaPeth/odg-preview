# 🪟 Guide d'Installation Windows - ODG Export

## ⚡ Installation Rapide (Sans Shapefile)

Cette installation **fonctionne immédiatement** sur Windows sans compiler GDAL.

### Étape 1 : Activer l'environnement virtuel

```powershell
cd C:\Users\LENOVO\Downloads\odg-preview-main\odg-preview-main\backend

# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Si erreur de politique, exécuter d'abord :
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Étape 2 : Installer les dépendances (version Windows)

```powershell
# Installation depuis requirements_windows.txt (sans GDAL)
pip install -r requirements_windows.txt
```

**Sortie attendue** : Toutes les dépendances s'installent sans erreur ✅

### Étape 3 : Vérifier l'installation

```powershell
python -c "import simplekml; print('✅ KML export OK')"
python -c "import gpxpy; print('✅ GPX export OK')"
python -c "import shapely; print('✅ Shapely OK')"
python -c "from src.services.geospatial_export import GeospatialExportService; print('✅ Export service OK')"
```

### Étape 4 : Lancer le serveur

```powershell
python run_server.py
```

**Accès** : http://localhost:5000

---

## 📊 Formats d'Export Disponibles

### ✅ Formats Fonctionnels (Sans GDAL)

| Format | Statut | Usage |
|--------|--------|-------|
| **GeoJSON** | ✅ Actif | Web, Leaflet, APIs |
| **KML** | ✅ Actif | Google Earth Desktop/Web |
| **KMZ** | ✅ Actif | Google Earth (compressé) |
| **CSV** | ✅ Actif | Excel, analyses |
| **WKT** | ✅ Actif | PostgreSQL, bases de données |
| **GPX** | ✅ Actif | GPS, randonnée |

### ⚠️ Format Optionnel (Nécessite GDAL)

| Format | Statut | Solution |
|--------|--------|----------|
| **Shapefile** | ⚠️ Optionnel | Voir section ci-dessous |

---

## 🔧 Installation Complète avec Shapefile (Optionnel)

Si vous avez **absolument besoin** d'exporter en Shapefile ESRI :

### Option 1 : Wheels Pré-compilés Gohlke (Recommandé)

1. **Télécharger les wheels depuis** : https://www.lfd.uci.edu/~gohlke/pythonlibs/

2. **Identifier votre version Python** :
   ```powershell
   python --version  # Ex: Python 3.11.x
   python -c "import struct; print(struct.calcsize('P') * 8)"  # Ex: 64 bits
   ```

3. **Télécharger dans l'ordre** :
   - `GDAL-3.8.3-cp311-cp311-win_amd64.whl` (adapter cp311 à votre version)
   - `Fiona-1.9.5-cp311-cp311-win_amd64.whl`
   - `rasterio-1.3.9-cp311-cp311-win_amd64.whl`

4. **Installer dans l'ordre** :
   ```powershell
   cd C:\Users\LENOVO\Downloads  # Dossier où vous avez téléchargé les .whl
   
   pip install GDAL-3.8.3-cp311-cp311-win_amd64.whl
   pip install Fiona-1.9.5-cp311-cp311-win_amd64.whl
   pip install rasterio-1.3.9-cp311-cp311-win_amd64.whl
   pip install geopandas==1.1.1
   ```

5. **Vérifier** :
   ```powershell
   python -c "import fiona; print('✅ Fiona OK, version:', fiona.__version__)"
   python -c "import geopandas; print('✅ GeoPandas OK')"
   ```

### Option 2 : Conda (Alternative)

```powershell
# Installer Miniconda : https://docs.conda.io/en/latest/miniconda.html

# Créer environnement conda
conda create -n odg python=3.11
conda activate odg

# Installer GDAL via conda-forge
conda install -c conda-forge gdal fiona geopandas

# Installer le reste
pip install -r requirements_windows.txt
```

---

## 🧪 Tests de Validation

### Test 1 : Export KML (Google Earth)

```powershell
# Lancer le serveur dans un terminal
python run_server.py

# Dans un autre terminal PowerShell
curl.exe -X GET "http://localhost:5000/api/geospatial/layers/1/export/kml" -o test.kml

# Ouvrir avec Google Earth
start test.kml
```

### Test 2 : Export CSV (Excel)

```powershell
curl.exe -X GET "http://localhost:5000/api/geospatial/layers/1/export/csv" -o test.csv

# Ouvrir avec Excel
start test.csv
```

### Test 3 : Export GPX (GPS)

```powershell
curl.exe -X GET "http://localhost:5000/api/geospatial/layers/1/export/gpx" -o test.gpx

# Vérifier le contenu
Get-Content test.gpx
```

### Test 4 : Export Batch

```powershell
# Créer un fichier JSON de test
@"
{
  "layer_ids": [1, 2, 3],
  "format": "kml"
}
"@ | Out-File -Encoding utf8 batch_request.json

# Envoyer la requête
curl.exe -X POST "http://localhost:5000/api/geospatial/export-batch" `
  -H "Content-Type: application/json" `
  -d "@batch_request.json" `
  -o batch_export.zip

# Extraire le ZIP
Expand-Archive -Path batch_export.zip -DestinationPath batch_export
Get-ChildItem batch_export
```

---

## 🚨 Dépannage

### Problème : "pip n'est pas reconnu"

**Solution** : L'environnement virtuel n'est pas activé

```powershell
cd backend
.\venv\Scripts\Activate.ps1
# Vous devriez voir (venv) au début de la ligne
```

### Problème : "Impossible de charger le fichier Activate.ps1"

**Solution** : Politique d'exécution PowerShell

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problème : "Module simplekml non trouvé"

**Solution** : Réinstaller les dépendances

```powershell
pip install --upgrade simplekml gpxpy lxml
```

### Problème : "Export Shapefile retourne erreur"

**Cause** : GDAL/Fiona non installés (normal sans installation complète)

**Solution** : 
1. **Option A** : Utiliser les autres formats (KML, CSV, GeoJSON)
2. **Option B** : Installer GDAL via wheels Gohlke (voir ci-dessus)

---

## ✅ Checklist de Validation

Après installation, vérifier :

- [ ] Environnement virtuel activé `(venv)` visible
- [ ] `python --version` retourne Python 3.11+
- [ ] `pip list` montre Flask, simplekml, gpxpy
- [ ] Serveur démarre : `python run_server.py`
- [ ] API répond : http://localhost:5000/api/dashboard/summary
- [ ] Export KML fonctionne (test curl)
- [ ] Export CSV fonctionne (test curl)

---

## 📊 Résumé des Capacités

### ✅ Ce qui fonctionne SANS GDAL :

- ✅ **Import** de données (déjà dans le code existant)
- ✅ **Stockage** PostGIS avec géométries
- ✅ **Affichage** sur carte Leaflet
- ✅ **Export** : GeoJSON, KML, KMZ, CSV, WKT, GPX (6 formats)
- ✅ **Analyses** spatiales PostGIS
- ✅ **API** REST complète

### ⚠️ Ce qui nécessite GDAL (optionnel) :

- ⚠️ **Export Shapefile** ESRI (.shp)
- ⚠️ **Import raster** TIFF (déjà désactivé si besoin)

**Conclusion** : Le système est **pleinement fonctionnel** pour 95% des cas d'usage, même sans Shapefile !

---

## 🎯 Prochaines Étapes

Une fois le serveur lancé :

1. **Frontend** : Ouvrir http://localhost:5173 (si frontend démarré)
2. **Tests API** : Utiliser Postman ou curl pour tester les exports
3. **Documentation** : Consulter `TECH_LEAD_ANALYSIS_COMPLETE.md`
4. **Validation** : Tester l'export KML dans Google Earth

---

## 📞 Support

**Documentation complète** :
- `TECH_LEAD_ANALYSIS_COMPLETE.md` - Analyse détaillée
- `GUIDE_INSTALLATION_CORRECTIFS.md` - Guide général
- `RESUME_EXECUTIF_TECH_LEAD.md` - Résumé exécutif

**Commandes utiles** :
```powershell
# Voir les packages installés
pip list

# Voir les logs du serveur
python run_server.py  # Logs en console

# Tester une route API
curl.exe http://localhost:5000/api/geospatial/supported-formats
```

---

**Version** : 1.0 Windows  
**Date** : 14 janvier 2026  
**Testé sur** : Windows 10/11, Python 3.11+
