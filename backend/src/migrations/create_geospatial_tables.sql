-- Migration PostGIS pour les couches géospatiales ODG
-- Version: 1.0
-- Date: 2025-11-17
-- Description: Création des tables pour l'import de données géospatiales

-- Activation de l'extension PostGIS si pas déjà fait
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Table principale pour les couches géospatiales
CREATE TABLE IF NOT EXISTS geospatial_layers (
    id SERIAL PRIMARY KEY,
    
    -- Métadonnées de base
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Configuration de la couche
    layer_type VARCHAR(50) NOT NULL CHECK (layer_type IN ('deposit', 'infrastructure', 'zone', 'custom')),
    geometry_type VARCHAR(20) NOT NULL CHECK (geometry_type IN ('POINT', 'LINESTRING', 'POLYGON', 'MULTIPOINT', 'MULTILINESTRING', 'MULTIPOLYGON')),
    source_format VARCHAR(10) NOT NULL CHECK (source_format IN ('KML', 'KMZ', 'SHP', 'GEOJSON', 'CSV', 'TXT', 'TIFF')),
    source_path VARCHAR(500),
    
    -- Statut et visibilité
    status VARCHAR(50) DEFAULT 'actif' CHECK (status IN ('actif', 'en_développement', 'exploration', 'terminé')),
    is_visible BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT TRUE,
    
    -- Configuration des styles (JSON)
    style_config JSONB DEFAULT '{"color": "#3b82f6", "fillColor": "#3b82f6", "fillOpacity": 0.3, "weight": 2, "opacity": 0.8, "iconUrl": null, "iconSize": [20, 20]}',
    
    -- Métadonnées additionnelles (JSON)
    metadata JSONB DEFAULT '{"properties": {}, "attributes": {}, "source_info": {}, "processing_info": {}}',
    
    -- Géométrie spatiale (PostGIS) - WGS84
    geom GEOMETRY(GEOMETRY, 4326),
    
    -- Statistiques calculées
    area_km2 DECIMAL(12, 4),
    length_km DECIMAL(10, 3),
    point_count INTEGER DEFAULT 1,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Relations (pour futures extensions)
    created_by_user_id INTEGER
);

