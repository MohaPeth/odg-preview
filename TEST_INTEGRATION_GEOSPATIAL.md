# 🧪 Test d'Intégration - Fonctionnalité Géospatiale ODG

## 📋 Vue d'Ensemble

Ce document décrit les tests à effectuer pour valider l'intégration complète de la fonctionnalité d'import géospatial dans l'application ODG.

## ✅ Phase 2 Frontend - TERMINÉE

### **Composants Créés**
- ✅ `AddGeospatialLayerModal.jsx` - Modal d'ajout avec workflow en 3 étapes
- ✅ `FileUploadZone.jsx` - Zone d'upload avec drag & drop
- ✅ `LayersManagementTable.jsx` - Tableau de gestion complet
- ✅ `DynamicLayerRenderer.jsx` - Rendu dynamique sur Leaflet
- ✅ `geospatialApi.js` - Services API et hooks React
- ✅ `WebGISMap.jsx` - Intégration avec système d'onglets

## 🚀 Tests à Effectuer

### **1. Test Backend (Phase 1)**

#### **1.1 Installation des Dépendances**
```bash
cd backend
pip install -r requirements.txt
```

**Vérifications :**
- [ ] Installation de `geoalchemy2==0.14.2`
- [ ] Installation de `lxml==4.9.3`
- [ ] Installation de `rasterio==1.3.9`
- [ ] Installation de `psycopg2-binary==2.9.9`

#### **1.2 Test du Service d'Import**
```bash
cd backend
python test_geospatial_import.py
```

**Résultats attendus :**
- [ ] ✅ Validation des fichiers
- [ ] ✅ Import GeoJSON
- [ ] ✅ Import CSV
- [ ] ✅ Import KML
- [ ] ✅ Import TXT
- [ ] ✅ Historique des uploads

#### **1.3 Test des Modèles PostGIS**
```bash
cd backend
python test_geospatial_setup.py
```

**Résultats attendus :**
- [ ] ✅ Création des modèles
- [ ] ✅ Opérations géospatiales
- [ ] ✅ Méthodes du modèle
- [ ] ✅ Historique des uploads

#### **1.4 Test des APIs REST**
```bash
cd backend
python src/main.py
```

**Endpoints à tester :**
- [ ] `POST /api/geospatial/upload` - Upload de fichiers
- [ ] `GET /api/geospatial/layers` - Liste des couches
- [ ] `GET /api/geospatial/layers/:id` - Détail d'une couche
- [ ] `PUT /api/geospatial/layers/:id` - Mise à jour
- [ ] `DELETE /api/geospatial/layers/:id` - Suppression
- [ ] `GET /api/geospatial/statistics` - Statistiques
- [ ] `GET /api/geospatial/supported-formats` - Formats supportés

### **2. Test Frontend (Phase 2)**

#### **2.1 Démarrage de l'Application**
```bash
cd frontend
npm install
npm run dev
```

**Vérifications :**
- [ ] Application démarre sans erreur
- [ ] Onglet "Couches" visible dans WebGIS
- [ ] Bouton "Importer une couche" fonctionnel

#### **2.2 Test du Modal d'Import**
**Actions à tester :**
- [ ] Clic sur "Importer une couche"
- [ ] Modal s'ouvre avec 3 étapes
- [ ] Étape 1 : Zone de drag & drop fonctionnelle
- [ ] Étape 2 : Configuration de la couche
- [ ] Étape 3 : Confirmation et import

#### **2.3 Test de la Zone d'Upload**
**Formats à tester :**
- [ ] Glisser-déposer un fichier GeoJSON
- [ ] Glisser-déposer un fichier CSV
- [ ] Glisser-déposer un fichier KML
- [ ] Validation des formats non supportés
- [ ] Validation de la taille de fichier

#### **2.4 Test du Tableau de Gestion**
**Fonctionnalités à tester :**
- [ ] Affichage de la liste des couches
- [ ] Recherche par nom
- [ ] Filtrage par type et statut
- [ ] Basculer la visibilité (œil)
- [ ] Menu d'actions (modifier, supprimer, exporter)
- [ ] Pagination si > 10 couches

#### **2.5 Test du Rendu sur Carte**
**Vérifications :**
- [ ] Couches visibles s'affichent sur la carte
- [ ] Styles différents selon le type
- [ ] Popups informatifs au clic
- [ ] Tooltips au survol
- [ ] Highlight au survol

