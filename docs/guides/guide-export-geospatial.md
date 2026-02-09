# 🌍 Export des Données Géospatiales - Configuration Terminée

## ✅ Problèmes Résolus

### 1. **Support GeoJSON Complet**
Les modèles `MiningDeposit`, `ExploitationArea`, et `Infrastructure` ont maintenant des méthodes `to_geojson_feature()` qui génèrent des Features GeoJSON valides :

```python
# Exemple pour un gisement (Point)
{
  "type": "Feature",
  "id": 1,
  "geometry": {
    "type": "Point",
    "coordinates": [longitude, latitude]  # Format GeoJSON: [lon, lat]
  },
  "properties": {
    "id": 1,
    "name": "Gisement d'Or",
    "type": "Or",
    "company": "Mining Corp",
    "status": "Actif",
    ...
  }
}
```

### 2. **Endpoints d'Export Créés**

| Endpoint | Format | Description |
|----------|--------|-------------|
| `/api/webgis/deposits/export/geojson` | GeoJSON | Tous les gisements en GeoJSON |
| `/api/webgis/deposits/export/kml` | KML | Gisements pour Google Earth |
| `/api/webgis/deposits/export/kmz` | KMZ | Gisements compressés pour GE |
| `/api/webgis/deposits/export/csv` | CSV | Données tabulaires avec coordonnées |
| `/api/webgis/exploitation-areas/export/geojson` | GeoJSON | Zones d'exploitation (polygones) |
| `/api/webgis/infrastructure/export/geojson` | GeoJSON | Infrastructures (lignes) |
| `/api/webgis/geojson/deposits` | GeoJSON | Pour affichage sur carte |
| `/api/webgis/geojson/exploitation-areas` | GeoJSON | Zones pour affichage carte |

### 3. **Compatibilité SQLite et PostGIS**

- **Actuellement (SQLite)** : Les géométries sont générées dynamiquement à partir des coordonnées JSON
- **Futur (PostgreSQL + PostGIS)** : Les colonnes `geom` pourront être ajoutées pour de meilleures performances

## 🚀 Comment Utiliser

### Depuis l'API (curl/Postman)

```bash
# Télécharger tous les gisements en GeoJSON
curl http://localhost:5000/api/webgis/deposits/export/geojson -o deposits.geojson

# Télécharger en KML pour Google Earth
curl http://localhost:5000/api/webgis/deposits/export/kml -o deposits.kml

# Télécharger en CSV
curl http://localhost:5000/api/webgis/deposits/export/csv -o deposits.csv
```

### Depuis le Frontend (React)

```javascript
// Télécharger en GeoJSON
const downloadGeoJSON = async () => {
  const response = await fetch('http://localhost:5000/api/webgis/deposits/export/geojson');
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'deposits.geojson';
  a.click();
};

// Charger pour affichage sur carte Leaflet
const loadDepositsOnMap = async () => {
  const response = await fetch('http://localhost:5000/api/webgis/geojson/deposits');
  const geojson = await response.json();
  
  L.geoJSON(geojson, {
    pointToLayer: (feature, latlng) => {
      return L.marker(latlng);
    },
    onEachFeature: (feature, layer) => {
      layer.bindPopup(`<b>${feature.properties.name}</b><br>${feature.properties.type}`);
    }
  }).addTo(map);
};
```

### Affichage dans QGIS

1. **Télécharger le GeoJSON** :
   ```bash
   curl http://localhost:5000/api/webgis/deposits/export/geojson -o deposits.geojson
   ```

2. **Ouvrir dans QGIS** :
   - Couche → Ajouter une couche → Ajouter une couche vecteur
   - Sélectionner `deposits.geojson`
   - La couche s'affiche avec tous les attributs

### Affichage dans Google Earth

1. **Télécharger le KML** :
   ```bash
   curl http://localhost:5000/api/webgis/deposits/export/kml -o deposits.kml
   ```

2. **Ouvrir dans Google Earth** :
   - Double-cliquer sur `deposits.kml`
   - Les gisements apparaissent avec leurs informations

## 📝 Formats de Coordonnées

