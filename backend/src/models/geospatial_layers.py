from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import json

from src.models.mining_data import db

class GeospatialLayer(db.Model):
    """
    Modèle pour stocker les couches géospatiales personnalisées
    Supporte les points, lignes et polygones avec métadonnées
    """
    __tablename__ = 'geospatial_layers'
    
    # Identifiants et métadonnées de base
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Configuration de la couche
    layer_type = db.Column(db.String(50), nullable=False, index=True)  # 'deposit', 'infrastructure', 'zone', 'custom'
    geometry_type = db.Column(db.String(20), nullable=False)  # 'POINT', 'LINESTRING', 'POLYGON', 'MULTIPOLYGON'
    source_format = db.Column(db.String(10), nullable=False)  # 'KML', 'SHP', 'GEOJSON', 'CSV', 'TXT', 'TIFF'
    source_path = db.Column(db.String(500))  # Chemin du fichier source original
    
    # Statut et visibilité
    status = db.Column(db.String(50), default='actif', index=True)  # 'actif', 'en_développement', 'exploration', 'terminé'
    is_visible = db.Column(db.Boolean, default=True)  # Visibilité sur la carte
    is_public = db.Column(db.Boolean, default=True)  # Accessible à tous les utilisateurs
    
    # Configuration des styles (JSON)
    style_config = db.Column(JSONB, nullable=False, default=dict, server_default='{}')
    
    def __init__(self, **kwargs):
        super(GeospatialLayer, self).__init__(**kwargs)
        if not self.style_config:
            self.style_config = {
                'color': '#3b82f6',
                'fillColor': '#3b82f6',
                'fillOpacity': 0.3,
                'weight': 2,
                'opacity': 0.8,
                'iconUrl': None,
                'iconSize': [20, 20]
            }
    
    # Métadonnées additionnelles (JSON)
    layer_metadata = db.Column(JSONB, nullable=False, default=dict, server_default='{}')
    
    # Géométrie spatiale (PostGIS)
    geom = db.Column(Geometry('GEOMETRY', srid=4326))  # WGS84
    
    # Statistiques calculées
    area_km2 = db.Column(db.Float)  # Superficie en km² (pour polygones)
    length_km = db.Column(db.Float)  # Longueur en km (pour lignes)
    point_count = db.Column(db.Integer, default=1)  # Nombre de points (pour multipoints)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relations (pour futures extensions)
    created_by_user_id = db.Column(db.Integer, nullable=True)  # ID utilisateur créateur
    
    def __repr__(self):
        return f'<GeospatialLayer {self.name} ({self.geometry_type})>'
    
    def to_dict(self):
        """Conversion en dictionnaire pour l'API JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'layerType': self.layer_type,
            'geometryType': self.geometry_type,
            'sourceFormat': self.source_format,
            'sourcePath': self.source_path,
            'status': self.status,
            'isVisible': self.is_visible,
            'isPublic': self.is_public,
            'styleConfig': self.style_config,
            'metadata': self.layer_metadata,
            'areaKm2': self.area_km2,
            'lengthKm': self.length_km,
            'pointCount': self.point_count,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'createdByUserId': self.created_by_user_id
        }
    
    def to_geojson_feature(self):
        """Conversion en Feature GeoJSON pour l'affichage cartographique"""
        from geoalchemy2.shape import to_shape
        
        if not self.geom:
            return None
        
        try:
            # Conversion de la géométrie PostGIS en Shapely puis GeoJSON
            geom_shape = to_shape(self.geom)
            
            # Utiliser __geo_interface__ pour une conversion robuste
            geometry = geom_shape.__geo_interface__
            
            return {
                'type': 'Feature',
                'id': self.id,
                'geometry': geometry,
                'properties': {
                    'id': self.id,
                    'name': self.name,
                    'description': self.description,
                    'layerType': self.layer_type,
                    'geometryType': self.geometry_type,
                    'status': self.status,
                    'styleConfig': self.style_config,
                    'metadata': self.layer_metadata,
                    'areaKm2': self.area_km2,
                    'lengthKm': self.length_km,
                    'pointCount': self.point_count
                }
            }
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Erreur conversion GeoJSON pour couche {self.id}: {str(e)}")
            return None
    
    @classmethod
    def get_by_status(cls, status):
        """Récupère les couches par statut"""
        return cls.query.filter_by(status=status, is_visible=True).all()
    
    @classmethod
    def get_by_layer_type(cls, layer_type):
        """Récupère les couches par type"""
        return cls.query.filter_by(layer_type=layer_type, is_visible=True).all()
    
    @classmethod
    def search_by_name(cls, search_term):
        """Recherche de couches par nom"""
        return cls.query.filter(
            cls.name.ilike(f'%{search_term}%'),
            cls.is_visible == True
        ).all()
    
    def update_statistics(self):
        """Met à jour les statistiques calculées (superficie, longueur)"""
        from geoalchemy2.shape import to_shape
        from geoalchemy2.functions import ST_Area, ST_Length
        
        if not self.geom:
            return
            
        try:
            geom_shape = to_shape(self.geom)
            
            if self.geometry_type in ['POLYGON', 'MULTIPOLYGON']:
                # Calcul de la superficie en km²
                # Note: ST_Area retourne en mètres carrés pour WGS84
                area_m2 = db.session.query(ST_Area(self.geom)).scalar()
                self.area_km2 = round(area_m2 / 1000000, 2) if area_m2 else 0
                
            elif self.geometry_type in ['LINESTRING', 'MULTILINESTRING']:
                # Calcul de la longueur en km
                # Note: ST_Length retourne en mètres pour WGS84
                length_m = db.session.query(ST_Length(self.geom)).scalar()
                self.length_km = round(length_m / 1000, 2) if length_m else 0
                
            elif self.geometry_type in ['POINT', 'MULTIPOINT']:
                # Comptage des points
                if geom_shape.geom_type == 'MultiPoint':
                    self.point_count = len(geom_shape.geoms)
                else:
                    self.point_count = 1
                    
        except Exception as e:
            print(f"Erreur lors du calcul des statistiques pour la couche {self.id}: {e}")
    
    def set_default_style_by_type(self):
        """Définit un style par défaut selon le type de couche et géométrie"""
        default_styles = {
            'deposit': {
                'POINT': {'color': '#FFD700', 'iconUrl': 'gold-icon.svg'},
                'POLYGON': {'fillColor': '#FFD700', 'fillOpacity': 0.3, 'color': '#F59500'}
            },
            'infrastructure': {
                'LINESTRING': {'color': '#8B4513', 'weight': 3},
                'POLYGON': {'fillColor': '#8B4513', 'fillOpacity': 0.2}
            },
            'zone': {
                'POLYGON': {'fillColor': '#22c55e', 'fillOpacity': 0.3, 'color': '#16a34a'}
            },
            'custom': {
                'POINT': {'color': '#3b82f6', 'iconUrl': None},
                'LINESTRING': {'color': '#3b82f6', 'weight': 2},
                'POLYGON': {'fillColor': '#3b82f6', 'fillOpacity': 0.3}
            }
        }
        
        # Styles par statut
        status_colors = {
            'actif': '#22c55e',
            'en_développement': '#eab308', 
            'exploration': '#3b82f6',
            'terminé': '#6b7280'
        }
        
        base_style = default_styles.get(self.layer_type, {}).get(self.geometry_type, {})
        status_color = status_colors.get(self.status, '#3b82f6')
        
        # Fusion du style de base avec la couleur du statut
        self.style_config = {
            **self.style_config,
            **base_style,
            'color': status_color,
            'fillColor': status_color
        }


