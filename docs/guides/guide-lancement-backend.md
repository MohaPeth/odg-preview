# 🚀 Guide de Lancement - ODG Backend

## 📋 Prérequis

- Python 3.11+ installé
- PostgreSQL 15+ avec PostGIS installé et en cours d'exécution
- Base de données `odg_mining` créée avec l'utilisateur `odg_user`

---

## 🔧 Configuration de la Base de Données

### Informations de Connexion PostgreSQL

```
Hôte: localhost
Port: 5432
Base de données: odg_mining
Utilisateur: odg_user
Mot de passe: root
```

### Chaîne de Connexion

```
postgresql://odg_user:root@localhost:5432/odg_mining
```

### Vérifier que PostgreSQL est en cours d'exécution

```powershell
# Vérifier le service PostgreSQL
Get-Service -Name postgresql*

# Tester la connexion
psql -U odg_user -h localhost -p 5432 -d odg_mining
```

---

## 🚀 Lancement du Backend

### Méthode 1 : Script Python (RECOMMANDÉ)

```bash
cd c:\Users\Moha\Desktop\test\reactJs\ODG_Modules_Complete\backend
python run_server.py
```

### Méthode 2 : Lancement manuel

```bash
cd c:\Users\Moha\Desktop\test\reactJs\ODG_Modules_Complete\backend

# Définir les variables d'environnement
$env:FLASK_ENV="development"
$env:DATABASE_URL="postgresql://odg_user:root@localhost:5432/odg_mining"

# Lancer le serveur
python src/main.py
```

---

## 🌐 Accès à l'API

Une fois le serveur lancé, l'API est accessible sur :

- **Local** : http://localhost:5000
- **Réseau** : http://192.168.1.17:5000

### Endpoints Principaux

- `GET /` - Liste des endpoints disponibles
- `GET /api/health` - Vérification de santé
- `GET /api/dashboard/summary` - Statistiques du dashboard
- `GET /api/operators` - Liste des opérateurs
- `GET /api/users` - Liste des utilisateurs
- `GET /api/blockchain/transactions` - Transactions blockchain
- `GET /api/webgis/layers` - Couches géospatiales

---

## 👤 Comptes de Test pour le Dashboard

### Compte Administrateur

```
Email: admin@odg.ga
Mot de passe: admin123
Rôle: admin
```

**Permissions** :
- Accès complet au dashboard
- Gestion des utilisateurs
- Gestion des partenaires
- Gestion des opérateurs
- Accès à toutes les fonctionnalités

### Compte Opérateur

```
Email: operator@odg.ga
Mot de passe: operator123
Rôle: operator
```

**Permissions** :
- Ajout de gisements miniers
- Gestion des transactions blockchain
- Visualisation des données géospatiales
- Accès limité au dashboard

### Compte Partenaire

```
Email: partner@odg.ga
Mot de passe: partner123
Rôle: partner
```

**Permissions** :
- Consultation des données
- Visualisation des transactions
- Accès en lecture seule

---

## 🔑 Création des Comptes de Test

Les comptes de test seront créés automatiquement au premier lancement du backend.

Si vous devez les créer manuellement :

```bash
cd c:\Users\Moha\Desktop\test\reactJs\ODG_Modules_Complete\backend
python create_test_users.py
```

---

## 🐛 Dépannage

### Erreur : "Cannot connect to database"

1. Vérifier que PostgreSQL est démarré
2. Vérifier les identifiants dans `.env`
3. Tester la connexion avec `psql`

### Erreur : "Module not found"

```bash
# Installer les dépendances
pip install -r requirements.txt
```

### Erreur : "Port 5000 already in use"

```bash
# Trouver le processus utilisant le port 5000
netstat -ano | findstr :5000

# Tuer le processus (remplacer PID par l'ID du processus)
taskkill /PID <PID> /F
```

### Base de données vide

```bash
# Réinitialiser la base de données
python init_production_db.py
```

---

## 📊 Vérification du Fonctionnement

### 1. Vérifier l'API

```bash
# Test de santé
curl http://localhost:5000/api/health

# Statistiques dashboard
curl http://localhost:5000/api/dashboard/summary
```

### 2. Vérifier la Base de Données

```sql
-- Se connecter à PostgreSQL
psql -U odg_user -h localhost -p 5432 -d odg_mining

-- Vérifier les tables
\dt

-- Vérifier les utilisateurs
SELECT id, email, role FROM users;

-- Vérifier les opérateurs
SELECT id, name, status FROM operators;
```

### 3. Tester la Connexion Frontend

1. Lancer le backend : `python run_server.py`
2. Lancer le frontend : `cd ../frontend && npm run dev`
3. Accéder à http://localhost:5173
4. Se connecter avec les identifiants admin

---

## 🔄 Arrêt du Serveur

Pour arrêter le serveur backend :

```
CTRL + C
```

---

## 📝 Notes Importantes

1. **Mode Développement** : Le serveur est configuré en mode développement avec `debug=True`
2. **CORS** : Configuré pour accepter les requêtes depuis `http://localhost:5173`
3. **Blockchain** : Désactivée par défaut (`BLOCKCHAIN_ENABLED=false`)
4. **Logs** : Les logs s'affichent dans la console

---

## 🆘 Support

En cas de problème, vérifier :

1. ✅ PostgreSQL est démarré
2. ✅ La base de données `odg_mining` existe
3. ✅ Les dépendances Python sont installées
4. ✅ Le fichier `.env` est configuré
5. ✅ Le port 5000 est disponible

---

**Dernière mise à jour** : 27 décembre 2024
