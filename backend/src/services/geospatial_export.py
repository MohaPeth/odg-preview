"""
Service d'export de données géospatiales pour ODG
Supporte KML, KMZ, Shapefile, GeoJSON, CSV, WKT
"""

import os
import io
import tempfile
import zipfile
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import csv as csv_module

from geoalchemy2.shape import to_shape

from src.models.geospatial_layers import GeospatialLayer

# Import conditionnel pour Shapely
try:
    from shapely.geometry import shape
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False

logger = logging.getLogger(__name__)

# Import conditionnel pour KML
try:
    import simplekml
    SIMPLEKML_AVAILABLE = True
    logger.info("Module simplekml disponible - Export KML activé")
except ImportError:
    SIMPLEKML_AVAILABLE = False
    logger.warning("Module simplekml non disponible. Installez: pip install simplekml")

# Import conditionnel pour GeoPandas/Fiona (Shapefile)
try:
    import geopandas as gpd
    import pandas as pd
    import fiona
    GEOPANDAS_AVAILABLE = True
    FIONA_AVAILABLE = True
    logger.info("Modules geopandas/fiona disponibles - Export Shapefile activé")
except ImportError as e:
    GEOPANDAS_AVAILABLE = False
    FIONA_AVAILABLE = False
    logger.warning(f"Modules geopandas/fiona non disponibles - Export Shapefile désactivé. Erreur: {str(e)}")
    logger.warning("Pour activer l'export Shapefile sur Windows, consultez: https://www.lfd.uci.edu/~gohlke/pythonlibs/")


