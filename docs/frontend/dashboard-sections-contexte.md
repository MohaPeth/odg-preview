# Dashboard ODG – Contexte et description des sections

**Plateforme** : ODG (Ogooué Digital Gold) – Géoportail minier et traçabilité blockchain pour l’industrie minière gabonaise.  
**Document** : Vue d’ensemble du dashboard, contexte métier et description de chaque section.

---

## 1. Contexte du dashboard

### 1.1 Objectif de la plateforme

ODG est une application web full-stack qui permet de :

- **Cartographier** les gisements miniers, zones d’exploitation et infrastructures au Gabon (WebGIS).
- **Gérer** les couches géospatiales (import KML, GeoJSON, Shapefile, etc.) et leur visibilité sur la carte.
- **Tracer** les flux de matériaux (or, diamant, etc.) via une blockchain (mode simulation ou réel).
- **Gérer** les acteurs : opérateurs miniers, partenaires investisseurs, utilisateurs (admin, opérateur, partenaire).

Le dashboard est l’interface principale après connexion. Il s’adresse aux **administrateurs** et **opérateurs** (vue complète) ou aux **partenaires** (vue lecture seule dédiée).

### 1.2 Structure globale

- **Entrée** : `App.jsx` – selon l’authentification et le rôle, affiche soit `Login`, soit `MainApp` (admin/opérateur), soit `PartnerDashboard` (partenaire).
- **Dashboard principal (admin/opérateur)** : `MainApp.jsx` – barre latérale (sidebar) + zone de contenu. La sidebar contient les liens vers chaque section ; le contenu change selon l’onglet actif.
- **Dashboard partenaire** : `PartnerDashboard.jsx` – tableau de bord simplifié (gisements, portefeuille, carte) en lecture seule.

Les sections listées ci-dessous correspondent aux **onglets de la sidebar** de `MainApp` et à leur contenu.

---

## 2. Sections du dashboard principal (MainApp)

### 2.1 Accueil (Home)

| Élément | Description |
|--------|-------------|
| **Id** | `home` |
| **Composant** | `HomeContent` (défini dans `MainApp.jsx`) |
| **Rôle** | Page d’accueil du dashboard : présentation de la plateforme et accès rapide aux autres sections. |
| **Contenu** | Hero (titre ODG, sous-titre), boutons « Explorer le Géoportail » et « Voir la Blockchain », cartes cliquables (Géoportail WebGIS, Traçabilité Blockchain, Analyses & Rapports), aperçu des opérateurs miniers (API), aperçu des partenaires (API), statistiques globales (placeholder ou API dashboard), bloc « À propos d’ODG ». |
| **APIs / Données** | Opérateurs (`fetchOperators`), partenaires (filtrés depuis `getUsers`), optionnellement `/api/dashboard/summary` pour les stats. |
| **Navigation** | Clic sur une carte ou un bouton change l’onglet actif (`setActiveTab`) vers `webgis`, `blockchain` ou `analytics`. |

---

### 2.2 Géoportail (WebGIS)

| Élément | Description |
|--------|-------------|
| **Id** | `webgis` |
| **Composant** | `WebGISMap.jsx` |
| **Rôle** | Carte interactive (Leaflet) pour visualiser gisements, zones d’exploitation, infrastructures et couches géospatiales importées. |
| **Contexte** | C’est le **géoportail minier** : l’utilisateur voit la carte du Gabon avec les données minières et peut interagir (recherche, filtres, ajout de gisement, gestion des couches). |
| **Structure** | Panneau latéral (sidebar) + carte en plein écran. Le panneau peut être replié (desktop) ou masqué (mobile). |
| **En-tête du panneau** | Titre « Géoportail Minier ODG » avec icône, bouton pour replier le panneau (desktop). |
| **Onglets du panneau** | **Gisements** : bouton « Ajouter un gisement », recherche, légende, liste des gisements (cliquables pour centrer la carte). **Couches** : bouton « Importer une couche », tableau compact des couches géospatiales (avec visibilité, « Agrandir » pour ouvrir le modal « Gestion des Couches Géospatiales »). |
| **Carte** | Tuiles OpenStreetMap, marqueurs (gisements), polygones (zones), polylines (infrastructures), rendu dynamique des couches géospatiales (GeoJSON, etc.). |
| **APIs / Données** | Gisements (`ApiService.getDeposits`), couches (`useGeospatialLayers`), dépôts/zones/infrastructures (mock ou API selon config). |

**Remarque** : Le panneau « Couches » dans le Géoportail réutilise `LayersManagementTable` en version compacte ; le bouton « Agrandir » ouvre le même modal que dans la section Couches du dashboard.

---

