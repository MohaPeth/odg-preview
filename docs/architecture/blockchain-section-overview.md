# Section Blockchain ODG – Synthèse Fonctionnelle

## 1. Rôle et objectifs

La section **Blockchain** de la plateforme ODG a pour objectif de :

- **Tracer** les mouvements de matériaux miniers (or, diamant, manganèse, etc.) tout au long de la chaîne de valeur.
- **Garantir la transparence** des flux (qui envoie quoi, à qui, quand, dans quel volume).
- **Générer des certificats de traçabilité** à partir des transactions confirmées.
- Fournir des **statistiques globales** sur les transactions et les volumes tracés.

En résumé : c’est le module qui permet de prouver, avec des enregistrements immuables, l’origine et le parcours des matières premières minières.

---

## 2. Fonctionnement de l’interface (frontend)

Composant principal : `frontend/src/components/BlockchainDashboard.jsx`

### 2.1. Chargement des données

Au chargement, le tableau de bord appelle 3 endpoints backend :

- `GET /api/blockchain/transactions`  → Liste des **transactions** blockchain
- `GET /api/blockchain/certificates`  → Liste des **certificats de traçabilité**
- `GET /api/blockchain/stats`         → **Statistiques agrégées**

Les réponses sont stockées côté React dans :

- `transactions` : transactions individuelles
- `certificates` : certificats construits à partir des transactions confirmées
- `stats` : statistiques globales (totaux, volumes, par matériau)

### 2.2. Statistiques principales

En haut de l’écran, 4 cartes résument la situation :

- **Total Transactions** : `stats.transactions.total`
- **Confirmées** : `stats.transactions.confirmed`
- **En attente** : `stats.transactions.pending`
- **Volume total tracé** (kg) : `stats.totalVolume`

> Ces valeurs proviennent directement du backend via `/api/blockchain/stats`.

### 2.3. Onglet « Transactions »

Objectif : suivre transaction par transaction les mouvements de matériaux.

Données affichées pour chaque transaction :

- **Statut** : `confirmed`, `pending`, `failed` (avec badge coloré)
- **Hash de transaction** : `transactionHash` (tronqué dans la liste, complet dans le détail)
- **Horodatage** : `timestamp`
- **Matériau** : `materialType` (Or, Diamant, etc.)
- **Quantité + unité** : `quantity` + `unit` (kg, carats, tonnes…)
- **Bloc** : `blockNumber`
- **Adresses** : `fromAddress` → `toAddress`

Fonctions clés :

- **Recherche** par hash, matériau ou adresse (champ de recherche en haut à droite).
- **Clique sur une transaction** → ouvre un **modal de détails** avec toutes les infos, y compris les **métadonnées JSON** associées.

### 2.4. Onglet « Certificats »

Objectif : afficher les certificats de traçabilité dérivés des transactions confirmées.

Chaque carte de certificat affiche notamment :

- **ID de certificat** : `CERT-000001` (format basé sur l’id de transaction)
- **Hash de transaction** : `transactionHash`
- **Matériau** : `materialType`
- **Quantité + unité** : `quantity` + `unit`
- **Origine** : `origin`
- **Destination** : `destination`
- **Date de certification** : `certificationDate`

Les certificats sont marqués **Valide** (status `Valid`) et un lien de type `qrCode` est prévu pour la vérification externe.

### 2.5. Onglet « Chaîne d’Approvisionnement »

Objectif : représenter visuellement les étapes de la chaîne (extraction → transport → raffinage).

- L’interface actuelle affiche un **exemple statique** (Mine Minkebe, étapes 1 à 3).
- Le backend expose déjà un endpoint générique : `GET /api/blockchain/supply-chain/<material_type>` qui renvoie les étapes réelles pour un matériau donné (à connecter plus tard à l’UI).

---

## 3. Ce qui est réellement stocké en base (backend)

Fichier clé backend : `backend/src/routes/blockchain.py`

Le modèle principal est `BlockchainTransaction` (défini dans `src/models/mining_data.py`). Les certificats ne sont pas une table à part, ils sont **dérivés** des transactions confirmées.

