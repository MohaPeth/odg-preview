# Analyse complète Frontend ODG – UI & UX

Document d’analyse du frontend (structure, parcours, états, accessibilité, points à améliorer).

---

## 1. Structure et parcours

### 1.1 Entrée

| Écran | Fichier | Rôle |
|-------|---------|------|
| **Login** | `Login.jsx` | Connexion email + mot de passe, "Se souvenir de moi", lien "Mot de passe oublié" (non fonctionnel) |
| **App** | `App.jsx` | Bascule Login / MainApp / PartnerDashboard selon auth et rôle. Mode démo (`DEMO_NO_AUTH`) pour afficher l’app sans backend. |

### 1.2 Après connexion (admin / opérateur)

| Zone | Fichier | Contenu |
|------|---------|--------|
| **MainApp** | `MainApp.jsx` | Sidebar (Accueil, Géoportail, Couches, Blockchain, Analyses, Partenaires, Utilisateurs, Paramètres) + zone de contenu |
| **Accueil** | `MainApp.jsx` (HomeContent) | Hero, cartes fonctionnalités, opérateurs (API), partenaires (API), stats globales (placeholder), À propos ODG |
| **Géoportail** | `WebGISMap.jsx` | Carte Leaflet, gisements/zones/infrastructures (mock + API couches), recherche, modals ajout gisement / couche |
| **Couches** | `LayersWorkspace.jsx` | Stats, tableau `LayersManagementTable`, import via `AddGeospatialLayerModalV2` |
| **Blockchain** | `BlockchainDashboard.jsx` | Statut blockchain (API), graphiques (mock), transactions, certificats |
| **Analyses** | `MainApp.jsx` (AnalyticsContent) | Placeholder "en développement" |
| **Partenaires** | `PartnersManagement.jsx` | Liste, recherche, filtres, création partenaire (API) |
| **Utilisateurs** | `UserManagement.jsx` | Liste, recherche, filtres, CRUD utilisateurs (API) |
| **Paramètres** | `SettingsWorkspace.jsx` | Blocs Environnement, Base de données, Rôles (données mock) |

### 1.3 Partenaire (lecture seule)

| Zone | Fichier | Contenu |
|------|---------|--------|
| **PartnerDashboard** | `PartnerDashboard.jsx` | Tableau de bord partenaire (gisements mock, stats portefeuille, carte) |

---

## 2. Points forts UI/UX

- **Design cohérent** : shadcn/ui (Card, Button, Badge, Tabs, Dialog, Table, etc.) + Tailwind, palette bleu/violet.
- **Loading** : Présent sur Login, Accueil (opérateurs/partenaires), PartnerDashboard, BlockchainDashboard, LayersManagementTable, PartnersManagement, UserManagement (spinner ou texte "Chargement...").
- **États vides** : "Aucun opérateur", "Aucun partenaire", "Aucune couche disponible" / "Aucun résultat pour cette recherche", "Aucun partenaire enregistré".
- **Gestion d’erreur** : Alert sur Login ; `operatorsError` sur Accueil ; `error` dans UserManagement, PartnersManagement, LayersManagementTable.
- **Responsive** : Sidebar repliable (desktop), overlay mobile, bouton menu, grilles `md:grid-cols-2` / `lg:grid-cols-3`.
- **Modals** : Import couche (étapes, progression, erreur/succès), ajout gisement, suppression couche avec confirmation.
- **Navigation** : Sidebar claire, onglets, boutons "Explorer le Géoportail" / "Voir la Blockchain" depuis l’Accueil.

---

## 3. Manques et améliorations

### 3.1 Critique – Déconnexion et profil

| Problème | Détail | Action recommandée |
|----------|--------|--------------------|
| **Pas de bouton Déconnexion (MainApp)** | `MainApp` est appelé avec `userProfile` et `onLogout` mais ne les déclare pas en props (`MainApp = () =>`) et ne les utilise pas. Aucun moyen de se déconnecter depuis l’app admin/opérateur. | Déclarer `userProfile` et `onLogout` en props et ajouter dans le header un menu utilisateur (nom/email + bouton "Déconnexion") appelant `onLogout`. |
| **Partenaire : déconnexion** | `PartnerDashboard` reçoit `onLogout` depuis `App.jsx` mais n’affiche pas de bouton Déconnexion dans l’extrait analysé. | Vérifier si un bouton existe ; sinon ajouter "Déconnexion" dans l’en-tête du tableau de bord partenaire. |
| **Profil dans le header** | Pas d’affichage du nom ou de l’email de l’utilisateur connecté dans le header MainApp. | Afficher nom/email (ou avatar) + dropdown avec "Déconnexion" dans le header. |