### MiningDeposit (Points)
```python
# Format stocké
latitude = -0.8037  # Latitude Gabon
longitude = 11.6094  # Longitude Gabon

# Format GeoJSON généré
{
  "type": "Point",
  "coordinates": [11.6094, -0.8037]  # [lon, lat]
}
```

### ExploitationArea (Polygones)
```python
# Format stocké (JSON)
coordinates = [
  [-0.8037, 11.6094],  # [lat, lon]
  [-0.8047, 11.6104],
  [-0.8057, 11.6094],
  [-0.8037, 11.6094]   # Fermé
]

# Format GeoJSON généré
{
  "type": "Polygon",
  "coordinates": [[
    [11.6094, -0.8037],  # [lon, lat]
    [11.6104, -0.8047],
    [11.6094, -0.8057],
    [11.6094, -0.8037]
  ]]
}
```

### Infrastructure (Lignes)
```python
# Format stocké (JSON)
coordinates = [
  [-0.8037, 11.6094],
  [-0.8047, 11.6104],
  [-0.8057, 11.6114]
]

# Format GeoJSON généré
{
  "type": "LineString",
  "coordinates": [
    [11.6094, -0.8037],
    [11.6104, -0.8047],
    [11.6114, -0.8057]
  ]
}
```

## 🗺️ Intégration avec les Cartes

### Leaflet
```javascript
// Charger et afficher automatiquement
fetch('/api/webgis/geojson/deposits')
  .then(res => res.json())
  .then(data => {
    L.geoJSON(data).addTo(map);
  });
```

### Mapbox GL JS
```javascript
map.addSource('deposits', {
  type: 'geojson',
  data: '/api/webgis/geojson/deposits'
});

map.addLayer({
  id: 'deposits-layer',
  type: 'circle',
  source: 'deposits',
  paint: {
    'circle-radius': 6,
    'circle-color': '#FFD700'
  }
});
```

### OpenLayers
```javascript
const vectorSource = new ol.source.Vector({
  url: '/api/webgis/geojson/deposits',
  format: new ol.format.GeoJSON()
});

const vectorLayer = new ol.layer.Vector({
  source: vectorSource
});

map.addLayer(vectorLayer);
```

## 🔄 Migration Future vers PostgreSQL/PostGIS

Quand vous migrerez vers PostgreSQL :

1. **Activer PostGIS** :
   ```sql
   CREATE EXTENSION postgis;
   ```

2. **Exécuter la migration** :
   ```bash
   psql -d odg_database -f backend/src/migrations/add_geometry_to_mining_tables.sql
   ```

3. **Les colonnes geom seront automatiquement remplies** via triggers

4. **Performance améliorée** :
   - Index spatiaux GIST
   - Requêtes spatiales (proximité, intersection, etc.)
   - Fonctions PostGIS (buffer, union, simplify, etc.)

## ✅ Checklist de Vérification

- [x] Modèles mis à jour avec méthodes `to_geojson_feature()`
- [x] Endpoints d'export créés et fonctionnels
- [x] Compatible avec SQLite (pas besoin de PostGIS)
- [x] Format GeoJSON valide selon RFC 7946
- [x] Coordonnées au bon format [longitude, latitude]
- [x] Export CSV avec toutes les données
- [x] Export KML/KMZ pour Google Earth
- [x] Prêt pour migration PostGIS future

## 🎯 Prochaines Étapes

1. **Tester les endpoints** avec des données réelles
2. **Créer des boutons d'export** dans le frontend
3. **Ajouter des filtres** (par statut, type, entreprise)
4. **Implémenter l'export par sélection** (IDs spécifiques)
5. **Planifier la migration vers PostgreSQL** si nécessaire

## 📚 Documentation Technique

- [GeoJSON RFC 7946](https://tools.ietf.org/html/rfc7946)
- [PostGIS Documentation](https://postgis.net/docs/)
- [Leaflet GeoJSON Tutorial](https://leafletjs.com/examples/geojson/)
- [QGIS GeoJSON Support](https://docs.qgis.org/latest/en/docs/user_manual/managing_data_source/supported_data.html#geojson)
