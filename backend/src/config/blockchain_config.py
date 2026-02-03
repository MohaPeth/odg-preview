"""
Configuration blockchain pour ODG Traçabilité.

Ce fichier centralise la configuration de la connexion blockchain.
Les valeurs peuvent être surchargées par des variables d'environnement.

Pour activer la blockchain en production :
1. Déployer le smart contract ODGTraceability.sol
2. Configurer les variables d'environnement :
   - BLOCKCHAIN_ENABLED=true
   - BLOCKCHAIN_NETWORK=polygon_mainnet (ou polygon_mumbai pour les tests)
   - BLOCKCHAIN_RPC_URL=https://polygon-rpc.com (ou URL Infura/Alchemy)
   - BLOCKCHAIN_PRIVATE_KEY=0x... (clé privée du wallet)
   - BLOCKCHAIN_CONTRACT_ADDRESS=0x... (adresse du contrat déployé)
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class NetworkConfig:
    """Configuration d'un réseau blockchain."""
    name: str
    rpc_url: str
    chain_id: int
    explorer_url: str
    native_currency: str
    is_testnet: bool


# Réseaux préconfigurés
NETWORKS = {
    # Polygon (recommandé pour ODG - frais bas, rapide)
    "polygon_mainnet": NetworkConfig(
        name="Polygon Mainnet",
        rpc_url="https://polygon-rpc.com",
        chain_id=137,
        explorer_url="https://polygonscan.com",
        native_currency="MATIC",
        is_testnet=False
    ),
    "polygon_mumbai": NetworkConfig(
        name="Polygon Mumbai Testnet",
        rpc_url="https://rpc-mumbai.maticvigil.com",
        chain_id=80001,
        explorer_url="https://mumbai.polygonscan.com",
        native_currency="MATIC",
        is_testnet=True
    ),
    "polygon_amoy": NetworkConfig(
        name="Polygon Amoy Testnet",
        rpc_url="https://rpc-amoy.polygon.technology",
        chain_id=80002,
        explorer_url="https://amoy.polygonscan.com",
        native_currency="MATIC",
        is_testnet=True
    ),
    
    # Ethereum
    "ethereum_mainnet": NetworkConfig(
        name="Ethereum Mainnet",
        rpc_url="https://mainnet.infura.io/v3/YOUR_PROJECT_ID",
        chain_id=1,
        explorer_url="https://etherscan.io",
        native_currency="ETH",
        is_testnet=False
    ),
    "ethereum_sepolia": NetworkConfig(
        name="Ethereum Sepolia Testnet",
        rpc_url="https://sepolia.infura.io/v3/YOUR_PROJECT_ID",
        chain_id=11155111,
        explorer_url="https://sepolia.etherscan.io",
        native_currency="ETH",
        is_testnet=True
    ),
    
    # Développement local
    "localhost": NetworkConfig(
        name="Local Development (Hardhat/Ganache)",
        rpc_url="http://127.0.0.1:8545",
        chain_id=31337,
        explorer_url="",
        native_currency="ETH",
        is_testnet=True
    ),
}


class BlockchainSettings:
    """Paramètres de configuration blockchain."""
    
    def __init__(self):
        # Activation de la blockchain
        self.enabled = os.environ.get("BLOCKCHAIN_ENABLED", "false").lower() == "true"
        
        # Réseau sélectionné
        self.network_name = os.environ.get("BLOCKCHAIN_NETWORK", "polygon_mumbai")
        
        # Configuration personnalisée (surcharge le réseau par défaut)
        self.custom_rpc_url = os.environ.get("BLOCKCHAIN_RPC_URL", "")
        self.custom_chain_id = os.environ.get("BLOCKCHAIN_CHAIN_ID", "")
        
        # Credentials
        self.private_key = os.environ.get("BLOCKCHAIN_PRIVATE_KEY", "")
        self.contract_address = os.environ.get("BLOCKCHAIN_CONTRACT_ADDRESS", "")
        
        # Options avancées
        try:
            self.gas_limit = int(os.environ.get("BLOCKCHAIN_GAS_LIMIT", "300000") or "300000")
        except ValueError:
            self.gas_limit = 300000
        
        try:
            self.confirmation_blocks = int(os.environ.get("BLOCKCHAIN_CONFIRMATIONS", "1") or "1")
        except ValueError:
            self.confirmation_blocks = 1
        
        try:
            self.timeout_seconds = int(os.environ.get("BLOCKCHAIN_TIMEOUT", "120") or "120")
        except ValueError:
            self.timeout_seconds = 120
    
    @property
    def network(self) -> Optional[NetworkConfig]:
        """Retourne la configuration du réseau sélectionné."""
        return NETWORKS.get(self.network_name)
    
    @property
    def rpc_url(self) -> str:
        """Retourne l'URL RPC (personnalisée ou par défaut du réseau)."""
        if self.custom_rpc_url:
            return self.custom_rpc_url
        if self.network:
            return self.network.rpc_url
        return ""
    
    @property
    def chain_id(self) -> int:
        """Retourne le chain ID (personnalisé ou par défaut du réseau)."""
        if self.custom_chain_id and self.custom_chain_id.strip():
            try:
                return int(self.custom_chain_id)
            except ValueError:
                pass
        if self.network:
            return self.network.chain_id
        return 0
    
    @property
    def explorer_url(self) -> str:
        """Retourne l'URL de l'explorateur blockchain."""
        if self.network:
            return self.network.explorer_url
        return ""
    
    def is_configured(self) -> bool:
        """Vérifie si la blockchain est correctement configurée."""
        return bool(
            self.enabled and
            self.rpc_url and
            self.private_key and
            self.contract_address
        )
    
    def get_tx_explorer_url(self, tx_hash: str) -> str:
        """Retourne l'URL de l'explorateur pour une transaction."""
        if self.explorer_url:
            return f"{self.explorer_url}/tx/{tx_hash}"
        return ""
    
    def get_address_explorer_url(self, address: str) -> str:
        """Retourne l'URL de l'explorateur pour une adresse."""
        if self.explorer_url:
            return f"{self.explorer_url}/address/{address}"
        return ""
    
    def to_dict(self) -> dict:
        """Exporte la configuration (sans les secrets)."""
        return {
            "enabled": self.enabled,
            "network": self.network_name,
            "networkName": self.network.name if self.network else "Unknown",
            "chainId": self.chain_id,
            "rpcUrl": self.rpc_url[:50] + "..." if len(self.rpc_url) > 50 else self.rpc_url,
            "explorerUrl": self.explorer_url,
            "contractAddress": self.contract_address,
            "isConfigured": self.is_configured(),
            "isTestnet": self.network.is_testnet if self.network else True,
            "gasLimit": self.gas_limit,
            "confirmationBlocks": self.confirmation_blocks
        }


# Instance singleton
_settings: Optional[BlockchainSettings] = None


def get_blockchain_settings() -> BlockchainSettings:
    """Retourne l'instance singleton des paramètres blockchain."""
    global _settings
    if _settings is None:
        _settings = BlockchainSettings()
    return _settings


def reload_blockchain_settings():
    """Recharge les paramètres blockchain (utile après modification des env vars)."""
    global _settings
    _settings = BlockchainSettings()
    return _settings
