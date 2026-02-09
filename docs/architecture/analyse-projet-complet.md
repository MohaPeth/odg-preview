# Analyse complète du projet ODG (Ogooué Digital Gold)

**Date :** 4 février 2026  
**Branche analysée :** master

---

## 1. Vue d’ensemble

**ODG** est une plateforme web full-stack pour la gestion et la traçabilité des ressources minières au Gabon. Elle combine :

- **WebGIS** : couches géospatiales, gisements, zones d’exploitation, infrastructures
- **Blockchain** : enregistrement des transactions de traçabilité (mode simulation par défaut)
- **Gestion des acteurs** : utilisateurs (admin / opérateur / partenaire), opérateurs miniers

---

## 2. Stack technique

| Couche      | Technologies |
|------------|--------------|
| **Backend** | Flask 3.1.1, SQLAlchemy 2.0, PostgreSQL 15+ (PostGIS), Python 3.x |
| **Frontend** | React 19, Vite 6, TailwindCSS 4, shadcn/ui (Radix), Leaflet / react-leaflet |
| **Blockchain** | Solidity (ODGTraceability.sol), web3.py 6.15, eth-account (mode simulation si non configuré) |
| **Géospatial** | GeoAlchemy2, Fiona, Shapely, GeoPandas, Rasterio, simplekml, gpxpy |
| **Charts** | Recharts |

---

## 3. Architecture backend

### 3.1 Point d’entrée

- **`backend/src/main.py`** : factory Flask `create_app()`, chargement du `.env`, enregistrement des blueprints, `db.create_all()`, données de test dans `init_database()`.
- **`backend/run_server.py`** : serveur de développement.
- **`backend/wsgi.py`** : entrée Gunicorn pour la production.

### 3.2 Blueprints enregistrés (dans `main.py`)

| Préfixe | Blueprint | Fichier | Rôle |
|---------|-----------|---------|------|
| `/api` | `user_bp` | `routes/user.py` | Auth (login), CRUD utilisateurs |
| `/api/webgis` | `webgis_bp` | `routes/webgis.py` | Gisements, zones, infrastructures, couches, export GeoJSON |
| `/api/blockchain` | `blockchain_bp` | `routes/blockchain.py` | CRUD transactions blockchain |
| `/api/blockchain-integration` | `blockchain_integration_bp` | `routes/blockchain_integration.py` | Publication / statut blockchain |
| `/api/dashboard` | `dashboard_bp` | `routes/dashboard.py` | Indicateurs (GET /summary) : gisements, transactions, couches, opérateurs |
| `/api/geospatial` | `geospatial_import_bp` | `routes/geospatial_import.py` | Upload / import KML, SHP (ZIP), GeoJSON, CSV, TXT, TIFF |
| `/api/operators` | `operators_bp` | `routes/operators.py` | CRUD opérateurs |
| `/api/mining` | `mining_import_bp` | `routes/mining_import.py` | Import gisements GeoJSON/CSV |

### 3.3 Gisements et shapefile

- **Gestion des gisements** : CRUD via **webgis** (`/api/webgis/deposits`), import en masse via **mining_import** (`POST /api/mining/import/deposits`). L’ancien module `deposit_endpoints.py` (modèle `MiningDepositGIS`, substances) a été **archivé** dans `backend/_archive/deposit_endpoints_archive.py` (modèles absents, doublon avec webgis + mining_import).
- **Import Shapefile** : un shapefile nécessite plusieurs fichiers (.shp, .shx, .dbf). L’upload n’accepte qu’un fichier ; il faut déposer une **archive ZIP** contenant au minimum .shp, .shx et .dbf. Voir [Import géospatial](guides/readme-geospatial-import.md).

### 3.4 Modèles de données

| Modèle | Fichier | Table | Rôle |
|--------|---------|--------|------|
| **User** | `models/user.py` | `users` | username, email, role (admin/operator/partner), status, operator_id |
| **Operator** | `models/mining_data.py` | `operators` | name, slug, country, status, commodities_json, permits_count |
| **MiningDeposit** | `models/mining_data.py` | `mining_deposits` | name, type, lat/lon, company, estimated_quantity, status |
| **ExploitationArea** | `models/mining_data.py` | `exploitation_areas` | name, company, status, coordinates (JSON), area, extracted_volume |
| **Infrastructure** | `models/mining_data.py` | `infrastructure` | name, type, coordinates (JSON), length, capacity, status |
| **BlockchainTransaction** | `models/mining_data.py` | `blockchain_transactions` | hash, block_number, from/to, material_type, quantity, unit, timestamp, status, metadata_json, deposit_id, operator_id |
| **GeospatialLayer** | `models/geospatial_layers.py` | `geospatial_layers` | name, layer_type, geometry_type, geom (PostGIS), style_config, layer_metadata, statuts |
| **LayerUploadHistory** | `models/geospatial_layers.py` | `layer_upload_history` | Traçabilité des imports (fichier, statut, feature_count, etc.) |