### 3.1. Transactions blockchain

Endpoint de création : `POST /api/blockchain/transactions`

Champs stockés pour une transaction :

- `transaction_hash` : hash simulé de transaction (type `0x...`)
- `block_number` : numéro de bloc (valeur simulée, générée aléatoirement)
- `from_address` : adresse émettrice (Ethereum-like, réelle ou simulée)
- `to_address` : adresse réceptrice
- `material_type` : type de matériau (par ex. `gold`, `diamond`, `manganese`)
- `quantity` : quantité du matériau
- `unit` : unité (kg, carats, tonnes, etc.)
- `timestamp` : date/heure d’enregistrement sur la « blockchain » interne
- `status` : `pending` à la création, puis `confirmed` ou `failed`
- `metadata_json` : JSON libre avec des informations métier, par exemple :
  - `origin` (mine ou site d’extraction)
  - `destination` (raffinerie, client…)
  - `location` (coordonnées, pays, ville)
  - `process` (extraction, transport, raffinage…)
  - `operator` (nom de l’opérateur)
  - `quality` (pureté, grade…)
  - `environmental_impact` (indicateurs CO2, etc.)

### 3.2. Confirmation de transaction

Endpoint : `PUT /api/blockchain/transactions/<id>/confirm`

- Met à jour `status` → `confirmed`.
- Met à jour `block_number` avec une nouvelle valeur (comme si la transaction était minée).

### 3.3. Certificats de traçabilité

Endpoint : `GET /api/blockchain/certificates`

- Récupère toutes les transactions `status = 'confirmed'`.
- Pour chaque transaction confirmée, construit un objet **certificat** :
  - `id` : `CERT-<id_transaction>`
  - `transactionHash` : hash de la transaction
  - `materialType`, `quantity`, `unit`
  - `origin`, `destination` (issus de `metadata_json`)
  - `certificationDate` : `timestamp` de la transaction
  - `qrCode` : URL simulée de vérification

Ces certificats sont donc **calculés côté API**, pas stockés dans une table dédiée pour l’instant.

### 3.4. Statistiques blockchain

Endpoint : `GET /api/blockchain/stats`

Calcule notamment :

- `transactions.total` : nombre total de transactions
- `transactions.confirmed` : nombre de transactions confirmées
- `transactions.pending` : nombre de transactions en attente
- `materials[]` :
  - `type` : matériau
  - `transactions` : nombre de transactions par matériau
  - `totalQuantity` : quantité totale par matériau
- `totalVolume` : somme des quantités de toutes les transactions confirmées
- `certificates` : nombre de transactions confirmées (équivalent au nombre de certificats "Valides")

### 3.5. Chaîne d’approvisionnement

Endpoint : `GET /api/blockchain/supply-chain/<material_type>`

Pour un type de matériau donné, renvoie :

- `materialType` : matériau concerné
- `totalSteps` : nombre d’étapes
- `supplyChain[]` : liste des étapes dans l’ordre chronologique, avec pour chacune :
  - `transactionHash`
  - `timestamp`
  - `fromAddress`, `toAddress`
  - `quantity`, `unit`
  - `location`, `process`, `operator`
  - `quality`, `environmental_impact` (dérivés des métadonnées)

---

## 4. Message clé pour la présentation

- La section **Blockchain** d’ODG n’est pas une blockchain publique comme Bitcoin ou Ethereum, mais une **couche de traçabilité métier** adaptée au contexte minier.
- Chaque mouvement important de matière (extraction, transport, raffinage, livraison) est enregistré sous forme de **transaction** avec : matériau, volume, adresses impliquées et métadonnées métiers.
- À partir de ces transactions confirmées, la plateforme génère des **certificats de traçabilité** consultables et vérifiables.
- Les décideurs peuvent visualiser :
  - Le **nombre de transactions** et leur statut
  - Les **volumes totaux tracés** par matériau
  - La **chaîne d’approvisionnement** complète d’un lot de minerai.

Cela permet à ODG de démontrer la transparence, la conformité et la traçabilité de sa production minière auprès de ses partenaires, régulateurs et investisseurs.
