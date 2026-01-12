# 🌍 ODG Backend - API Flask + PostgreSQL/PostGIS

Backend de la plateforme ODG (Ogooué Digital Gold) pour la gestion et la traçabilité des ressources minières.

---

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.11+
- PostgreSQL 15+ avec PostGIS
- Base de données `odg_mining` configurée

### Installation

```bash
# 1. Cloner le projet
cd backend

# 2. Créer l'environnement virtuel
python -m venv venv

# 3. Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# 6. Lancer le serveur
python run_server.py
```

### Accès
- **API** : http://localhost:5000
- **Documentation** : Voir `GUIDE_LANCEMENT.md`

---

## 📁 Structure du Projet

```
backend/
├── .env                          # Configuration (ne pas commiter)
├── .env.example                  # Template de configuration
├── config_production.py          # Configuration production/dev
├── requirements.txt              # Dépendances Python
├── wsgi.py                       # Point d'entrée WSGI (production)
├── run_server.py                 # Script de lancement (développement)
├── create_test_users.py          # Création utilisateurs de test
├── init_production_db.py         # Initialisation base production
│
├── _archive/                     # Scripts de setup PostgreSQL
│
├── contracts/                    # Smart contracts Solidity
│   └── ODGTraceability.sol
│
└── src/                          # Code source
    ├── main.py                   # Application Flask
    ├── config/                   # Configuration
    ├── models/                   # Modèles de données
    ├── routes/                   # Endpoints API
    └── services/                 # Services métier
```

---

## 🔧 Configuration

### Variables d'environnement (.env)

```bash
# Base de données
DATABASE_URL=postgresql://odg_user:root@localhost:5432/odg_mining

# Flask
FLASK_ENV=development
SECRET_KEY=votre-secret-key-ici

# Blockchain (optionnel)
BLOCKCHAIN_ENABLED=false
BLOCKCHAIN_NETWORK=polygon_mumbai
```

### Base de données

```sql
-- Créer la base de données
CREATE DATABASE odg_mining;

-- Activer PostGIS
CREATE EXTENSION postgis;

-- Créer l'utilisateur
CREATE USER odg_user WITH PASSWORD 'root';
GRANT ALL PRIVILEGES ON DATABASE odg_mining TO odg_user;
```

---

## 📡 API Endpoints

### Authentification
- `POST /api/auth/login` - Connexion utilisateur

### Utilisateurs
- `GET /api/users` - Liste des utilisateurs
- `POST /api/users` - Créer un utilisateur
- `PUT /api/users/:id` - Modifier un utilisateur
- `DELETE /api/users/:id` - Supprimer un utilisateur

### Opérateurs
- `GET /api/operators` - Liste des opérateurs miniers
- `POST /api/operators` - Créer un opérateur
- `PUT /api/operators/:id` - Modifier un opérateur
- `DELETE /api/operators/:id` - Supprimer un opérateur

### WebGIS
- `GET /api/webgis/layers` - Liste des couches géospatiales
- `POST /api/geospatial/upload` - Importer une couche
- `POST /api/geospatial/preview` - Prévisualiser un fichier
- `GET /api/geospatial/layers/:id` - Détails d'une couche
- `DELETE /api/geospatial/layers/:id` - Supprimer une couche

### Blockchain
- `GET /api/blockchain/transactions` - Liste des transactions
- `POST /api/blockchain/transactions` - Créer une transaction
- `GET /api/blockchain-integration/status` - Statut blockchain
- `POST /api/blockchain-integration/publish/:id` - Publier sur blockchain

### Dashboard
- `GET /api/dashboard/summary` - Statistiques globales

---

## 👥 Utilisateurs de Test

Après avoir lancé `python create_test_users.py` :

| Rôle | Email | Username | Accès |
|------|-------|----------|-------|
| Admin | admin@odg.ga | admin | Complet |
| Opérateur | operator@odg.ga | operator | Gestion gisements |
| Partenaire | partner@odg.ga | partner | Lecture seule |

⚠️ **Note** : L'authentification actuelle ne vérifie pas de mot de passe (à corriger avant production).

---

## 🛠️ Développement

### Lancer en mode développement

```bash
python run_server.py
```

### Créer des utilisateurs de test

```bash
python create_test_users.py
```

### Initialiser la base de données

```bash
python init_production_db.py
```

### Structure des modèles

