# État des doublons et des tests – ODG

**Date :** 4 février 2026

---

## 1. Doublons

### Vérifications effectuées

| Élément | État | Détail |
|--------|------|--------|
| **Config Flask** | OK | Un seul `app.config.from_object(Config)` dans `main.py` (doublon supprimé). |
| **Blueprints** | OK | Chaque blueprint enregistré une seule fois, préfixes distincts (`/api`, `/api/webgis`, `/api/dashboard`, etc.). |
| **Routes dépôts** | OK | CRUD gisements : `webgis` (`/api/webgis/deposits`). Import fichier : `mining_import` (`/api/mining/import/deposits`). Rôles différents, pas de doublon. |
| **Routes couches** | OK | Couches géospatiales : `geospatial_import` (`/api/geospatial/layers`). Pas de `/layers` dans webgis. |
| **deposit_endpoints** | OK | Archivé dans `backend/_archive/deposit_endpoints_archive.py`, plus aucun fichier actif dupliqué. |
| **URL API frontend** | OK | `api.js`, `geospatialApi.js`, `operatorsApi.js`, `usersApi.js` utilisent des URLs **relatives** (`/api/...`). |

### Point à garder en tête

- **`frontend/src/config/index.js`** : `apiBaseUrl` a un fallback `'http://localhost:5000'`. Utilisé uniquement pour l'**affichage** dans Paramètres (SettingsWorkspace). Pour que l'affichage soit cohérent en prod (même origine), le fallback peut être `''` et définir `VITE_API_BASE_URL` en production. Optionnel.

**Conclusion :** Aucun doublon bloquant. Architecture cohérente après les corrections du plan.

---

## 2. Modes de test

### État actuel

| Couche | Tests automatisés | Remarque |
|--------|-------------------|----------|
| **Backend** | Oui | `pytest`, `pytest-flask`, `pytest-cov` dans `requirements.txt` ; `backend/tests/` (conftest.py, test_dashboard.py, test_webgis_deposits.py) ; `pytest.ini`. |
| **Frontend** | Oui | Vitest, @testing-library/react, jsdom ; script `test` et `test:run` dans `package.json` ; tests dans `src/**/*.test.js`. |
| **Intégration** | Non | Pas de suite de tests E2E (ex. Cypress/Playwright) ni de scénarios d'intégration API documentés et automatisés. |

**Comment lancer les tests :** voir [Lancer les tests](../guides/lancer-les-tests.md) (commandes backend `pytest` et frontend `pnpm test` / `npm run test`).

---

## 3. Synthèse

- **Doublons :** Aucun doublon critique identifié ; config et routes sont cohérents.
- **Tests :** Suite de tests en place (pytest backend, Vitest frontend). Procédure détaillée : [Lancer les tests](../guides/lancer-les-tests.md). E2E optionnel pour plus tard.
