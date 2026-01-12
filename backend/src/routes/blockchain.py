from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from src.models.mining_data import (
    db,
    BlockchainTransaction,
    MiningDeposit,
    Operator,
)
from datetime import datetime
import json
import hashlib
import random
import string

blockchain_bp = Blueprint('blockchain', __name__)

def generate_transaction_hash():
    """Génère un hash de transaction simulé"""
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    return '0x' + hashlib.sha256(random_string.encode()).hexdigest()

def generate_address():
    """Génère une adresse Ethereum simulée"""
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    return '0x' + hashlib.sha256(random_string.encode()).hexdigest()[:40]

@blockchain_bp.route('/transactions', methods=['GET'])
@cross_origin()
def get_transactions():
    """Récupère toutes les transactions blockchain"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        material_type = request.args.get('material_type')
        
        query = BlockchainTransaction.query
        
        if status:
            query = query.filter_by(status=status)
        if material_type:
            query = query.filter_by(material_type=material_type)
        
        transactions = query.order_by(BlockchainTransaction.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [tx.to_dict() for tx in transactions.items],
            'pagination': {
                'page': page,
                'pages': transactions.pages,
                'per_page': per_page,
                'total': transactions.total
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/transactions/<int:transaction_id>', methods=['GET'])
@cross_origin()
def get_transaction(transaction_id):
    """Récupère une transaction spécifique"""
    try:
        transaction = BlockchainTransaction.query.get_or_404(transaction_id)
        return jsonify({
            'success': True,
            'data': transaction.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/transactions', methods=['POST'])
@cross_origin()
def create_transaction():
    """Crée une nouvelle transaction blockchain"""
    try:
        data = request.get_json()
        metadata = data.get('metadata', {}) or {}
        deposit_id = data.get('depositId')
        operator_id = data.get('operatorId')

        deposit = MiningDeposit.query.get(deposit_id) if deposit_id else None
        operator = Operator.query.get(operator_id) if operator_id else None

        metadata = enrich_metadata_with_entities(metadata, deposit, operator)

        transaction = BlockchainTransaction(
            transaction_hash=generate_transaction_hash(),
            block_number=random.randint(1000000, 9999999),
            from_address=data.get('fromAddress', generate_address()),
            to_address=data.get('toAddress', generate_address()),
            material_type=data['materialType'],
            quantity=data['quantity'],
            unit=data['unit'],
            timestamp=datetime.utcnow(),
            status='pending',
            metadata_json=json.dumps(metadata),
            deposit_id=deposit.id if deposit else None,
            operator_id=operator.id if operator else None,
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': transaction.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/transactions/<int:transaction_id>/confirm', methods=['PUT'])
@cross_origin()
def confirm_transaction(transaction_id):
    """Confirme une transaction"""
    try:
        transaction = BlockchainTransaction.query.get_or_404(transaction_id)
        payload = request.get_json(silent=True) or {}

        transaction.status = 'confirmed'
        transaction.block_number = random.randint(1000000, 9999999)

        deposit_id = payload.get('depositId')
        operator_id = payload.get('operatorId')
        metadata_updates = payload.get('metadata', {})

        deposit = (
            MiningDeposit.query.get(deposit_id)
            if deposit_id
            else transaction.deposit
        )
        operator = (
            Operator.query.get(operator_id)
            if operator_id
            else transaction.operator
        )

        transaction.deposit = deposit
        transaction.operator = operator

        current_metadata = (
            json.loads(transaction.metadata_json)
            if transaction.metadata_json
            else {}
        )
        current_metadata.update(metadata_updates or {})
        current_metadata = enrich_metadata_with_entities(
            current_metadata, deposit, operator
        )

        transaction.metadata_json = json.dumps(current_metadata)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': transaction.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/certificates', methods=['GET'])
@cross_origin()
def get_certificates():
    """Récupère les certificats de traçabilité"""
    try:
        transactions = BlockchainTransaction.query.filter_by(status='confirmed').all()
        
        certificates = []
        for tx in transactions:
            metadata = json.loads(tx.metadata_json) if tx.metadata_json else {}
            deposit = tx.deposit
            operator = tx.operator

            certificate = {
                'id': f"CERT-{tx.id:06d}",
                'transactionHash': tx.transaction_hash,
                'materialType': tx.material_type,
                'quantity': tx.quantity,
                'unit': tx.unit,
                'origin': metadata.get('origin') or (deposit.name if deposit else 'Unknown'),
                'destination': metadata.get('destination') or (operator.name if operator else 'Unknown'),
                'certificationDate': tx.timestamp.isoformat(),
                'status': 'Valid',
                'qrCode': f"https://blockchain.odg.com/cert/CERT-{tx.id:06d}",
                'metadata': metadata,
                'deposit': deposit.to_dict() if deposit else None,
                'operator': operator.to_dict() if operator else None,
            }
            certificates.append(certificate)
        
        return jsonify({
            'success': True,
            'data': certificates,
            'count': len(certificates)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/supply-chain/<material_type>', methods=['GET'])
@cross_origin()
def get_supply_chain(material_type):
    """Récupère la chaîne d'approvisionnement pour un type de matériau"""
    try:
        transactions = BlockchainTransaction.query.filter_by(
            material_type=material_type,
            status='confirmed'
        ).order_by(BlockchainTransaction.timestamp).all()
        
        supply_chain = []
        for tx in transactions:
            metadata = json.loads(tx.metadata_json) if tx.metadata_json else {}
            
            step = {
                'transactionHash': tx.transaction_hash,
                'timestamp': tx.timestamp.isoformat(),
                'fromAddress': tx.from_address,
                'toAddress': tx.to_address,
                'quantity': tx.quantity,
                'unit': tx.unit,
                'location': metadata.get('location', 'Unknown'),
                'process': metadata.get('process', 'Transfer'),
                'operator': metadata.get('operator', 'Unknown'),
                'quality': metadata.get('quality', {}),
                'environmental_impact': metadata.get('environmental_impact', {})
            }
            supply_chain.append(step)
        
        return jsonify({
            'success': True,
            'data': {
                'materialType': material_type,
                'totalSteps': len(supply_chain),
                'supplyChain': supply_chain
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/stats', methods=['GET'])
@cross_origin()
def get_blockchain_stats():
    """Récupère les statistiques blockchain"""
    try:
        total_transactions = BlockchainTransaction.query.count()
        confirmed_transactions = BlockchainTransaction.query.filter_by(status='confirmed').count()
        pending_transactions = BlockchainTransaction.query.filter_by(status='pending').count()
        
        # Statistiques par type de matériau
        material_stats = db.session.query(
            BlockchainTransaction.material_type,
            db.func.count(BlockchainTransaction.id),
            db.func.sum(BlockchainTransaction.quantity)
        ).group_by(BlockchainTransaction.material_type).all()
        
        # Volume total tracé
        total_volume = db.session.query(
            db.func.sum(BlockchainTransaction.quantity)
        ).filter_by(status='confirmed').scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'transactions': {
                    'total': total_transactions,
                    'confirmed': confirmed_transactions,
                    'pending': pending_transactions
                },
                'materials': [
                    {
                        'type': material[0],
                        'transactions': material[1],
                        'totalQuantity': material[2]
                    }
                    for material in material_stats
                ],
                'totalVolume': total_volume,
                'certificates': confirmed_transactions
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/verify/<certificate_id>', methods=['GET'])
@cross_origin()
def verify_certificate(certificate_id):
    """Vérifie un certificat de traçabilité"""
    try:
        # Extraction de l'ID de transaction du certificat
        if certificate_id.startswith('CERT-'):
            tx_id = int(certificate_id.replace('CERT-', ''))
            transaction = BlockchainTransaction.query.get(tx_id)
            
            if not transaction:
                return jsonify({
                    'success': False,
                    'error': 'Certificate not found'
                }), 404
            
            if transaction.status != 'confirmed':
                return jsonify({
                    'success': False,
                    'error': 'Certificate not confirmed on blockchain'
                }), 400
            
            metadata = json.loads(transaction.metadata_json) if transaction.metadata_json else {}
            
            verification_result = {
                'certificateId': certificate_id,
                'isValid': True,
                'transactionHash': transaction.transaction_hash,
                'blockNumber': transaction.block_number,
                'materialType': transaction.material_type,
                'quantity': transaction.quantity,
                'unit': transaction.unit,
                'timestamp': transaction.timestamp.isoformat(),
                'origin': metadata.get('origin', 'Unknown'),
                'destination': metadata.get('destination', 'Unknown'),
                'verificationDate': datetime.utcnow().isoformat()
            }
            
            return jsonify({
                'success': True,
                'data': verification_result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid certificate format'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

