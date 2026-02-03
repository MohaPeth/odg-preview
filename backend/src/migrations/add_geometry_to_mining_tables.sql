-- Migration SQL: Ajout des colonnes géométriques PostGIS aux tables minières
-- Date: 2026-01-20
-- Description: Ajoute le support PostGIS complet pour les données minières

-- ========================================
-- 1. Activation de PostGIS (si pas déjà fait)
-- ========================================
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- ========================================
-- 2. Ajout de la colonne geometry à mining_deposits
-- ========================================

-- Vérifier si la colonne existe déjà
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'mining_deposits' 
        AND column_name = 'geom'
    ) THEN
        -- Ajouter la colonne geometry
        ALTER TABLE mining_deposits 
        ADD COLUMN geom geometry(POINT, 4326);
        
        RAISE NOTICE 'Colonne geom ajoutée à mining_deposits';
    ELSE
        RAISE NOTICE 'Colonne geom existe déjà dans mining_deposits';
    END IF;
END $$;

-- Créer un index spatial pour la performance
CREATE INDEX IF NOT EXISTS idx_mining_deposits_geom 
ON mining_deposits USING GIST(geom);

-- Mettre à jour les géométries existantes depuis latitude/longitude
UPDATE mining_deposits 
SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
WHERE latitude IS NOT NULL 
  AND longitude IS NOT NULL 
  AND geom IS NULL;

-- ========================================
-- 3. Ajout de la colonne geometry à exploitation_areas
-- ========================================

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'exploitation_areas' 
        AND column_name = 'geom'
    ) THEN
        -- Ajouter la colonne geometry (POLYGON)
        ALTER TABLE exploitation_areas 
        ADD COLUMN geom geometry(POLYGON, 4326);
        
        RAISE NOTICE 'Colonne geom ajoutée à exploitation_areas';
    ELSE
        RAISE NOTICE 'Colonne geom existe déjà dans exploitation_areas';
    END IF;
END $$;

-- Créer un index spatial
CREATE INDEX IF NOT EXISTS idx_exploitation_areas_geom 
ON exploitation_areas USING GIST(geom);

-- Mettre à jour les géométries existantes depuis coordinates JSON
-- Cette fonction sera appelée par Python car nécessite un parsing JSON complexe
-- Voir le script Python: update_geometries.py

-- ========================================
-- 4. Ajout de la colonne geometry à infrastructure
-- ========================================

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'infrastructure' 
        AND column_name = 'geom'
    ) THEN
        -- Ajouter la colonne geometry (LINESTRING)
        ALTER TABLE infrastructure 
        ADD COLUMN geom geometry(LINESTRING, 4326);
        
        RAISE NOTICE 'Colonne geom ajoutée à infrastructure';
    ELSE
        RAISE NOTICE 'Colonne geom existe déjà dans infrastructure';
    END IF;
END $$;

-- Créer un index spatial
CREATE INDEX IF NOT EXISTS idx_infrastructure_geom 
ON infrastructure USING GIST(geom);

-- ========================================
-- 5. Statistiques et validation
-- ========================================

-- Afficher les statistiques
DO $$
DECLARE
    deposits_with_geom INTEGER;
    deposits_total INTEGER;
    areas_total INTEGER;
    infra_total INTEGER;
BEGIN
    SELECT COUNT(*) INTO deposits_total FROM mining_deposits;
    SELECT COUNT(*) INTO deposits_with_geom FROM mining_deposits WHERE geom IS NOT NULL;
    SELECT COUNT(*) INTO areas_total FROM exploitation_areas;
    SELECT COUNT(*) INTO infra_total FROM infrastructure;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Migration PostGIS - Résultats:';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Mining Deposits: % avec géométrie / % total', deposits_with_geom, deposits_total;
    RAISE NOTICE 'Exploitation Areas: % lignes', areas_total;
    RAISE NOTICE 'Infrastructure: % lignes', infra_total;
    RAISE NOTICE '========================================';
END $$;

-- ========================================
-- 6. Triggers pour auto-update (optionnel mais recommandé)
-- ========================================

-- Trigger pour mining_deposits: auto-update geom quand lat/lon change
CREATE OR REPLACE FUNCTION update_mining_deposit_geometry()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
        NEW.geom := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_mining_deposit_geom ON mining_deposits;
CREATE TRIGGER trigger_update_mining_deposit_geom
    BEFORE INSERT OR UPDATE OF latitude, longitude ON mining_deposits
    FOR EACH ROW
    EXECUTE FUNCTION update_mining_deposit_geometry();

-- Note: Pour exploitation_areas et infrastructure, 
-- l'update se fait via Python car le format JSON est plus complexe

-- ========================================
-- 7. Fonctions utilitaires PostGIS
-- ========================================

-- Fonction pour calculer la distance entre deux dépôts
CREATE OR REPLACE FUNCTION distance_between_deposits(deposit_id1 INTEGER, deposit_id2 INTEGER)
RETURNS FLOAT AS $$
DECLARE
    distance_km FLOAT;
BEGIN
    SELECT ST_Distance(
        d1.geom::geography,
        d2.geom::geography
    ) / 1000.0 INTO distance_km
    FROM mining_deposits d1, mining_deposits d2
    WHERE d1.id = deposit_id1 AND d2.id = deposit_id2;
    
    RETURN distance_km;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour trouver les dépôts dans un rayon (en km)
CREATE OR REPLACE FUNCTION find_deposits_in_radius(
    center_lat FLOAT, 
    center_lon FLOAT, 
    radius_km FLOAT
)
RETURNS TABLE(
    id INTEGER,
    name VARCHAR,
    distance_km FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.name,
        ROUND(ST_Distance(
            ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography,
            d.geom::geography
        )::NUMERIC / 1000.0, 2) AS distance_km
    FROM mining_deposits d
    WHERE d.geom IS NOT NULL
      AND ST_DWithin(
          ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography,
          d.geom::geography,
          radius_km * 1000
      )
    ORDER BY distance_km;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- Migration terminée
-- ========================================

RAISE NOTICE '========================================';
RAISE NOTICE 'Migration PostGIS terminée avec succès!';
RAISE NOTICE 'Les tables sont prêtes pour l''export géospatial.';
RAISE NOTICE '========================================';
