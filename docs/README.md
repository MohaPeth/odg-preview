# Documentation ODG - Ogooué Digital Gold

Index principal de la documentation du projet, organisée par responsabilité (Clean Architecture / séparation des concerns).

---

## Par où commencer ?

Choisissez votre profil pour accéder au bon parcours :

| Profil | Parcours | Lien |
|--------|----------|------|
| **Je suis développeur / nouveau sur le projet** | Suivre **exactement** les étapes : clone, variables d’env, base, migration auth, comptes de test, lancer backend et frontend | [Démarrage développeur](guides/demarrage-developpeur.md) |
| **Je suis utilisateur métier** | Admin, opérateur, partenaire – utilisation de la plateforme | [Utilisation de la plateforme](guides/guide-utilisation-odg.md) |
| **Je suis en charge du déploiement / de la production** | PostGIS, production, auth (déjà en place) | [Opérations](operations/README.md) : [PostGIS](operations/installation-postgis-guide.md), [Auth et sécurité](operations/auth-et-securite.md) |
| **Je contribue au code / aux tests** | Lancer les tests, structure, où contribuer | [Contribuer et lancer les tests](guides/contribuer-et-tests.md) |

---

## Structure de la documentation

```
docs/
├── README.md                 ← Vous êtes ici
├── architecture/             # Décisions techniques, analyse, vue système
├── guides/                   # Installation, démarrage, utilisation
├── metier/                   # Fonctionnalités, plans, règles métier
├── operations/               # Déploiement, production, PostGIS
└── historique/               # Corrections, rapports (référence)
```

---

## Architecture

Documentation technique et décisions d'architecture.

| Document | Description |
|----------|-------------|
| [Analyse complète du projet](architecture/analyse-projet-complet.md) | Stack, backend/frontend, modèles, API, points d'attention |
| [Vue d'ensemble Blockchain](architecture/blockchain-section-overview.md) | Module blockchain et intégration |
| [Modules ODG](architecture/readme-odg-modules.md) | Présentation des modules applicatifs |

---

## Guides

Guides pas à pas : démarrage, utilisation, tests manuels, géospatial.

| Document | Description |
|----------|-------------|
| [Démarrage développeur](guides/demarrage-developpeur.md) | **Parcours principal** : ordre exact (clone → .env → base → migration auth → create_test_users → run backend/frontend). Où trouver les variables d’environnement, comptes de test (admin@odg.ga / odg2025!). |
| [Installation Windows (détaillée)](guides/installation-windows.md) | Prérequis et installation sous Windows (sans Docker) |
| [Lancement backend](guides/guide-lancement-backend.md) | Démarrer le serveur backend seul |
| [Utilisation ODG](guides/guide-utilisation-odg.md) | Utilisation de la plateforme (métier) |
| [Tests manuels](guides/tests-manuels.md) | Checklist de test manuel (interface, couches, carte) |
| [Lancer les tests (automatisés)](guides/lancer-les-tests.md) | Commandes pytest (backend) et Vitest (frontend) |
| [Export géospatial](guides/guide-export-geospatial.md) | Export des données géospatiales |
| [Import géospatial](guides/readme-geospatial-import.md) | Import KML, SHP, GeoJSON, etc. |

---

## Métier

Fonctionnalités, plans et règles métier.

| Document | Description |
|----------|-------------|
| [Plan fonctionnalités ODG](metier/plan-fonctionnalites-odg.md) | Fonctionnalités prévues |
| [Plan implémentation géospatial](metier/plan-implementation-geospatial.md) | Roadmap géospatial |
| [Phase 1 – Plan de projet](metier/phase-1-plan.md) | Planning et objectifs phase 1 (roadmap) |

---

## Opérations

Déploiement, production, base de données.

| Document | Description |
|----------|-------------|
| [Installation PostGIS](operations/installation-postgis-guide.md) | Configuration PostGIS pour ODG |
| [Production readiness](operations/production-readiness-check.md) | Checklist mise en production |
| [Auth et sécurité](operations/auth-et-securite.md) | État actuel auth, recommandations phase 2 |
| [État doublons et tests](operations/etat-doublons-et-tests.md) | Vérification doublons, état des tests automatisés |
| [Hébergement Hostinger – configuration](operations/hebergement-hostinger-configuration.md) | Type d'hébergement (VPS), configuration détaillée pour le stagiaire |
| [Ce qu'il manque](operations/ce-quil-manque.md) | Synthèse des manques et actions à faire (auth, DB, déploiement, monitoring) |
| [Intégration géospatial - tests](operations/test-integration-geospatial.md) | Tests d'intégration géospatiale |

---

## Archive / Historique

Rapports de corrections et vérifications, conservés pour traçabilité. Ils ne font pas partie du parcours principal.

**[→ Voir l'historique des corrections](historique/README.md)**

---

## Références racine

- **[README principal](../README.md)** : Vue d'ensemble et démarrage rapide du dépôt.
- **[CLAUDE.md](../CLAUDE.md)** : Contexte pour l'assistant IA (stack, commandes, patterns).

---

*Documentation organisée selon les principes de séparation des responsabilités et de maintenabilité.*
