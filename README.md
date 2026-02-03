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

```bash
cd backend

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer dépendances
pip install -r requirements.txt

# Configurer variables d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs

# Initialiser la base de données
python -c "from src.main import app, init_database; init_database()"

# Lancer le serveur
python run_server.py
```

Le backend sera accessible sur `http://localhost:5000`

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
odg-preview-main/
├── backend/                    # Backend Flask
│   ├── src/
│   │   ├── models/            # Modèles SQLAlchemy
│   │   ├── routes/            # Endpoints API
│   │   ├── services/          # Logique métier
│   │   └── config/            # Configuration
│   ├── _debug_scripts/        # Scripts utilitaires (dev uniquement)
│   ├── _archive/              # Scripts d'installation archivés
│   ├── requirements.txt       # Dépendances Python
│   ├── config_production.py   # Configuration production/dev
│   └── .env.example           # Template configuration
│
├── frontend/                   # Frontend React
│   ├── src/
│   │   ├── components/        # Composants React
│   │   ├── services/          # API clients
│   │   ├── hooks/             # React hooks personnalisés
│   │   └── config/            # Configuration frontend
│   ├── package.json
│   └── .env.example
│
├── docker-compose.yml          # PostgreSQL + PostGIS
└── README.md                   # Ce fichier
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

## 📚 Documentation Complémentaire

- [Guide d'installation Windows](GUIDE_INSTALLATION_WINDOWS.md)
- [Guide de démarrage rapide](GUIDE_DEMARRAGE_RAPIDE_WINDOWS.md)
- [Documentation modules](README_ODG_Modules.md)
- [Rapport bugs corrigés](RAPPORT_BUGS_CORRIGES.md)
- [Corrections React](CORRECTIONS_CRASH_REACT.md)

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
- Windows : Voir [GUIDE_INSTALLATION_WINDOWS.md](GUIDE_INSTALLATION_WINDOWS.md)
- Installer GDAL, Fiona depuis wheels précompilés

## 👥 Équipe

Développé pour l'initiative Ogooué Digital Gold (ODG) - Gabon

## 📄 Licence

Propriétaire - Tous droits réservés

---

Pour toute question ou assistance : [Contact ODG](mailto:support@odg.ga)
