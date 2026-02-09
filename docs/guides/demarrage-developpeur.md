# Démarrage développeur – ODG

Guide pas à pas pour qu’un collègue puisse **installer et lancer le projet exactement** (clone → variables d’environnement → base → auth → serveurs).

---

## Ordre exact à suivre

1. Cloner le dépôt
2. Backend : venv + `pip install -r requirements.txt`
3. **Variables d’environnement** : copier `backend/.env.example` en `backend/.env`, éditer (au minimum `DATABASE_URL`, `SECRET_KEY`)
4. **Base de données** : créer PostgreSQL + PostGIS, base `odg_mining`, utilisateur `odg_user`
5. **Migration auth** : exécuter `backend/src/migrations/add_password_hash_to_users.sql` sur la base
6. **Initialiser les tables** : `python init_production_db.py`
7. **Comptes de test** : `python create_test_users.py` (mots de passe pour le login)
8. **Lancer le backend** : `python run_server.py`
9. **Frontend** : dans un autre terminal, `cd frontend` → `pnpm install` → `pnpm dev`
10. **Tester** : http://localhost:5173 → connexion **admin@odg.ga** / **odg2025!**

---

## Prérequis

- **Python** 3.8+ (3.11+ recommandé)
- **Node.js** 16+ (LTS recommandé)
- **pnpm** ou npm
- **PostgreSQL** 15+ avec extension **PostGIS** (ou Docker pour PostgreSQL + PostGIS)

---

## 1. Cloner le dépôt

```bash
git clone <url-du-repo>
cd odg-preview
```

---

## 2. Backend

### 2.1 Environnement virtuel et dépendances

```bash
cd backend
python -m venv venv
```

**Windows (PowerShell) :**
```powershell
.\venv\Scripts\Activate.ps1
```

**Linux / macOS :**
```bash
source venv/bin/activate
```

Puis :
```bash
pip install -r requirements.txt
```

### 2.2 Variables d'environnement

**Où les trouver / les créer :**

- **Fichier modèle** : `backend/.env.example` (liste toutes les variables et leur rôle).
- **Fichier à créer** : `backend/.env` (jamais versionné). À créer en **copiant** le modèle.

**Commandes :**

**Windows (depuis `backend/`) :**
```powershell
Copy-Item .env.example .env
```

**Linux / macOS :**
```bash
cp .env.example .env
```

**Éditer `backend/.env`** et renseigner au minimum :

| Variable       | Exemple (développement) |
|----------------|-------------------------|
| `DATABASE_URL` | `postgresql://odg_user:root@localhost:5432/odg_mining` |
| `SECRET_KEY`   | `dev-secret-key-UNSAFE-change-me` |
| `FLASK_ENV`    | `development` |

Les autres variables (blockchain, CORS) sont optionnelles pour le développement local.

**Si vous n’avez pas encore la base** : créez l’utilisateur et la base PostgreSQL (voir [Installation PostGIS](../operations/installation-postgis-guide.md) ou `docker-compose up -d` si vous utilisez Docker), puis utilisez la chaîne de connexion correspondante dans `DATABASE_URL`.

### 2.3 Base de données

**Étape A – Créer la base et l’utilisateur** (si ce n’est pas déjà fait)

Exemple avec PostgreSQL en local :

- Base : `odg_mining`
- Utilisateur : `odg_user`
- Mot de passe : au choix (ex. `root`)
- Activer PostGIS : `CREATE EXTENSION IF NOT EXISTS postgis;` dans la base `odg_mining`

**Étape B – Migration auth (mot de passe)**

Une seule fois : appliquer le script SQL qui ajoute la colonne `password_hash` à la table `users`.

- **Fichier** : `backend/src/migrations/add_password_hash_to_users.sql`
- **Méthode** : exécuter ce fichier sur la base `odg_mining` (avec `psql`, pgAdmin, DBeaver, etc.)

Exemple avec `psql` (remplacer par votre chaîne de connexion) :

```bash
psql postgresql://odg_user:root@localhost:5432/odg_mining -f src/migrations/add_password_hash_to_users.sql
```

**Étape C – Initialiser les tables et les données**

```bash
python init_production_db.py
```

**Étape D – Créer les comptes de test (mots de passe pour le login)**

```bash
python create_test_users.py
```

Cela crée ou met à jour les comptes :

- **admin@odg.ga** (admin)
- **operator@odg.ga** (opérateur)
- **partner@odg.ga** (partenaire)

**Mot de passe par défaut** : `odg2025!` (ou la valeur de la variable d’environnement `ODG_TEST_PASSWORD` si vous l’avez définie).

### 2.4 Lancer le serveur

```bash
python run_server.py
```

Le backend est accessible sur **http://localhost:5000**.

---

## 3. Frontend

Dans un **autre terminal**, depuis la racine du projet :

```bash
cd frontend
pnpm install
# ou : npm install
pnpm dev
# ou : npm run dev
```

Le frontend est accessible sur **http://localhost:5173**. Les requêtes `/api` sont proxifiées vers le backend (voir `vite.config.js`).

**Variables d’environnement frontend** : optionnel en dev. Le fichier modèle est `frontend/.env.example`. En développement, le proxy Vite pointe déjà vers `http://localhost:5000`. Créez `frontend/.env` si vous devez changer l’URL de l’API.

---

## 4. Vérification rapide

- **Health check (sans connexion)** : http://localhost:5000/api/health  
  Réponse attendue : `{"status":"ok","database":"connected"}` (ou 503 si la base est indisponible).

- **Application** : http://localhost:5173 → page de connexion ODG.

- **Connexion** : utiliser **admin@odg.ga** / **odg2025!** (ou un autre compte créé par `create_test_users.py` avec le même mot de passe par défaut).

Après connexion, vous devez voir le tableau de bord (accueil, WebGIS, Blockchain, Couches, etc.).

---

## Références utiles

| Besoin | Document |
|--------|----------|
| Installation Windows détaillée (sans Docker) | [Installation Windows](installation-windows.md) |
| Lancement backend seul (dépannage, config DB) | [Lancement backend](guide-lancement-backend.md) |
| PostGIS (production / déploiement) | [Installation PostGIS](../operations/installation-postgis-guide.md) |
| Auth (JWT, protection des routes, rate limiting) | [Auth et sécurité](../operations/auth-et-securite.md) |
| Où trouver les variables d’environnement | `backend/.env.example` ; créer `backend/.env` (voir section 2.2 ci-dessus) |

---

*Document mis à jour pour permettre à un collègue de suivre exactement les étapes d’installation et de démarrage.*