### 2.3 Couches (Layers)

| Élément | Description |
|--------|-------------|
| **Id** | `layers` |
| **Composant** | `LayersWorkspace.jsx` (qui contient `LayersManagementTable`, `AddGeospatialLayerModalV2`) |
| **Rôle** | Gestion centralisée des couches géospatiales : import, liste, filtres, visibilité, export, suppression. |
| **Contenu** | En-tête « Gestion des Couches », boutons Rafraîchir et Importer une couche, cartes de stats (Total, Visibles, Masquées), carte « Tableau des couches » avec `LayersManagementTable` (recherche, filtre par statut/type, tableau ou grille, bouton « Agrandir » pour le modal plein écran), conseils d’utilisation. |
| **APIs / Données** | `/api/geospatial/layers` (liste, pagination), mise à jour visibilité (PUT), suppression (DELETE), import (upload). |
| **Modal « Gestion des Couches Géospatiales »** | Ouvert via « Agrandir » dans le tableau. Affiche les couches en cartes (nom, statut, type, format, éléments, date, visibilité) avec menu d’actions (Modifier, Exporter GeoJSON/KML, Supprimer). Un seul bouton de fermeture (X). |

---

### 2.4 Blockchain

| Élément | Description |
|--------|-------------|
| **Id** | `blockchain` |
| **Composant** | `BlockchainDashboard.jsx` |
| **Rôle** | Visualisation du statut blockchain, des transactions et des certificats de traçabilité. |
| **Contenu** | Statut de la blockchain (API), graphiques (évolution des transactions, distribution par matériau), onglets Transactions / Certificats / Chaîne d’approvisionnement, liste des transactions avec recherche et actions (publier sur la blockchain, etc.). |
| **APIs / Données** | `/api/blockchain-integration/status`, `/api/blockchain/transactions`, `/api/blockchain/stats`, publication via `/api/blockchain-integration/publish/:id`. |
| **Contexte** | En production, la blockchain enregistre de manière immuable les flux de matériaux ; en développement, un mode simulation est souvent utilisé. |

---

### 2.5 Analyses et Rapports (Analytics)

| Élément | Description |
|--------|-------------|
| **Id** | `analytics` |
| **Composant** | `AnalyticsWorkspace.jsx` |
| **Rôle** | Tableau de bord d’analyse : indicateurs clés et graphiques pour le pilotage. |
| **Contenu** | Cartes KPI (Gisements actifs, Transactions confirmées, Volume tracé, Couches actives, Opérateurs), graphiques (statut des transactions, transactions par type de matériau, gisements WebGIS par type/statut, gisements par entreprise), bouton Actualiser, synthèse textuelle des indicateurs. |
| **APIs / Données** | `getAnalyticsData()` agrège `/api/dashboard/summary`, `/api/blockchain/stats`, `/api/webgis/stats`. |
| **Remarque** | Les graphiques sont alimentés par les APIs ; en mode démo ou sans backend, certaines valeurs peuvent être à zéro avec message explicatif. |

---

### 2.6 Partenaires

| Élément | Description |
|--------|-------------|
| **Id** | `partners` |
| **Composant** | `PartnersManagement.jsx` |
| **Rôle** | Gestion des comptes « partenaire » (investisseurs, lecteurs) : création, liste, détail, modification, suppression. |
| **Contenu** | En-tête, bouton « Créer un partenaire », stats (Total, Actifs, En attente, Avec opérateur), filtres (recherche, statut), tableau (partenaire, opérateur associé, statut, inscription, dernière connexion, actions Voir / Modifier / Supprimer), dialogs Création, Détail, Modification, Confirmation suppression. |
| **APIs / Données** | Partenaires = utilisateurs avec `role: "partner"` : `getUsers()`, `createUser`, `updateUser`, `deleteUser` (via `usersApi.js`). Opérateurs pour association optionnelle : `fetchOperators()`. |

---

### 2.7 Utilisateurs

| Élément | Description |
|--------|-------------|
| **Id** | `users` |
| **Composant** | `UserManagement.jsx` |
| **Rôle** | Gestion de tous les utilisateurs (admin, opérateur, partenaire, analyste) : CRUD, rôle, statut, opérateur associé. |
| **Contenu** | Bouton « Ajouter un utilisateur », stats (Total, Partenaires, Actifs, En attente), filtres (recherche, rôle), tableau des utilisateurs avec actions Modifier / Supprimer, dialogs Ajout et Édition (nom, email, rôle, opérateur associé, etc.). |
| **APIs / Données** | `getUsers`, `createUser`, `updateUser`, `deleteUser` (`/api/users`). Rôles côté backend : `admin`, `operator`, `partner` (et éventuellement d’autres valeurs selon le modèle). |