- **PostGIS** : optionnel ; si absent (ex. SQLite), `USE_POSTGIS = False` dans `mining_data.py`, et les couches géospatiales PostGIS ne sont pas utilisées.
- **User** : pas de champ `password_hash` ; l’auth est uniquement par email (aucune vérification de mot de passe).

### 3.5 Configuration

- **`config_production.py`** : `ProductionConfig` et `DevelopmentConfig`, `get_config()` selon `FLASK_ENV`, `validate_production_config()` (SECRET_KEY, DATABASE_URL, CORS_ORIGINS).
- **`.env`** : DATABASE_URL, SECRET_KEY, FLASK_ENV, CORS_ORIGINS, BLOCKCHAIN_* (RPC, private key, contract, network, etc.).

---

## 4. Architecture frontend

### 4.1 Entrée et routage métier

- **`App.jsx`** : état auth via `localStorage` (`odg_user`). Si connecté : `PartnerDashboard` (role `partner`) ou `MainApp` (admin/operator). Sinon : `Login`.
- **`main.jsx`** : point d’entrée React ; pas de React Router dans le flux actuel (tout géré par onglets dans `MainApp`).

### 4.2 Composants principaux

| Composant | Rôle |
|-----------|------|
| **Login** | Formulaire email → appel `/api/auth/login`, stockage du profil |
| **MainApp** | Onglets : Accueil, Géoportail, Couches, Blockchain, Analyses, Partenaires, Utilisateurs, Paramètres |
| **PartnerDashboard** | Vue partenaire (lecture seule) |
| **WebGISMap** | Carte Leaflet : gisements, zones, infrastructures, couches dynamiques |
| **BlockchainDashboard** | Transactions et indicateurs blockchain |
| **LayersWorkspace** | Gestion des couches géospatiales (liste, upload, modal) |
| **UserManagement** | CRUD utilisateurs |
| **PartnersManagement** | Gestion partenaires (liste dérivée des users role=partner) |
| **SettingsWorkspace** | Paramètres applicatifs |
| **AddDepositModal** / **AddGeospatialLayerModal** | Création gisement / couche |

### 4.3 Services API

- **`api.js`** : `ApiService` (getLayers, getDeposits, createDeposit, getDepositDetails, getCommunities, searchLocations, getStatistics, getSubstances) + hook `useNotifications` + `GeoUtils`. **URL en dur** : `http://localhost:5000/api/webgis` (pas de proxy relatif dans ce fichier).
- **`geospatialApi.js`** : appels couches géospatiales / import.
- **`blockchainApi.js`** : transactions et intégration blockchain.
- **`operatorsApi.js`** : CRUD opérateurs.
- **`usersApi.js`** : utilisateurs et auth.

- **Vite** : proxy `/api` → `http://localhost:5000` dans `vite.config.js`. Les appels en `/api/...` depuis le front sont bien proxifiés ; les appels en `http://localhost:5000/...` dans `api.js` contournent le proxy.

### 4.4 UI

- **shadcn/ui** : nombreux composants dans `components/ui/` (Tabs, Card, Button, Dialog, Form, Table, etc.).
- **TailwindCSS 4** via `@tailwindcss/vite`.
- **Lucide React** pour les icônes.

---

## 5. Flux métier principaux

1. **Authentification** : Login par email → `POST /api/auth/login` → pas de mot de passe ; profil stocké en localStorage. Voir [Auth et sécurité](operations/auth-et-securite.md) pour l’état actuel et les recommandations phase 2.
2. **Dashboard** : `GET /api/dashboard/summary` renvoie les indicateurs (gisements actifs, transactions, couches, opérateurs).
3. **WebGIS** : Données depuis `/api/webgis/deposits`, `/areas`, `/infrastructure`, `/layers` ; création gisement via `POST /api/webgis/deposits` ; carte avec Leaflet et couches dynamiques.
4. **Couches** : Upload via `/api/geospatial/upload` ; formats KML, KMZ, SHP, GeoJSON, CSV, TXT, TIFF ; stockage en `geospatial_layers` (PostGIS ou métadonnées GeoJSON).
5. **Blockchain** : Transactions en base ; publication optionnelle vers le smart contract si `BLOCKCHAIN_ENABLED=true` ; sinon mode simulation.
6. **Import gisements** : `POST /api/mining/import/deposits` (GeoJSON) ; mapping explicite GeoJSON → `MiningDeposit` (type, company, estimated_quantity, etc.).

---

## 6. Sécurité

