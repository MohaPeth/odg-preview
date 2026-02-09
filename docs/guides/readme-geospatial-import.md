# 🗺️ Module d'Import Géospatial ODG

## 📋 Vue d'Ensemble

Ce module permet l'ajout dynamique de nouvelles couches géospatiales au système ODG (Ogooué Digital Gold). Il supporte l'import de fichiers dans différents formats et leur intégration dans la base PostGIS pour affichage sur la carte Leaflet.

## ✅ Phase 1.1 - TERMINÉE ✅

### **Fonctionnalités Implémentées**

#### 🏗️ **Modèle de Données PostGIS**
- **Table `geospatial_layers`** : Stockage des couches géospatiales
- **Table `layer_upload_history`** : Historique des imports
- **Support géométries** : POINT, LINESTRING, POLYGON, MULTI*
- **Métadonnées JSON** : Configuration styles et propriétés
- **Statistiques automatiques** : Superficie, longueur, nombre de points

#### 🔧 **Infrastructure Backend**
- **Modèle SQLAlchemy** avec GeoAlchemy2
- **Triggers PostGIS** pour calculs automatiques
- **Index spatiaux** pour performances optimales
- **Vues SQL** pour requêtes fréquentes
- **Fonctions spatiales** intégrées

#### 🧪 **Tests et Validation**
- **Script de test complet** : `test_geospatial_setup.py`
- **Données de test** : 3 couches géospatiales du Gabon
- **Validation PostGIS** : Vérification des extensions
- **Tests des méthodes** : CRUD et conversions

## 📁 Fichiers Créés

```
backend/
├── src/
│   ├── models/
│   │   └── geospatial_layers.py      ✅ Modèles PostGIS
│   └── migrations/
│       └── create_geospatial_tables.sql ✅ Migration complète
├── test_geospatial_setup.py          ✅ Tests de validation
└── requirements.txt                   ✅ Dépendances mises à jour
```

## 🚀 Installation et Configuration

### **1. Dépendances Python**
```bash
# Installation des nouvelles dépendances
pip install geoalchemy2==0.14.2 lxml==4.9.3 rasterio==1.3.9 psycopg2-binary==2.9.9
```

### **2. Configuration PostgreSQL/PostGIS**
```sql
-- Exécuter la migration
psql -d odg_database -f backend/src/migrations/create_geospatial_tables.sql
```

### **3. Tests de Validation**
```bash
# Tester l'installation
cd backend
python test_geospatial_setup.py
```

## 📊 Données de Test Incluses

### **Couches Géospatiales du Gabon**
1. **Points d'Intérêt Libreville** (POINT)
   - Coordonnées : 9.4536°E, 0.3901°N
   - Type : Points d'intérêt urbains

2. **Route Nationale N1** (LINESTRING) 
   - Tracé : Libreville → Lambaréné
   - Longueur : ~450 km

3. **Parc National de la Lopé** (POLYGON)
   - Superficie : 4,970 km²
   - Statut : Zone protégée UNESCO

## 🔧 Utilisation du Modèle

### **Création d'une Couche**
```python
from src.models.geospatial_layers import GeospatialLayer
from geoalchemy2.functions import ST_GeomFromText

# Nouveau point d'intérêt
layer = GeospatialLayer(
    name="Nouveau Gisement",
    description="Gisement aurifère découvert",
    layer_type="deposit",
    geometry_type="POINT", 
    source_format="GPS",
    status="exploration",
    geom=ST_GeomFromText('POINT(10.5 -1.2)', 4326)
)

# Style automatique selon le type
layer.set_default_style_by_type()

# Sauvegarde avec calcul automatique des stats
db.session.add(layer)
db.session.commit()
```

### **Recherche Spatiale**
```python
# Recherche par zone géographique
layers_in_bounds = search_layers_within_bounds(
    min_lat=-1.0, min_lon=9.0,
    max_lat=1.0, max_lon=11.0
)

# Recherche par nom
results = GeospatialLayer.search_by_name("Libreville")

# Filtrage par statut
active_layers = GeospatialLayer.get_by_status("actif")
```

