# Script de configuration PostgreSQL/PostGIS pour ODG Platform
# Executer apres redemarrage et installation de PostgreSQL

# Variables de configuration
$DB_NAME = "odg_database"
$DB_USER = "odg_user"
$DB_PASSWORD = "ODG_SecurePass2025!"
$POSTGRES_USER = "postgres"

Write-Host "Configuration PostgreSQL/PostGIS pour ODG Platform" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan

# 1. Verifier l'installation PostgreSQL
Write-Host "`n[1] Verification de PostgreSQL..." -ForegroundColor Yellow
try {
    $postgresVersion = psql --version
    Write-Host "[OK] PostgreSQL detecte: $postgresVersion" -ForegroundColor Green
}
catch {
    Write-Host "[ERREUR] PostgreSQL non trouve. Verifiez l'installation." -ForegroundColor Red
    exit 1
}

# 2. Tester la connexion
Write-Host "`n[2] Test de connexion..." -ForegroundColor Yellow
try {
    $connectionTest = psql -U $POSTGRES_USER -h localhost -p 5432 -c "SELECT version();" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Connexion PostgreSQL reussie" -ForegroundColor Green
    }
    else {
        Write-Host "[ERREUR] Echec de connexion. Verifiez le service PostgreSQL." -ForegroundColor Red
        Write-Host "[CONSEIL] Redemarrez le service: net start postgresql-x64-15" -ForegroundColor Cyan
        exit 1
    }
}
catch {
    Write-Host "[ERREUR] Erreur de connexion PostgreSQL" -ForegroundColor Red
    exit 1
}

# 3. Creer la base de donnees ODG
Write-Host "`n[3] Creation de la base de donnees ODG..." -ForegroundColor Yellow
$createDBCommand = @"
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME
    WITH ENCODING 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252'
    TEMPLATE template0;
"@

try {
    $createDBCommand | psql -U $POSTGRES_USER -h localhost -p 5432
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Base de donnees '$DB_NAME' creee avec succes" -ForegroundColor Green
    }
    else {
        Write-Host "[ATTENTION] Base de donnees existante, recreation..." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "[ERREUR] Erreur creation base de donnees" -ForegroundColor Red
    exit 1
}

# 4. Creer l'utilisateur ODG
Write-Host "`n[4] Creation de l'utilisateur ODG..." -ForegroundColor Yellow
$createUserCommand = @"
DROP USER IF EXISTS $DB_USER;
CREATE USER $DB_USER WITH
    PASSWORD '$DB_PASSWORD'
    CREATEDB
    NOSUPERUSER
    NOCREATEROLE;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
"@

try {
    $createUserCommand | psql -U $POSTGRES_USER -h localhost -p 5432
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Utilisateur '$DB_USER' cree avec succes" -ForegroundColor Green
    }
}
catch {
    Write-Host "[ERREUR] Erreur creation utilisateur" -ForegroundColor Red
}

# 5. Installer PostGIS
Write-Host "`n[5] Installation des extensions PostGIS..." -ForegroundColor Yellow
$postgisCommand = @"
-- Creer l'extension PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS postgis_sfcgal;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;

-- Verifier les versions
SELECT PostGIS_Version();
SELECT PostGIS_GEOS_Version();
SELECT PostGIS_Proj_Version();
"@

try {
    $postgisCommand | psql -U $POSTGRES_USER -h localhost -p 5432 -d $DB_NAME
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Extensions PostGIS installees avec succes" -ForegroundColor Green
    }
}
catch {
    Write-Host "[ERREUR] Erreur installation PostGIS" -ForegroundColor Red
    Write-Host "[CONSEIL] Assurez-vous que PostGIS est installe avec PostgreSQL" -ForegroundColor Cyan
}

# 6. Accorder les permissions sur les extensions
Write-Host "`n[6] Configuration des permissions..." -ForegroundColor Yellow
$permissionsCommand = @"
GRANT ALL ON schema public TO $DB_USER;
GRANT ALL ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO $DB_USER;

-- Permissions sur les tables PostGIS
GRANT SELECT ON spatial_ref_sys TO $DB_USER;
GRANT ALL ON geometry_columns TO $DB_USER;
GRANT ALL ON geography_columns TO $DB_USER;
"@

try {
    $permissionsCommand | psql -U $POSTGRES_USER -h localhost -p 5432 -d $DB_NAME
    Write-Host "[OK] Permissions configurees" -ForegroundColor Green
}
catch {
    Write-Host "[ATTENTION] Avertissement: Certaines permissions ont echoue" -ForegroundColor Yellow
}

# 7. Test de connexion avec l'utilisateur ODG
Write-Host "`n[7] Test de connexion utilisateur ODG..." -ForegroundColor Yellow
$env:PGPASSWORD = $DB_PASSWORD
try {
    $userTest = psql -U $DB_USER -h localhost -p 5432 -d $DB_NAME -c "SELECT current_user, current_database();"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Connexion utilisateur ODG reussie" -ForegroundColor Green
    }
}
catch {
    Write-Host "[ERREUR] Echec connexion utilisateur ODG" -ForegroundColor Red
}

# 8. Creer le fichier de configuration de connexion
Write-Host "`n[8] Creation du fichier de configuration..." -ForegroundColor Yellow
$configContent = @"
# Configuration PostgreSQL/PostGIS pour ODG Platform
# Genere le $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

[DATABASE]
HOST=localhost
PORT=5432
NAME=$DB_NAME
USER=$DB_USER
PASSWORD=$DB_PASSWORD

[CONNECTION_STRING]
postgresql://$DB_USER`:$DB_PASSWORD@localhost`:5432/$DB_NAME

[VERIFICATION]
# Pour tester la connexion:
# psql -U $DB_USER -h localhost -p 5432 -d $DB_NAME

[POSTGIS_INFO]
# Extensions installees:
# - postgis (geometries et geographie)
# - postgis_topology (topologie)
# - postgis_sfcgal (3D et geometries avancees)
# - fuzzystrmatch (correspondance floue)
# - postgis_tiger_geocoder (geocodage US)
"@

$configPath = "database_config.txt"
$configContent | Out-File -FilePath $configPath -Encoding utf8
Write-Host "[OK] Configuration sauvegardee dans: $configPath" -ForegroundColor Green

# 9. Resume final
Write-Host "`n[TERMINE] CONFIGURATION TERMINEE" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "Base de donnees: $DB_NAME" -ForegroundColor White
Write-Host "Utilisateur: $DB_USER" -ForegroundColor White
Write-Host "Host: localhost:5432" -ForegroundColor White
Write-Host "URI de connexion: postgresql://$DB_USER`:$DB_PASSWORD@localhost`:5432/$DB_NAME" -ForegroundColor White

Write-Host "`n[ETAPES SUIVANTES]:" -ForegroundColor Yellow
Write-Host "1. Executer la migration: python src/migrate_to_postgis.py" -ForegroundColor Cyan
Write-Host "2. Demarrer l'API: python src/main_postgis.py" -ForegroundColor Cyan
Write-Host "3. Tester l'API: http://localhost:5000/api/health" -ForegroundColor Cyan

Write-Host "`n[OK] PostgreSQL/PostGIS pret pour ODG Platform!" -ForegroundColor Green
