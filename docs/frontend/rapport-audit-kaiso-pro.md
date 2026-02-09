# Rapport d'audit – Application (Kaiso Pro / ODG)

**Date** : février 2026  
**Périmètre** : Frontend React (ODG Platform) et cohérence avec le backend Flask.

---

## Définitions des niveaux de priorité

| Niveau | Définition |
|--------|------------|
| **Critique** | Blocage ou risque sécurité ; doit être traité en priorité. |
| **Majeur** | Défaut fonctionnel ou UX important ; correction attendue rapidement. |
| **Mineur** | Amélioration souhaitable ; peut être planifiée dans un second temps. |

---

## 1. Liste des problèmes identifiés par zone

### 1.1 Section Analyse (Analytics)

| # | Problème | Priorité |
|---|----------|----------|
| A1 | Section non implémentée : contenu placeholder uniquement (« Fonctionnalité en Développement »). | Majeur |
| A2 | Aucune documentation produit ou technique pour les futurs modules d'analyse. | Mineur |
| A3 | Entrée « Analyses » visible dans la sidebar alors que la page n'offre pas de valeur utilisateur (risque de confusion). | Majeur |

### 1.2 Gestion des rôles et permissions

| # | Problème | Priorité |
|---|----------|----------|
| R1 | Aucune permission différenciée côté API : admin, operator et partner ont le même accès à toutes les routes. | Majeur |
| R2 | Incohérence des libellés : Settings affiche « Administrateur », « Analyste », « Opérateur terrain » alors que le backend utilise `admin`, `operator`, `partner` (pas de rôle « Analyste »). | Majeur |
| R3 | Pas de document de référence « Rôles et responsabilités ». | Mineur |
| R4 | Frontend : pas de masquage des onglets selon le rôle (ex. Utilisateurs visible par tous, y compris opérateur). | Majeur |

### 1.3 Paramètres (Settings)

| # | Problème | Priorité |
|---|----------|----------|
| P1 | Données mock (environnement, tables, rôles) non distinguées des données réelles. | Majeur |
| P2 | Bouton « Gérer les utilisateurs » ouvre `window.open('/user-management', '_blank')` : l'app n'utilise pas cette route, le lien est inefficace. | Majeur |
| P3 | Switches (ex. mode maintenance) désactivés et non reliés à une API. | Mineur |
| P4 | Manque de regroupement « Lecture seule » vs « Actions configurables ». | Mineur |

### 1.4 Audit UI/UX global

| # | Problème | Priorité |
|---|----------|----------|
| U1 | Pas de bouton Déconnexion dans MainApp (userProfile et onLogout passés mais non utilisés). | Critique |
| U2 | PartnerDashboard : pas de bouton Déconnexion visible. | Critique |
| U3 | Toaster (Sonner) non monté dans l'app : aucun toast après actions (CRUD, import couche). | Majeur |
| U4 | Statistiques globales (Accueil) : placeholder non connecté à l'API. | Majeur |
| U5 | Profil utilisateur (nom/email) non affiché dans le header MainApp. | Majeur |

### 1.5 Section Couches – modal « Gestion des Couches Géospatiales »

| # | Problème | Priorité |
|---|----------|----------|
| C1 | Double contrôle de fermeture : X natif de DialogContent + bouton « Fermer » dans l'en-tête du modal. | Majeur |
| C2 | Responsivité : vérifier comportement scroll (max-h-[90vh], flex-1 overflow-auto) sur petit écran et agrandissement. | Mineur |
| C3 | Incohérence d'interaction : ce modal est le seul à afficher un bouton « Fermer » en plus du X ; les autres modals n'ont que le X. | Mineur |

---

## 2. Recommandations concrètes et actionnables

### 2.1 Section Analyse

| Problème | Action |
|----------|--------|
| A1, A3 | Option 1 : Afficher un contenu minimal « Bientôt disponible » avec lien vers une roadmap ou doc. Option 2 : Masquer l'entrée « Analyses » dans la sidebar tant que la fonctionnalité n'est pas livrée. |
| A2 | Rédiger une fiche dans `docs/` ou ce rapport : objectifs et périmètre prévus pour la section Analyse (rapports de production, analyses environnementales, etc.). |

### 2.2 Rôles et permissions