### **3. Test d'Intégration Complète**

#### **3.1 Workflow Complet d'Import**
1. [ ] Créer un fichier GeoJSON de test
2. [ ] L'importer via le modal
3. [ ] Vérifier l'affichage dans le tableau
4. [ ] Vérifier l'affichage sur la carte
5. [ ] Modifier la visibilité
6. [ ] Exporter la couche
7. [ ] Supprimer la couche

#### **3.2 Test avec Différents Formats**
**GeoJSON :**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [9.4536, 0.3901]
      },
      "properties": {
        "name": "Test Point",
        "description": "Point de test"
      }
    }
  ]
}
```

**CSV :**
```csv
name,latitude,longitude,type,description
Test Mine,0.3901,9.4536,Or,Mine de test
```

**KML :**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Test Route</name>
      <LineString>
        <coordinates>9.4536,0.3901,0 9.5,0.4,0</coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>
```

#### **3.3 Test de Performance**
- [ ] Import d'un fichier > 1MB
- [ ] Import avec > 100 features
- [ ] Affichage de > 10 couches simultanément
- [ ] Temps de réponse des APIs < 2s

#### **3.4 Test de Gestion d'Erreurs**
- [ ] Fichier corrompu
- [ ] Format non supporté
- [ ] Fichier trop volumineux
- [ ] Erreur réseau
- [ ] Données géospatiales invalides

### **4. Test de Compatibilité**

#### **4.1 Navigateurs**
- [ ] Chrome (dernière version)
- [ ] Firefox (dernière version)
- [ ] Safari (si disponible)
- [ ] Edge (si disponible)

#### **4.2 Responsive Design**
- [ ] Desktop (1920x1080)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

## 📊 Critères de Validation

### **Critères Obligatoires**
- [ ] Tous les tests backend passent
- [ ] Import de fichiers GeoJSON, CSV, KML fonctionnel
- [ ] Affichage des couches sur la carte
- [ ] Gestion de la visibilité des couches
- [ ] Interface utilisateur intuitive

### **Critères Optionnels**
- [ ] Support des fichiers Shapefile
- [ ] Support des fichiers TIFF
- [ ] Export dans différents formats
- [ ] Édition des propriétés des couches
- [ ] Statistiques avancées

## 🐛 Problèmes Connus et Solutions

### **Problème : Import React manquant**
**Erreur :** `React is not defined`
**Solution :** Ajouter `import React from 'react';` dans les composants

### **Problème : PostGIS non configuré**
**Erreur :** `PostGIS extension not found`
**Solution :** 
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

### **Problème : CORS**
**Erreur :** `CORS policy blocked`
**Solution :** Vérifier la configuration Flask-CORS

### **Problème : Leaflet Icons**
**Erreur :** Icônes manquantes
**Solution :** Configuration des icônes dans WebGISMap.jsx

## 📝 Rapport de Test

### **Environnement de Test**
- **OS :** Windows
- **Node.js :** v18+
- **Python :** v3.8+
- **Navigateur :** Chrome
- **Base de données :** SQLite (dev) / PostgreSQL (prod)

### **Résultats**
| Test | Statut | Commentaires |
|------|--------|--------------|
| Backend APIs | ⏳ En cours | |
| Frontend Components | ⏳ En cours | |
| Integration | ⏳ En cours | |
| Performance | ⏳ En attente | |
| Compatibility | ⏳ En attente | |

### **Bugs Identifiés**
| ID | Description | Priorité | Statut |
|----|-------------|----------|--------|
| - | - | - | - |

### **Améliorations Suggérées**
- [ ] Ajout d'un indicateur de progression pour gros fichiers
- [ ] Preview des données avant import
- [ ] Validation côté client plus poussée
- [ ] Cache des couches pour améliorer les performances
- [ ] Support du clustering pour les points nombreux

## 🎯 Prochaines Étapes

1. **Phase 3 : Tests et Validation** (en cours)
2. **Phase 4 : Fonctionnalités Avancées**
   - Export multi-formats
   - Édition de couches
   - Styles personnalisés
   - Analyse spatiale
3. **Phase 5 : Optimisation et Déploiement**
   - Optimisation des performances
   - Tests de charge
   - Documentation utilisateur
   - Déploiement en production

---

**Dernière Mise à Jour :** 17 novembre 2025, 16:30  
**Version :** 2.0  
**Statut :** 🧪 Phase 2 Terminée - Tests en cours
