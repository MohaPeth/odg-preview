# Ce qu'il manque – ODG

Synthèse de ce qui manque ou reste à faire pour que le projet soit prêt pour une mise en production sécurisée et maintenable.

---

## Critique (avant mise en production réelle)

### 1. Authentification ✅ (implémenté)

- **Mot de passe + JWT** : le login accepte email + password, vérifie le hash, émet un JWT et renvoie `{ token, user }`.
- **Protection des routes** : toutes les routes `/api/*` (sauf login et health) exigent un JWT valide ; sinon 401.
- **Frontend** : token stocké (`odg_token`), header `Authorization: Bearer <token>`, gestion du 401 (déconnexion).

**Référence** : [Auth et sécurité](auth-et-securite.md) — phase 2 en place (password_hash, JWT, protection routes, rate limiting).

---

### 2. Base de données en production

- En **développement**, le projet peut tourner avec SQLite si `DATABASE_URL` n'est pas définie.
- En **production**, il **faut** PostgreSQL + PostGIS (Hostinger : uniquement sur VPS).
- Le script **`init_production_db.py`** existe et est compatible SQLAlchemy 2.0 ; il reste à l'exécuter sur l'environnement cible après création de la base et des extensions.

**À faire** : provisionner PostgreSQL + PostGIS (VPS ou managed), créer la base et l'utilisateur, exécuter `init_production_db.py`, vérifier avec les commandes indiquées dans [Hébergement Hostinger](hebergement-hostinger-configuration.md).

---

### 3. Dépendance Gunicorn ✅ (en place)

- **Gunicorn** est listé dans `backend/requirements.txt` (section Production).
- Le script `deploy_production.sh` utilise l'environnement virtuel et les dépendances du projet.

---

### 4. Script de déploiement (`deploy_production.sh`) ✅ (corrigé)

- La fonction **`run_tests()`** appelle `pytest tests/ -q --tb=short` si le dossier `tests/` existe et pytest est disponible.
- Sinon l'étape tests est ignorée (avertissement, pas d'échec).

---

## Important (sécurité et opérations)

### 5. Sauvegardes base de données ✅ (en place)

- **Script** : `scripts/backup_postgres.sh` exécute `pg_dump` avec `DATABASE_URL` et enregistre un fichier daté.
- **Documentation** : section 6.1 dans [Hébergement Hostinger](hebergement-hostinger-configuration.md) (cron, stockage, restauration).

---

### 6. Rate limiting / protection brute-force ✅ (en place)

- **Flask-Limiter** sur `POST /api/auth/login` (ex. 10 requêtes / minute par IP). Documenté dans [Auth et sécurité](auth-et-securite.md). Option Nginx possible (voir Hostinger).

---

### 7. Monitoring et logs ✅ (health check en place)

- **Health check** : `GET /api/health` (public) vérifie la connexion à la base et renvoie `{ status, database }` (200 ok ou 503 en erreur). Fichier : `backend/src/routes/health.py`.
- **Logs** : la production peut écrire dans un fichier (voir `config_production.py`). Optionnel : métriques Prometheus, Uptime Robot, Sentry.

---

## Mineur (amélioration continue)

### 8. Pagination

- Les listes (couches, gisements, utilisateurs, transactions) ne sont **pas paginées** ; en cas de gros volumes, les réponses et le temps de chargement peuvent devenir problématiques.

**À faire** : ajouter une pagination côté API (paramètres `page`, `per_page`) et l'utiliser côté frontend pour les tableaux et listes.

---

### 9. Données mock dans le dashboard

- **CLAUDE.md** indique que « Some statistics are hardcoded in components instead of fetched from API ». Certaines stats du dashboard peuvent encore être en dur.

**À faire** : vérifier les composants dashboard et s'assurer que toutes les statistiques viennent de l'API (ex. `/api/dashboard/summary`).

---

### 10. Documentation API

- Pas de **documentation API** formelle (OpenAPI/Swagger) ; les endpoints sont décrits dans les guides et le code.

**À faire** : optionnel — ajouter une spec OpenAPI et une UI (ex. Swagger UI) pour faciliter l'intégration et l'onboarding.

---

### 11. Tests E2E

- Pas de **tests end-to-end** (Cypress, Playwright) pour les parcours critiques (login, carte, import de couche).

**À faire** : optionnel — ajouter une suite E2E pour les scénarios prioritaires (voir [État doublons et tests](etat-doublons-et-tests.md)).

---

### 12. Blockchain (mode simulation)

- La **blockchain** est en mode simulation par défaut (`BLOCKCHAIN_ENABLED=false`).
- Le contrat **ODGTraceability.sol** n'est pas déployé ; les transactions sont simulées en base.

**À faire** : si la traçabilité blockchain est requise en production, déployer le contrat, configurer RPC et clés, et documenter la procédure (voir [Vue d'ensemble Blockchain](../architecture/blockchain-section-overview.md)).

---

## Résumé par priorité

| Priorité | Élément | Statut | Référence |
|----------|---------|--------|-----------|
| Critique | Authentification (mot de passe + JWT + protection routes) | ✅ En place | [Auth et sécurité](auth-et-securite.md) |
| Critique | PostgreSQL + PostGIS en production + init_production_db | À configurer sur le serveur | [Hébergement Hostinger](hebergement-hostinger-configuration.md) |
| Critique | Gunicorn dans requirements.txt | ✅ En place | `backend/requirements.txt` |
| Critique | deploy_production.sh : tests (pytest ou ignorés) | ✅ En place | `deploy_production.sh` |
| Important | Sauvegardes PostgreSQL (script + doc) | ✅ En place | `scripts/backup_postgres.sh`, Hostinger § 6.1 |
| Important | Rate limiting login | ✅ En place | Auth et sécurité, Flask-Limiter |
| Important | Health check | ✅ En place | `GET /api/health`, backend/src/routes/health.py |
| Mineur | Pagination listes | À ajouter | Backend + frontend |
| Mineur | Données mock dashboard | À vérifier | Composants dashboard |
| Mineur | Doc API (OpenAPI) | Optionnel | - |
| Mineur | Tests E2E | Optionnel | etat-doublons-et-tests |
| Mineur | Blockchain réelle | Si besoin métier | blockchain-section-overview |

---

*Document de synthèse — à mettre à jour au fur et à mesure des évolutions. Dernière mise à jour : février 2026.*
