# Modèle Substances pour système SIG ODG
from src.models.mining_data import db
from datetime import datetime

# Fonction pour créer les substances par défaut (accessible hors de la classe)
def create_default_substances():
    """Créer les substances par défaut du système"""
    default_substances = [
        {
            'name': 'Or',
            'symbol': 'Au',
            'color_code': '#FFD700',
            'description': 'Métal précieux, excellent conducteur électrique et résistant à la corrosion',
            'market_price': 65000.0,
            'unit': 'kg',
            'density': 19.3,
            'hardness': 2.5
        },
        {
            'name': 'Diamant',
            'symbol': 'C',
            'color_code': '#87CEEB',
            'description': 'Pierre précieuse, matériau naturel le plus dur connu',
            'market_price': 55000.0,
            'unit': 'carats',
            'density': 3.5,
            'hardness': 10.0,
            'icon_type': 'diamond'
        },
        {
            'name': 'Fer',
            'symbol': 'Fe',
            'color_code': '#8B0000',
            'description': 'Métal ferreux, base de la sidérurgie et de la construction',
            'market_price': 120.0,
            'unit': 'tonnes',
            'density': 7.8,
            'hardness': 4.0
        },
        {
            'name': 'Sable',
            'symbol': 'Si',
            'color_code': '#F5F5DC',
            'description': 'Silice, matériau de construction et industrie du verre',
            'market_price': 25.0,
            'unit': 'tonnes',
            'density': 1.6,
            'hardness': 7.0,
            'icon_type': 'square'
        },
        {
            'name': 'Manganèse',
            'symbol': 'Mn',
            'color_code': '#9370DB',
            'description': 'Métal de transition, utilisé dans la production d\'acier',
            'market_price': 1800.0,
            'unit': 'tonnes',
            'density': 7.2,
            'hardness': 6.0
        },
        {
            'name': 'Uranium',
            'symbol': 'U',
            'color_code': '#32CD32',
            'description': 'Métal radioactif, combustible nucléaire',
            'market_price': 130000.0,
            'unit': 'kg',
            'density': 19.1,
            'hardness': 6.0
        }
    ]
    
    created_substances = []
    for substance_data in default_substances:
        # Vérifier si la substance existe déjà
        existing = Substance.query.filter_by(name=substance_data['name']).first()
        if not existing:
            substance = Substance(**substance_data)
            substance.price_last_update = datetime.utcnow()
            substance.created_by = 'system'
            db.session.add(substance)
            created_substances.append(substance_data['name'])
    
    try:
        db.session.commit()
        return {
            'success': True,
            'created': created_substances,
            'message': f'{len(created_substances)} substances créées avec succès'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la création des substances'
        }

class Substance(db.Model):
    """Modèle pour les types de minerais/matériaux"""
    __tablename__ = 'substances'
    
    # Clé primaire
    id = db.Column(db.Integer, primary_key=True)
    
    # Informations de base
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Affichage cartographique
    color_code = db.Column(db.String(7), nullable=False)  # Code couleur hex (#FFD700)
    icon_type = db.Column(db.String(20), default='circle')  # circle, square, diamond
    
    # Données économiques
    market_price = db.Column(db.Float)              # Prix actuel par unité
    price_currency = db.Column(db.String(3), default='EUR')
    price_last_update = db.Column(db.DateTime)
    
    # Propriétés physiques
    unit = db.Column(db.String(20), default='kg')   # kg, tonnes, carats, m³
    density = db.Column(db.Float)                   # Densité pour calculs de volume
    hardness = db.Column(db.Float)                  # Dureté (échelle de Mohs)
    
    # Métadonnées système
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))
    
    def to_dict(self):
        """Conversion en dictionnaire pour JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'symbol': self.symbol,
            'description': self.description,
            'colorCode': self.color_code,
            'iconType': self.icon_type,
            'marketPrice': self.market_price,
            'priceCurrency': self.price_currency,
            'priceLastUpdate': self.price_last_update.isoformat() if self.price_last_update else None,
            'unit': self.unit,
            'density': self.density,
            'hardness': self.hardness,
            'isActive': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_legend_item(self):
        """Format spécial pour légende cartographique"""
        return {
            'id': self.id,
            'name': self.name,
            'symbol': self.symbol,
            'color': self.color_code,
            'icon': self.icon_type,
            'unit': self.unit,
            'visible': True,  # Par défaut visible
            'opacity': 100    # Opacité 100%
        }

    # Plus de méthode create_default_substances ici, elle est maintenant au niveau module

    def __repr__(self):
        return f'<Substance {self.name} ({self.symbol})>'
