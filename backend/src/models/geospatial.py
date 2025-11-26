# Modèles Géospatiaux PostGIS pour ODG Platform
from geoalchemy2 import Geometry
from models.mining_data import db
from datetime import datetime
import json

class MiningDepositGIS(db.Model):
    """Gisements miniers avec géométrie PostGIS"""
    __tablename__ = 'mining_deposits_gis'
    
    # Clé primaire
    id = db.Column(db.Integer, primary_key=True)
    
    # Informations de base
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Géométrie PostGIS (Point avec projection WGS84)
    geom = db.Column(Geometry('POINT', srid=4326), nullable=False, index=True)
    
    # Relations
    substance_id = db.Column(db.Integer, db.ForeignKey('substances.id'), nullable=False)
    substance = db.relationship('Substance', backref='deposits', lazy='joined')
    
    # Informations entreprise
    company = db.Column(db.String(100), nullable=False, index=True)
    company_contact = db.Column(db.String(200))
    
    # Données géologiques
    estimated_quantity = db.Column(db.Float)         # Quantité estimée
    quantity_unit = db.Column(db.String(20))         # Unité de la quantité
    quality_grade = db.Column(db.Float)              # Teneur/qualité (%)
    confidence_level = db.Column(db.String(20), default='medium')  # low, medium, high
    
    # Géologie détaillée
    geological_formation = db.Column(db.String(100))  # Formation géologique
    rock_type = db.Column(db.String(50))              # Type de roche
    ore_type = db.Column(db.String(50))               # Type de minerai
    
    # Profondeur et accès
    depth_min = db.Column(db.Float)                   # Prof. minimum (mètres)
    depth_max = db.Column(db.Float)                   # Prof. maximum (mètres)
    surface_area = db.Column(db.Float)                # Superficie (hectares)
    accessibility = db.Column(db.String(50))          # easy, moderate, difficult
    
    # Informations temporelles
    discovery_date = db.Column(db.Date)
    last_survey = db.Column(db.Date)
    first_exploitation = db.Column(db.Date)
    
    # Statut et permis
    status = db.Column(db.String(50), nullable=False, default='Exploration', index=True)
    # Statuts: Exploration, En_développement, Actif, Suspendu, Fermé, Réhabilité
    
    exploitation_permit = db.Column(db.String(50))
    permit_expiry = db.Column(db.Date)
    permit_holder = db.Column(db.String(100))
    
    # Données économiques
    estimated_value = db.Column(db.Float)             # Valeur estimée (EUR)
    investment_required = db.Column(db.Float)         # Investissement requis
    annual_production_capacity = db.Column(db.Float)  # Capacité annuelle
    
    # Impact environnemental
    environmental_impact_level = db.Column(db.String(20))  # low, medium, high
    protected_area_distance = db.Column(db.Float)          # Distance zone protégée (km)
    water_source_distance = db.Column(db.Float)            # Distance source d'eau (km)
    
    # Données administratives
    data_source = db.Column(db.String(100))          # Source des données
    data_quality = db.Column(db.String(20), default='draft')  # draft, validated, certified
    
    # Workflow et validation
    created_by = db.Column(db.String(100))
    approved_by = db.Column(db.String(100))
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approval_date = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    # Métadonnées techniques
    coordinate_precision = db.Column(db.Float)        # Précision coordonnées (mètres)
    survey_method = db.Column(db.String(50))          # GPS, DGPS, Total_Station, etc.
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_coordinates(self):
        """Extraire latitude et longitude de la géométrie"""
        if self.geom:
            # Requête pour obtenir les coordonnées
            result = db.session.execute(
                db.text("SELECT ST_X(geom) as lng, ST_Y(geom) as lat FROM mining_deposits_gis WHERE id = :id"),
                {"id": self.id}
            ).fetchone()
            if result:
                return {
                    'latitude': float(result.lat),
                    'longitude': float(result.lng),
                    'coordinates': [float(result.lng), float(result.lat)]  # [lng, lat] format GeoJSON
                }
        return None
    
    def to_dict(self, include_geom=True, include_relations=True):
        """Conversion complète en dictionnaire"""
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'company': self.company,
            'companyContact': self.company_contact,
            'estimatedQuantity': self.estimated_quantity,
            'quantityUnit': self.quantity_unit,
            'qualityGrade': self.quality_grade,
            'confidenceLevel': self.confidence_level,
            'geologicalFormation': self.geological_formation,
            'rockType': self.rock_type,
            'oreType': self.ore_type,
            'depthMin': self.depth_min,
            'depthMax': self.depth_max,
            'surfaceArea': self.surface_area,
            'accessibility': self.accessibility,
            'discoveryDate': self.discovery_date.isoformat() if self.discovery_date else None,
            'lastSurvey': self.last_survey.isoformat() if self.last_survey else None,
            'firstExploitation': self.first_exploitation.isoformat() if self.first_exploitation else None,
            'status': self.status,
            'exploitationPermit': self.exploitation_permit,
            'permitExpiry': self.permit_expiry.isoformat() if self.permit_expiry else None,
            'permitHolder': self.permit_holder,
            'estimatedValue': self.estimated_value,
            'investmentRequired': self.investment_required,
            'annualProductionCapacity': self.annual_production_capacity,
            'environmentalImpactLevel': self.environmental_impact_level,
            'protectedAreaDistance': self.protected_area_distance,
            'waterSourceDistance': self.water_source_distance,
            'dataSource': self.data_source,
            'dataQuality': self.data_quality,
            'approvalStatus': self.approval_status,
            'approvalDate': self.approval_date.isoformat() if self.approval_date else None,
            'coordinatePrecision': self.coordinate_precision,
            'surveyMethod': self.survey_method,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Inclure les relations
        if include_relations and self.substance:
            result['substance'] = self.substance.to_dict()
        
        # Inclure la géométrie
        if include_geom:
            coords = self.get_coordinates()
            if coords:
                result.update(coords)
        
        return result
    
    def to_geojson_feature(self):
        """Conversion en feature GeoJSON"""
        coords = self.get_coordinates()
        if not coords:
            return None
        
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coords['coordinates']  # [lng, lat]
            },
            "properties": {
                "id": self.id,
                "name": self.name,
                "substance": self.substance.name if self.substance else None,
                "substanceSymbol": self.substance.symbol if self.substance else None,
                "colorCode": self.substance.color_code if self.substance else '#CCCCCC',
                "company": self.company,
                "status": self.status,
                "estimatedQuantity": self.estimated_quantity,
                "quantityUnit": self.quantity_unit,
                "qualityGrade": self.quality_grade,
                "description": self.description
            }
        }
    
    def to_legend_item(self):
        """Format pour légende cartographique"""
        if not self.substance:
            return None
        
        return {
            'id': f"deposit_{self.id}",
            'name': f"{self.name} ({self.substance.symbol})",
            'substanceId': self.substance.id,
            'substanceName': self.substance.name,
            'color': self.substance.color_code,
            'status': self.status,
            'company': self.company,
            'visible': True,
            'opacity': 100
        }
    
    @staticmethod
    def get_by_substance(substance_id, include_inactive=False):
        """Récupérer gisements par substance"""
        query = MiningDepositGIS.query.filter_by(substance_id=substance_id)
        if not include_inactive:
            query = query.filter(MiningDepositGIS.status.in_(['Exploration', 'En_développement', 'Actif']))
        return query.all()
    
    @staticmethod
    def get_within_radius(center_lat, center_lng, radius_km):
        """Récupérer gisements dans un rayon donné"""
        center_point = f"POINT({center_lng} {center_lat})"
        radius_meters = radius_km * 1000
        
        return MiningDepositGIS.query.filter(
            db.func.ST_DWithin(
                MiningDepositGIS.geom,
                db.func.ST_GeomFromText(center_point, 4326),
                radius_meters
            )
        ).all()
    
    def __repr__(self):
        return f'<MiningDepositGIS {self.name} ({self.substance.name if self.substance else "Unknown"})>'


