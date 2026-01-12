from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class MiningDeposit(db.Model):
    __tablename__ = 'mining_deposits'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Or, Diamant, etc.
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    company = db.Column(db.String(100), nullable=False)
    estimated_quantity = db.Column(db.String(50))
    status = db.Column(db.String(50), nullable=False)  # Actif, En développement, Exploration
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'coordinates': [self.latitude, self.longitude],
            'company': self.company,
            'estimatedQuantity': self.estimated_quantity,
            'status': self.status,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ExploitationArea(db.Model):
    __tablename__ = 'exploitation_areas'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # En cours, Terminé, Permis en attente
    coordinates = db.Column(db.Text, nullable=False)  # JSON string of polygon coordinates
    area = db.Column(db.String(50))
    extracted_volume = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'company': self.company,
            'status': self.status,
            'coordinates': json.loads(self.coordinates) if self.coordinates else [],
            'area': self.area,
            'extractedVolume': self.extracted_volume,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Infrastructure(db.Model):
    __tablename__ = 'infrastructure'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Route, Chemin de fer, Pipeline
    coordinates = db.Column(db.Text, nullable=False)  # JSON string of line coordinates
    length = db.Column(db.String(50))
    capacity = db.Column(db.String(50))
    status = db.Column(db.String(50))  # Bon état, En maintenance, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'coordinates': json.loads(self.coordinates) if self.coordinates else [],
            'length': self.length,
            'capacity': self.capacity,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class BlockchainTransaction(db.Model):
    __tablename__ = 'blockchain_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_hash = db.Column(db.String(66), unique=True, nullable=False)
    block_number = db.Column(db.Integer)
    from_address = db.Column(db.String(42), nullable=False)
    to_address = db.Column(db.String(42), nullable=False)
    material_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, failed
    metadata_json = db.Column(db.Text)  # JSON string for additional data
    deposit_id = db.Column(db.Integer, db.ForeignKey('mining_deposits.id'), nullable=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('operators.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    deposit = db.relationship('MiningDeposit', backref=db.backref('blockchain_transactions', lazy=True))
    operator = db.relationship('Operator', backref=db.backref('blockchain_transactions', lazy=True))
    
    def to_dict(self):
        metadata = json.loads(self.metadata_json) if self.metadata_json else {}
        deposit_data = self.deposit.to_dict() if self.deposit else None
        operator_data = self.operator.to_dict() if self.operator else None
        return {
            'id': self.id,
            'transactionHash': self.transaction_hash,
            'blockNumber': self.block_number,
            'fromAddress': self.from_address,
            'toAddress': self.to_address,
            'materialType': self.material_type,
            'quantity': self.quantity,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'status': self.status,
            'metadata': metadata,
            'deposit': deposit_data,
            'operator': operator_data,
            'depositId': self.deposit_id,
            'operatorId': self.operator_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Operator(db.Model):
    """Opérateur minier (entité métier utilisée par le dashboard et le front public).

    Modèle volontairement simple pour l'onboarding :
    - liste des commodités stockée en JSON texte pour éviter de multiplier les tables
    - nombre de permis agrégé (pour affichage rapide)
    """

    __tablename__ = 'operators'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    slug = db.Column(db.String(150), unique=True, nullable=False, index=True)
    country = db.Column(db.String(100))
    status = db.Column(db.String(50), default='Actif', index=True)
    logo_url = db.Column(db.String(255))
    description = db.Column(db.Text)

    # Stockage léger des commodités sous forme de JSON [{"code": "AU", "label": "Or"}, ...]
    commodities_json = db.Column(db.Text)

    # Agrégat simple pour l'onboarding (nombre de permis associés)
    permits_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        try:
            commodities = json.loads(self.commodities_json) if self.commodities_json else []
        except Exception:
            commodities = []

        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'country': self.country,
            'status': self.status,
            'logoUrl': self.logo_url,
            'description': self.description,
            'commodities': commodities,
            'permitsCount': self.permits_count or 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
