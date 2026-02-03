# Modules WebGIS et Blockchain ODG

## Vue d'ensemble

Ce projet contient les modules frontend et backend intégrés pour la plateforme Ogooué Digital Gold (ODG), incluant un géoportail WebGIS et un système de traçabilité blockchain pour l'industrie minière gabonaise.

## Architecture

### Frontend (React)
- **Localisation**: `/home/ubuntu/odg-webgis-frontend/`
- **Framework**: React avec Vite
- **UI Components**: Shadcn/UI, Tailwind CSS
- **Cartographie**: Leaflet et React-Leaflet
- **Graphiques**: Recharts
- **Icônes**: Lucide React

### Backend (Flask)
- **Localisation**: `/home/ubuntu/odg-webgis-backend/`
- **Framework**: Flask avec SQLAlchemy
- **Base de données**: SQLite (développement)
- **API**: RESTful avec CORS activé
- **Géospatial**: Support des coordonnées géographiques

## Fonctionnalités Développées

### 1. Module WebGIS

#### Frontend
- **Carte interactive** avec Leaflet
- **Visualisation des gisements** miniers du Gabon
- **Panneau latéral** avec informations détaillées
- **Recherche et filtrage** des gisements
- **Légende interactive** avec types de matériaux
- **Popups d'information** pour chaque gisement
- **Interface responsive** pour mobile et desktop

#### Backend
- **API REST** pour les données géospatiales
- **Endpoints**:
  - `GET /api/webgis/deposits` - Liste des gisements
  - `GET /api/webgis/deposits/<id>` - Détails d'un gisement
  - `GET /api/webgis/search` - Recherche de gisements
- **Modèles de données** pour les gisements miniers
- **Données de test** avec 3 gisements (Minkebe, Myaning, Eteke)

### 2. Module Blockchain

#### Frontend
- **Tableau de bord** avec statistiques en temps réel
- **Graphiques interactifs** (évolution, distribution)
- **Onglets organisés**:
  - Transactions blockchain
  - Certificats de traçabilité
  - Chaîne d'approvisionnement
- **Recherche et filtrage** des transactions
- **Modal de détails** pour les transactions
- **Interface intuitive** pour la compréhension blockchain

#### Backend
- **API REST** pour la blockchain
- **Endpoints**:
  - `GET /api/blockchain/transactions` - Liste des transactions
  - `POST /api/blockchain/transactions` - Nouvelle transaction
  - `GET /api/blockchain/certificates` - Certificats
  - `GET /api/blockchain/supply-chain/<material>` - Chaîne d'approvisionnement
  - `POST /api/blockchain/verify/<certificate_id>` - Vérification
  - `GET /api/blockchain/stats` - Statistiques
- **Modèles de données** pour les transactions blockchain
- **Simulation** de transactions avec métadonnées

### 3. Interface Principale Intégrée

- **Navigation unifiée** entre modules
- **Page d'accueil** avec présentation ODG
- **Sidebar responsive** avec menu de navigation
- **Design cohérent** avec la charte graphique ODG
- **Statistiques rapides** sur la page d'accueil
- **Sections futures** (Analyses, Paramètres)

## Installation et Démarrage

### Prérequis
- Node.js 20.x
- Python 3.11
- pnpm (gestionnaire de paquets)

### Frontend
```bash
cd /home/ubuntu/odg-webgis-frontend
pnpm install
pnpm run dev  # Développement
pnpm run build  # Production
```

### Backend
```bash
cd /home/ubuntu/odg-webgis-backend
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

### Application Intégrée
L'application complète est accessible sur `http://localhost:5000` avec le backend Flask servant les fichiers frontend buildés.

## Structure des Fichiers

### Frontend
```
odg-webgis-frontend/
├── src/
│   ├── components/
│   │   ├── WebGISMap.jsx          # Composant carte WebGIS
│   │   ├── BlockchainDashboard.jsx # Tableau de bord blockchain
│   │   └── MainApp.jsx            # Application principale
│   ├── App.jsx                    # Point d'entrée React
│   └── main.jsx                   # Bootstrap React
├── public/                        # Assets statiques
└── dist/                         # Build de production
```

### Backend
```
odg-webgis-backend/
├── src/
│   ├── models/
│   │   └── mining_data.py         # Modèles de données
│   ├── routes/
│   │   ├── webgis.py             # Routes WebGIS
│   │   └── blockchain.py         # Routes Blockchain
│   ├── static/                   # Frontend intégré
│   └── main.py                   # Application Flask
└── requirements.txt              # Dépendances Python
```