### **Export GeoJSON**
```python
# Conversion en GeoJSON Feature
feature = layer.to_geojson_feature()
print(json.dumps(feature, indent=2))
```

## 📈 Performances et Optimisations

### **Index Spatiaux**
- **GIST Index** sur la colonne `geom`
- **Index B-Tree** sur `name`, `layer_type`, `status`
- **Index GIN** sur les colonnes JSONB

### **Statistiques Automatiques**
- **Superficie** calculée automatiquement (km²)
- **Longueur** calculée pour les lignes (km)
- **Comptage** des points pour MultiPoint

### **Vues Optimisées**
- `active_geospatial_layers` : Couches visibles
- `layer_statistics_by_type` : Statistiques agrégées

## 🎯 Prochaines Étapes (Phase 1.2)

### **Service d'Import de Fichiers**
- [ ] Parser KML/KMZ (Google Earth)
- [ ] Parser Shapefile (ESRI)
- [ ] Parser GeoJSON (standard web)
- [ ] Parser CSV avec coordonnées
- [ ] Parser TXT (coordonnées brutes)
- [ ] Support TIFF (rasters)

### **APIs REST**
- [ ] `POST /api/geospatial/upload` - Upload de fichiers
- [ ] `GET /api/geospatial/layers` - Liste des couches
- [ ] `DELETE /api/geospatial/layers/:id` - Suppression
- [ ] `GET /api/geospatial/export/:id/:format` - Export

## 🔍 Formats Supportés (Prévus)

| Format | Extension | Description | Statut |
|--------|-----------|-------------|---------|
| KML | `.kml` | Google Earth | 🔄 En cours |
| KMZ | `.kmz` | KML compressé | 🔄 En cours |
| Shapefile | `.shp` (via ZIP) | ESRI Standard | ✅ Via archive ZIP |
| GeoJSON | `.geojson` | JSON géospatial | 🔄 En cours |
| CSV | `.csv` | Coordonnées tabulaires | 🔄 En cours |
| TXT | `.txt` | Coordonnées brutes | 🔄 En cours |
| TIFF | `.tiff` | Images géoréférencées | 🔄 En cours |

### **Import Shapefile (SHP)**
Un shapefile est un **ensemble de fichiers** (.shp, .shx, .dbf, optionnellement .prj). L’upload n’accepte qu’un seul fichier à la fois. Pour importer un shapefile :
- **Recommandé** : déposez une **archive ZIP** contenant au minimum les fichiers `.shp`, `.shx` et `.dbf` (même nom de base, ex. `couche.shp`, `couche.shx`, `couche.dbf`).
- Si vous uploadez uniquement le fichier `.shp`, l’import échouera car les fichiers compagnons sont requis.

## 🚨 Notes Importantes

### **Configuration PostGIS Requise**
- Cette fonctionnalité nécessite **PostgreSQL avec PostGIS**
- SQLite n'est **pas supporté** pour les géométries
- Extensions requises : `postgis`, `postgis_topology`

### **Projections Géographiques**
- **Système de référence** : WGS84 (EPSG:4326)
- **Reprojection automatique** des fichiers sources
- **Validation** des géométries à l'import

### **Limites de Performance**
- **Fichiers volumineux** : Pagination recommandée
- **Géométries complexes** : Simplification possible
- **Index spatiaux** : Essentiels pour les performances

## 📞 Support Technique

### **Dépannage Courant**

#### Erreur PostGIS
```
ERROR: PostGIS extension not found
```
**Solution** : Installer PostGIS
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

#### Erreur GeoAlchemy2
```
ImportError: No module named 'geoalchemy2'
```
**Solution** : Installer la dépendance
```bash
pip install geoalchemy2==0.14.2
```

#### Erreur de Géométrie
```
ERROR: Invalid geometry
```
**Solution** : Vérifier le format WKT/coordonnées

### **Logs de Debug**
```python
# Activation des logs SQLAlchemy
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

---

**Auteur** : Équipe ODG  
**Version** : 1.1  
**Date** : 17 novembre 2025  
**Statut** : ✅ Phase 1.1 Terminée - Prêt pour Phase 1.2