| Problème | Action |
|----------|--------|
| R1 | Côté backend : appliquer `@require_roles('admin')` sur les routes sensibles (ex. CRUD utilisateurs). Documenter dans `docs/operations/auth-et-securite.md`. |
| R2 | Dans `SettingsWorkspace.jsx` : remplacer les libellés mock par les rôles réels (Admin, Opérateur, Partenaire) ou ajouter une mention « Données illustratives ». |
| R3 | Ajouter un tableau « Rôles et responsabilités » dans `docs/operations/auth-et-securite.md` (admin / operator / partner avec permissions associées). |
| R4 | Côté frontend : filtrer les entrées de la sidebar selon `userProfile.role` (ex. masquer « Utilisateurs » et « Paramètres » pour le rôle `operator` si le métier l'exige). |

### 2.3 Paramètres

| Problème | Action |
|----------|--------|
| P1 | Ajouter une mention en en-tête de la section ou par carte : « Données illustratives » ou « Non connecté à l'API » pour les blocs mock. |
| P2 | Remplacer le lien « Gérer les utilisateurs » par un callback passé par MainApp (ex. `onNavigateToUsers`) qui change l'onglet actif vers « Utilisateurs ». |
| P3, P4 | Documenter les actions réellement disponibles vs prévues ; restructurer en sous-sections claires. |

### 2.4 UI/UX global

| Problème | Action |
|----------|--------|
| U1, U5 | Dans `MainApp.jsx` : déclarer les props `userProfile` et `onLogout` ; dans le header, afficher le nom ou l'email de l'utilisateur et un bouton ou menu « Déconnexion » appelant `onLogout`. |
| U2 | Dans `PartnerDashboard.jsx` : utiliser la prop `onLogout` et ajouter un bouton « Déconnexion » dans l'en-tête. |
| U3 | Dans `main.jsx` : importer et rendre le composant `<Toaster />` (Sonner). Dans les composants concernés (UserManagement, PartnersManagement, AddGeospatialLayerModalV2, etc.), appeler `toast.success()` / `toast.error()` après les actions. |

### 2.5 Modal Couches

| Problème | Action |
|----------|--------|
| C1 | Option A (recommandée) : Supprimer le bouton personnalisé « Fermer » dans l'en-tête du modal (`LayersManagementTable.jsx`) et garder uniquement le X de `DialogContent`. Option B : Ajouter une prop `hideClose` dans `DialogContent` pour masquer le X lorsque le modal fournit son propre bouton, et n'afficher que « Fermer » ici. |
| C2 | Vérifier en test manuel le comportement du scroll (une seule zone de scroll dans le contenu interne) sur mobile et fenêtre redimensionnée. |
| C3 | Documenter la règle : modals avec en-tête custom n'affichent qu'un seul contrôle de fermeture (soit X par défaut, soit bouton custom). |

---

## 3. Synthèse par axe d'audit

### 3.1 Cohérence visuelle

- **Points forts** : Palette bleu/violet, composants shadcn/ui homogènes, badges et cartes cohérents.
- **À améliorer** : Uniformiser la fermeture des modals (voir C1, C3).

### 3.2 Hiérarchie de l'information

- **Points forts** : Cartes avec titre, description, contenu ; tableaux avec en-têtes clairs.
- **À améliorer** : Section Paramètres : distinguer lecture seule vs actions ; Section Analyses : clarifier le statut (à venir / masqué).

### 3.3 Ergonomie des parcours

- **Points forts** : Navigation sidebar claire, boutons d'action visibles (Rafraîchir, Importer).
- **À améliorer** : Déconnexion accessible (MainApp, PartnerDashboard) ; feedback après actions (toasts) ; lien « Gérer les utilisateurs » depuis Settings fonctionnel.

### 3.4 Qualité des contenus

- **Points forts** : Textes en français, états vides et messages d'erreur présents sur les écrans principaux.
- **À améliorer** : Placeholders (Analyses, Statistiques globales) à connecter ou à expliciter ; données mock à labelliser dans Settings.

---

## 4. Suggestions d'amélioration produit

- **Section Analyse** : Prévoir une roadmap (rapports de production, analyses environnementales, export multi-formats) et la lier depuis l'interface ou la doc.
- **Rôles** : Définir une matrice de permissions (qui peut faire quoi) et la faire valider par le métier avant d'implémenter les restrictions backend et le masquage des menus.
- **Paramètres** : À terme, connecter les blocs Environnement et BDD à des endpoints de lecture seule (si l'architecture le permet) pour afficher des données réelles.
- **Accessibilité** : Planifier un audit WCAG (labels, focus, aria, contraste) sur les écrans critiques (Login, header, formulaires).
- **Session expirée** : Afficher un toast ou un bandeau « Session expirée, veuillez vous reconnecter » lors d'une réponse 401 avant la redirection vers le login.

---

*Rapport généré dans le cadre du plan d'audit Kaiso Pro / ODG. À mettre à jour après application des corrections.*