---

### 2.8 Paramètres (Settings)

| Élément | Description |
|--------|-------------|
| **Id** | `settings` |
| **Composant** | `SettingsWorkspace.jsx` |
| **Rôle** | Vue de configuration et d’état de la plateforme (environnement, sécurité, rôles, base de données, checklist production). Les données affichées sont principalement illustratives (non connectées à une API de config). |
| **Contenu** | Bandeau « Données illustratives », cartes Environnement (mode, API, front, mode maintenance), Sécurité & audits, Rôles & accès (liste des rôles alignée backend + bouton « Gérer les utilisateurs » qui bascule vers l’onglet Utilisateurs), Base de données & tables, Variables d’environnement, Checklist avant production. |
| **Remarque** | Le bouton « Gérer les utilisateurs » appelle `onNavigateToUsers()` fourni par `MainApp` pour changer l’onglet actif vers « Utilisateurs ». |

---

## 3. Éléments communs au dashboard

### 3.1 Barre latérale (sidebar)

- **Contenu** : Logo / titre « ODG Platform », boutons pour replier la sidebar (desktop) et la fermer (mobile), liste des onglets (Accueil, Géoportail, Couches, Blockchain, Analyses, Partenaires, Utilisateurs, Paramètres).
- **Comportement** : Sur desktop, la sidebar peut être repliée (icônes seules). Sur mobile, elle est en overlay avec bouton menu pour ouvrir/fermer.

### 3.2 En-tête (header) de la zone de contenu

- **Contenu** : Bouton menu (mobile), nom de l’onglet actif, nom ou email de l’utilisateur connecté (si disponible), bouton « Déconnexion ».
- **Comportement** : Le clic sur « Déconnexion » appelle `onLogout` passé par `App.jsx` et redirige vers la page de connexion.

### 3.3 Responsivité

- Padding des zones de contenu : `p-4 sm:p-6`.
- Tables (Partenaires, Utilisateurs, Couches) : conteneur en `overflow-x-auto` pour éviter le débordement horizontal sur petit écran.
- Modals : largeur max et hauteur max (ex. `max-w-[95vw]`, `max-h-[90vh]`) avec contenu scrollable.

---

## 4. Dashboard partenaire (PartnerDashboard)

- **Affiché quand** : `userProfile.role === "partner"` dans `App.jsx`.
- **Contenu** : Tableau de bord simplifié : titre « Tableau de bord partenaire », badge « Accès partenaire », boutons Actualiser et Déconnexion, cartes de stats (gisements suivis, parts totales, valeur estimée, dernière MAJ), liste/cartes des gisements avec parts partenaires, carte Leaflet (aperçu), éventuellement d’autres blocs en lecture seule.
- **Données** : Actuellement mock (`mockDeposits`) ; à terme, à connecter à des APIs « partenaire » (dépôts liés, parts, etc.).

---

## 5. Fichiers principaux

| Rôle | Fichier |
|------|---------|
| Point d’entrée dashboard | `frontend/src/App.jsx` |
| Dashboard admin/opérateur | `frontend/src/components/MainApp.jsx` |
| Dashboard partenaire | `frontend/src/components/PartnerDashboard.jsx` |
| Géoportail (carte + panneau Gisements/Couches) | `frontend/src/components/WebGISMap.jsx` |
| Gestion des couches (hors carte) | `frontend/src/components/LayersWorkspace.jsx`, `LayersManagementTable.jsx` |
| Blockchain | `frontend/src/components/BlockchainDashboard.jsx` |
| Analyses | `frontend/src/components/AnalyticsWorkspace.jsx` |
| Partenaires | `frontend/src/components/PartnersManagement.jsx` |
| Utilisateurs | `frontend/src/components/UserManagement.jsx` |
| Paramètres | `frontend/src/components/SettingsWorkspace.jsx` |

---

## 6. Améliorations apportées au dashboard (responsivité)

- **MainApp** : Zone de contenu avec `overflow-x-hidden` et padding responsif (`p-4 sm:p-6`).
- **WebGISMap** : Conteneur racine `overflow-hidden min-w-0` ; panneau latéral `max-w-[85vw]` sur mobile, `overflow-x-hidden` ; zone carte `min-w-0` ; onglet Couches avec wrapper `overflow-x-auto` autour du tableau et bouton « Importer une couche » adapté (truncate, flex-wrap).
- **Tables** (Partenaires, Utilisateurs, Couches) : `overflow-x-auto` et padding responsif sur les cartes.

---

*Document à jour avec la structure du projet (février 2026). À faire évoluer en fonction des changements d’interface et des nouvelles sections.*