-- Table d'historique des uploads
CREATE TABLE IF NOT EXISTS layer_upload_history (
    id SERIAL PRIMARY KEY,
    layer_id INTEGER REFERENCES geospatial_layers(id) ON DELETE SET NULL,
    
    -- Informations sur le fichier
    original_filename VARCHAR(255) NOT NULL,
    file_size_bytes BIGINT,
    file_format VARCHAR(10) NOT NULL,
    
    -- Statut du traitement
    upload_status VARCHAR(20) DEFAULT 'pending' CHECK (upload_status IN ('pending', 'processing', 'success', 'error')),
    error_message TEXT,
    
    -- Statistiques du traitement
    features_count INTEGER,
    processing_time_seconds DECIMAL(8, 3),
    
    -- Métadonnées du fichier
    file_metadata JSONB,
    
    -- Timestamps
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Index pour les performances
CREATE INDEX IF NOT EXISTS idx_geospatial_layers_name ON geospatial_layers(name);
CREATE INDEX IF NOT EXISTS idx_geospatial_layers_layer_type ON geospatial_layers(layer_type);
CREATE INDEX IF NOT EXISTS idx_geospatial_layers_status ON geospatial_layers(status);
CREATE INDEX IF NOT EXISTS idx_geospatial_layers_visible ON geospatial_layers(is_visible);
CREATE INDEX IF NOT EXISTS idx_geospatial_layers_created_at ON geospatial_layers(created_at);

-- Index spatial principal (GIST pour PostGIS)
CREATE INDEX IF NOT EXISTS idx_geospatial_layers_geom ON geospatial_layers USING GIST (geom);

-- Index sur les métadonnées JSON pour les recherches
CREATE INDEX IF NOT EXISTS idx_geospatial_layers_metadata ON geospatial_layers USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_geospatial_layers_style_config ON geospatial_layers USING GIN (style_config);

-- Index pour l'historique des uploads
CREATE INDEX IF NOT EXISTS idx_upload_history_layer_id ON layer_upload_history(layer_id);
CREATE INDEX IF NOT EXISTS idx_upload_history_status ON layer_upload_history(upload_status);
CREATE INDEX IF NOT EXISTS idx_upload_history_uploaded_at ON layer_upload_history(uploaded_at);

-- Trigger pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_geospatial_layers_updated_at 
    BEFORE UPDATE ON geospatial_layers 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Fonction pour calculer automatiquement les statistiques géométriques
CREATE OR REPLACE FUNCTION calculate_geometry_statistics()
RETURNS TRIGGER AS $$
BEGIN
    -- Calcul de la superficie pour les polygones (en km²)
    IF NEW.geometry_type IN ('POLYGON', 'MULTIPOLYGON') AND NEW.geom IS NOT NULL THEN
        NEW.area_km2 = ST_Area(NEW.geom::geography) / 1000000.0;
    END IF;
    
    -- Calcul de la longueur pour les lignes (en km)
    IF NEW.geometry_type IN ('LINESTRING', 'MULTILINESTRING') AND NEW.geom IS NOT NULL THEN
        NEW.length_km = ST_Length(NEW.geom::geography) / 1000.0;
    END IF;
    
    -- Comptage des points pour les multipoints
    IF NEW.geometry_type = 'MULTIPOINT' AND NEW.geom IS NOT NULL THEN
        NEW.point_count = ST_NumGeometries(NEW.geom);
    ELSIF NEW.geometry_type = 'POINT' THEN
        NEW.point_count = 1;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER calculate_geospatial_statistics
    BEFORE INSERT OR UPDATE ON geospatial_layers
    FOR EACH ROW
    EXECUTE FUNCTION calculate_geometry_statistics();

-- Vues utiles pour les requêtes fréquentes

-- Vue des couches actives avec statistiques
CREATE OR REPLACE VIEW active_geospatial_layers AS
SELECT 
    id,
    name,
    description,
    layer_type,
    geometry_type,
    status,
    area_km2,
    length_km,
    point_count,
    ST_AsGeoJSON(geom) as geojson,
    style_config,
    created_at,
    updated_at
FROM geospatial_layers 
WHERE is_visible = TRUE AND status = 'actif'
ORDER BY created_at DESC;

-- Vue des statistiques par type de couche
CREATE OR REPLACE VIEW layer_statistics_by_type AS
SELECT 
    layer_type,
    geometry_type,
    COUNT(*) as layer_count,
    SUM(CASE WHEN area_km2 IS NOT NULL THEN area_km2 ELSE 0 END) as total_area_km2,
    SUM(CASE WHEN length_km IS NOT NULL THEN length_km ELSE 0 END) as total_length_km,
    SUM(CASE WHEN point_count IS NOT NULL THEN point_count ELSE 0 END) as total_points,
    AVG(CASE WHEN area_km2 IS NOT NULL THEN area_km2 ELSE NULL END) as avg_area_km2
FROM geospatial_layers 
WHERE is_visible = TRUE
GROUP BY layer_type, geometry_type
ORDER BY layer_type, geometry_type;

-- Fonction pour la recherche spatiale
CREATE OR REPLACE FUNCTION search_layers_within_bounds(
    min_lat DECIMAL, 
    min_lon DECIMAL, 
    max_lat DECIMAL, 
    max_lon DECIMAL
)
RETURNS TABLE(
    id INTEGER,
    name VARCHAR(255),
    layer_type VARCHAR(50),
    geometry_type VARCHAR(20),
    geojson TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        l.id,
        l.name,
        l.layer_type,
        l.geometry_type,
        ST_AsGeoJSON(l.geom) as geojson
    FROM geospatial_layers l
    WHERE l.is_visible = TRUE 
    AND l.geom && ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326);
END;
$$ LANGUAGE plpgsql;

-- Données de test pour validation
INSERT INTO geospatial_layers (
    name, 
    description, 
    layer_type, 
    geometry_type, 
    source_format, 
    status,
    geom
) VALUES 
(
    'Test Point Libreville',
    'Point de test pour validation PostGIS',
    'custom',
    'POINT',
    'CSV',
    'actif',
    ST_GeomFromText('POINT(9.4536 0.3901)', 4326)
),
(
    'Test Route Libreville-Port-Gentil',
    'Ligne de test pour validation PostGIS',
    'infrastructure',
    'LINESTRING',
    'KML',
    'actif',
    ST_GeomFromText('LINESTRING(9.4536 0.3901, 8.7817 -0.7193)', 4326)
),
(
    'Test Zone Estuaire',
    'Polygone de test pour validation PostGIS',
    'zone',
    'POLYGON',
    'SHP',
    'actif',
    ST_GeomFromText('POLYGON((9.0 0.0, 10.0 0.0, 10.0 1.0, 9.0 1.0, 9.0 0.0))', 4326)
);

-- Vérification de l'installation
SELECT 'PostGIS Extension Version: ' || PostGIS_Version() as info
UNION ALL
SELECT 'Total test layers created: ' || COUNT(*)::text FROM geospatial_layers
UNION ALL
SELECT 'Spatial index exists: ' || CASE WHEN EXISTS(
    SELECT 1 FROM pg_indexes 
    WHERE tablename = 'geospatial_layers' 
    AND indexname = 'idx_geospatial_layers_geom'
) THEN 'YES' ELSE 'NO' END;

COMMIT;
