-- Script de configuration PostgreSQL pour ODG Platform
-- Exécutez ce script via pgAdmin ou l'outil psql

-- 1. Créer la base de données ODG
DROP DATABASE IF EXISTS odg_database;
CREATE DATABASE odg_database
    WITH ENCODING 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252'
    TEMPLATE template0;

-- 2. Se connecter à la base de données ODG
\c odg_database;

-- 3. Créer l'utilisateur ODG
DROP ROLE IF EXISTS odg_user;
CREATE ROLE odg_user WITH
    LOGIN
    PASSWORD 'root'
    CREATEDB
    NOSUPERUSER
    NOCREATEROLE;

-- 4. Accorder les permissions sur la base de données ODG
GRANT ALL PRIVILEGES ON DATABASE odg_database TO odg_user;
GRANT ALL ON SCHEMA public TO odg_user;

-- 5. Installer les extensions PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;

-- 6. Vérifier les versions PostGIS
SELECT PostGIS_Version();
SELECT PostGIS_GEOS_Version();
SELECT PostGIS_Proj_Version();

-- 7. Configuration des permissions sur les tables PostGIS
GRANT SELECT ON spatial_ref_sys TO odg_user;
GRANT ALL ON geometry_columns TO odg_user;
GRANT ALL ON geography_columns TO odg_user;

-- 8. Message de fin
\echo 'Configuration PostgreSQL/PostGIS terminée pour ODG Platform'
\echo 'Base de données: odg_database'
\echo 'Utilisateur: odg_user / Mot de passe: root'
