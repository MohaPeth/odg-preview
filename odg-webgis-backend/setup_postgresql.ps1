# Script de configuration PostgreSQL/PostGIS pour ODG Platform
# Exécuter après redémarrage et installation de PostgreSQL

# Variables de configuration
$DB_NAME = "odg_database"
$DB_USER = "odg_user"
$DB_PASSWORD = "ODG_SecurePass2025!"
$POSTGRES_USER = "postgres"

Write-Host "🔧 Configuration PostgreSQL/PostGIS pour ODG Platform" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan

# 1. Vérifier l'installation PostgreSQL
Write-Host "`n1️⃣ Vérification de PostgreSQL..." -ForegroundColor Yellow
try {
    $postgresVersion = psql --version
    Write-Host "✅ PostgreSQL détecté: $postgresVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ PostgreSQL non trouvé. Vérifiez l'installation." -ForegroundColor Red
    exit 1
}

# 2. Tester la connexion
Write-Host "`n2️⃣ Test de connexion..." -ForegroundColor Yellow
try {
    $connectionTest = psql -U $POSTGRES_USER -h localhost -p 5432 -c "SELECT version();" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Connexion PostgreSQL réussie" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Échec de connexion. Vérifiez le service PostgreSQL." -ForegroundColor Red
        Write-Host "💡 Redémarrez le service: net start postgresql-x64-15" -ForegroundColor Cyan
        exit 1
    }
}
catch {
    Write-Host "❌ Erreur de connexion PostgreSQL" -ForegroundColor Red
    exit 1
}

# 3. Créer la base de données ODG
Write-Host "`n3️⃣ Création de la base de données ODG..." -ForegroundColor Yellow
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
        Write-Host "✅ Base de données '$DB_NAME' créée avec succès" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️ Base de données existante, recréation..." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ Erreur création base de données" -ForegroundColor Red
    exit 1
}

# 4. Créer l'utilisateur ODG
Write-Host "`n4️⃣ Création de l'utilisateur ODG..." -ForegroundColor Yellow
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
        Write-Host "✅ Utilisateur '$DB_USER' créé avec succès" -ForegroundColor Green
    }
}
catch {
    Write-Host "❌ Erreur création utilisateur" -ForegroundColor Red
}

# 5. Installer PostGIS
Write-Host "`n5️⃣ Installation des extensions PostGIS..." -ForegroundColor Yellow
$postgisCommand = @"
-- Créer l'extension PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS postgis_sfcgal;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;

-- Vérifier les versions
SELECT PostGIS_Version();
SELECT PostGIS_GEOS_Version();
SELECT PostGIS_Proj_Version();
"@

try {
    $postgisCommand | psql -U $POSTGRES_USER -h localhost -p 5432 -d $DB_NAME
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Extensions PostGIS installées avec succès" -ForegroundColor Green
    }
}
catch {
    Write-Host "❌ Erreur installation PostGIS" -ForegroundColor Red
    Write-Host "💡 Assurez-vous que PostGIS est installé avec PostgreSQL" -ForegroundColor Cyan
}

# 6. Accorder les permissions sur les extensions
Write-Host "`n6️⃣ Configuration des permissions..." -ForegroundColor Yellow
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
    Write-Host "✅ Permissions configurées" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Avertissement: Certaines permissions ont échoué" -ForegroundColor Yellow
}

# 7. Test de connexion avec l'utilisateur ODG
Write-Host "`n7️⃣ Test de connexion utilisateur ODG..." -ForegroundColor Yellow
$env:PGPASSWORD = $DB_PASSWORD
try {
    $userTest = psql -U $DB_USER -h localhost -p 5432 -d $DB_NAME -c "SELECT current_user, current_database();"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Connexion utilisateur ODG réussie" -ForegroundColor Green
    }
}
catch {
    Write-Host "❌ Échec connexion utilisateur ODG" -ForegroundColor Red
}

# 8. Créer le fichier de configuration de connexion
Write-Host "`n8️⃣ Création du fichier de configuration..." -ForegroundColor Yellow
$configContent = @"
# Configuration PostgreSQL/PostGIS pour ODG Platform
# Généré le $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

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
# Extensions installées:
# - postgis (géométries et géographie)
# - postgis_topology (topologie)
# - postgis_sfcgal (3D et géométries avancées)
# - fuzzystrmatch (correspondance floue)
# - postgis_tiger_geocoder (géocodage US)
"@

$configPath = "database_config.txt"
$configContent | Out-File -FilePath $configPath -Encoding utf8
Write-Host "✅ Configuration sauvegardée dans: $configPath" -ForegroundColor Green

# 9. Résumé final
Write-Host "`n🎉 CONFIGURATION TERMINÉE" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "Base de données: $DB_NAME" -ForegroundColor White
Write-Host "Utilisateur: $DB_USER" -ForegroundColor White
Write-Host "Host: localhost:5432" -ForegroundColor White
Write-Host "URI de connexion: postgresql://$DB_USER`:$DB_PASSWORD@localhost`:5432/$DB_NAME" -ForegroundColor White

Write-Host "`n📋 ÉTAPES SUIVANTES:" -ForegroundColor Yellow
Write-Host "1. Exécuter la migration: python src/migrate_to_postgis.py" -ForegroundColor Cyan
Write-Host "2. Démarrer l'API: python src/main_postgis.py" -ForegroundColor Cyan
Write-Host "3. Tester l'API: http://localhost:5000/api/health" -ForegroundColor Cyan

Write-Host "`n✨ PostgreSQL/PostGIS prêt pour ODG Platform!" -ForegroundColor Green