class GeospatialExportService:
    """Service principal pour l'export de couches géospatiales"""
    
    SUPPORTED_FORMATS = {
        'GEOJSON': 'application/geo+json',
        'KML': 'application/vnd.google-earth.kml+xml',
        'KMZ': 'application/vnd.google-earth.kmz',
        'SHP': 'application/x-shapefile',
        'CSV': 'text/csv',
        'WKT': 'text/plain',
        'GPX': 'application/gpx+xml'
    }
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix='odg_export_')
        logger.info(f"Service d'export initialisé. Dossier temp: {self.temp_dir}")
    
    def export_layer(self, layer: GeospatialLayer, format: str) -> Tuple[bool, str, Optional[bytes], Optional[str]]:
        """
        Export principal d'une couche géospatiale
        
        Args:
            layer: Couche GeospatialLayer à exporter
            format: Format d'export (geojson, kml, shp, csv, wkt)
            
        Returns:
            Tuple (success, message, file_content_bytes, mime_type)
        """
        format_upper = format.upper()
        
        if format_upper not in self.SUPPORTED_FORMATS:
            return False, f"Format non supporté: {format}", None, None
        
        try:
            logger.info(f"Début export de la couche {layer.id} en format {format_upper}")
            
            if format_upper == 'GEOJSON':
                return self._export_geojson(layer)
            
            elif format_upper == 'KML':
                return self._export_kml(layer)
            
            elif format_upper == 'KMZ':
                return self._export_kmz(layer)
            
            elif format_upper == 'SHP':
                return self._export_shapefile(layer)
            
            elif format_upper == 'CSV':
                return self._export_csv(layer)
            
            elif format_upper == 'WKT':
                return self._export_wkt(layer)
            
            elif format_upper == 'GPX':
                return self._export_gpx(layer)
            
            else:
                return False, f"Format {format_upper} non implémenté", None, None
                
        except Exception as e:
            logger.error(f"Erreur lors de l'export en {format_upper}: {str(e)}")
            return False, f"Erreur d'export: {str(e)}", None, None
    
    def _export_geojson(self, layer: GeospatialLayer) -> Tuple[bool, str, bytes, str]:
        """Export en GeoJSON (déjà fonctionnel dans le modèle)"""
        try:
            feature = layer.to_geojson_feature()
            if not feature:
                return False, "Impossible de générer le GeoJSON", None, None
            
            import json
            geojson_str = json.dumps(feature, indent=2, ensure_ascii=False)
            content = geojson_str.encode('utf-8')
            
            logger.info(f"Export GeoJSON réussi pour la couche {layer.id}")
            return True, "Export GeoJSON réussi", content, self.SUPPORTED_FORMATS['GEOJSON']
            
        except Exception as e:
            logger.error(f"Erreur export GeoJSON: {str(e)}")
            return False, f"Erreur GeoJSON: {str(e)}", None, None
    
    def _export_kml(self, layer: GeospatialLayer) -> Tuple[bool, str, bytes, str]:
        """Export en KML (Google Earth)"""
        if not SIMPLEKML_AVAILABLE:
            return False, "Module simplekml non disponible. Installez: pip install simplekml", None, None
        
        try:
            kml = simplekml.Kml()
            kml.document.name = layer.name
            
            # Récupération de la géométrie
            if not layer.geom:
                return False, "Aucune géométrie disponible", None, None
            
            geom_shape = to_shape(layer.geom)
            
            # Style personnalisé
            style = simplekml.Style()
            
            # Configuration selon le type de géométrie
            if layer.geometry_type in ['POINT', 'MULTIPOINT']:
                style.iconstyle.icon.href = layer.style_config.get('iconUrl', 'http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png')
                style.iconstyle.color = self._hex_to_kml_color(layer.style_config.get('color', '#3b82f6'))
                style.iconstyle.scale = 1.2
                
                if geom_shape.geom_type == 'Point':
                    pnt = kml.newpoint(name=layer.name)
                    pnt.coords = [(geom_shape.x, geom_shape.y)]
                    pnt.style = style
                    pnt.description = self._generate_kml_description(layer)
                
                elif geom_shape.geom_type == 'MultiPoint':
                    for idx, point in enumerate(geom_shape.geoms):
                        pnt = kml.newpoint(name=f"{layer.name} - Point {idx+1}")
                        pnt.coords = [(point.x, point.y)]
                        pnt.style = style
                        pnt.description = self._generate_kml_description(layer)
            
            elif layer.geometry_type in ['LINESTRING', 'MULTILINESTRING']:
                style.linestyle.color = self._hex_to_kml_color(layer.style_config.get('color', '#3b82f6'))
                style.linestyle.width = layer.style_config.get('weight', 2)
                
                if geom_shape.geom_type == 'LineString':
                    lin = kml.newlinestring(name=layer.name)
                    lin.coords = list(geom_shape.coords)
                    lin.style = style
                    lin.description = self._generate_kml_description(layer)
                
                elif geom_shape.geom_type == 'MultiLineString':
                    for idx, line in enumerate(geom_shape.geoms):
                        lin = kml.newlinestring(name=f"{layer.name} - Segment {idx+1}")
                        lin.coords = list(line.coords)
                        lin.style = style
                        lin.description = self._generate_kml_description(layer)
            
            elif layer.geometry_type in ['POLYGON', 'MULTIPOLYGON']:
                style.polystyle.color = self._hex_to_kml_color(
                    layer.style_config.get('fillColor', '#3b82f6'),
                    alpha=int(layer.style_config.get('fillOpacity', 0.3) * 255)
                )
                style.linestyle.color = self._hex_to_kml_color(layer.style_config.get('color', '#3b82f6'))
                style.linestyle.width = layer.style_config.get('weight', 2)
                
                if geom_shape.geom_type == 'Polygon':
                    pol = kml.newpolygon(name=layer.name)
                    pol.outerboundaryis = list(geom_shape.exterior.coords)
                    if geom_shape.interiors:
                        pol.innerboundaryis = [list(interior.coords) for interior in geom_shape.interiors]
                    pol.style = style
                    pol.description = self._generate_kml_description(layer)
                
                elif geom_shape.geom_type == 'MultiPolygon':
                    for idx, polygon in enumerate(geom_shape.geoms):
                        pol = kml.newpolygon(name=f"{layer.name} - Zone {idx+1}")
                        pol.outerboundaryis = list(polygon.exterior.coords)
                        if polygon.interiors:
                            pol.innerboundaryis = [list(interior.coords) for interior in polygon.interiors]
                        pol.style = style
                        pol.description = self._generate_kml_description(layer)
            
            # Génération du KML
            kml_str = kml.kml()
            content = kml_str.encode('utf-8')
            
            logger.info(f"Export KML réussi pour la couche {layer.id}")
            return True, "Export KML réussi", content, self.SUPPORTED_FORMATS['KML']
            
        except Exception as e:
            logger.error(f"Erreur export KML: {str(e)}")
            return False, f"Erreur KML: {str(e)}", None, None
    
    def _export_kmz(self, layer: GeospatialLayer) -> Tuple[bool, str, bytes, str]:
        """Export en KMZ (KML compressé)"""
        # Export d'abord en KML
        success, message, kml_content, _ = self._export_kml(layer)
        
        if not success:
            return False, message, None, None
        
        try:
            # Création d'un ZIP avec le KML
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr('doc.kml', kml_content)
            
            content = zip_buffer.getvalue()
            
            logger.info(f"Export KMZ réussi pour la couche {layer.id}")
            return True, "Export KMZ réussi", content, self.SUPPORTED_FORMATS['KMZ']
            
        except Exception as e:
            logger.error(f"Erreur export KMZ: {str(e)}")
            return False, f"Erreur KMZ: {str(e)}", None, None
    
    def _export_shapefile(self, layer: GeospatialLayer) -> Tuple[bool, str, bytes, str]:
        """Export en Shapefile ESRI (format ZIP contenant .shp, .shx, .dbf, .prj)"""
        if not GEOPANDAS_AVAILABLE or not FIONA_AVAILABLE:
            return False, "Export Shapefile non disponible. Installez geopandas et fiona (nécessite GDAL sur Windows). Consultez: https://www.lfd.uci.edu/~gohlke/pythonlibs/", None, None
        
        try:
            if not layer.geom:
                return False, "Aucune géométrie disponible", None, None
            
            # Conversion en GeoDataFrame
            geom_shape = to_shape(layer.geom)
            
            # Création du GeoDataFrame
            data = {
                'id': [layer.id],
                'name': [layer.name[:80]],  # Limite 80 caractères pour DBF
                'layer_type': [layer.layer_type[:50]],
                'status': [layer.status[:50]],
                'area_km2': [layer.area_km2 if layer.area_km2 else None],
                'length_km': [layer.length_km if layer.length_km else None],
                'geometry': [geom_shape]
            }
            
            gdf = gpd.GeoDataFrame(data, crs='EPSG:4326')
            
            # Export dans un dossier temporaire
            shp_name = f"layer_{layer.id}"
            shp_dir = os.path.join(self.temp_dir, shp_name)
            os.makedirs(shp_dir, exist_ok=True)
            shp_path = os.path.join(shp_dir, f"{shp_name}.shp")
            
            gdf.to_file(shp_path, driver='ESRI Shapefile')
            
            # Compression en ZIP
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg']:
                    file_path = shp_path.replace('.shp', ext)
                    if os.path.exists(file_path):
                        zip_file.write(file_path, os.path.basename(file_path))
            
            content = zip_buffer.getvalue()
            
            logger.info(f"Export Shapefile réussi pour la couche {layer.id}")
            return True, "Export Shapefile réussi", content, self.SUPPORTED_FORMATS['SHP']
            
        except Exception as e:
            logger.error(f"Erreur export Shapefile: {str(e)}")
            return False, f"Erreur Shapefile: {str(e)}", None, None
    
    def _export_csv(self, layer: GeospatialLayer) -> Tuple[bool, str, bytes, str]:
        """Export en CSV avec coordonnées"""
        try:
            if not layer.geom:
                return False, "Aucune géométrie disponible", None, None
            
            geom_shape = to_shape(layer.geom)
            
            # Buffer CSV
            csv_buffer = io.StringIO()
            writer = csv_module.writer(csv_buffer)
            
            # En-têtes
            if layer.geometry_type in ['POINT', 'MULTIPOINT']:
                writer.writerow(['id', 'name', 'layer_type', 'status', 'longitude', 'latitude', 'description'])
                
                if geom_shape.geom_type == 'Point':
                    writer.writerow([
                        layer.id,
                        layer.name,
                        layer.layer_type,
                        layer.status,
                        geom_shape.x,
                        geom_shape.y,
                        layer.description or ''
                    ])
                elif geom_shape.geom_type == 'MultiPoint':
                    for idx, point in enumerate(geom_shape.geoms):
                        writer.writerow([
                            f"{layer.id}_{idx}",
                            f"{layer.name} - Point {idx+1}",
                            layer.layer_type,
                            layer.status,
                            point.x,
                            point.y,
                            layer.description or ''
                        ])
            
            elif layer.geometry_type in ['LINESTRING', 'MULTILINESTRING']:
                writer.writerow(['id', 'name', 'layer_type', 'status', 'length_km', 'wkt', 'description'])
                writer.writerow([
                    layer.id,
                    layer.name,
                    layer.layer_type,
                    layer.status,
                    layer.length_km or '',
                    geom_shape.wkt,
                    layer.description or ''
                ])
            
            elif layer.geometry_type in ['POLYGON', 'MULTIPOLYGON']:
                writer.writerow(['id', 'name', 'layer_type', 'status', 'area_km2', 'wkt', 'description'])
                writer.writerow([
                    layer.id,
                    layer.name,
                    layer.layer_type,
                    layer.status,
                    layer.area_km2 or '',
                    geom_shape.wkt,
                    layer.description or ''
                ])
            
            content = csv_buffer.getvalue().encode('utf-8-sig')  # BOM pour Excel
            
            logger.info(f"Export CSV réussi pour la couche {layer.id}")
            return True, "Export CSV réussi", content, self.SUPPORTED_FORMATS['CSV']
            
        except Exception as e:
            logger.error(f"Erreur export CSV: {str(e)}")
            return False, f"Erreur CSV: {str(e)}", None, None
    
    def _export_wkt(self, layer: GeospatialLayer) -> Tuple[bool, str, bytes, str]:
        """Export en WKT (Well-Known Text)"""
        try:
            if not layer.geom:
                return False, "Aucune géométrie disponible", None, None
            
            geom_shape = to_shape(layer.geom)
            wkt_str = geom_shape.wkt
            
            # Ajout des métadonnées en commentaire
            content_lines = [
                f"# Couche: {layer.name}",
                f"# Type: {layer.geometry_type}",
                f"# Statut: {layer.status}",
                f"# SRID: 4326 (WGS84)",
                "",
                wkt_str
            ]
            
            content = '\n'.join(content_lines).encode('utf-8')
            
            logger.info(f"Export WKT réussi pour la couche {layer.id}")
            return True, "Export WKT réussi", content, self.SUPPORTED_FORMATS['WKT']
            
        except Exception as e:
            logger.error(f"Erreur export WKT: {str(e)}")
            return False, f"Erreur WKT: {str(e)}", None, None
    
    def _export_gpx(self, layer: GeospatialLayer) -> Tuple[bool, str, bytes, str]:
        """Export en GPX (GPS Exchange Format) - pour points uniquement"""
        if layer.geometry_type not in ['POINT', 'MULTIPOINT']:
            return False, "Format GPX disponible uniquement pour les points", None, None
        
        try:
            if not layer.geom:
                return False, "Aucune géométrie disponible", None, None
            
            geom_shape = to_shape(layer.geom)
            
            # Génération XML GPX
            gpx_lines = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<gpx version="1.1" creator="ODG Geospatial" xmlns="http://www.topografix.com/GPX/1/1">',
                f'  <metadata>',
                f'    <name>{layer.name}</name>',
                f'    <desc>{layer.description or "Export ODG"}</desc>',
                f'  </metadata>'
            ]
            
            if geom_shape.geom_type == 'Point':
                gpx_lines.extend([
                    f'  <wpt lat="{geom_shape.y}" lon="{geom_shape.x}">',
                    f'    <name>{layer.name}</name>',
                    f'    <desc>{layer.description or ""}</desc>',
                    f'    <type>{layer.layer_type}</type>',
                    f'  </wpt>'
                ])
            elif geom_shape.geom_type == 'MultiPoint':
                for idx, point in enumerate(geom_shape.geoms):
                    gpx_lines.extend([
                        f'  <wpt lat="{point.y}" lon="{point.x}">',
                        f'    <name>{layer.name} - Point {idx+1}</name>',
                        f'    <desc>{layer.description or ""}</desc>',
                        f'    <type>{layer.layer_type}</type>',
                        f'  </wpt>'
                    ])
            
            gpx_lines.append('</gpx>')
            
            content = '\n'.join(gpx_lines).encode('utf-8')
            
            logger.info(f"Export GPX réussi pour la couche {layer.id}")
            return True, "Export GPX réussi", content, self.SUPPORTED_FORMATS['GPX']
            
        except Exception as e:
            logger.error(f"Erreur export GPX: {str(e)}")
            return False, f"Erreur GPX: {str(e)}", None, None
    
    def _generate_kml_description(self, layer: GeospatialLayer) -> str:
        """Génère une description HTML pour les popups KML"""
        desc_parts = [
            f"<h3>{layer.name}</h3>",
            f"<p><b>Type:</b> {layer.layer_type}</p>",
            f"<p><b>Statut:</b> {layer.status}</p>"
        ]
        
        if layer.description:
            desc_parts.append(f"<p><b>Description:</b> {layer.description}</p>")
        
        if layer.area_km2:
            desc_parts.append(f"<p><b>Superficie:</b> {layer.area_km2:.2f} km²</p>")
        
        if layer.length_km:
            desc_parts.append(f"<p><b>Longueur:</b> {layer.length_km:.2f} km</p>")
        
        if layer.point_count and layer.point_count > 1:
            desc_parts.append(f"<p><b>Nombre de points:</b> {layer.point_count}</p>")
        
        return '\n'.join(desc_parts)
    
    def _hex_to_kml_color(self, hex_color: str, alpha: int = 255) -> str:
        """Convertit une couleur hex en format KML (aabbggrr)"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f"{alpha:02x}{b:02x}{g:02x}{r:02x}"
    
    def cleanup(self):
        """Nettoyage du dossier temporaire"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Nettoyage du dossier temporaire: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"Impossible de nettoyer {self.temp_dir}: {str(e)}")
    
    def __del__(self):
        """Nettoyage automatique à la destruction"""
        self.cleanup()


# Fonction utilitaire pour export batch
def export_multiple_layers(layer_ids: List[int], format: str) -> Tuple[bool, str, Optional[bytes], Optional[str]]:
    """
    Export de plusieurs couches en un seul fichier ZIP
    
    Args:
        layer_ids: Liste des IDs de couches à exporter
        format: Format d'export
        
    Returns:
        Tuple (success, message, zip_content, mime_type)
    """
    try:
        export_service = GeospatialExportService()
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for layer_id in layer_ids:
                layer = GeospatialLayer.query.get(layer_id)
                if not layer:
                    continue
                
                success, message, content, _ = export_service.export_layer(layer, format)
                if success and content:
                    filename = f"{layer.name}_{layer.id}.{format.lower()}"
                    zip_file.writestr(filename, content)
        
        export_service.cleanup()
        content = zip_buffer.getvalue()
        
        return True, f"{len(layer_ids)} couches exportées", content, 'application/zip'
        
    except Exception as e:
        logger.error(f"Erreur export multiple: {str(e)}")
        return False, f"Erreur: {str(e)}", None, None