class Community(db.Model):
    """Communautés locales avec géolocalisation"""
    __tablename__ = 'communities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    geom = db.Column(Geometry('POINT', srid=4326), nullable=False, index=True)
    
    # Données démographiques
    population = db.Column(db.Integer)
    population_year = db.Column(db.Integer, default=2025)
    main_language = db.Column(db.String(50))
    secondary_languages = db.Column(db.String(200))
    
    # Administration
    administrative_level = db.Column(db.String(50))   # village, town, city
    canton = db.Column(db.String(50))
    department = db.Column(db.String(50))
    province = db.Column(db.String(50))
    
    # Services et infrastructure
    has_electricity = db.Column(db.Boolean, default=False)
    has_water = db.Column(db.Boolean, default=False)
    has_school = db.Column(db.Boolean, default=False)
    has_health_center = db.Column(db.Boolean, default=False)
    has_market = db.Column(db.Boolean, default=False)
    road_access = db.Column(db.String(50))            # paved, unpaved, track, none
    
    # Relations avec activités minières
    nearest_mine_distance = db.Column(db.Float)       # Distance (km)
    affected_by_mining = db.Column(db.Boolean, default=False)
    mining_benefits_level = db.Column(db.String(20))  # none, low, medium, high
    mining_impact_level = db.Column(db.String(20))    # none, low, medium, high
    
    # Économie locale
    main_activities = db.Column(db.String(200))       # agriculture, fishing, etc.
    employment_in_mining = db.Column(db.Integer, default=0)
    
    # Métadonnées
    data_source = db.Column(db.String(100))
    last_census = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_coordinates(self):
        """Extraire coordonnées"""
        if self.geom:
            result = db.session.execute(
                db.text("SELECT ST_X(geom) as lng, ST_Y(geom) as lat FROM communities WHERE id = :id"),
                {"id": self.id}
            ).fetchone()
            if result:
                return {
                    'latitude': float(result.lat),
                    'longitude': float(result.lng),
                    'coordinates': [float(result.lng), float(result.lat)]
                }
        return None
    
    def to_dict(self, include_geom=True):
        """Conversion en dictionnaire"""
        result = {
            'id': self.id,
            'name': self.name,
            'population': self.population,
            'populationYear': self.population_year,
            'mainLanguage': self.main_language,
            'secondaryLanguages': self.secondary_languages,
            'administrativeLevel': self.administrative_level,
            'canton': self.canton,
            'department': self.department,
            'province': self.province,
            'hasElectricity': self.has_electricity,
            'hasWater': self.has_water,
            'hasSchool': self.has_school,
            'hasHealthCenter': self.has_health_center,
            'hasMarket': self.has_market,
            'roadAccess': self.road_access,
            'nearestMineDistance': self.nearest_mine_distance,
            'affectedByMining': self.affected_by_mining,
            'miningBenefitsLevel': self.mining_benefits_level,
            'miningImpactLevel': self.mining_impact_level,
            'mainActivities': self.main_activities,
            'employmentInMining': self.employment_in_mining,
            'dataSource': self.data_source,
            'lastCensus': self.last_census.isoformat() if self.last_census else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_geom:
            coords = self.get_coordinates()
            if coords:
                result.update(coords)
        
        return result
    
    def to_geojson_feature(self):
        """Conversion en feature GeoJSON"""
        coords = self.get_coordinates()
        if not coords:
            return None
        
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coords['coordinates']
            },
            "properties": {
                "id": self.id,
                "name": self.name,
                "type": "community",
                "population": self.population,
                "administrativeLevel": self.administrative_level,
                "services": {
                    "electricity": self.has_electricity,
                    "water": self.has_water,
                    "school": self.has_school,
                    "healthCenter": self.has_health_center,
                    "market": self.has_market
                },
                "miningRelated": {
                    "affected": self.affected_by_mining,
                    "nearestMineDistance": self.nearest_mine_distance,
                    "employment": self.employment_in_mining
                }
            }
        }
    
    def __repr__(self):
        return f'<Community {self.name} ({self.population} hab.)>'
