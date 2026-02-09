# Hébergement ODG sur Hostinger – Guide de configuration (stagiaire)

Ce document décrit le type d’hébergement recommandé chez Hostinger pour le dashboard ODG et son backend, ainsi que les étapes détaillées de configuration pour un stagiaire développeur.

---

## 1. Analyse du projet et besoins serveur

### 1.1 Stack technique ODG

| Composant | Technologie | Remarque |
|-----------|-------------|----------|
| **Backend** | Flask 3.1, Gunicorn (prod) | Python 3.8+, WSGI |
| **Frontend** | React 19, Vite | Build statique (fichiers dans `frontend/dist`) |
| **Base de données** | PostgreSQL 15+ avec **PostGIS** | Obligatoire pour les couches géospatiales |
| **Serveur web** | Nginx (recommandé) ou Apache | Reverse proxy + fichiers statiques |

### 1.2 Pourquoi pas d’hébergement mutualisé (shared) ?

- **PostgreSQL + PostGIS** : chez Hostinger, PostgreSQL (et donc PostGIS) n’est **pas disponible** sur les offres Web / Cloud mutualisées ; il est disponible uniquement sur **VPS**.
- **Python / Gunicorn** : l’exécution d’une app Flask avec Gunicorn et un venv demande un accès SSH et des droits d’installation (Python, pip, libs système), typiquement sur un **VPS**.
- **Node.js (build)** : le build du frontend (npm/pnpm) est fait une fois en déploiement ; il peut être fait en local puis envoyé, ou sur le VPS si Node est installé.

**Conclusion :** il faut un **VPS Hostinger** pour faire tourner backend + frontend + PostgreSQL/PostGIS sur la même machine (ou une base gérée ailleurs si vous choisissez une DB externe).

---

## 2. Type d’hébergement recommandé : VPS Hostinger

### 2.1 Choix du plan VPS

| Plan | vCPU | RAM | Stockage | Bande passante | Usage recommandé ODG |
|------|------|-----|----------|----------------|------------------------|
| **KVM 1** | 1 | 4 Go | 50 Go NVMe | 4 To/mois | Petit déploiement, démo, faible trafic |
| **KVM 2** | 2 | 8 Go | 100 Go NVMe | 8 To/mois | **Recommandé** : production légère à moyenne |
| **KVM 4** | 4 | 16 Go | 200 Go NVMe | 16 To/mois | Fort trafic ou beaucoup de données géospatiales |

**Recommandation pour démarrer :** **KVM 1** (démo / staging) ou **KVM 2** (production avec marge).

- Le backend Flask + Gunicorn (4 workers) et PostgreSQL/PostGIS tiennent bien sur 4 Go RAM ; 8 Go laissent de la marge pour pics et évolutions.
- Le frontend est servi en statique (Nginx), coût négligeable.
- Les imports géospatiaux (Fiona, Rasterio, GeoPandas) peuvent être gourmands en RAM ; 4 Go minimum, 8 Go conseillé en production.

### 2.2 Offre PostgreSQL Hostinger

- Hostinger propose du **PostgreSQL via Docker** sur VPS (one-click).
- **PostGIS** : extension PostgreSQL ; à activer après création de la base (`CREATE EXTENSION postgis;`).
- Vous pouvez aussi installer **PostgreSQL + PostGIS** vous-même sur le VPS (paquets système), ce qui donne un contrôle total.

---

## 3. Vérification de la base de données (fonctionnalité)

### 3.1 Prérequis pour que la base soit fonctionnelle

1. **PostgreSQL 15+** installé et accessible (localhost ou IP).
2. **Extension PostGIS** activée sur la base ODG :  
   `CREATE EXTENSION IF NOT EXISTS postgis;`
3. **Utilisateur dédié** avec droits sur la base (ex. `odg_user`).
4. **Script d’initialisation** exécuté une fois :  
   `python init_production_db.py` (depuis `backend/`, avec `DATABASE_URL` et `SECRET_KEY` dans l’environnement).

### 3.2 Comment vérifier que la base est fonctionnelle

**A. Connexion et PostGIS**

```bash
# Depuis le VPS ou une machine ayant accès à la base
psql "$DATABASE_URL" -c "SELECT PostGIS_Version();"
```

- Une version s’affiche (ex. `3.3 USE_GEOS=1 USE_PROJ=1`) → PostGIS est opérationnel.

**B. Tables créées**

```bash
psql "$DATABASE_URL" -c "\dt"
```

- Vous devez voir au moins : `geospatial_layers`, `layer_upload_history`, et les tables métier (`mining_deposits`, `users`, etc.) après `init_production_db.py` et/ou le premier lancement de l’app (si `db.create_all()` est utilisé).

**C. Test depuis l’application**

- Démarrer le backend avec `FLASK_ENV=production` et la même `DATABASE_URL`.
- Appeler par exemple :  
  `GET /api/dashboard/summary` ou `GET /api/webgis/layers`.  
- Pas d’erreur 500 et réponses JSON cohérentes → la base est utilisée correctement.

### 3.3 En cas de problème