- **User** : Utilisateurs de la plateforme
- **Operator** : Opérateurs miniers
- **MiningDeposit** : Gisements miniers
- **ExploitationArea** : Zones d'exploitation
- **BlockchainTransaction** : Transactions de traçabilité
- **GeospatialLayer** : Couches géospatiales
- **Substance** : Référentiel des substances minérales

---

## 📦 Déploiement Production

### Avec Gunicorn

```bash
# Installer Gunicorn
pip install gunicorn

# Lancer avec Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

### Variables d'environnement production

```bash
FLASK_ENV=production
SECRET_KEY=<générer-une-clé-forte>
DATABASE_URL=postgresql://user:pass@host:5432/dbname
BLOCKCHAIN_ENABLED=true
BLOCKCHAIN_PRIVATE_KEY=<votre-clé-privée>
BLOCKCHAIN_CONTRACT_ADDRESS=<adresse-contrat>
```

### Checklist déploiement

- [ ] Configurer `SECRET_KEY` forte
- [ ] Activer HTTPS
- [ ] Configurer CORS correctement
- [ ] Sauvegardes automatiques de la BDD
- [ ] Monitoring et logs
- [ ] Certificats SSL
- [ ] Firewall configuré
- [ ] Variables d'environnement sécurisées

---

## 🔒 Sécurité

### Points critiques

⚠️ **À corriger avant production** :
1. Implémenter l'authentification par mot de passe
2. Ajouter tokens JWT ou sessions
3. Valider toutes les entrées utilisateur
4. Limiter les tentatives de connexion
5. Activer HTTPS uniquement
6. Sécuriser les clés blockchain

### Bonnes pratiques

- Ne jamais commiter `.env`
- Utiliser des secrets forts
- Chiffrer les données sensibles
- Auditer les logs régulièrement
- Mettre à jour les dépendances

---

## 🧪 Tests

### Créer des tests

Créer un dossier `tests/` :

```bash
mkdir tests
cd tests
```

Structure recommandée :
```
tests/
├── test_api.py
├── test_models.py
├── test_services.py
└── test_blockchain.py
```

### Lancer les tests

```bash
pytest tests/
```

---

## 📚 Documentation

- **`GUIDE_LANCEMENT.md`** - Guide complet de lancement
- **`ANALYSE_NETTOYAGE_BACKEND.md`** - Analyse de la structure
- **`NETTOYAGE_COMPLETE.md`** - Rapport de nettoyage
- **`_archive/`** - Scripts de setup PostgreSQL

---

## 🤝 Contribution

### Workflow

1. Créer une branche : `git checkout -b feature/ma-fonctionnalite`
2. Développer et tester
3. Commit : `git commit -m "feat: description"`
4. Push : `git push origin feature/ma-fonctionnalite`
5. Créer une Pull Request

### Standards de code

- **PEP 8** pour Python
- **Docstrings** pour les fonctions
- **Type hints** quand possible
- **Tests unitaires** pour les nouvelles fonctionnalités

---

## 🐛 Dépannage

### Erreur de connexion PostgreSQL

```bash
# Vérifier que PostgreSQL est démarré
Get-Service postgresql*

# Tester la connexion
psql -U odg_user -h localhost -d odg_mining
```

### Erreur d'import

```bash
# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

### Port 5000 déjà utilisé

```bash
# Trouver le processus
netstat -ano | findstr :5000

# Tuer le processus
taskkill /PID <PID> /F
```

---

## 📞 Support

Pour toute question ou problème :
1. Consulter `GUIDE_LANCEMENT.md`
2. Vérifier les logs du serveur
3. Consulter `_archive/GUIDE_RESOLUTION_POSTGRESQL.md` pour les problèmes PostgreSQL

---

## 📄 Licence

Propriétaire - ODG Platform © 2024

---

## 🎯 Roadmap

### Phase 1 (Actuel)
- ✅ API REST complète
- ✅ Gestion utilisateurs et opérateurs
- ✅ Import de données géospatiales
- ✅ Intégration blockchain (simulation)
- ⚠️ Authentification à sécuriser

### Phase 2 (À venir)
- [ ] Authentification JWT complète
- [ ] Tests unitaires et d'intégration
- [ ] Blockchain en production
- [ ] API de recherche avancée
- [ ] Notifications en temps réel

### Phase 3 (Futur)
- [ ] API GraphQL
- [ ] Webhooks
- [ ] Analytics avancés
- [ ] Machine Learning (prédictions)
- [ ] API mobile dédiée

---

**Version** : 1.0.0  
**Dernière mise à jour** : 27 décembre 2024
