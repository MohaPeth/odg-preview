# Contribuer et lancer les tests – ODG

Parcours pour les contributeurs : lancer les tests automatisés, comprendre la structure du code et les points d’entrée utiles.

---

## Lancer les tests

### Backend (pytest)

Depuis la racine du projet :

```bash
cd backend
pytest
```

Détails et options (couverture, etc.) : [Lancer les tests](lancer-les-tests.md).

### Frontend (Vitest)

Depuis la racine du projet :

```bash
cd frontend
pnpm test
# ou : npm run test
```

Exécution une fois (CI) : `pnpm run test:run` ou `npm run test:run`.  
Détails : [Lancer les tests](lancer-les-tests.md).

---

## Où sont les tests ?

| Pile     | Emplacement                          | Config              |
|----------|--------------------------------------|---------------------|
| Backend  | `backend/tests/` (conftest.py, test_*.py) | `backend/pytest.ini` |
| Frontend | `frontend/src/**/*.test.js` (ou `*.spec.js`) | `frontend/vite.config.js` (section test) |

---

## Structure des dossiers utiles

- **Backend** : `backend/src/` — `main.py`, `routes/`, `models/`, `services/`, `config/`  
- **Frontend** : `frontend/src/` — `components/`, `services/`, `App.jsx`, `main.jsx`  

Voir aussi [CLAUDE.md](../../CLAUDE.md) pour les patterns et commandes du projet.

---

## Checklist avant PR (recommandée)

1. Lancer les tests backend : `cd backend && pytest`  
2. Lancer les tests frontend : `cd frontend && pnpm run test:run`  
3. Linter : `cd frontend && pnpm run lint` (frontend) ; vérifier le code Python (format, bonnes pratiques)  

---

## Voir aussi

- [Lancer les tests](lancer-les-tests.md) — commandes détaillées backend et frontend  
- [État doublons et tests](../operations/etat-doublons-et-tests.md) — état des doublons et des tests automatisés  
- [Tests manuels](tests-manuels.md) — checklist de test manuel de l’interface