- **« PostGIS non disponible »** : exécuter `CREATE EXTENSION postgis;` (et éventuellement `postgis_topology`) dans la base ODG.
- **« relation … does not exist »** : réexécuter `init_production_db.py` (ou le script qui fait `db.create_all()` + migrations).
- **Erreur de connexion** : vérifier `DATABASE_URL`, pare-feu, et que PostgreSQL écoute sur l’IP/port prévus (ex. `0.0.0.0:5432` ou `127.0.0.1:5432`).

Le script `init_production_db.py` a été mis à jour pour être compatible **SQLAlchemy 2.0** (exécution des requêtes SQL brutes via `text()` et `db.engine.connect()`).

---

## 4. Architecture de déploiement sur le VPS

```
                    Internet
                        |
                   [Nginx :80/:443]
                        |
         +--------------+--------------+
         |                             |
    [Frontend]                   [/api/*]
    (fichiers statiques)              |
    frontend/dist                      v
                                 [Gunicorn :5000]
                                 (Flask backend)
                                        |
                                 [PostgreSQL + PostGIS]
                                 (localhost:5432)
```

- **Nginx** : sert le build React (`/`) et reverse proxy vers Gunicorn pour `/api/`.
- **Gunicorn** : lance l’app Flask (`wsgi:application`).
- **PostgreSQL** : tourne en local sur le VPS (ou sur une instance dédiée) avec PostGIS activé.

---

## 5. Étapes de configuration détaillées (stagiaire)

### 5.1 Prérequis sur le VPS

- Accès **SSH** au VPS Hostinger.
- Un **nom de domaine** (ou sous-domaine) pointant vers l’IP du VPS (ex. `odg.votredomaine.com`).
- **Python 3.10+** et **Node.js 18+** (pour le build) installés sur le VPS.

### 5.2 Installation des paquets (exemple : Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib
# PostGIS
sudo apt install -y postgis postgresql-15-postgis-3   # adapter 15 à votre version PG
```

### 5.3 PostgreSQL et PostGIS

```bash
sudo -u postgres psql -c "CREATE USER odg_user WITH PASSWORD 'votre_mot_de_passe_fort';"
sudo -u postgres psql -c "CREATE DATABASE odg_mining OWNER odg_user;"
sudo -u postgres psql -d odg_mining -c "CREATE EXTENSION IF NOT EXISTS postgis;"
sudo -u postgres psql -d odg_mining -c "CREATE EXTENSION IF NOT EXISTS postgis_topology;"
```

Vérification :

```bash
sudo -u postgres psql -d odg_mining -c "SELECT PostGIS_Version();"
```

### 5.4 Déploiement du code

- Cloner le dépôt sur le VPS (ou copier les fichiers) dans un répertoire dédié, par exemple `/var/www/odg/`.

```bash
cd /var/www/odg
git clone <url-du-repo> .
# ou upload via SFTP/rsync
```

### 5.5 Backend

```bash
cd /var/www/odg/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

Créer le fichier `.env` (à ne jamais commiter) :

```env
FLASK_ENV=production
SECRET_KEY=votre_secret_key_long_et_aleatoire
DATABASE_URL=postgresql://odg_user:votre_mot_de_passe_fort@localhost:5432/odg_mining
CORS_ORIGINS=https://odg.votredomaine.com,https://www.odg.votredomaine.com
```

Initialiser la base :

```bash
source venv/bin/activate
export $(grep -v '^#' .env | xargs)
python init_production_db.py
```

Tester Gunicorn à la main :

```bash
gunicorn -w 4 -b 127.0.0.1:5000 wsgi:application
# Puis : curl http://127.0.0.1:5000/api/dashboard/summary
```

### 5.6 Frontend (build)

Sur votre machine locale (ou sur le VPS si Node est installé) :

```bash
cd frontend
pnpm install
pnpm run build
```

Puis copier le contenu de `frontend/dist/` vers le serveur, par exemple dans `/var/www/odg/frontend/dist/` (ou le chemin utilisé par Nginx).

### 5.7 Servir le frontend depuis le backend (option simple)

Le projet peut servir le frontend depuis Flask (dossier `backend/static/`). Après le build, copier le contenu de `frontend/dist/` vers `backend/static/` sur le serveur. Ainsi, une seule app (Gunicorn) sert à la fois l’API et l’interface. Dans ce cas, Nginx peut faire uniquement reverse proxy vers Gunicorn (pas besoin de `root` pour le frontend).

Alternative : Nginx sert directement `frontend/dist` pour `/` et proxy vers Gunicorn pour `/api/` (comme dans le script `deploy_production.sh`).

### 5.8 Nginx (exemple de configuration)

Fichier : `/etc/nginx/sites-available/odg` (puis lien symbolique dans `sites-enabled`).

```nginx
server {
    listen 80;
    server_name odg.votredomaine.com;

    # Frontend statique (si vous servez le build depuis Nginx)
    location / {
        root /var/www/odg/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API Backend
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
}
```

Tester et recharger Nginx :

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 5.9 Service systemd pour Gunicorn

