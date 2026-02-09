# Authentification et sécurité ODG

État actuel et recommandations pour une mise en production sécurisée.

---

## Phase 2 implémentée (février 2026)

### Authentification

- **Login** : `POST /api/auth/login` accepte `email` + `password`. Vérification du hash avec Werkzeug ; en succès, émission d'un **JWT** (PyJWT) et renvoi de `{ "token": "<jwt>", "user": <profil minimal> }`.
- **Modèle User** : colonne `password_hash` (nullable pour migration) ; méthodes `set_password()` / `check_password()` dans [backend/src/models/user.py](../backend/src/models/user.py).
- **Frontend** : token stocké (ex. `localStorage` sous `odg_token`), profil sous `odg_user` ; header `Authorization: Bearer <token>` sur les appels API ; gestion du 401 (déconnexion et redirection vers login).

### Autorisation

- **Middleware** : [backend/src/auth.py](../backend/src/auth.py) décode le JWT et attache l'utilisateur à `g.current_user`. Dans [backend/src/main.py](../backend/src/main.py), un `before_request` exige un JWT valide pour toutes les routes `/api/*` sauf `POST /api/auth/login` et `GET /api/health`. Sans token valide : 401.

### Rate limiting

- **Flask-Limiter** sur `POST /api/auth/login` (ex. 10 requêtes / minute par IP). Configuration dans [backend/src/limiter.py](../backend/src/limiter.py), décorateur sur la route login dans [backend/src/routes/user.py](../backend/src/routes/user.py).

### Fichiers concernés

| Rôle | Fichier |
|------|--------|
| Modèle User + password_hash | `backend/src/models/user.py` |
| Migration password_hash | `backend/src/migrations/add_password_hash_to_users.sql` |
| Login JWT | `backend/src/routes/user.py` |
| Middleware / protection routes | `backend/src/auth.py`, `backend/src/main.py` |
| Health check (public) | `backend/src/routes/health.py` |
| Rate limiting | `backend/src/limiter.py` |
| Comptes de test (mots de passe) | `backend/create_test_users.py` |
| Frontend token + 401 | `frontend/src/services/authUtils.js`, `frontend/src/App.jsx`, services API |

---

## Objectif cible (phase 2)

- **Authentification** : mot de passe (hash) + vérification au login ; émission d’un **JWT** ou utilisation de **sessions Flask** (cookie sécurisé).
- **Autorisation** : protection des routes sensibles par rôle (admin, operator, partner) via un middleware ou décorateur qui vérifie le token/session et le rôle.
- **Côté frontend** : envoi du token (header `Authorization`) ou utilisation de cookies de session ; suppression du stockage du profil en clair dans `localStorage` si sensible, ou renforcement (token uniquement, pas de données sensibles).

---

## Étapes recommandées (phase 2)

1. **Modèle User**
   - Ajouter une colonne `password_hash` (ou `password` avec hash côté application) dans la table `users`.
   - Utiliser `werkzeug.security.generate_password_hash` / `check_password_hash` ou bcrypt pour le hash.

2. **Inscription / premier mot de passe**
   - Soit migration des utilisateurs existants avec mot de passe par défaut temporaire (à changer au premier login).
   - Soit endpoint d’« activation » ou de définition du mot de passe par l’admin.

3. **Login**
   - Modifier `POST /api/auth/login` pour accepter `email` + `password`.
   - Vérifier le mot de passe avec le hash stocké.
   - En cas de succès : générer un **JWT** (ex. avec `PyJWT`) ou créer une **session Flask** (cookie `HttpOnly`, `Secure` en HTTPS).
   - Renvoyer le token (ou confirmer la session) et un profil minimal (id, role, etc.) sans données sensibles.

4. **Protection des routes**
   - Créer un décorateur ou middleware qui :
     - lit le JWT (header `Authorization`) ou la session ;
     - vérifie la validité et la non‑expiration ;
     - attache l’utilisateur au contexte (ex. `g.current_user`) ;
     - optionnel : vérifie le rôle (admin / operator / partner) selon la route.
   - Appliquer ce décorateur aux routes sensibles (CRUD users, deposits, blockchain, geospatial upload, etc.).
   - Laisser publiques uniquement les routes nécessaires (ex. login, santé).

5. **Frontend**
   - Après login, stocker le token (ex. en mémoire + refresh) ou s’appuyer sur les cookies de session.
   - Envoyer le token dans `Authorization: Bearer <token>` pour les appels API protégés.
   - Gérer l’expiration (déconnexion, refresh token si implémenté).

6. **Sécurité générale**
   - HTTPS uniquement en production.
   - `SECRET_KEY` forte et unique.
   - CORS restreint aux origines autorisées.
   - Limitation des tentatives de login (rate limiting).
   - Ne jamais commiter les fichiers `.env` ni les clés.

---

## Références dans le projet

- **Login** : [backend/src/routes/user.py](../backend/src/routes/user.py) — route `login` (email + password, JWT).
- **Modèle User** : [backend/src/models/user.py](../backend/src/models/user.py) (password_hash, set_password, check_password).
- **Auth / protection** : [backend/src/auth.py](../backend/src/auth.py), [backend/src/main.py](../backend/src/main.py).
- **Health** : [backend/src/routes/health.py](../backend/src/routes/health.py).
- **Contexte global** : [docs/architecture/analyse-projet-complet.md](../architecture/analyse-projet-complet.md) (section Sécurité).

---

*Document mis à jour après implémentation de la phase 2 (février 2026).*