## API Documentation

### WebGIS Endpoints

#### GET /api/webgis/deposits
Retourne la liste de tous les gisements miniers.

**Réponse:**
```json
{
  "success": true,
  "count": 3,
  "data": [
    {
      "id": 1,
      "name": "Gisement Minkebe",
      "type": "Or",
      "coordinates": [-0.5, 12.0],
      "status": "Actif",
      "company": "ODG",
      "estimatedQuantity": "755 Km²",
      "description": "Gisement aurifère dans la province de Woleu-Ntem"
    }
  ]
}
```

#### GET /api/webgis/deposits/<id>
Retourne les détails d'un gisement spécifique.

### Blockchain Endpoints

#### GET /api/blockchain/transactions
Retourne la liste des transactions blockchain avec pagination.

**Paramètres:**
- `page` (optionnel): Numéro de page (défaut: 1)
- `per_page` (optionnel): Éléments par page (défaut: 20)

**Réponse:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "transactionHash": "0x1234567890abcdef...",
      "fromAddress": "0xabcdef1234567890...",
      "toAddress": "0x1234567890abcdef...",
      "materialType": "Or",
      "quantity": 10.5,
      "unit": "kg",
      "status": "confirmed",
      "timestamp": "2025-07-11T14:55:46.644283",
      "blockNumber": 1234567,
      "metadata": {
        "origin": "Mine Minkebe",
        "destination": "Raffinerie Libreville",
        "operator": "ODG",
        "quality": {
          "purity": "99.5%"
        }
      }
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 20,
    "total": 2
  }
}
```

#### POST /api/blockchain/transactions
Crée une nouvelle transaction blockchain.

**Corps de la requête:**
```json
{
  "fromAddress": "0x...",
  "toAddress": "0x...",
  "materialType": "Or",
  "quantity": 5.0,
  "unit": "kg",
  "metadata": {
    "origin": "Mine Source",
    "destination": "Destination",
    "operator": "ODG"
  }
}
```

## Données de Test

### Gisements WebGIS
1. **Gisement Minkebe** - Or, 755 Km², Actif
2. **Gisement Myaning** - Or, 150 Km², En développement  
3. **Gisement Eteke** - Or, 765 Km², Exploration

### Transactions Blockchain
1. **Transaction confirmée** - 10.5 kg d'or, Mine Minkebe → Raffinerie Libreville
2. **Transaction en attente** - 5.2 kg d'or, Mine Myaning → Export Terminal

## Fonctionnalités Techniques

### Sécurité
- **CORS** activé pour les requêtes cross-origin
- **Validation** des données d'entrée
- **Gestion d'erreurs** robuste

### Performance
- **Pagination** des résultats API
- **Optimisation** des requêtes base de données
- **Mise en cache** des assets statiques

### Responsive Design
- **Mobile-first** approach
- **Breakpoints** adaptatifs
- **Touch support** pour les interactions mobiles

## Déploiement

### Développement Local
L'application est configurée pour fonctionner en local avec:
- Frontend: `http://localhost:5173` (développement)
- Backend: `http://localhost:5000`
- Application intégrée: `http://localhost:5000`

### Production
Pour le déploiement en production:
1. Builder le frontend: `pnpm run build`
2. Copier les fichiers dans `/src/static/`
3. Configurer un serveur WSGI (Gunicorn, uWSGI)
4. Utiliser une base de données PostgreSQL/MySQL

## Évolutions Futures

### Fonctionnalités Prévues
- **Authentification** et gestion des utilisateurs
- **Analyses avancées** avec tableaux de bord personnalisables
- **Rapports automatisés** de production
- **Intégration blockchain** réelle (Ethereum, Hyperledger)
- **Notifications** en temps réel
- **API mobile** pour applications natives

### Améliorations Techniques
- **Tests unitaires** et d'intégration
- **Documentation API** avec Swagger
- **Monitoring** et logging avancés
- **Cache Redis** pour les performances
- **CDN** pour les assets statiques

## Support et Maintenance

### Logs
Les logs de l'application sont disponibles dans la console Flask en mode développement.

### Debugging
- Mode debug activé en développement
- Source maps disponibles pour le frontend
- Debugger PIN affiché au démarrage Flask

### Contact
Pour toute question technique ou support, contacter l'équipe de développement ODG.

---

**Version**: 1.0.0  
**Date**: Juillet 2025  
**Auteur**: Équipe de développement ODG

