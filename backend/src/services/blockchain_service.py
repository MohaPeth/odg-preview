"""
Service d'intégration blockchain pour ODG Traçabilité.

Ce module gère la connexion à la blockchain (Ethereum/Polygon) et l'interaction
avec le smart contract ODGTraceability pour enregistrer les transactions de
traçabilité des matériaux miniers.

Configuration requise (variables d'environnement) :
- BLOCKCHAIN_RPC_URL : URL du nœud RPC (Infura, Alchemy, etc.)
- BLOCKCHAIN_PRIVATE_KEY : Clé privée du wallet pour signer les transactions
- BLOCKCHAIN_CONTRACT_ADDRESS : Adresse du smart contract déployé
- BLOCKCHAIN_CHAIN_ID : ID de la chaîne (137 pour Polygon, 80001 pour Mumbai testnet)
"""

import os
import json
import hashlib
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

# Web3 sera importé conditionnellement pour éviter les erreurs si non installé
try:
    from web3 import Web3
    from web3.middleware import geth_poa_middleware
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    Web3 = None


class BlockchainConfig:
    """Configuration de la connexion blockchain."""
    
    # Réseaux préconfigurés
    NETWORKS = {
        "polygon_mainnet": {
            "rpc_url": "https://polygon-rpc.com",
            "chain_id": 137,
            "explorer": "https://polygonscan.com",
            "name": "Polygon Mainnet"
        },
        "polygon_mumbai": {
            "rpc_url": "https://rpc-mumbai.maticvigil.com",
            "chain_id": 80001,
            "explorer": "https://mumbai.polygonscan.com",
            "name": "Polygon Mumbai Testnet"
        },
        "ethereum_mainnet": {
            "rpc_url": "https://mainnet.infura.io/v3/YOUR_PROJECT_ID",
            "chain_id": 1,
            "explorer": "https://etherscan.io",
            "name": "Ethereum Mainnet"
        },
        "ethereum_sepolia": {
            "rpc_url": "https://sepolia.infura.io/v3/YOUR_PROJECT_ID",
            "chain_id": 11155111,
            "explorer": "https://sepolia.etherscan.io",
            "name": "Ethereum Sepolia Testnet"
        },
        "localhost": {
            "rpc_url": "http://127.0.0.1:8545",
            "chain_id": 31337,
            "explorer": "",
            "name": "Local Development"
        }
    }
    
    def __init__(self):
        self.rpc_url = os.environ.get("BLOCKCHAIN_RPC_URL", "")
        self.private_key = os.environ.get("BLOCKCHAIN_PRIVATE_KEY", "")
        self.contract_address = os.environ.get("BLOCKCHAIN_CONTRACT_ADDRESS", "")
        self.chain_id = int(os.environ.get("BLOCKCHAIN_CHAIN_ID", "80001"))
        self.network = os.environ.get("BLOCKCHAIN_NETWORK", "polygon_mumbai")
        self.enabled = os.environ.get("BLOCKCHAIN_ENABLED", "false").lower() == "true"
        
        # Si pas de RPC URL configurée, utiliser celle du réseau par défaut
        if not self.rpc_url and self.network in self.NETWORKS:
            self.rpc_url = self.NETWORKS[self.network]["rpc_url"]
            self.chain_id = self.NETWORKS[self.network]["chain_id"]
    
    def is_configured(self) -> bool:
        """Vérifie si la blockchain est correctement configurée."""
        return bool(
            self.enabled and
            self.rpc_url and
            self.private_key and
            self.contract_address
        )
    
    def get_explorer_url(self, tx_hash: str) -> str:
        """Retourne l'URL de l'explorateur pour une transaction."""
        if self.network in self.NETWORKS:
            explorer = self.NETWORKS[self.network]["explorer"]
            if explorer:
                return f"{explorer}/tx/{tx_hash}"
        return ""


