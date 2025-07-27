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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
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
            'metadata': json.loads(self.metadata_json) if self.metadata_json else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