- **Auth** : aucun mot de passe ; login par email uniquement. Pas de JWT/session côté backend pour les routes protégées. Voir [Auth et sécurité](operations/auth-et-securite.md) pour l’état actuel et le plan phase 2 (mot de passe, JWT/session, protection des routes).
- **Autorisation** : pas de middleware par rôle sur les routes ; un client peut appeler n’importe quel endpoint s’il connaît l’API.
- **CORS** : en dev souvent `*` ; en production à restreindre via `CORS_ORIGINS`.
- **Fichiers** : validation (type MIME, extension) dans `geospatial_import` ; `MAX_CONTENT_LENGTH` configuré (50–100 MB).
- **Secrets** : SECRET_KEY et clés blockchain à définir via `.env`, jamais en dur.

---

## 7. Problèmes résolus et points d’attention

### Résolus (implémentation plan cohérence)

- **Dashboard** : `dashboard_bp` est enregistré dans `main.py` ; `GET /api/dashboard/summary` est disponible.
- **Import mining** : mapping explicite `_deposit_data_to_model_kwargs()` dans `mining_import.py` (type, company, estimated_quantity, status).
- **Config** : doublon `app.config.from_object(Config)` supprimé dans `main.py`.
- **deposit_endpoints** : archivé dans `backend/_archive/deposit_endpoints_archive.py` ; gestion gisements via webgis + mining_import.
- **URL frontend** : `api.js` utilise une URL relative `/api/webgis` (plus d’URL absolue localhost).
- **Import SHP** : `_create_geospatial_layer` utilise `layer_metadata` (plus `metadata`) ; message d’erreur SHP indique d’utiliser un ZIP ; doc utilisateur mise à jour (shapefile = ZIP).

### 7.5 Point d’attention : API frontend

- **Fichier** : `frontend/src/services/api.js`
- **État** : URL relative `/api/webgis` en place. Vérifier que les autres services (geospatialApi, blockchainApi, etc.) n’utilisent pas d’URL absolue.

---

## 8. Points forts

- Séparation claire backend (blueprints, modèles, services) / frontend (composants, services API).
- Support multi-formats géospatial (KML, SHP, GeoJSON, CSV, TXT, TIFF) et validation des uploads.
- PostGIS optionnel avec repli possible (SQLite) pour les modèles non géospatiaux.
- Blockchain optionnelle (mode simulation si web3 non configuré).
- Configuration production (validation env, CORS, logging) déjà préparée.
- UI moderne (React 19, Vite, shadcn, Tailwind) et expérience utilisateur soignée.

---

## 9. Recommandations

1. **Enregistrer le blueprint dashboard** pour que l’accueil et les indicateurs fonctionnent.
2. **Corriger le mapping** dans `mining_import._parse_geojson_deposits` pour alimenter correctement `MiningDeposit`.
3. **Ajouter une vraie authentification** : mot de passe (hash), JWT ou sessions, et protéger les routes sensibles par rôle.
4. **Remplacer l’URL absolue** dans `api.js` par une base relative (`/api` ou variable d’env).
5. **Clarifier le rôle de `deposit_endpoints.py`** : intégration ou archivage.
6. **Documenter** les variables d’environnement (déjà partiellement fait dans `.env.example`) et les prérequis PostGIS pour la prod.
7. **Tests** : ajouter des tests unitaires et d’intégration (backend et, si possible, frontend) pour les routes critiques et l’import géospatial/mining.

---

## 10. Résumé des fichiers clés

| Fichier | Rôle |
|---------|------|
| `backend/src/main.py` | Factory Flask, blueprints, init DB, route SPA |
| `backend/config_production.py` | Config dev/prod, validation, logging |
| `backend/src/models/mining_data.py` | Modèles MiningDeposit, ExploitationArea, Infrastructure, BlockchainTransaction, Operator |
| `backend/src/models/user.py` | Modèle User |
| `backend/src/models/geospatial_layers.py` | GeospatialLayer, LayerUploadHistory |
| `backend/src/routes/user.py` | Auth login, CRUD users |
| `backend/src/routes/webgis.py` | Deposits, areas, infrastructure, layers (CRUD + GeoJSON) |
| `backend/src/routes/geospatial_import.py` | Upload et import de fichiers géospatialux |
| `backend/src/routes/mining_import.py` | Import gisements GeoJSON/CSV |
| `backend/src/services/blockchain_service.py` | Connexion Web3 et contrat ODGTraceability |
| `frontend/src/App.jsx` | Auth et choix MainApp / PartnerDashboard |
| `frontend/src/components/MainApp.jsx` | Navigation et contenu par onglet |
| `frontend/vite.config.js` | Proxy `/api` → backend |
| `frontend/src/services/api.js` | Appels WebGIS + notifications + GeoUtils |

---

*Document généré à partir de l’analyse du dépôt (branche master).*
