"""
Service d'import de données géospatiales pour ODG
Supporte KML, KMZ, Shapefile, GeoJSON, CSV, TXT, TIFF
"""

import os
import json
import zipfile
import tempfile
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon
from geoalchemy2.functions import ST_GeomFromText
from werkzeug.utils import secure_filename

from src.models.geospatial_layers import GeospatialLayer, LayerUploadHistory, db

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeospatialImportService:
    """Service principal pour l'import de fichiers géospatiaux"""
    
    SUPPORTED_FORMATS = {
        'KML': ['.kml'],
        'KMZ': ['.kmz'], 
        'SHP': ['.shp'],
        'GEOJSON': ['.geojson', '.json'],
        'CSV': ['.csv'],
        'TXT': ['.txt'],
        'TIFF': ['.tiff', '.tif']
    }
    
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_FEATURES = 10000  # Limite de features par fichier
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix='odg_import_')
        logger.info(f"Service d'import initialisé. Dossier temp: {self.temp_dir}")
    
    def import_file(self, file_path: str, layer_config: Dict[str, Any]) -> Tuple[bool, str, Optional[GeospatialLayer]]:
        """
        Import principal d'un fichier géospatial
        
        Args:
            file_path: Chemin vers le fichier à importer
            layer_config: Configuration de la couche (nom, description, etc.)
            
        Returns:
            Tuple (success, message, layer_object)
        """
        start_time = datetime.now()
        upload_record = None
        
        try:
            # Validation du fichier
            if not os.path.exists(file_path):
                return False, f"Fichier non trouvé: {file_path}", None
            
            file_size = os.path.getsize(file_path)
            if file_size > self.MAX_FILE_SIZE:
                return False, f"Fichier trop volumineux: {file_size/1024/1024:.1f}MB (max: {self.MAX_FILE_SIZE/1024/1024}MB)", None
            
            # Détection du format
            file_format = self._detect_format(file_path)
            if not file_format:
                return False, "Format de fichier non supporté", None
            
            # Création de l'enregistrement d'historique
            upload_record = LayerUploadHistory(
                original_filename=os.path.basename(file_path),
                file_size_bytes=file_size,
                file_format=file_format,
                upload_status='processing'
            )
            db.session.add(upload_record)
            db.session.commit()
            
            logger.info(f"Début import fichier {file_path} (format: {file_format})")
            
            # Parsing selon le format
            gdf = self._parse_file(file_path, file_format)
            if gdf is None or gdf.empty:
                upload_record.upload_status = 'error'
                upload_record.error_message = "Aucune donnée géospatiale trouvée"
                db.session.commit()
                return False, "Aucune donnée géospatiale trouvée dans le fichier", None
            
            # Validation des données
            validation_result = self._validate_geodataframe(gdf)
            if not validation_result[0]:
                upload_record.upload_status = 'error'
                upload_record.error_message = validation_result[1]
                db.session.commit()
                return False, validation_result[1], None
            
            # Création de la couche géospatiale
            layer = self._create_geospatial_layer(gdf, layer_config, file_format, file_path)
            if not layer:
                upload_record.upload_status = 'error'
                upload_record.error_message = "Erreur lors de la création de la couche"
                db.session.commit()
                return False, "Erreur lors de la création de la couche", None
            
            # Sauvegarde
            db.session.add(layer)
            db.session.commit()
            
            # Mise à jour de l'historique
            processing_time = (datetime.now() - start_time).total_seconds()
            upload_record.layer_id = layer.id
            upload_record.upload_status = 'success'
            upload_record.features_count = len(gdf)
            upload_record.processing_time_seconds = processing_time
            upload_record.processed_at = datetime.now()
            upload_record.file_metadata = {
                'crs': str(gdf.crs) if gdf.crs else 'Unknown',
                'bounds': gdf.total_bounds.tolist() if not gdf.empty else [],
                'geometry_types': gdf.geometry.geom_type.unique().tolist()
            }
            db.session.commit()
            
            logger.info(f"Import réussi: {len(gdf)} features en {processing_time:.2f}s")
            return True, f"Import réussi: {len(gdf)} features importées", layer
            
        except Exception as e:
            logger.error(f"Erreur lors de l'import: {str(e)}")
            if upload_record:
                upload_record.upload_status = 'error'
                upload_record.error_message = str(e)
                upload_record.processed_at = datetime.now()
                db.session.commit()
            return False, f"Erreur lors de l'import: {str(e)}", None
    
    def preview_file(self, file_path: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Analyse un fichier géospatial sans créer de couche en base.
        Retourne uniquement des métadonnées pour l'aperçu (compte, bounds, types)."""
        try:
            if not os.path.exists(file_path):
                return False, f"Fichier non trouvé: {file_path}", None

            file_size = os.path.getsize(file_path)
            if file_size > self.MAX_FILE_SIZE:
                return False, (
                    f"Fichier trop volumineux: {file_size/1024/1024:.1f}MB "
                    f"(max: {self.MAX_FILE_SIZE/1024/1024}MB)"
                ), None

            file_format = self._detect_format(file_path)
            if not file_format:
                return False, "Format de fichier non supporté", None

            gdf = self._parse_file(file_path, file_format)
            if gdf is None or gdf.empty:
                return False, "Aucune donnée géospatiale trouvée dans le fichier", None

            is_valid, message = self._validate_geodataframe(gdf)
            if not is_valid:
                return False, message, None

            bounds = gdf.total_bounds.tolist() if not gdf.empty else []
            geom_types = gdf.geometry.geom_type.value_counts()
            main_geom_type = geom_types.index[0].upper() if not geom_types.empty else None

            preview_data: Dict[str, Any] = {
                'fileFormat': file_format,
                'featureCount': len(gdf),
                'geometryTypes': geom_types.to_dict(),
                'mainGeometryType': main_geom_type,
                'bounds': bounds,
                'crs': str(gdf.crs) if gdf.crs else 'Unknown',
                'fileSizeBytes': file_size,
            }

            return True, (
                f"Prévisualisation réussie: {len(gdf)} features détectées"
            ), preview_data
        except Exception as e:
            logger.error(f"Erreur lors de la prévisualisation: {str(e)}")
            return False, f"Erreur lors de la prévisualisation: {str(e)}", None
    
    def _detect_format(self, file_path: str) -> Optional[str]:
        """Détecte le format du fichier"""
        file_ext = Path(file_path).suffix.lower()
        
        for format_name, extensions in self.SUPPORTED_FORMATS.items():
            if file_ext in extensions:
                return format_name
        return None
    
    def _parse_file(self, file_path: str, file_format: str) -> Optional[gpd.GeoDataFrame]:
        """Parse le fichier selon son format"""
        try:
            if file_format == 'KML':
                return self._parse_kml(file_path)
            elif file_format == 'KMZ':
                return self._parse_kmz(file_path)
            elif file_format == 'SHP':
                return self._parse_shapefile(file_path)
            elif file_format == 'GEOJSON':
                return self._parse_geojson(file_path)
            elif file_format == 'CSV':
                return self._parse_csv(file_path)
            elif file_format == 'TXT':
                return self._parse_txt(file_path)
            elif file_format == 'TIFF':
                return self._parse_tiff(file_path)
            else:
                logger.error(f"Format non supporté: {file_format}")
                return None
        except Exception as e:
            logger.error(f"Erreur parsing {file_format}: {str(e)}")
            return None
    
    def _parse_kml(self, file_path: str) -> Optional[gpd.GeoDataFrame]:
        """Parse un fichier KML"""
        try:
            # GeoPandas peut lire les KML directement
            gdf = gpd.read_file(file_path, driver='KML')
            return self._standardize_geodataframe(gdf)
        except Exception as e:
            logger.error(f"Erreur parsing KML: {str(e)}")
            return None
    
    def _parse_kmz(self, file_path: str) -> Optional[gpd.GeoDataFrame]:
        """Parse un fichier KMZ (KML compressé)"""
        try:
            with zipfile.ZipFile(file_path, 'r') as kmz:
                # Chercher le fichier KML principal
                kml_files = [f for f in kmz.namelist() if f.endswith('.kml')]
                if not kml_files:
                    raise ValueError("Aucun fichier KML trouvé dans le KMZ")
                
                # Extraire le premier KML
                kml_file = kml_files[0]
                temp_kml = os.path.join(self.temp_dir, 'temp.kml')
                
                with kmz.open(kml_file) as kml_data:
                    with open(temp_kml, 'wb') as f:
                        f.write(kml_data.read())
                
                return self._parse_kml(temp_kml)
        except Exception as e:
            logger.error(f"Erreur parsing KMZ: {str(e)}")
            return None
    
    def _parse_shapefile(self, file_path: str) -> Optional[gpd.GeoDataFrame]:
        """Parse un Shapefile"""
        try:
            gdf = gpd.read_file(file_path)
            return self._standardize_geodataframe(gdf)
        except Exception as e:
            logger.error(f"Erreur parsing Shapefile: {str(e)}")
            return None
    
    def _parse_geojson(self, file_path: str) -> Optional[gpd.GeoDataFrame]:
        """Parse un fichier GeoJSON"""
        try:
            gdf = gpd.read_file(file_path)
            return self._standardize_geodataframe(gdf)
        except Exception as e:
            logger.error(f"Erreur parsing GeoJSON: {str(e)}")
            return None
    
    def _parse_csv(self, file_path: str) -> Optional[gpd.GeoDataFrame]:
        """Parse un CSV avec coordonnées"""
        try:
            df = pd.read_csv(file_path)
            
            # Détection automatique des colonnes de coordonnées
            coord_columns = self._detect_coordinate_columns(df)
            if not coord_columns:
                raise ValueError("Colonnes de coordonnées non trouvées")
            
            lon_col, lat_col = coord_columns
            
            # Création des géométries Point
            geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]
            gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
            
            return self._standardize_geodataframe(gdf)
        except Exception as e:
            logger.error(f"Erreur parsing CSV: {str(e)}")
            return None
    
    def _parse_txt(self, file_path: str) -> Optional[gpd.GeoDataFrame]:
        """Parse un fichier TXT avec coordonnées"""
        try:
            # Essayer différents délimiteurs
            for delimiter in ['\t', ' ', ',', ';']:
                try:
                    df = pd.read_csv(file_path, delimiter=delimiter)
                    if len(df.columns) >= 2:
                        break
                except:
                    continue
            else:
                raise ValueError("Format TXT non reconnu")
            
            # Utiliser les deux premières colonnes comme coordonnées
            if len(df.columns) >= 2:
                df.columns = ['longitude', 'latitude'] + list(df.columns[2:])
                geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
                gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
                return self._standardize_geodataframe(gdf)
            
            return None
        except Exception as e:
            logger.error(f"Erreur parsing TXT: {str(e)}")
            return None
    
    def _parse_tiff(self, file_path: str) -> Optional[gpd.GeoDataFrame]:
        """Parse un fichier TIFF géoréférencé (raster)"""
        try:
            import rasterio
            from rasterio.features import shapes
            from shapely.geometry import shape
            
            with rasterio.open(file_path) as src:
                # Conversion du raster en polygones
                mask = src.read(1) != src.nodata
                results = (
                    {'properties': {'raster_val': v}, 'geometry': s}
                    for i, (s, v) in enumerate(shapes(src.read(1), mask=mask, transform=src.transform))
                )
                
                geoms = list(results)
                if not geoms:
                    return None
                
                # Création du GeoDataFrame
                gdf = gpd.GeoDataFrame.from_features(geoms, crs=src.crs)
                return self._standardize_geodataframe(gdf)
                
        except ImportError:
            logger.error("rasterio non installé - impossible de lire les TIFF")
            return None
        except Exception as e:
            logger.error(f"Erreur parsing TIFF: {str(e)}")
            return None
    
    def _detect_coordinate_columns(self, df: pd.DataFrame) -> Optional[Tuple[str, str]]:
        """Détecte les colonnes de coordonnées dans un DataFrame"""
        possible_lon = ['longitude', 'lon', 'lng', 'x', 'long']
        possible_lat = ['latitude', 'lat', 'y']
        
        columns_lower = [col.lower() for col in df.columns]
        
        lon_col = None
        lat_col = None
        
        for col in possible_lon:
            if col in columns_lower:
                lon_col = df.columns[columns_lower.index(col)]
                break
        
        for col in possible_lat:
            if col in columns_lower:
                lat_col = df.columns[columns_lower.index(col)]
                break
        
        if lon_col and lat_col:
            return lon_col, lat_col
        
        # Fallback: utiliser les deux premières colonnes numériques
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) >= 2:
            return numeric_cols[0], numeric_cols[1]
        
        return None
    
    def _standardize_geodataframe(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Standardise un GeoDataFrame (projection, nettoyage)"""
        # Reprojection vers WGS84 si nécessaire
        if gdf.crs and gdf.crs != 'EPSG:4326':
            gdf = gdf.to_crs('EPSG:4326')
        elif not gdf.crs:
            gdf.crs = 'EPSG:4326'
        
        # Nettoyage des géométries invalides
        gdf = gdf[gdf.geometry.is_valid]
        
        # Suppression des géométries vides
        gdf = gdf[~gdf.geometry.is_empty]
        
        return gdf
    
    def _validate_geodataframe(self, gdf: gpd.GeoDataFrame) -> Tuple[bool, str]:
        """Valide un GeoDataFrame"""
        if gdf.empty:
            return False, "Aucune donnée géospatiale valide"
        
        if len(gdf) > self.MAX_FEATURES:
            return False, f"Trop de features: {len(gdf)} (max: {self.MAX_FEATURES})"
        
        # Vérification des types de géométrie
        geom_types = gdf.geometry.geom_type.unique()
        valid_types = ['Point', 'LineString', 'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon']
        
        for geom_type in geom_types:
            if geom_type not in valid_types:
                return False, f"Type de géométrie non supporté: {geom_type}"
        
        return True, "Validation réussie"
    
    def _create_geospatial_layer(self, gdf: gpd.GeoDataFrame, layer_config: Dict[str, Any], 
                                file_format: str, file_path: str) -> Optional[GeospatialLayer]:
        """Crée une couche géospatiale à partir d'un GeoDataFrame"""
        try:
            # Détermination du type de géométrie principal
            geom_types = gdf.geometry.geom_type.value_counts()
            main_geom_type = geom_types.index[0].upper()
            
            # Conversion des géométries en WKT pour PostGIS
            if len(gdf) == 1:
                # Une seule géométrie
                geom_wkt = gdf.geometry.iloc[0].wkt
            else:
                # Plusieurs géométries - créer une GeometryCollection ou MultiGeometry
                if main_geom_type == 'POINT':
                    from shapely.geometry import MultiPoint
                    multi_geom = MultiPoint(gdf.geometry.tolist())
                    geom_wkt = multi_geom.wkt
                    main_geom_type = 'MULTIPOINT'
                elif main_geom_type == 'LINESTRING':
                    from shapely.geometry import MultiLineString
                    multi_geom = MultiLineString(gdf.geometry.tolist())
                    geom_wkt = multi_geom.wkt
                    main_geom_type = 'MULTILINESTRING'
                elif main_geom_type == 'POLYGON':
                    from shapely.geometry import MultiPolygon
                    multi_geom = MultiPolygon(gdf.geometry.tolist())
                    geom_wkt = multi_geom.wkt
                    main_geom_type = 'MULTIPOLYGON'
                else:
                    # Prendre la première géométrie par défaut
                    geom_wkt = gdf.geometry.iloc[0].wkt
            
            # Création de la couche
            layer = GeospatialLayer(
                name=layer_config.get('name', f'Import {file_format}'),
                description=layer_config.get('description', f'Données importées depuis {os.path.basename(file_path)}'),
                layer_type=layer_config.get('layer_type', 'custom'),
                geometry_type=main_geom_type,
                source_format=file_format,
                source_path=file_path,
                status=layer_config.get('status', 'actif'),
                geom=ST_GeomFromText(geom_wkt, 4326),
                metadata={
                    'properties': gdf.drop('geometry', axis=1).to_dict('records') if len(gdf.columns) > 1 else {},
                    'source_info': {
                        'original_crs': str(gdf.crs),
                        'feature_count': len(gdf),
                        'geometry_types': geom_types.to_dict(),
                        'bounds': gdf.total_bounds.tolist()
                    },
                    'processing_info': {
                        'import_date': datetime.now().isoformat(),
                        'file_size_bytes': os.path.getsize(file_path)
                    }
                }
            )
            
            # Application du style par défaut
            layer.set_default_style_by_type()
            
            return layer
            
        except Exception as e:
            logger.error(f"Erreur création couche: {str(e)}")
            return None
    
    def cleanup(self):
        """Nettoyage des fichiers temporaires"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            logger.info("Nettoyage des fichiers temporaires terminé")
        except Exception as e:
            logger.warning(f"Erreur lors du nettoyage: {str(e)}")
    
    def __del__(self):
        """Destructeur - nettoyage automatique"""
        self.cleanup()


class FileValidator:
    """Validateur de fichiers géospatiaux"""
    
    @staticmethod
    def validate_file_upload(file) -> Tuple[bool, str]:
        """Valide un fichier uploadé via Flask"""
        if not file or not file.filename:
            return False, "Aucun fichier sélectionné"
        
        # Vérification de l'extension
        filename = secure_filename(file.filename)
        file_ext = Path(filename).suffix.lower()
        
        all_extensions = []
        for extensions in GeospatialImportService.SUPPORTED_FORMATS.values():
            all_extensions.extend(extensions)
        
        if file_ext not in all_extensions:
            return False, f"Format non supporté: {file_ext}"
        
        return True, "Fichier valide"
    
    @staticmethod
    def get_supported_extensions() -> List[str]:
        """Retourne la liste des extensions supportées"""
        all_extensions = []
        for extensions in GeospatialImportService.SUPPORTED_FORMATS.values():
            all_extensions.extend(extensions)
        return sorted(all_extensions)