# ABI du smart contract (interface pour interagir avec le contrat)
CONTRACT_ABI = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "transactionHash", "type": "bytes32"},
            {"indexed": False, "name": "materialType", "type": "string"},
            {"indexed": False, "name": "quantity", "type": "uint256"},
            {"indexed": False, "name": "timestamp", "type": "uint256"},
            {"indexed": True, "name": "recorder", "type": "address"}
        ],
        "name": "RecordCreated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "transactionHash", "type": "bytes32"},
            {"indexed": True, "name": "invalidatedBy", "type": "address"},
            {"indexed": False, "name": "timestamp", "type": "uint256"}
        ],
        "name": "RecordInvalidated",
        "type": "event"
    },
    {
        "inputs": [{"name": "_recorder", "type": "address"}],
        "name": "authorizeRecorder",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "_transactionHash", "type": "bytes32"},
            {"name": "_materialType", "type": "string"},
            {"name": "_quantity", "type": "uint256"},
            {"name": "_origin", "type": "string"},
            {"name": "_destination", "type": "string"}
        ],
        "name": "createRecord",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "_transactionHash", "type": "bytes32"}],
        "name": "getRecord",
        "outputs": [
            {"name": "materialType", "type": "string"},
            {"name": "quantity", "type": "uint256"},
            {"name": "timestamp", "type": "uint256"},
            {"name": "recorder", "type": "address"},
            {"name": "origin", "type": "string"},
            {"name": "destination", "type": "string"},
            {"name": "isValid", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getTotalRecords",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "_transactionHash", "type": "bytes32"}],
        "name": "invalidateRecord",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "_transactionHash", "type": "bytes32"}],
        "name": "verifyRecord",
        "outputs": [
            {"name": "exists", "type": "bool"},
            {"name": "isValid", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]


class BlockchainService:
    """Service principal pour l'interaction avec la blockchain."""
    
    def __init__(self, config: Optional[BlockchainConfig] = None):
        self.config = config or BlockchainConfig()
        self.web3 = None
        self.contract = None
        self.account = None
        self._initialized = False
        
        if self.config.is_configured() and WEB3_AVAILABLE:
            self._initialize()
    
    def _initialize(self):
        """Initialise la connexion Web3 et le contrat."""
        try:
            # Connexion au nœud RPC
            self.web3 = Web3(Web3.HTTPProvider(self.config.rpc_url))
            
            # Middleware pour les chaînes PoA (Polygon, etc.)
            self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            # Vérifier la connexion
            if not self.web3.is_connected():
                print(f"[Blockchain] Impossible de se connecter à {self.config.rpc_url}")
                return
            
            # Charger le compte depuis la clé privée
            self.account = Account.from_key(self.config.private_key)
            
            # Charger le contrat
            self.contract = self.web3.eth.contract(
                address=Web3.to_checksum_address(self.config.contract_address),
                abi=CONTRACT_ABI
            )
            
            self._initialized = True
            print(f"[Blockchain] Connecté à {self.config.network}")
            print(f"[Blockchain] Adresse du wallet: {self.account.address}")
            print(f"[Blockchain] Contrat: {self.config.contract_address}")
            
        except Exception as e:
            print(f"[Blockchain] Erreur d'initialisation: {e}")
            self._initialized = False
    
    def is_available(self) -> bool:
        """Vérifie si le service blockchain est disponible."""
        return self._initialized and self.web3 and self.web3.is_connected()
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut de la connexion blockchain."""
        if not WEB3_AVAILABLE:
            return {
                "available": False,
                "reason": "web3.py non installé",
                "configured": False
            }
        
        if not self.config.is_configured():
            return {
                "available": False,
                "reason": "Configuration blockchain manquante",
                "configured": False,
                "enabled": self.config.enabled
            }
        
        if not self._initialized:
            return {
                "available": False,
                "reason": "Échec de l'initialisation",
                "configured": True
            }
        
        try:
            block_number = self.web3.eth.block_number
            balance = self.web3.eth.get_balance(self.account.address)
            balance_eth = self.web3.from_wei(balance, 'ether')
            
            return {
                "available": True,
                "configured": True,
                "network": self.config.network,
                "chainId": self.config.chain_id,
                "blockNumber": block_number,
                "walletAddress": self.account.address,
                "walletBalance": float(balance_eth),
                "contractAddress": self.config.contract_address
            }
        except Exception as e:
            return {
                "available": False,
                "reason": str(e),
                "configured": True
            }
    
    def generate_transaction_hash(self, data: Dict[str, Any]) -> str:
        """Génère un hash unique pour une transaction de traçabilité."""
        # Créer une chaîne déterministe à partir des données
        hash_input = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def to_bytes32(self, hex_string: str) -> bytes:
        """Convertit un hash hexadécimal en bytes32."""
        if hex_string.startswith("0x"):
            hex_string = hex_string[2:]
        return bytes.fromhex(hex_string.ljust(64, '0')[:64])
    
    async def create_record(
        self,
        transaction_hash: str,
        material_type: str,
        quantity: float,
        origin: str,
        destination: str
    ) -> Dict[str, Any]:
        """
        Enregistre une transaction de traçabilité sur la blockchain.
        
        Args:
            transaction_hash: Hash unique de la transaction
            material_type: Type de matériau (Or, Diamant, etc.)
            quantity: Quantité en grammes
            origin: Origine du matériau
            destination: Destination
            
        Returns:
            Dict avec le résultat de la transaction blockchain
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Service blockchain non disponible",
                "simulated": True
            }
        
        try:
            # Convertir le hash en bytes32
            tx_hash_bytes = self.to_bytes32(transaction_hash)
            
            # Convertir la quantité en entier (grammes * 1000 pour précision)
            quantity_int = int(quantity * 1000)
            
            # Construire la transaction
            nonce = self.web3.eth.get_transaction_count(self.account.address)
            
            tx = self.contract.functions.createRecord(
                tx_hash_bytes,
                material_type,
                quantity_int,
                origin,
                destination
            ).build_transaction({
                'chainId': self.config.chain_id,
                'gas': 300000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': nonce
            })
            
            # Signer la transaction
            signed_tx = self.web3.eth.account.sign_transaction(
                tx, 
                private_key=self.config.private_key
            )
            
            # Envoyer la transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Attendre la confirmation
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            return {
                "success": receipt.status == 1,
                "transactionHash": tx_hash.hex(),
                "blockNumber": receipt.blockNumber,
                "gasUsed": receipt.gasUsed,
                "explorerUrl": self.config.get_explorer_url(tx_hash.hex()),
                "simulated": False
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "simulated": False
            }
    
    def create_record_sync(
        self,
        transaction_hash: str,
        material_type: str,
        quantity: float,
        origin: str,
        destination: str
    ) -> Dict[str, Any]:
        """Version synchrone de create_record."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.create_record(
                transaction_hash,
                material_type,
                quantity,
                origin,
                destination
            )
        )
    
    def verify_record(self, transaction_hash: str) -> Dict[str, Any]:
        """
        Vérifie si un enregistrement existe sur la blockchain.
        
        Args:
            transaction_hash: Hash de la transaction à vérifier
            
        Returns:
            Dict avec le statut de vérification
        """
        if not self.is_available():
            return {
                "verified": False,
                "error": "Service blockchain non disponible",
                "simulated": True
            }
        
        try:
            tx_hash_bytes = self.to_bytes32(transaction_hash)
            exists, is_valid = self.contract.functions.verifyRecord(tx_hash_bytes).call()
            
            return {
                "verified": True,
                "exists": exists,
                "isValid": is_valid,
                "simulated": False
            }
            
        except Exception as e:
            return {
                "verified": False,
                "error": str(e),
                "simulated": False
            }
    
    def get_record(self, transaction_hash: str) -> Dict[str, Any]:
        """
        Récupère les détails d'un enregistrement depuis la blockchain.
        
        Args:
            transaction_hash: Hash de la transaction
            
        Returns:
            Dict avec les détails de l'enregistrement
        """
        if not self.is_available():
            return {
                "found": False,
                "error": "Service blockchain non disponible",
                "simulated": True
            }
        
        try:
            tx_hash_bytes = self.to_bytes32(transaction_hash)
            result = self.contract.functions.getRecord(tx_hash_bytes).call()
            
            material_type, quantity, timestamp, recorder, origin, destination, is_valid = result
            
            return {
                "found": True,
                "materialType": material_type,
                "quantity": quantity / 1000,  # Reconvertir en grammes
                "timestamp": timestamp,
                "timestampISO": datetime.fromtimestamp(timestamp).isoformat(),
                "recorder": recorder,
                "origin": origin,
                "destination": destination,
                "isValid": is_valid,
                "simulated": False
            }
            
        except Exception as e:
            return {
                "found": False,
                "error": str(e),
                "simulated": False
            }
    
    def get_total_records(self) -> int:
        """Retourne le nombre total d'enregistrements sur la blockchain."""
        if not self.is_available():
            return 0
        
        try:
            return self.contract.functions.getTotalRecords().call()
        except Exception:
            return 0


# Instance singleton du service
_blockchain_service: Optional[BlockchainService] = None


def get_blockchain_service() -> BlockchainService:
    """Retourne l'instance singleton du service blockchain."""
    global _blockchain_service
    if _blockchain_service is None:
        _blockchain_service = BlockchainService()
    return _blockchain_service


def simulate_blockchain_record(
    transaction_hash: str,
    material_type: str,
    quantity: float,
    origin: str,
    destination: str
) -> Dict[str, Any]:
    """
    Simule un enregistrement blockchain (pour le mode développement).
    
    Utilisé quand la blockchain n'est pas configurée ou disponible.
    """
    import random
    import string
    
    # Générer un faux hash de transaction
    fake_tx_hash = "0x" + "".join(random.choices(string.hexdigits.lower(), k=64))
    
    return {
        "success": True,
        "transactionHash": fake_tx_hash,
        "blockNumber": random.randint(1000000, 9999999),
        "gasUsed": random.randint(50000, 150000),
        "explorerUrl": "",
        "simulated": True,
        "note": "Transaction simulée - blockchain non configurée"
    }
