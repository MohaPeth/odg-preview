"""
Service d'import de données géospatiales pour ODG
Supporte KML, KMZ, Shapefile, GeoJSON, CSV, TXT, TIFF
"""

import os
import json
import zipfile
import tempfile
import logging
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from geoalchemy2.functions import ST_GeomFromText
from werkzeug.utils import secure_filename

from src.models.geospatial_layers import GeospatialLayer, LayerUploadHistory, db

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import conditionnel pour GeoPandas/Shapely
try:
    import geopandas as gpd
    import pandas as pd
    from shapely.geometry import Point, LineString, Polygon
    GEOPANDAS_AVAILABLE = True
    SHAPELY_AVAILABLE = True
except ImportError as e:
    GEOPANDAS_AVAILABLE = False
    SHAPELY_AVAILABLE = False
    logger.warning(f"GeoPandas/Shapely non disponibles: {str(e)}")

# Import conditionnel pour RAR
try:
    import rarfile
    RARFILE_AVAILABLE = True
    logger.info("Module rarfile disponible - Support RAR activé")
except ImportError:
    RARFILE_AVAILABLE = False
    logger.warning("Module rarfile non disponible. Support RAR désactivé.")

class GeospatialImportService:
    """Service principal pour l'import de fichiers géospatiaux"""
    
    @staticmethod
    def _to_list(obj):
        """Convertit un objet en liste de manière sûre"""
        if isinstance(obj, list):
            return obj
        # Vérifier si c'est un numpy array ou pandas Series/Index
        try:
            import numpy as np
            if isinstance(obj, np.ndarray):
                return obj.tolist()
        except ImportError:
            pass
        
        # Pour les objets pandas (Series, Index, etc.)
        if hasattr(obj, 'tolist') and callable(obj.tolist):
            try:
                return obj.tolist()
            except AttributeError:
                pass
        
        # Dernier recours : conversion simple
        try:
            return list(obj)
        except (TypeError, ValueError):
            return [obj]
    
    SUPPORTED_FORMATS = {
        'KML': ['.kml'],
        'KMZ': ['.kmz'], 
        'SHP': ['.shp'],
        'ZIP': ['.zip'],  # Archive ZIP contenant un shapefile
        'RAR': ['.rar'],  # Archive RAR contenant un shapefile
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
            
            # Création de l'enregistrement d'historique (optionnel)
            upload_record = None
            try:
                upload_record = LayerUploadHistory(
                    original_filename=os.path.basename(file_path),
                    file_size_bytes=file_size,
                    file_format=file_format,
                    upload_status='processing'
                )
                db.session.add(upload_record)
                db.session.commit()
            except Exception as e:
                logger.warning(f"Impossible de créer l'historique d'upload: {str(e)}")
                db.session.rollback()
                upload_record = None
            
            logger.info(f"Début import fichier {file_path} (format: {file_format})")
            
            # Parsing selon le format
            gdf = self._parse_file(file_path, file_format)
            
            # Vérifier si le parsing a réussi
            is_empty = False
            if gdf is None:
                is_empty = True
            elif hasattr(gdf, 'empty'):  # GeoDataFrame standard
                is_empty = gdf.empty
            elif hasattr(gdf, '_length'):  # Notre FakeGeoDataFrame
                is_empty = (gdf._length == 0)
            else:
                is_empty = (len(gdf) == 0)
            
            if is_empty:
                if upload_record:
                    upload_record.upload_status = 'error'
                    upload_record.error_message = "Aucune donnée géospatiale trouvée"
                    db.session.commit()
                logger.error(f"Parsing retourné des données vides pour {file_path}")
                return False, "Aucune donnée géospatiale trouvée dans le fichier", None
            
            logger.info(f"Parsing réussi: {len(gdf)} features détectées")
            
            # Validation des données
            validation_result = self._validate_geodataframe(gdf)
            if not validation_result[0]:
                if upload_record:
                    upload_record.upload_status = 'error'
                    upload_record.error_message = validation_result[1]
                    db.session.commit()
                return False, validation_result[1], None
            
            # Création de la couche géospatiale
            layer = self._create_geospatial_layer(gdf, layer_config, file_format, file_path)
            if not layer:
                if upload_record:
                    upload_record.upload_status = 'error'
                    upload_record.error_message = "Erreur lors de la création de la couche"
                    db.session.commit()
                return False, "Erreur lors de la création de la couche", None
            
            # Sauvegarde
            db.session.add(layer)
            db.session.commit()
            
            # Mise à jour de l'historique
            if upload_record:
                processing_time = (datetime.now() - start_time).total_seconds()
                upload_record.layer_id = layer.id
                upload_record.upload_status = 'success'
                upload_record.features_count = len(gdf)
                upload_record.processing_time_seconds = processing_time
                upload_record.processed_at = datetime.now()
                upload_record.file_metadata = {
                    'crs': str(gdf.crs) if gdf.crs else 'Unknown',
                    'bounds': self._to_list(gdf.total_bounds) if len(gdf) > 0 else [],
                    'geometry_types': self._to_list(gdf.geometry.unique()) if hasattr(gdf.geometry, 'unique') else []
                }
                db.session.commit()
            
            processing_time = (datetime.now() - start_time).total_seconds()
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
                logger.error(f"Fichier non trouvé: {file_path}")
                return False, f"Fichier non trouvé: {file_path}", None

            file_size = os.path.getsize(file_path)
            if file_size > self.MAX_FILE_SIZE:
                return False, (
                    f"Fichier trop volumineux: {file_size/1024/1024:.1f}MB "
                    f"(max: {self.MAX_FILE_SIZE/1024/1024}MB)"
                ), None

            file_format = self._detect_format(file_path)
            if not file_format:
                logger.error(f"Format non supporté pour: {file_path}")
                return False, "Format de fichier non supporté. Formats acceptés: KML, KMZ, SHP, GeoJSON, CSV, TXT, TIFF", None

            logger.info(f"Parsing fichier {file_path} (format: {file_format})")
            try:
                gdf = self._parse_file(file_path, file_format)
            except ValueError as ve:
                # Propager les erreurs de validation avec message explicite
                logger.error(f"Erreur de validation: {str(ve)}")
                return False, str(ve), None
            
            if gdf is None:
                logger.error(f"Échec du parsing pour {file_path}")
                return False, f"Impossible de lire le fichier {file_format}. Vérifiez que le fichier est valide.", None
            
            # Vérifier si le parsing a retourné des données
            is_empty = False
            if hasattr(gdf, 'empty'):  # GeoDataFrame standard
                is_empty = gdf.empty
            elif hasattr(gdf, '_length'):  # Notre FakeGeoDataFrame
                is_empty = (gdf._length == 0)
            else:
                is_empty = (len(gdf) == 0)
            
            if is_empty:
                logger.error(f"Aucune donnée dans {file_path}")
                return False, "Aucune donnée géospatiale trouvée dans le fichier", None

            is_valid, message = self._validate_geodataframe(gdf)
            if not is_valid:
                return False, message, None

            bounds = self._to_list(gdf.total_bounds) if len(gdf) > 0 else []
            
            # Gérer les types de géométrie de manière sûre
            if hasattr(gdf, 'geojson'):
                # FakeGeoDataFrame
                geom_types_list = gdf.geometry.unique()
                main_geom_type = geom_types_list[0].upper() if geom_types_list else None
                geom_types_dict = {gt: 1 for gt in geom_types_list}
            else:
                # GeoDataFrame standard
                geom_types = gdf.geometry.geom_type.value_counts()
                main_geom_type = geom_types.index[0].upper() if not geom_types.empty else None
                geom_types_dict = geom_types.to_dict()

            preview_data: Dict[str, Any] = {
                'fileFormat': file_format,
                'featureCount': len(gdf),
                'geometryTypes': geom_types_dict,
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
            elif file_format == 'ZIP':
                return self._parse_zip_shapefile(file_path)
            elif file_format == 'RAR':
                return self._parse_rar_shapefile(file_path)
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
        except ValueError as ve:
            # Propager les ValueError (erreurs de validation)
            raise ve
        except Exception as e:
            logger.error(f"Erreur parsing {file_format}: {str(e)}", exc_info=True)
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
        """Parse un Shapefile
        
        Note: Un shapefile nécessite plusieurs fichiers (.shp, .shx, .dbf, .prj)
        Le file_path doit pointer vers le fichier .shp principal
        """
        try:
            # Vérifier que c'est bien un fichier .shp
            if not file_path.lower().endswith('.shp'):
                logger.error(f"Le fichier doit être un .shp, reçu: {file_path}")
                raise ValueError("Impossible de lire le fichier SHP. Vérifiez que le fichier est valide.")
            
            # Vérifier l'existence des fichiers compagnons requis
            base_path = file_path[:-4]  # Enlever .shp
            required_files = ['.shp', '.shx', '.dbf']
            missing_files = []
            
            for ext in required_files:
                companion_file = base_path + ext
                if not os.path.exists(companion_file):
                    missing_files.append(ext)
            
            if missing_files:
                logger.error(f"Fichiers manquants pour le shapefile: {missing_files}")
                raise ValueError(f"Impossible de lire le fichier SHP. Fichiers manquants: {', '.join(missing_files)}")
            
            # Lire le shapefile
            gdf = gpd.read_file(file_path)
            
            if gdf.empty:
                logger.error("Le shapefile ne contient aucune géométrie")
                raise ValueError("Aucune donnée géospatiale trouvée dans le fichier")
            
            return self._standardize_geodataframe(gdf)
            
        except ValueError as ve:
            # Propager les erreurs de validation
            raise ve
        except Exception as e:
            logger.error(f"Erreur parsing Shapefile: {str(e)}", exc_info=True)
            raise ValueError("Impossible de lire le fichier SHP. Vérifiez que le fichier est valide.")
    
    def _parse_zip_shapefile(self, file_path: str) -> Optional[gpd.GeoDataFrame]:
        """Parse un fichier ZIP contenant un shapefile
        
        Le ZIP doit contenir au minimum les fichiers .shp, .shx, .dbf
        """
        try:
            logger.info(f"Extraction du ZIP: {file_path}")
            
            # Créer un dossier temporaire pour l'extraction
            extract_dir = os.path.join(self.temp_dir, 'zip_extract')
            os.makedirs(extract_dir, exist_ok=True)
            
            # Extraire le contenu du ZIP
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Chercher le fichier .shp dans l'extraction
            shp_files = []
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file.lower().endswith('.shp'):
                        shp_files.append(os.path.join(root, file))
            
            if not shp_files:
                raise ValueError("Aucun fichier .shp trouvé dans l'archive ZIP")
            
            if len(shp_files) > 1:
                logger.warning(f"Plusieurs fichiers .shp trouvés, utilisation du premier: {shp_files[0]}")
            
            # Parser le shapefile trouvé
            shp_path = shp_files[0]
            logger.info(f"Shapefile trouvé: {shp_path}")
            
            return self._parse_shapefile(shp_path)
            
        except ValueError as ve:
            raise ve
        except Exception as e:
            logger.error(f"Erreur parsing ZIP: {str(e)}", exc_info=True)
            raise ValueError(f"Impossible de lire l'archive ZIP: {str(e)}")
    
    def _parse_rar_shapefile(self, file_path: str) -> Optional[gpd.GeoDataFrame]:
        """Parse un fichier RAR contenant un shapefile
        
        Le RAR doit contenir au minimum les fichiers .shp, .shx, .dbf
        Nécessite le module rarfile (pip install rarfile)
        """
        try:
            if not RARFILE_AVAILABLE:
                raise ValueError(
                    "Le support RAR n'est pas disponible. "
                    "Veuillez installer rarfile: pip install rarfile"
                )
            
            logger.info(f"Extraction du RAR: {file_path}")
            
            # Créer un dossier temporaire pour l'extraction
            extract_dir = os.path.join(self.temp_dir, 'rar_extract')
            os.makedirs(extract_dir, exist_ok=True)
            
            # Extraire le contenu du RAR
            with rarfile.RarFile(file_path, 'r') as rar_ref:
                rar_ref.extractall(extract_dir)
            
            # Chercher le fichier .shp dans l'extraction
            shp_files = []
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file.lower().endswith('.shp'):
                        shp_files.append(os.path.join(root, file))
            
            if not shp_files:
                raise ValueError("Aucun fichier .shp trouvé dans l'archive RAR")
            
            if len(shp_files) > 1:
                logger.warning(f"Plusieurs fichiers .shp trouvés, utilisation du premier: {shp_files[0]}")
            
            # Parser le shapefile trouvé
            shp_path = shp_files[0]
            logger.info(f"Shapefile trouvé: {shp_path}")
            
            return self._parse_shapefile(shp_path)
            
        except ValueError as ve:
            raise ve
        except Exception as e:
            logger.error(f"Erreur parsing RAR: {str(e)}", exc_info=True)
            raise ValueError(f"Impossible de lire l'archive RAR: {str(e)}")
    
    def _parse_geojson(self, file_path: str) -> Optional[gpd.GeoDataFrame]:
        """Parse un fichier GeoJSON
        
        Fonctionne avec ou sans GeoPandas :
        - Si GeoPandas est disponible, utilise gpd.read_file()
        - Sinon, parse le JSON manuellement et retourne un objet simulant un GeoDataFrame
        """
        try:
            if not GEOPANDAS_AVAILABLE:
                # Parsing manuel sans GeoPandas - retourne un objet compatible
                logger.info("Parsing GeoJSON sans GeoPandas (mode JSON pur)")
                return self._parse_geojson_as_json(file_path)
            
            # Parsing avec GeoPandas (méthode classique)
            gdf = gpd.read_file(file_path)
            return self._standardize_geodataframe(gdf)
        except Exception as e:
            logger.error(f"Erreur parsing GeoJSON: {str(e)}")
            # Fallback sur parsing manuel
            if GEOPANDAS_AVAILABLE:
                logger.info("Tentative de parsing manuel en fallback")
                return self._parse_geojson_as_json(file_path)
            return None
    
    def _parse_geojson_as_json(self, file_path: str):
        """Parse GeoJSON comme JSON pur, sans GeoPandas ni Shapely
        
        Retourne un objet simulant un GeoDataFrame pour compatibilité
        """
        try:
            import json
            
            with open(file_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
            
            # Vérifier le format
            if 'type' not in geojson_data:
                raise ValueError("Fichier GeoJSON invalide")
            
            # Créer un objet simulant un GeoDataFrame
            class FakeGeoDataFrame:
                def __init__(self, geojson):
                    self.geojson = geojson
                    self.crs = "EPSG:4326"
                    self.empty = False
                    
                    # Compter les features
                    if geojson['type'] == 'FeatureCollection':
                        self.features = geojson.get('features', [])
                    elif geojson['type'] == 'Feature':
                        self.features = [geojson]
                    else:
                        self.features = []
                    
                    self._length = len(self.features)
                
                def __len__(self):
                    return self._length
                
                @property
                def total_bounds(self):
                    """Calcule les bounds sans Shapely"""
                    if not self.features:
                        return [0, 0, 0, 0]
                    
                    min_lon, min_lat, max_lon, max_lat = 180, 90, -180, -90
                    
                    for feature in self.features:
                        geom = feature.get('geometry', {})
                        coords = geom.get('coordinates', [])
                        
                        if geom.get('type') == 'Point':
                            lon, lat = coords[0], coords[1]
                            min_lon = min(min_lon, lon)
                            max_lon = max(max_lon, lon)
                            min_lat = min(min_lat, lat)
                            max_lat = max(max_lat, lat)
                        elif geom.get('type') in ['LineString', 'MultiPoint']:
                            for coord in coords:
                                lon, lat = coord[0], coord[1]
                                min_lon = min(min_lon, lon)
                                max_lon = max(max_lon, lon)
                                min_lat = min(min_lat, lat)
                                max_lat = max(max_lat, lat)
                        elif geom.get('type') in ['Polygon', 'MultiLineString']:
                            for ring in coords:
                                for coord in ring:
                                    lon, lat = coord[0], coord[1]
                                    min_lon = min(min_lon, lon)
                                    max_lon = max(max_lon, lon)
                                    min_lat = min(min_lat, lat)
                                    max_lat = max(max_lat, lat)
                    
                    return [min_lon, min_lat, max_lon, max_lat]
                
                @property
                def geometry(self):
                    """Simule une GeoSeries pour compatibilité"""
                    class FakeGeoSeries:
                        def __init__(self, features):
                            self.features = features
                        
                        def geom_type(self):
                            types = []
                            for f in self.features:
                                gtype = f.get('geometry', {}).get('type', 'Unknown')
                                if gtype not in types:
                                    types.append(gtype)
                            return self
                        
                        def unique(self):
                            types = []
                            for f in self.features:
                                gtype = f.get('geometry', {}).get('type', 'Unknown')
                                if gtype not in types:
                                    types.append(gtype)
                            return types
                        
                        def tolist(self):
                            return [None] * len(self.features)
                    
                    return FakeGeoSeries(self.features)
            
            fake_gdf = FakeGeoDataFrame(geojson_data)
            
            if len(fake_gdf) == 0:
                raise ValueError("Aucune feature trouvée dans le GeoJSON")
            
            logger.info(f"GeoJSON parsé: {len(fake_gdf)} features (mode JSON pur)")
            return fake_gdf
            
        except Exception as e:
            logger.error(f"Erreur parsing GeoJSON JSON: {str(e)}")
            raise ValueError(f"Impossible de lire le GeoJSON: {str(e)}")
    
    def _parse_geojson_manual(self, file_path: str) -> Optional[gpd.GeoDataFrame]:
        """Parse un fichier GeoJSON manuellement sans GeoPandas
        
        Retourne un GeoDataFrame compatible ou lève une exception
        """
        try:
            import json
            from shapely.geometry import shape, Point, LineString, Polygon
            
            # Lire le fichier JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
            
            # Vérifier que c'est un GeoJSON valide
            if 'type' not in geojson_data:
                raise ValueError("Fichier GeoJSON invalide : champ 'type' manquant")
            
            features = []
            if geojson_data['type'] == 'FeatureCollection':
                features = geojson_data.get('features', [])
            elif geojson_data['type'] == 'Feature':
                features = [geojson_data]
            else:
                raise ValueError(f"Type GeoJSON non supporté : {geojson_data['type']}")
            
            if not features:
                raise ValueError("Aucune feature trouvée dans le GeoJSON")
            
            # Extraire les données
            rows = []
            geometries = []
            
            for i, feature in enumerate(features):
                if 'geometry' not in feature or not feature['geometry']:
                    logger.warning(f"Feature {i} sans géométrie, ignorée")
                    continue
                
                try:
                    # Convertir la géométrie GeoJSON en Shapely
                    geom = shape(feature['geometry'])
                    geometries.append(geom)
                    
                    # Extraire les propriétés
                    properties = feature.get('properties', {})
                    if not properties:
                        properties = {'id': i}
                    
                    rows.append(properties)
                    
                except Exception as e:
                    logger.warning(f"Erreur conversion géométrie feature {i}: {e}")
                    continue
            
            if not geometries:
                raise ValueError("Aucune géométrie valide trouvée")
            
            # Créer un GeoDataFrame
            if not GEOPANDAS_AVAILABLE:
                # Si GeoPandas n'est vraiment pas disponible, on ne peut pas créer de GeoDataFrame
                # Dans ce cas, on doit retourner None et signaler l'erreur
                raise ValueError(
                    "GeoPandas est requis pour importer des fichiers géospatiaux. "
                    "Installez-le avec: pip install geopandas"
                )
            
            gdf = gpd.GeoDataFrame(rows, geometry=geometries, crs='EPSG:4326')
            return self._standardize_geodataframe(gdf)
            
        except ValueError as ve:
            # Propager les erreurs de validation
            raise ve
        except Exception as e:
            logger.error(f"Erreur parsing GeoJSON manuel: {str(e)}")
            raise ValueError(f"Impossible de lire le fichier GeoJSON: {str(e)}")
    
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
        # Support pour FakeGeoDataFrame (mode JSON pur)
        if hasattr(gdf, 'geojson'):
            if len(gdf) == 0:
                return False, "Aucune donnée géospatiale valide"
            if len(gdf) > self.MAX_FEATURES:
                return False, f"Trop de features: {len(gdf)} (max: {self.MAX_FEATURES})"
            return True, "Validation réussie (mode JSON pur)"
        
        # Mode normal avec GeoPandas
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
            # Mode JSON pur (sans GeoPandas/Shapely)
            if hasattr(gdf, 'geojson'):
                return self._create_layer_from_json(gdf, layer_config, file_format, file_path)
            
            # Mode normal avec GeoPandas/Shapely
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
                    # Utiliser _to_list pour éviter l'erreur 'list' object has no attribute 'tolist'
                    geom_list = GeospatialImportService._to_list(gdf.geometry)
                    multi_geom = MultiPoint(geom_list)
                    geom_wkt = multi_geom.wkt
                    main_geom_type = 'MULTIPOINT'
                elif main_geom_type == 'LINESTRING':
                    from shapely.geometry import MultiLineString
                    geom_list = GeospatialImportService._to_list(gdf.geometry)
                    multi_geom = MultiLineString(geom_list)
                    geom_wkt = multi_geom.wkt
                    main_geom_type = 'MULTILINESTRING'
                elif main_geom_type == 'POLYGON':
                    from shapely.geometry import MultiPolygon
                    geom_list = GeospatialImportService._to_list(gdf.geometry)
                    multi_geom = MultiPolygon(geom_list)
                    geom_wkt = multi_geom.wkt
                    main_geom_type = 'MULTIPOLYGON'
                else:
                    # Prendre la première géométrie par défaut
                    geom_wkt = gdf.geometry.iloc[0].wkt
            
            # Préparation des métadonnées
            metadata_dict = {
                'properties': gdf.drop('geometry', axis=1).to_dict('records') if len(gdf.columns) > 1 else [],
                'source_info': {
                    'original_crs': str(gdf.crs) if gdf.crs else 'Unknown',
                    'feature_count': len(gdf),
                    'geometry_types': geom_types.to_dict(),
                    'bounds': self._to_list(gdf.total_bounds)
                },
                'processing_info': {
                    'import_date': datetime.now().isoformat(),
                    'file_size_bytes': os.path.getsize(file_path)
                }
            }
            
            # Création de la couche
            layer = GeospatialLayer(
                name=layer_config.get('name', f'Import {file_format}'),
                description=layer_config.get('description', f'Données importées depuis {os.path.basename(file_path)}'),
                layer_type=layer_config.get('layer_type', 'custom'),
                geometry_type=main_geom_type,
                source_format=file_format,
                source_path=file_path,
                status=layer_config.get('status', 'actif'),
                is_visible=True,  # BUG FIX #3: Explicitement visible par défaut
                geom=ST_GeomFromText(geom_wkt, 4326),
                metadata=metadata_dict
            )
            
            # Application du style par défaut
            layer.set_default_style_by_type()
            
            return layer
            
        except Exception as e:
            logger.error(f"Erreur création couche: {str(e)}", exc_info=True)
            return None
    
    def _create_layer_from_json(self, fake_gdf, layer_config: Dict[str, Any],
                               file_format: str, file_path: str) -> Optional[GeospatialLayer]:
        """Crée une couche à partir d'un GeoJSON pur (sans Shapely)"""
        try:
            geojson = fake_gdf.geojson
            
            # Déterminer le type de géométrie
            geom_types = fake_gdf.geometry.unique()
            main_geom_type = geom_types[0].upper() if geom_types else 'UNKNOWN'
            
            # Créer un WKT simple pour la première feature (pour compatibilité PostGIS)
            # Note: pour SQLite, on peut stocker juste les coordonnées en JSON
            first_feature = fake_gdf.features[0] if fake_gdf.features else None
            geom_wkt = None
            
            if first_feature and first_feature.get('geometry'):
                geom = first_feature['geometry']
                coords = geom.get('coordinates', [])
                
                # Créer un WKT basique
                if geom['type'] == 'Point':
                    geom_wkt = f"POINT({coords[0]} {coords[1]})"
                elif geom['type'] == 'LineString':
                    coords_str = ', '.join([f"{c[0]} {c[1]}" for c in coords])
                    geom_wkt = f"LINESTRING({coords_str})"
                elif geom['type'] == 'Polygon':
                    # Premier anneau seulement
                    ring = coords[0] if coords else []
                    coords_str = ', '.join([f"{c[0]} {c[1]}" for c in ring])
                    geom_wkt = f"POLYGON(({coords_str}))"
            
            # Métadonnées
            metadata_dict = {
                'geojson': geojson,  # Stocker le GeoJSON complet
                'source_info': {
                    'original_crs': 'EPSG:4326',
                    'feature_count': len(fake_gdf),
                    'geometry_types': geom_types,
                    'bounds': fake_gdf.total_bounds
                },
                'processing_info': {
                    'import_date': datetime.now().isoformat(),
                    'file_size_bytes': os.path.getsize(file_path),
                    'import_mode': 'json_pure'
                }
            }
            
            logger.info(f"Metadata dict keys: {list(metadata_dict.keys())}")
            logger.info(f"Geojson type: {type(geojson)}, has 'features': {'features' in geojson if isinstance(geojson, dict) else False}")
            
            # Création de la couche
            layer = GeospatialLayer(
                name=layer_config.get('name', f'Import {file_format}'),
                description=layer_config.get('description', f'Données importées depuis {os.path.basename(file_path)}'),
                layer_type=layer_config.get('layer_type', 'custom'),
                geometry_type=main_geom_type,
                source_format=file_format,
                source_path=file_path,
                status=layer_config.get('status', 'actif'),
                is_visible=True,  # BUG FIX #3: Explicitement visible par défaut
                geom=ST_GeomFromText(geom_wkt, 4326) if geom_wkt else None,
                layer_metadata=metadata_dict,  # CORRIGÉ: layer_metadata au lieu de metadata
                point_count=len(fake_gdf) if main_geom_type in ['POINT', 'MULTIPOINT'] else None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Style par défaut
            layer.set_default_style_by_type()
            
            logger.info(f"Couche créée en mode JSON pur: {len(fake_gdf)} features")
            return layer
            
        except Exception as e:
            logger.error(f"Erreur création couche JSON: {str(e)}", exc_info=True)
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
