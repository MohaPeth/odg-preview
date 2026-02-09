# Lancer les tests – ODG

Comment exécuter les tests automatisés (backend et frontend).

---

## Backend (pytest)

Depuis la racine du projet :

```bash
cd backend
pytest
```

Ou uniquement le dossier de tests :

```bash
cd backend
pytest tests/
```

**Exécution avec rapport de couverture (optionnel) :**

```bash
cd backend
pytest tests/ --cov=src --cov-report=term-missing
```

**Prérequis :** environnement virtuel activé, dépendances installées (`pip install -r requirements.txt`). Les tests utilisent une base SQLite en mémoire (voir `backend/tests/conftest.py`).

---

## Frontend (Vitest)

Depuis la racine du projet :

```bash
cd frontend
pnpm test
```

Ou avec npm :

```bash
cd frontend
npm run test
```

**Exécution une fois (CI / validation) :**

```bash
cd frontend
pnpm run test:run
# ou
npm run test:run
```

**Prérequis :** dépendances installées (`pnpm install` ou `npm install`). Les tests utilisent jsdom (voir `frontend/vite.config.js` → `test`).

---

## Où sont les tests ?

| Pile     | Dossier / Fichiers                    | Config        |
|----------|----------------------------------------|---------------|
| Backend  | `backend/tests/` (conftest.py, test_*.py) | `backend/pytest.ini` |
| Frontend | `frontend/src/**/*.test.js` ou `*.spec.js` | `frontend/vite.config.js` (section test) |

---

## Voir aussi

- [Contribuer et lancer les tests](contribuer-et-tests.md) – parcours Contributeur
- [État doublons et tests](../operations/etat-doublons-et-tests.md) – état des doublons et des tests
