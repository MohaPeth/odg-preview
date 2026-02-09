# Guide d'Utilisation - Plateforme ODG

## Introduction

La plateforme Ogooué Digital Gold (ODG) est un système intégré qui combine un géoportail WebGIS et un système de traçabilité blockchain pour l'industrie minière gabonaise. Ce guide vous explique comment utiliser efficacement les différents modules de la plateforme.

## Accès à la Plateforme

### URL d'accès
- **Développement**: `http://localhost:5000`
- **Production**: [URL à définir lors du déploiement]

### Navigation Principale

La plateforme dispose d'une barre latérale de navigation avec 5 sections principales :

1. **🏠 Accueil** - Vue d'ensemble et statistiques
2. **🗺️ Géoportail** - Cartographie et gisements miniers
3. **🛡️ Blockchain** - Traçabilité et transactions
4. **📊 Analyses** - Rapports et tableaux de bord (à venir)
5. **⚙️ Paramètres** - Configuration système (à venir)

## Module Géoportail WebGIS

### Vue d'ensemble
Le géoportail permet de visualiser et d'explorer les gisements miniers du Gabon sur une carte interactive.

### Fonctionnalités Principales

#### 1. Carte Interactive
- **Zoom** : Utilisez les boutons `+` et `-` ou la molette de la souris
- **Navigation** : Cliquez et glissez pour déplacer la carte
- **Couches** : Cliquez sur l'icône des couches pour gérer l'affichage

#### 2. Gisements Miniers
Les gisements sont représentés par des marqueurs colorés sur la carte :
- **🟡 Jaune** : Gisements d'or
- **🔵 Bleu** : Gisements de diamant
- **🟢 Vert** : Zones en exploitation
- **⚫ Gris** : Zones terminées

#### 3. Informations Détaillées
Cliquez sur un marqueur pour afficher :
- **Nom du gisement**
- **Type de matériau**
- **Entreprise exploitante**
- **Superficie estimée**
- **Statut d'exploitation**
- **Description détaillée**

#### 4. Recherche
- Utilisez la barre de recherche en haut à gauche
- Tapez le nom d'un gisement, d'une entreprise ou d'un type de matériau
- Les résultats s'affichent automatiquement

#### 5. Panneau Latéral
Le panneau gauche contient :
- **Légende** : Explication des symboles et couleurs
- **Liste des gisements** : Informations résumées avec statuts

### Gisements Disponibles

1. **Gisement Minkebe**
   - Type : Or
   - Superficie : 755 Km²
   - Statut : Actif
   - Localisation : Province de Woleu-Ntem

2. **Gisement Myaning**
   - Type : Or
   - Superficie : 150 Km²
   - Statut : En développement
   - Localisation : 70 Km de Lambaréné

3. **Gisement Eteke**
   - Type : Or
   - Superficie : 765 Km²
   - Statut : Exploration
   - Localisation : Sud-est du Gabon, province de la Ngounié

## Module Blockchain

### Vue d'ensemble
Le module blockchain assure la traçabilité et la transparence des activités minières à travers un système de transactions sécurisées.

### Tableau de Bord Principal

#### Statistiques Clés
Le tableau de bord affiche 4 indicateurs principaux :
- **Total Transactions** : Nombre total de transactions enregistrées
- **Confirmées** : Transactions validées sur la blockchain
- **En Attente** : Transactions en cours de validation
- **Volume Total** : Quantité totale de matériaux tracés (en kg)

#### Graphiques
1. **Évolution des Transactions** : Graphique linéaire montrant l'activité dans le temps
2. **Distribution par Matériau** : Graphique circulaire des types de matériaux

### Onglet Transactions

#### Liste des Transactions
Chaque transaction affiche :
- **Statut** : Badge coloré (Vert=Confirmée, Jaune=En attente, Rouge=Échouée)
- **Hash de transaction** : Identifiant unique tronqué
- **Date et heure** : Timestamp de la transaction
- **Matériau et quantité** : Type et volume traité
- **Numéro de bloc** : Position dans la blockchain
- **Adresses** : Expéditeur et destinataire

#### Recherche de Transactions
- Utilisez la barre de recherche pour filtrer par :
  - Hash de transaction
  - Type de matériau
  - Adresse expéditeur ou destinataire
- Les résultats se mettent à jour en temps réel

#### Détails d'une Transaction
Cliquez sur une transaction pour voir :
- **Hash complet** de la transaction
- **Adresses complètes** expéditeur et destinataire
- **Métadonnées** : Informations supplémentaires (origine, destination, qualité, etc.)
- **Statut de validation**
- **Numéro de bloc** et timestamp

### Onglet Certificats

