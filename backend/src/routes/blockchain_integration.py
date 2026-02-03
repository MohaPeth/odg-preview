"""
Routes d'intégration blockchain pour ODG Traçabilité.

Ces routes permettent de :
- Vérifier le statut de la connexion blockchain
- Publier des transactions sur la blockchain
- Vérifier des enregistrements existants
- Récupérer les détails d'un enregistrement blockchain
"""

from flask import Blueprint, jsonify, request, current_app
from flask_cors import cross_origin

from src.models.mining_data import db, BlockchainTransaction

try:
    from src.services.blockchain_service import (
        get_blockchain_service,
        simulate_blockchain_record
    )
    from src.config.blockchain_config import get_blockchain_settings
    BLOCKCHAIN_IMPORTS_OK = True
except ImportError:
    BLOCKCHAIN_IMPORTS_OK = False

import json

blockchain_integration_bp = Blueprint('blockchain_integration', __name__)


@blockchain_integration_bp.route('/status', methods=['GET'])
@cross_origin()
def get_blockchain_status():
    """
    Retourne le statut de la connexion blockchain.
    
    Response:
        - available: bool - Si la blockchain est disponible
        - configured: bool - Si la blockchain est configurée
        - network: str - Nom du réseau
        - walletAddress: str - Adresse du wallet (si connecté)
        - contractAddress: str - Adresse du smart contract
    """
    if not BLOCKCHAIN_IMPORTS_OK:
        return jsonify({
            "success": True,
            "data": {
                "available": True,  # Mode simulation activé
                "configured": True,
                "mode": "simulation",
                "network": "Simulation locale",
                "networkName": "Réseau de démonstration",
                "chainId": "demo-1",
                "walletAddress": "0xDEMO0000000000000000000000000000000DEMO",
                "walletBalance": "1000.00",
                "contractAddress": "0xCONTRACT00000000000000000000000000000",
                "message": "Mode démonstration activé (module web3 non installé)"
            }
        })
    
    try:
        service = get_blockchain_service()
        settings = get_blockchain_settings()
        
        status = service.get_status()
        status["settings"] = settings.to_dict()
        
        return jsonify({
            "success": True,
            "data": status
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blockchain_integration_bp.route('/config', methods=['GET'])
@cross_origin()
def get_blockchain_config():
    """
    Retourne la configuration blockchain (sans les secrets).
    """
    try:
        settings = get_blockchain_settings()
        return jsonify({
            "success": True,
            "data": settings.to_dict()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blockchain_integration_bp.route('/publish/<int:transaction_id>', methods=['POST'])
@cross_origin()
def publish_to_blockchain(transaction_id):
    """
    Publie une transaction de traçabilité sur la blockchain.
    
    Cette route prend une transaction existante dans la base de données
    et l'enregistre sur la blockchain via le smart contract.
    
    Args:
        transaction_id: ID de la transaction dans la base de données
        
    Response:
        - success: bool
        - blockchainTx: dict - Détails de la transaction blockchain
        - explorerUrl: str - Lien vers l'explorateur
    """
    try:
        # Récupérer la transaction depuis la base
        transaction = BlockchainTransaction.query.get_or_404(transaction_id)
        
        # Vérifier que la transaction est confirmée
        if transaction.status != 'confirmed':
            return jsonify({
                "success": False,
                "error": "La transaction doit être confirmée avant publication sur la blockchain"
            }), 400
        
        # Extraire les métadonnées
        metadata = {}
        if transaction.metadata_json:
            try:
                metadata = json.loads(transaction.metadata_json)
            except:
                pass
        
        origin = metadata.get('origin', 'Unknown')
        destination = metadata.get('destination', 'Unknown')
        
        # Obtenir le service blockchain
        service = get_blockchain_service()
        
        # Publier sur la blockchain (ou simuler si non configuré)
        if service.is_available():
            result = service.create_record_sync(
                transaction_hash=transaction.transaction_hash,
                material_type=transaction.material_type,
                quantity=transaction.quantity,
                origin=origin,
                destination=destination
            )
        else:
            # Mode simulation
            result = simulate_blockchain_record(
                transaction_hash=transaction.transaction_hash,
                material_type=transaction.material_type,
                quantity=transaction.quantity,
                origin=origin,
                destination=destination
            )
        
        # Mettre à jour la transaction avec les infos blockchain
        if result.get("success"):
            # Stocker les infos blockchain dans les métadonnées
            metadata["blockchain"] = {
                "published": True,
                "txHash": result.get("transactionHash"),
                "blockNumber": result.get("blockNumber"),
                "explorerUrl": result.get("explorerUrl"),
                "simulated": result.get("simulated", False),
                "publishedAt": str(transaction.timestamp)
            }
            transaction.metadata_json = json.dumps(metadata)
            db.session.commit()
        
        return jsonify({
            "success": result.get("success", False),
            "data": {
                "transactionId": transaction_id,
                "blockchainTx": result,
                "simulated": result.get("simulated", False)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blockchain_integration_bp.route('/verify/<transaction_hash>', methods=['GET'])
@cross_origin()
def verify_on_blockchain(transaction_hash):
    """
    Vérifie si une transaction existe sur la blockchain.
    
    Args:
        transaction_hash: Hash de la transaction à vérifier
        
    Response:
        - exists: bool - Si l'enregistrement existe
        - isValid: bool - Si l'enregistrement est valide
        - details: dict - Détails de l'enregistrement (si trouvé)
    """
    try:
        service = get_blockchain_service()
        
        if not service.is_available():
            return jsonify({
                "success": True,
                "data": {
                    "verified": False,
                    "reason": "Service blockchain non disponible",
                    "simulated": True
                }
            })
        
        # Vérifier l'existence
        verification = service.verify_record(transaction_hash)
        
        # Si existe, récupérer les détails
        details = None
        if verification.get("exists"):
            details = service.get_record(transaction_hash)
        
        return jsonify({
            "success": True,
            "data": {
                "transactionHash": transaction_hash,
                "verification": verification,
                "details": details
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blockchain_integration_bp.route('/record/<transaction_hash>', methods=['GET'])
@cross_origin()
def get_blockchain_record(transaction_hash):
    """
    Récupère les détails complets d'un enregistrement blockchain.
    
    Args:
        transaction_hash: Hash de la transaction
        
    Response:
        - found: bool
        - record: dict - Détails de l'enregistrement
    """
    try:
        service = get_blockchain_service()
        
        if not service.is_available():
            return jsonify({
                "success": True,
                "data": {
                    "found": False,
                    "reason": "Service blockchain non disponible",
                    "simulated": True
                }
            })
        
        record = service.get_record(transaction_hash)
        
        return jsonify({
            "success": True,
            "data": record
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blockchain_integration_bp.route('/stats', methods=['GET'])
@cross_origin()
def get_blockchain_integration_stats():
    """
    Retourne les statistiques d'intégration blockchain.
    
    Response:
        - totalOnChain: int - Nombre d'enregistrements sur la blockchain
        - totalInDb: int - Nombre de transactions confirmées en base
        - publishedCount: int - Nombre de transactions publiées
        - pendingCount: int - Nombre de transactions en attente de publication
    """
    try:
        service = get_blockchain_service()
        
        # Stats depuis la base de données
        total_confirmed = BlockchainTransaction.query.filter_by(status='confirmed').count()
        
        # Compter les transactions publiées (ont des métadonnées blockchain)
        published_count = 0
        pending_count = 0
        
        confirmed_txs = BlockchainTransaction.query.filter_by(status='confirmed').all()
        for tx in confirmed_txs:
            if tx.metadata_json:
                try:
                    metadata = json.loads(tx.metadata_json)
                    if metadata.get("blockchain", {}).get("published"):
                        published_count += 1
                    else:
                        pending_count += 1
                except:
                    pending_count += 1
            else:
                pending_count += 1
        
        # Stats depuis la blockchain (si disponible)
        total_on_chain = 0
        if service.is_available():
            total_on_chain = service.get_total_records()
        
        return jsonify({
            "success": True,
            "data": {
                "totalOnChain": total_on_chain,
                "totalConfirmedInDb": total_confirmed,
                "publishedCount": published_count,
                "pendingPublicationCount": pending_count,
                "blockchainAvailable": service.is_available()
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blockchain_integration_bp.route('/batch-publish', methods=['POST'])
@cross_origin()
def batch_publish_to_blockchain():
    """
    Publie plusieurs transactions sur la blockchain en batch.
    
    Body:
        - transactionIds: list[int] - Liste des IDs de transactions à publier
        
    Response:
        - results: list - Résultats pour chaque transaction
        - successCount: int
        - failureCount: int
    """
    try:
        data = request.get_json()
        transaction_ids = data.get('transactionIds', [])
        
        if not transaction_ids:
            return jsonify({
                "success": False,
                "error": "Aucune transaction spécifiée"
            }), 400
        
        service = get_blockchain_service()
        results = []
        success_count = 0
        failure_count = 0
        
        for tx_id in transaction_ids:
            try:
                transaction = BlockchainTransaction.query.get(tx_id)
                
                if not transaction:
                    results.append({
                        "transactionId": tx_id,
                        "success": False,
                        "error": "Transaction non trouvée"
                    })
                    failure_count += 1
                    continue
                
                if transaction.status != 'confirmed':
                    results.append({
                        "transactionId": tx_id,
                        "success": False,
                        "error": "Transaction non confirmée"
                    })
                    failure_count += 1
                    continue
                
                # Extraire les métadonnées
                metadata = {}
                if transaction.metadata_json:
                    try:
                        metadata = json.loads(transaction.metadata_json)
                    except:
                        pass
                
                # Vérifier si déjà publiée
                if metadata.get("blockchain", {}).get("published"):
                    results.append({
                        "transactionId": tx_id,
                        "success": True,
                        "alreadyPublished": True
                    })
                    success_count += 1
                    continue
                
                origin = metadata.get('origin', 'Unknown')
                destination = metadata.get('destination', 'Unknown')
                
                # Publier
                if service.is_available():
                    result = service.create_record_sync(
                        transaction_hash=transaction.transaction_hash,
                        material_type=transaction.material_type,
                        quantity=transaction.quantity,
                        origin=origin,
                        destination=destination
                    )
                else:
                    result = simulate_blockchain_record(
                        transaction_hash=transaction.transaction_hash,
                        material_type=transaction.material_type,
                        quantity=transaction.quantity,
                        origin=origin,
                        destination=destination
                    )
                
                if result.get("success"):
                    metadata["blockchain"] = {
                        "published": True,
                        "txHash": result.get("transactionHash"),
                        "blockNumber": result.get("blockNumber"),
                        "explorerUrl": result.get("explorerUrl"),
                        "simulated": result.get("simulated", False)
                    }
                    transaction.metadata_json = json.dumps(metadata)
                    success_count += 1
                else:
                    failure_count += 1
                
                results.append({
                    "transactionId": tx_id,
                    "success": result.get("success", False),
                    "blockchainTx": result
                })
                
            except Exception as e:
                results.append({
                    "transactionId": tx_id,
                    "success": False,
                    "error": str(e)
                })
                failure_count += 1
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": {
                "results": results,
                "successCount": success_count,
                "failureCount": failure_count,
                "totalProcessed": len(transaction_ids)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
