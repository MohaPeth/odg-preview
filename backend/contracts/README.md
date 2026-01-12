# ODG Traçabilité - Smart Contract

## Description

Le smart contract `ODGTraceability.sol` permet d'enregistrer de manière immuable les transactions de traçabilité des matériaux miniers (or, diamant, manganèse, etc.) sur la blockchain.

## Fonctionnalités

- **Enregistrement** : Créer un enregistrement de traçabilité avec hash, type de matériau, quantité, origine et destination
- **Vérification** : Vérifier l'existence et la validité d'un enregistrement
- **Consultation** : Récupérer les détails d'un enregistrement
- **Invalidation** : Marquer un enregistrement comme invalide (sans le supprimer)
- **Contrôle d'accès** : Seules les adresses autorisées peuvent enregistrer

## Prérequis

- Node.js >= 18
- npm ou yarn
- Un wallet avec des fonds (MATIC pour Polygon, ETH pour Ethereum)

## Installation des outils de développement

```bash
# Installer Hardhat (recommandé)
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox

# Ou Foundry (alternative)
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

## Déploiement

### Option 1 : Avec Hardhat

1. **Initialiser le projet Hardhat** (si pas déjà fait) :
```bash
cd backend/contracts
npx hardhat init
```

2. **Créer le script de déploiement** `scripts/deploy.js` :
```javascript
const hre = require("hardhat");

async function main() {
  const ODGTraceability = await hre.ethers.getContractFactory("ODGTraceability");
  const contract = await ODGTraceability.deploy();
  await contract.waitForDeployment();
  
  console.log("ODGTraceability deployed to:", await contract.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

3. **Configurer le réseau** dans `hardhat.config.js` :
```javascript
require("@nomicfoundation/hardhat-toolbox");

module.exports = {
  solidity: "0.8.19",
  networks: {
    polygon_mumbai: {
      url: "https://rpc-mumbai.maticvigil.com",
      accounts: [process.env.PRIVATE_KEY],
      chainId: 80001
    },
    polygon_mainnet: {
      url: "https://polygon-rpc.com",
      accounts: [process.env.PRIVATE_KEY],
      chainId: 137
    }
  }
};
```

4. **Déployer** :
```bash
# Testnet (Mumbai)
npx hardhat run scripts/deploy.js --network polygon_mumbai

# Mainnet (Polygon)
npx hardhat run scripts/deploy.js --network polygon_mainnet
```

### Option 2 : Avec Remix IDE (plus simple)

1. Aller sur [Remix IDE](https://remix.ethereum.org)
2. Créer un nouveau fichier `ODGTraceability.sol`
3. Copier le contenu du smart contract
4. Compiler avec Solidity 0.8.19+
5. Déployer via "Injected Provider" (MetaMask)
6. Copier l'adresse du contrat déployé

### Option 3 : Avec Foundry

```bash
# Compiler
forge build

# Déployer sur Mumbai
forge create --rpc-url https://rpc-mumbai.maticvigil.com \
  --private-key $PRIVATE_KEY \
  src/ODGTraceability.sol:ODGTraceability
```

## Configuration Backend

Après le déploiement, configurer les variables d'environnement :

```bash
# Dans backend/.env
BLOCKCHAIN_ENABLED=true
BLOCKCHAIN_NETWORK=polygon_mumbai  # ou polygon_mainnet
BLOCKCHAIN_PRIVATE_KEY=0x...       # Clé privée du wallet
BLOCKCHAIN_CONTRACT_ADDRESS=0x...  # Adresse du contrat déployé
```

## Obtenir des tokens de test

### Polygon Mumbai (Testnet)
- [Polygon Faucet](https://faucet.polygon.technology/)
- [Alchemy Mumbai Faucet](https://mumbaifaucet.com/)

### Sepolia (Testnet Ethereum)
- [Sepolia Faucet](https://sepoliafaucet.com/)
- [Alchemy Sepolia Faucet](https://sepoliafaucet.com/)

## Vérification du contrat

Pour vérifier le contrat sur l'explorateur (PolygonScan) :

```bash
npx hardhat verify --network polygon_mumbai CONTRACT_ADDRESS
```

## Coûts estimés

| Opération | Gas estimé | Coût (MATIC ~$0.50) |
|-----------|------------|---------------------|
| Déploiement | ~1,500,000 | ~$0.015 |
| createRecord | ~150,000 | ~$0.0015 |
| verifyRecord | ~30,000 | Gratuit (view) |
| getRecord | ~50,000 | Gratuit (view) |

## Sécurité

- ⚠️ Ne jamais exposer la clé privée
- Utiliser un wallet dédié pour les transactions automatiques
- Tester d'abord sur testnet (Mumbai)
- Auditer le contrat avant déploiement mainnet

## API Backend

Une fois configuré, les endpoints suivants sont disponibles :

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/blockchain-integration/status` | GET | Statut de la connexion |
| `/api/blockchain-integration/config` | GET | Configuration (sans secrets) |
| `/api/blockchain-integration/publish/<id>` | POST | Publier une transaction |
| `/api/blockchain-integration/verify/<hash>` | GET | Vérifier un enregistrement |
| `/api/blockchain-integration/record/<hash>` | GET | Détails d'un enregistrement |
| `/api/blockchain-integration/stats` | GET | Statistiques |
| `/api/blockchain-integration/batch-publish` | POST | Publication en batch |

## Support

Pour toute question, contacter l'équipe ODG.