#### Certificats de Traçabilité
Les certificats garantissent l'authenticité et la traçabilité des matériaux :
- **ID du certificat** : Identifiant unique (format CERT-XXXXXX)
- **Matériau certifié** : Type et quantité
- **Origine et destination** : Traçabilité complète
- **Date de certification**
- **Statut de validité**

#### Actions sur les Certificats
- **QR Code** : Génération de code QR pour vérification mobile
- **Détails** : Informations complètes du certificat
- **Vérification** : Validation de l'authenticité

### Onglet Chaîne d'Approvisionnement

#### Traçabilité Complète
Visualisation étape par étape du parcours des matériaux :

1. **Extraction** : Mine d'origine avec quantité extraite
2. **Transport** : Acheminement vers les installations de traitement
3. **Raffinage** : Purification et amélioration de la qualité
4. **Distribution** : Livraison vers les destinations finales

#### Informations par Étape
Chaque étape affiche :
- **Numéro d'ordre** dans la chaîne
- **Description** de l'opération
- **Localisation** géographique
- **Données techniques** (pureté, impact environnemental, etc.)
- **Statut** de validation
- **Timestamp** de l'opération

## Page d'Accueil

### Présentation ODG
La page d'accueil présente :
- **Mission d'ODG** : Digitalisation des activités minières
- **Technologies utilisées** : WebGIS et Blockchain
- **Objectifs** : Visibilité, traçabilité, transparence

### Accès Rapide
Deux boutons principaux permettent d'accéder directement aux modules :
- **Explorer le Géoportail** : Accès direct au module WebGIS
- **Voir la Blockchain** : Accès direct au module Blockchain

### Statistiques Rapides
Quatre indicateurs clés :
- **3 Gisements Actifs** : Nombre de sites en exploitation
- **2 Transactions Confirmées** : Activité blockchain validée
- **15.7 kg Or Tracé** : Volume total sous traçabilité
- **100% Transparence** : Niveau de transparence atteint

### Cartes de Fonctionnalités
Trois cartes détaillent les capacités de chaque module :

1. **Géoportail WebGIS**
   - Cartographie des gisements
   - Zones d'exploitation en temps réel
   - Infrastructure minière
   - Recherche et filtrage avancés

2. **Traçabilité Blockchain**
   - Transactions sécurisées et immuables
   - Certificats de traçabilité
   - Chaîne d'approvisionnement complète
   - Vérification en temps réel

3. **Analyses & Rapports**
   - Tableaux de bord interactifs
   - Rapports de production
   - Analyses environnementales
   - Exportation de données

## Conseils d'Utilisation

### Navigation Optimale
- **Utilisez la sidebar** pour naviguer rapidement entre les modules
- **Explorez les onglets** dans chaque module pour accéder à toutes les fonctionnalités
- **Utilisez la recherche** pour trouver rapidement des informations spécifiques

### Compréhension des Données
- **Statuts colorés** : Vert=Actif/Confirmé, Jaune=En cours, Rouge=Problème
- **Coordonnées géographiques** : Format décimal (latitude, longitude)
- **Hash blockchain** : Identifiants uniques tronqués pour l'affichage

### Interactivité
- **Cliquez sur les éléments** pour obtenir plus de détails
- **Utilisez les filtres** pour affiner vos recherches
- **Explorez les graphiques** pour comprendre les tendances

## Résolution de Problèmes

### Problèmes Courants

#### La carte ne s'affiche pas
- Vérifiez votre connexion internet
- Actualisez la page (F5)
- Vérifiez que JavaScript est activé

#### Les données ne se chargent pas
- Vérifiez que le serveur backend est démarré
- Consultez la console du navigateur (F12) pour les erreurs
- Contactez l'administrateur système

#### Interface non responsive
- Vérifiez la taille de votre écran
- Utilisez le menu hamburger (☰) sur mobile
- Testez avec un navigateur différent

### Support Technique
Pour toute assistance technique :
- Consultez les logs de l'application
- Contactez l'équipe de développement ODG
- Vérifiez la documentation technique

## Bonnes Pratiques

### Sécurité
- Ne partagez pas les hash de transactions sensibles
- Vérifiez toujours l'authenticité des certificats
- Utilisez des connexions sécurisées (HTTPS en production)

### Performance
- Fermez les popups après consultation
- Utilisez les filtres pour limiter les résultats
- Évitez d'ouvrir trop d'onglets simultanément

### Données
- Vérifiez la cohérence des informations affichées
- Signalez les anomalies à l'équipe technique
- Utilisez les fonctions d'export pour sauvegarder les données importantes

---

**Version du Guide**: 1.0.0  
**Dernière Mise à Jour**: Juillet 2025  
**Support**: Équipe ODG

