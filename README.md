# 🌍 ODG - Ogooué Digital Gold Platform

Plateforme WebGIS et blockchain pour la traçabilité des ressources minières du Gabon.

## 📋 Vue d'ensemble

ODG est une plateforme intégrée comprenant :
- **Module WebGIS** : Cartographie interactive avec Leaflet pour visualiser les gisements miniers
- **Module Blockchain** : Traçabilité des transactions via smart contracts (Ethereum/Polygon)
- **Import Géospatial** : Support multi-formats (KML, KMZ, SHP, GeoJSON, CSV, TIFF)
- **API REST** : Backend Flask avec PostgreSQL/PostGIS

## 🚀 Démarrage Rapide

### Prérequis

#### Backend
- Python 3.8+
- PostgreSQL 13+ avec extension PostGIS
- pip

#### Frontend
- Node.js 16+
- pnpm (ou npm)

### Installation

#### 1. Backend

**Variables d'environnement** : le modèle est dans `backend/.env.example`. Créez `backend/.env` en copiant ce fichier, puis éditez (au minimum `DATABASE_URL`, `SECRET_KEY`). Voir [Démarrage développeur](docs/guides/demarrage-developpeur.md) pour le détail.

```bash
cd backend

# Créer environnement virtuel
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Créer .env depuis le modèle (puis éditer DATABASE_URL, SECRET_KEY)
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/macOS

# Base de données : créer la base PostgreSQL + PostGIS (voir docs/operations/installation-postgis-guide.md), puis :
# 1) Appliquer la migration auth (une fois) : exécuter backend/src/migrations/add_password_hash_to_users.sql sur la base (psql, pgAdmin, etc.)
# 2) Initialiser tables et données
python init_production_db.py
# 3) Créer les comptes de test (mot de passe par défaut : odg2025!)
python create_test_users.py

# Lancer le serveur
python run_server.py
```

Le backend sera accessible sur `http://localhost:5000`. Connexion à l'interface : **admin@odg.ga** / **odg2025!** (ou voir `create_test_users.py`).

#### 2. Frontend

```bash
cd frontend

# Installer dépendances
pnpm install  # ou npm install

# Configurer variables d'environnement
cp .env.example .env
# Éditer .env si nécessaire

# Lancer en développement
pnpm dev  # ou npm run dev
```

Le frontend sera accessible sur `http://localhost:5173`

### Démarrage avec Docker (Recommandé pour PostgreSQL)

```bash
# Démarrer PostgreSQL avec PostGIS
docker-compose up -d

# Vérifier que PostgreSQL est prêt
docker-compose ps
```

## 📁 Structure du Projet

```
odg-preview/
├── backend/                    # Backend Flask
│   ├── src/
│   │   ├── models/            # Modèles SQLAlchemy
│   │   ├── routes/            # Endpoints API (user, health, webgis, blockchain, etc.)
│   │   ├── services/          # Logique métier
│   │   ├── auth.py            # Authentification JWT
│   │   ├── limiter.py         # Rate limiting (login)
│   │   └── migrations/       # Scripts SQL (ex. add_password_hash_to_users.sql)
│   ├── _archive/              # Scripts d'installation archivés
│   ├── requirements.txt      # Dépendances Python
│   ├── config_production.py  # Configuration production/dev
│   ├── .env.example           # Template variables d'environnement (copier en .env)
│   ├── run_server.py         # Lancer le serveur de dev
│   ├── create_test_users.py  # Créer les comptes de test (admin, operator, partner)
│   └── init_production_db.py # Initialiser les tables et données
│
├── frontend/                   # Frontend React
│   ├── src/
│   │   ├── components/        # Composants React
│   │   ├── services/          # API clients (authUtils, usersApi, etc.)
│   │   └── hooks/             # React hooks personnalisés
│   ├── package.json
│   └── .env.example           # Template (copier en .env si besoin)
│
├── docs/                       # Documentation
│   ├── README.md              # Index (par où commencer)
│   ├── guides/                # Démarrage, utilisation, tests (développeur)
│   ├── operations/           # Déploiement, auth, PostGIS, Hostinger
│   ├── architecture/         # Analyse technique
│   ├── metier/                # Plans et fonctionnalités
│   └── historique/           # Corrections passées
├── scripts/
│   └── backup_postgres.sh     # Sauvegarde PostgreSQL (prod)
├── docker-compose.yml         # PostgreSQL + PostGIS (optionnel)
└── README.md                  # Ce fichier
```

## ⚙️ Configuration

### Variables d'Environnement Backend (.env)