Fichier : `/etc/systemd/system/odg.service`.

```ini
[Unit]
Description=ODG Flask Application
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/odg/backend
Environment="PATH=/var/www/odg/backend/venv/bin"
EnvironmentFile=/var/www/odg/backend/.env
ExecStart=/var/www/odg/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Puis :

```bash
sudo systemctl daemon-reload
sudo systemctl enable odg
sudo systemctl start odg
sudo systemctl status odg
```

### 5.10 SSL (HTTPS)

Sur un VPS Linux, utiliser **Certbot** (Let’s Encrypt) :

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d odg.votredomaine.com
```

Après configuration, mettre à jour `CORS_ORIGINS` dans `.env` avec `https://...` et redémarrer le service ODG.

---

## 6. Résumé des commandes utiles

| Action | Commande |
|--------|----------|
| Vérifier PostGIS | `psql "$DATABASE_URL" -c "SELECT PostGIS_Version();"` |
| Initialiser la base | `cd backend && source venv/bin/activate && python init_production_db.py` |
| Lancer Gunicorn (test) | `gunicorn -w 4 -b 127.0.0.1:5000 wsgi:application` |
| Logs application | `sudo journalctl -u odg -f` |
| Logs Nginx | `sudo tail -f /var/log/nginx/error.log` |
| Recharger Nginx | `sudo systemctl reload nginx` |
| Redémarrer l’app | `sudo systemctl restart odg` |

---

## 6.1 Sauvegardes PostgreSQL

### Script de sauvegarde

Un script `scripts/backup_postgres.sh` à la racine du projet exécute `pg_dump` et enregistre un fichier daté.

**Usage (depuis la racine du projet) :**

```bash
# Charger les variables depuis backend/.env (DATABASE_URL)
export $(grep -v '^#' backend/.env | xargs)

# Créer le répertoire des sauvegardes
mkdir -p backups

# Lancer la sauvegarde (fichier dans ./backups/ par défaut)
bash scripts/backup_postgres.sh
# ou vers un répertoire précis :
bash scripts/backup_postgres.sh /var/backups/odg
```

Le fichier généré est du type `odg_backup_YYYYMMDD_HHMMSS.sql`.

### Planification (cron)

Exemple de sauvegarde quotidienne à 2 h du matin :

```bash
crontab -e
# Ajouter :
0 2 * * * cd /var/www/odg && bash scripts/backup_postgres.sh /var/backups/odg
```

S'assurer que `DATABASE_URL` est disponible dans l'environnement du cron (ex. en sourçant `backend/.env` dans le script ou en définissant les variables dans crontab).

### Lieu de stockage

- Stocker les sauvegardes hors du répertoire web (ex. `/var/backups/odg/`).
- Conserver au moins les 7 derniers jours ; une rotation manuelle ou un script peut supprimer les fichiers plus anciens.
- Optionnel : copie vers un stockage externe (autre serveur, S3, etc.).

### Restauration

Pour restaurer une sauvegarde :

```bash
# Arrêter l'application si besoin
sudo systemctl stop odg

# Restaurer (remplacer DB_NAME et le fichier .sql)
psql -U odg_user -h localhost -d odg_mining -f /var/backups/odg/odg_backup_YYYYMMDD_HHMMSS.sql

# Redémarrer l'application
sudo systemctl start odg
```

En cas de base existante, une restauration complète peut nécessiter de recréer la base vide puis restaurer, ou d'utiliser `pg_restore` si le format est personnal (-F c).

**Option : rate limiting Nginx** — En complément de Flask-Limiter sur le login, on peut configurer Nginx avec `limit_req_zone` sur `location /api/auth/login` ; voir la doc Nginx pour les paramètres.

---

## 7. Checklist avant mise en production

- [ ] VPS Hostinger (KVM 1 ou KVM 2) provisionné.
- [ ] PostgreSQL + PostGIS installés et extension activée.
- [ ] `DATABASE_URL` et `SECRET_KEY` définis dans `.env`, CORS avec les URLs réelles (pas `*`).
- [ ] `init_production_db.py` exécuté avec succès ; tables et PostGIS vérifiés.
- [ ] Build frontend déployé (dans `backend/static/` ou répertoire Nginx).
- [ ] Gunicorn configuré (service systemd) et Nginx en reverse proxy.
- [ ] SSL activé (Certbot) et CORS en `https`.
- [ ] Sauvegardes PostgreSQL planifiées (cron + `scripts/backup_postgres.sh`, voir section 6.1).
- [ ] Authentification : mot de passe + JWT en place ; voir [Auth et sécurité](auth-et-securite.md).

---

## 8. Références projet

- [Production readiness](production-readiness-check.md)
- [Installation PostGIS](installation-postgis-guide.md)
- [Auth et sécurité](auth-et-securite.md)
- Script de déploiement : `deploy_production.sh` (à adapter chemins et noms de domaine)
- Configuration production backend : `backend/config_production.py`

---

*Document rédigé pour la configuration de l’hébergement ODG sur Hostinger par un stagiaire développeur. Dernière mise à jour : février 2026.*