### 3.2 Important – Feedback et données

| Problème | Détail | Action recommandée |
|----------|--------|--------------------|
| **Toasts globaux absents** | Le composant Sonner (`Toaster`) existe dans `ui/sonner.jsx` mais n’est pas rendu dans `main.jsx`. Aucun toast après création/suppression utilisateur ou partenaire, import couche, etc. | Monter `<Toaster />` dans `main.jsx` (ou `App.jsx`) et utiliser `toast.success()` / `toast.error()` dans les handlers (UserManagement, PartnersManagement, AddGeospatialLayerModalV2, etc.). |
| **Statistiques globales (Accueil)** | La carte "Statistiques globales" est un placeholder non connecté à l’API. | Connecter à `/api/dashboard/summary` (ou équivalent) et afficher les indicateurs réels. |
| **Analyses** | L’onglet "Analyses" est un placeholder "Fonctionnalité en Développement". | Soit connecter à des endpoints d’analyses, soit afficher un message clair "Bientôt disponible" et masquer l’entrée si non livré. |
| **PartnerDashboard** | Données gisements/portefeuille en mock (`mockDeposits`), pas d’appel API. | Remplacer par des appels API réels (ex. dépôts liés au partenaire, parts) si le backend le permet. |

### 3.3 Mineur – UX et accessibilité

| Problème | Détail | Action recommandée |
|----------|--------|--------------------|
| **Mot de passe oublié** | Lien présent sur la page Login mais non fonctionnel. | Implémenter un flux "Mot de passe oublié" (email + backend) ou retirer le lien en attendant. |
| **Correction typo** | MainApp ligne ~233 : séparateur pays/statut opérateur affiché " b7 " au lieu du caractère " • ". | Remplacer par " • " (déjà corrigé dans le cadre de cette analyse). |
| **Paramètres** | Données Environnement / Tables / Rôles en mock. | Soit connecter à une API de config (si prévu), soit indiquer "Informations illustratives" pour éviter toute confusion. |
| **Accessibilité** | Non audité en détail. | Vérifier labels des champs, focus clavier, aria-labels sur boutons/icônes, contraste (WCAG). |
| **Messages 401** | En cas de token expiré, les services déclenchent `odg-unauthorized` et déconnexion. | S’assurer qu’un message court ("Session expirée, veuillez vous reconnecter") s’affiche (toast ou bandeau) avant redirection login. |

---

## 4. Synthèse par écran

| Écran | Loading | Empty | Erreur | Déconnexion | Données réelles |
|-------|---------|-------|--------|-------------|-----------------|
| Login | Oui | - | Oui (Alert) | - | - |
| MainApp (Accueil) | Oui (opérateurs, partenaires) | Oui | Oui (opérateurs) | Non | Partiel (stats globales placeholder) |
| WebGISMap | - | - | - | Non | Partiel (couches API, gisements mock) |
| LayersWorkspace | Via tableau | Via tableau | Via tableau | Non | Oui (API couches) |
| BlockchainDashboard | Oui | - | - | Non | Partiel (statut API, graphiques mock) |
| Analyses | - | - | - | Non | Non (placeholder) |
| UserManagement | Oui | - | Oui | Non | Oui (API users) |
| PartnersManagement | Oui | Oui | Oui | Non | Oui (API users/partenaires) |
| SettingsWorkspace | - | - | - | Non | Non (mock) |
| PartnerDashboard | Oui | - | - | À vérifier | Non (mock) |

---

## 5. Recommandations prioritaires

1. **Déconnexion** : Ajouter dans MainApp (et PartnerDashboard si absent) un header avec profil utilisateur + bouton "Déconnexion" utilisant `onLogout`.
2. **Toasts** : Monter `<Toaster />` et utiliser `toast.success` / `toast.error` pour les actions (CRUD, import couche, etc.).
3. **Statistiques Accueil** : Brancher la section "Statistiques globales" sur `/api/dashboard/summary`.
4. **Mot de passe oublié** : Implémenter ou retirer le lien sur la page Login.
5. **Accessibilité** : Audit rapide (labels, focus, aria) sur Login, header et formulaires principaux.

---

*Analyse réalisée sur la base du code frontend (février 2026). À mettre à jour au fil des évolutions.*