```env
# Base de données
DATABASE_URL=postgresql://odg_user:password@localhost:5432/odg_database

# Flask
FLASK_ENV=development
SECRET_KEY=votre-clé-secrète-aléatoire

# CORS (domaines autorisés séparés par virgules)
CORS_ORIGINS=http://localhost:5173

# Blockchain (optionnel)
BLOCKCHAIN_ENABLED=false
BLOCKCHAIN_NETWORK=polygon_mumbai
```

### Variables d'Environnement Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:5000
VITE_APP_ENV=development
VITE_FEATURE_BLOCKCHAIN=true
```

## 🔑 Fonctionnalités Principales

### Module WebGIS
- ✅ Carte interactive Leaflet
- ✅ Import multi-formats géospatiaux
- ✅ Gestion de couches (ajout, édition, suppression)
- ✅ Visualisation des gisements miniers
- ✅ Export vers GeoJSON, KML, Shapefile

### Module Blockchain
- ✅ Enregistrement des transactions sur blockchain
- ✅ Support Ethereum et Polygon
- ✅ Certificats de traçabilité
- ✅ Dashboard de visualisation

### Gestion Utilisateurs
- ✅ 3 rôles : Admin, Opérateur, Partenaire
- ✅ Authentification
- ✅ Permissions par rôle

## 📚 Documentation

**Nouveau sur le projet ?** Suivez **exactement** le guide pas à pas : **[Démarrage développeur](docs/guides/demarrage-developpeur.md)** (prérequis, variables d'environnement, base de données, migration auth, comptes de test, lancer backend et frontend).

**Où trouver quoi :**
- **Variables d'environnement** : modèle dans `backend/.env.example` → créer `backend/.env` et éditer (voir [Démarrage développeur](docs/guides/demarrage-developpeur.md)).
- **Connexion à l'application** : après `create_test_users.py`, utiliser **admin@odg.ga** / **odg2025!** (ou voir le script pour les autres comptes).

**[→ Index de la documentation](docs/README.md)** — autres parcours :

- **Utilisateur métier** : [Utilisation de la plateforme](docs/guides/guide-utilisation-odg.md)
- **Déploiement / production** : [Opérations](docs/operations/README.md)
- **Contributeur** : [Contribuer et lancer les tests](docs/guides/contribuer-et-tests.md)

## 🛠️ Technologies Utilisées

### Backend
- Flask 3.1+ (Framework web)
- SQLAlchemy 2.0+ (ORM)
- PostgreSQL + PostGIS (Base de données spatiale)
- GeoAlchemy2 (Extension spatiale SQLAlchemy)
- GeoPandas (Manipulation données géospatiales)
- Web3.py (Intégration blockchain)

### Frontend
- React 18+ (UI Framework)
- Vite (Build tool)
- Tailwind CSS + Shadcn/UI (Styles)
- Leaflet + React-Leaflet (Cartographie)
- Recharts (Graphiques)
- Axios (HTTP client)

## 🧪 Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
pnpm test
```

## 📝 Scripts Disponibles

### Backend
- `python run_server.py` - Lancer le serveur de développement
- `python -m src.main` - Alternative pour lancer l'application

### Frontend
- `pnpm dev` - Serveur de développement
- `pnpm build` - Build de production
- `pnpm preview` - Prévisualiser le build

## 🔒 Sécurité

⚠️ **Important pour la production** :
1. Changez `SECRET_KEY` par une valeur aléatoire forte
2. Configurez `CORS_ORIGINS` avec vos domaines réels
3. Utilisez HTTPS
4. Ne commitez JAMAIS les fichiers `.env`
5. Activez les logs de production dans `/var/log/odg/`

## 🐛 Problèmes Connus & Solutions

### Backend ne démarre pas
- Vérifiez que PostgreSQL est démarré : `docker-compose ps`
- Vérifiez DATABASE_URL dans `.env`
- Vérifiez les dépendances : `pip install -r requirements.txt`

### Erreur "Module blockchain désactivé"
- Normal si web3 n'est pas installé
- Installer : `pip install web3 eth-account`
- Ou désactiver dans .env : `BLOCKCHAIN_ENABLED=false`

### Imports géospatiaux échouent
- Windows : Voir [Guide installation Windows](docs/guides/installation-windows.md)
- Installer GDAL, Fiona depuis wheels précompilés

## 👥 Équipe

Développé pour l'initiative Ogooué Digital Gold (ODG) - Gabon

## 📄 Licence

Propriétaire - Tous droits réservés

---

Pour toute question ou assistance : [Contact ODG](mailto:support@odg.ga)