class LayerUploadHistory(db.Model):
    """
    Historique des uploads de couches géospatiales
    Pour traçabilité et debugging
    """
    __tablename__ = 'layer_upload_history'
    
    id = db.Column(db.Integer, primary_key=True)
    layer_id = db.Column(db.Integer, db.ForeignKey('geospatial_layers.id'), nullable=True)
    
    # Informations sur le fichier
    original_filename = db.Column(db.String(255), nullable=False)
    file_size_bytes = db.Column(db.BigInteger)
    file_format = db.Column(db.String(10), nullable=False)
    
    # Statut du traitement
    upload_status = db.Column(db.String(20), default='pending')  # 'pending', 'processing', 'success', 'error'
    error_message = db.Column(db.Text)
    
    # Statistiques du traitement
    features_count = db.Column(db.Integer)
    processing_time_seconds = db.Column(db.Float)
    
    # Métadonnées du fichier
    file_metadata = db.Column(JSONB)
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    processed_at = db.Column(db.DateTime)
    
    # Relations
    layer = db.relationship('GeospatialLayer', backref='upload_history')
    
    def __repr__(self):
        return f'<LayerUploadHistory {self.original_filename} ({self.upload_status})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'layerId': self.layer_id,
            'originalFilename': self.original_filename,
            'fileSizeBytes': self.file_size_bytes,
            'fileFormat': self.file_format,
            'uploadStatus': self.upload_status,
            'errorMessage': self.error_message,
            'featuresCount': self.features_count,
            'processingTimeSeconds': self.processing_time_seconds,
            'fileMetadata': self.file_metadata,
            'uploadedAt': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'processedAt': self.processed_at.isoformat() if self.processed_at else None
        }
