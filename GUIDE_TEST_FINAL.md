# 🧪 GUIDE DE TEST - ODG WebGIS

## ✅ Serveurs en ligne

- **Backend Flask** : http://localhost:5000 ✅
- **Frontend Vite** : http://localhost:5173 ✅

## 🔍 Tests à effectuer

### 1. Ouvrir le navigateur

```
http://localhost:5173
```

### 2. Ouvrir la console développeur (F12)

**Appuyez sur F12** et allez dans l'onglet **Console**

### 3. Logs à observer

Vous devriez voir dans la console :

#### A. Logs d'appel API :
```
📡 [ApiClient] Requête: http://localhost:5173/api/geospatial/layers?page=1&per_page=20&include_geojson=false
📡 [ApiClient] Status: 200 OK
📡 [ApiClient] Données reçues: { success: true, data: [...], pagination: {...} }
```

#### B. Logs de fetchLayers :
```
🔄 [fetchLayers] Appel API avec filtres: {...}
✅ [fetchLayers] Réponse API reçue: {...}
✅ [fetchLayers] Données extraites: Array(2)
✅ [fetchLayers] Nombre de couches: 2
```

#### C. Logs de WebGISMap :
```
🗺️ [DEBUG] Couches géospatiales: Array(2)
🗺️ [DEBUG] Nombre de couches: 2
🗺️ [DEBUG] Couches visibles: Array(1 ou 2)
```

#### D. Logs du renderer (si couches visibles) :
```
🎨 [DynamicLayerRenderer] Création couche: "Couche Geojson" ID: 23
🎨 [DynamicLayerRenderer] Visible: true
🎨 [DynamicLayerRenderer] Réponse API pour couche 23: {...}
✅ [DynamicLayerRenderer] GeoJSON récupéré: {...}
```

### 4. Si vous voyez des erreurs

#### Erreur : "❌ Backend indisponible"
→ Le backend ne répond pas. Vérifiez que http://localhost:5000 fonctionne

#### Erreur : "Nombre de couches: 0"
→ L'API retourne un tableau vide. Vérifiez PostgreSQL

#### Erreur : "data is undefined"
→ Le format de réponse n'est pas celui attendu

### 5. Tests visuels

Dans l'interface :

1. **Allez dans l'onglet "Couches"** (sidebar gauche)
2. **Vérifiez les statistiques** :
   - Devrait afficher "2 couches totales" (ou plus si vous en avez créé)
   - "X visibles" • "Y masquées"

3. **Regardez la carte** :
   - Les couches visibles devraient apparaître
   - Cliquez sur "œil" pour toggle la visibilité
   - Les marqueurs devraient avoir des icônes emoji (⛏️, 🏗️, 🗺️)

### 6. Test de création

1. Cliquez sur "Ajouter une couche"
2. Importez un fichier GeoJSON
3. Vérifiez que la nouvelle couche apparaît dans la liste

## 🐛 Problèmes connus résolus

✅ Leaflet CSS bloqué par Tracking Prevention → **Résolu** (importé localement)
✅ Hauteur de carte 0px → **Résolu** (min-height: 400px)
✅ `.env` non chargé → **Résolu** (dotenv ajouté)
✅ SQLite au lieu de PostgreSQL → **Résolu** (DATABASE_URL chargée)

## 📋 Que m'envoyer

**Copiez-collez les logs de la console** et dites-moi :

1. Combien de couches s'affichent dans les stats ?
2. Voyez-vous des marqueurs sur la carte ?
3. Y a-t-il des erreurs en rouge dans la console ?

---

**Dernière mise à jour** : 21/01/2026 01:50
