# Script de réinitialisation du mot de passe PostgreSQL
# Ce script permet de réinitialiser le mot de passe de l'utilisateur postgres
# et de configurer l'authentification pour l'application ODG

# Variables
$PG_VERSION = "17"  # Version de PostgreSQL installée
$PG_DATA_DIR = "C:\Program Files\PostgreSQL\$PG_VERSION\data"  # Répertoire des données
$PG_BIN_DIR = "C:\Program Files\PostgreSQL\$PG_VERSION\bin"  # Répertoire des binaires
$PG_SERVICE_NAME = "postgresql-x64-$PG_VERSION"
$POSTGRES_PASSWORD = "root"  # Nouveau mot de passe pour postgres
$DB_USER = "odg_user"
$DB_PASSWORD = "root"
$DB_NAME = "odg_database"

# Fonction pour vérifier si un service est en cours d'exécution
function Is-ServiceRunning {
    param ($serviceName)
    $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    return ($service -and $service.Status -eq 'Running')
}

# 1. Vérifier le service PostgreSQL
Write-Host "`n[1] Vérification du service PostgreSQL..." -ForegroundColor Yellow
if (Is-ServiceRunning $PG_SERVICE_NAME) {
    Write-Host "[OK] Le service PostgreSQL est en cours d'exécution" -ForegroundColor Green
}
else {
    Write-Host "[ATTENTION] Le service PostgreSQL n'est pas en cours d'exécution." -ForegroundColor Yellow
    Write-Host "Tentative de démarrage du service..." -ForegroundColor Cyan
    Start-Service -Name $PG_SERVICE_NAME -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
    
    if (Is-ServiceRunning $PG_SERVICE_NAME) {
        Write-Host "[OK] Service PostgreSQL démarré avec succès" -ForegroundColor Green
    }
    else {
        Write-Host "[ERREUR] Impossible de démarrer le service PostgreSQL" -ForegroundColor Red
        Write-Host "Vérifiez l'installation PostgreSQL ou exécutez: Start-Service $PG_SERVICE_NAME" -ForegroundColor Cyan
        exit 1
    }
}

# 2. Arrêter le service pour modifier les paramètres d'authentification
Write-Host "`n[2] Arrêt temporaire du service PostgreSQL..." -ForegroundColor Yellow
Stop-Service -Name $PG_SERVICE_NAME
Start-Sleep -Seconds 2

if (Is-ServiceRunning $PG_SERVICE_NAME) {
    Write-Host "[ATTENTION] Impossible d'arrêter le service PostgreSQL. Arrêtez-le manuellement." -ForegroundColor Red
    exit 1
}
else {
    Write-Host "[OK] Service PostgreSQL arrêté temporairement" -ForegroundColor Green
}

# 3. Modifier le fichier pg_hba.conf pour permettre l'authentification par mot de passe
Write-Host "`n[3] Configuration de l'authentification (pg_hba.conf)..." -ForegroundColor Yellow
$pgHbaPath = Join-Path -Path $PG_DATA_DIR -ChildPath "pg_hba.conf"

if (Test-Path $pgHbaPath) {
    # Sauvegarder le fichier original
    Copy-Item -Path $pgHbaPath -Destination "$pgHbaPath.bak" -Force
    Write-Host "[INFO] Fichier pg_hba.conf sauvegardé: $pgHbaPath.bak" -ForegroundColor Cyan
    
    # Remplacer les méthodes d'authentification par "md5" (mot de passe)
    $content = Get-Content -Path $pgHbaPath
    $newContent = $content -replace "scram-sha-256", "md5" -replace "peer", "md5" -replace "ident", "md5"
    
    # Ajouter des entrées spécifiques pour notre application
    $newContent += @"

# Configuration spécifique pour l'application ODG
host    $DB_NAME    $DB_USER    127.0.0.1/32    md5
host    $DB_NAME    $DB_USER    ::1/128         md5
host    all         postgres    127.0.0.1/32    md5
host    all         postgres    ::1/128         md5
"@
    
    # Écrire le nouveau contenu
    $newContent | Set-Content -Path $pgHbaPath -Force
    Write-Host "[OK] Fichier pg_hba.conf modifié pour l'authentification par mot de passe" -ForegroundColor Green
}
else {
    Write-Host "[ERREUR] Fichier pg_hba.conf introuvable: $pgHbaPath" -ForegroundColor Red
    Write-Host "Vérifiez le chemin d'installation de PostgreSQL" -ForegroundColor Cyan
    exit 1
}

# 4. Redémarrer PostgreSQL en mode auth 'trust' temporairement
Write-Host "`n[4] Redémarrage temporaire de PostgreSQL en mode 'trust'..." -ForegroundColor Yellow
$pgHbaTrustPath = Join-Path -Path $PG_DATA_DIR -ChildPath "pg_hba.conf.trust"

# Créer un fichier pg_hba.conf temporaire avec auth 'trust'
@"
# Configuration temporaire (trust)
local   all             postgres                                trust
host    all             postgres         127.0.0.1/32           trust
host    all             postgres         ::1/128                trust
local   all             all                                     trust
host    all             all              127.0.0.1/32           trust
host    all             all              ::1/128                trust
"@ | Set-Content -Path $pgHbaTrustPath -Force

# Renommer temporairement pour utiliser le fichier trust
Rename-Item -Path $pgHbaPath -NewName "pg_hba.conf.original" -Force
Rename-Item -Path $pgHbaTrustPath -NewName "pg_hba.conf" -Force

# Démarrer PostgreSQL avec auth 'trust'
Start-Service -Name $PG_SERVICE_NAME
Start-Sleep -Seconds 3

if (Is-ServiceRunning $PG_SERVICE_NAME) {
    Write-Host "[OK] PostgreSQL démarré temporairement en mode 'trust'" -ForegroundColor Green
}
else {
    Write-Host "[ERREUR] Impossible de démarrer PostgreSQL en mode 'trust'" -ForegroundColor Red
    exit 1
}

# 5. Réinitialiser le mot de passe de l'utilisateur postgres
Write-Host "`n[5] Réinitialisation du mot de passe postgres..." -ForegroundColor Yellow
$resetCommand = @"
ALTER USER postgres WITH PASSWORD '$POSTGRES_PASSWORD';
"@

$resetCommand | & "$PG_BIN_DIR\psql" -U postgres -h localhost -p 5432 -d postgres -c "ALTER USER postgres WITH PASSWORD '$POSTGRES_PASSWORD';"

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Mot de passe de l'utilisateur 'postgres' réinitialisé" -ForegroundColor Green
}
else {
    Write-Host "[ERREUR] Échec de la réinitialisation du mot de passe" -ForegroundColor Red
}

# 6. Reconfigurer la base de données pour l'application
Write-Host "`n[6] Configuration de la base de données ODG..." -ForegroundColor Yellow

# Créer la base de données si elle n'existe pas
$createDBCommand = @"
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME
    WITH ENCODING 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252'
    TEMPLATE template0;
"@

$createDBCommand | & "$PG_BIN_DIR\psql" -U postgres -h localhost -p 5432 -d postgres
Write-Host "[OK] Base de données '$DB_NAME' créée ou reconfigurée" -ForegroundColor Green

# Créer l'utilisateur de l'application
$createUserCommand = @"
DROP USER IF EXISTS $DB_USER;
CREATE USER $DB_USER WITH
    PASSWORD '$DB_PASSWORD'
    CREATEDB
    NOSUPERUSER
    NOCREATEROLE;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
"@

$createUserCommand | & "$PG_BIN_DIR\psql" -U postgres -h localhost -p 5432 -d postgres
Write-Host "[OK] Utilisateur '$DB_USER' créé avec le mot de passe spécifié" -ForegroundColor Green

# 7. Rétablir le fichier pg_hba.conf d'origine
Write-Host "`n[7] Rétablissement du fichier pg_hba.conf..." -ForegroundColor Yellow
Stop-Service -Name $PG_SERVICE_NAME
Start-Sleep -Seconds 2

# Supprimer le fichier pg_hba.conf temporaire et restaurer l'original
Remove-Item -Path "$PG_DATA_DIR\pg_hba.conf" -Force
Rename-Item -Path "$PG_DATA_DIR\pg_hba.conf.original" -NewName "pg_hba.conf" -Force

# 8. Redémarrer PostgreSQL avec la configuration mise à jour
Write-Host "`n[8] Redémarrage final de PostgreSQL..." -ForegroundColor Yellow
Start-Service -Name $PG_SERVICE_NAME
Start-Sleep -Seconds 3

if (Is-ServiceRunning $PG_SERVICE_NAME) {
    Write-Host "[OK] Service PostgreSQL démarré avec succès" -ForegroundColor Green
}
else {
    Write-Host "[ERREUR] Impossible de démarrer le service PostgreSQL" -ForegroundColor Red
    exit 1
}

# 9. Tester la connexion avec les nouveaux paramètres
Write-Host "`n[9] Test de connexion..." -ForegroundColor Yellow

# Test de connexion avec l'utilisateur postgres
$env:PGPASSWORD = $POSTGRES_PASSWORD
$testPostgres = & "$PG_BIN_DIR\psql" -U postgres -h localhost -p 5432 -c "SELECT current_user, current_database();" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Connexion réussie avec l'utilisateur 'postgres'" -ForegroundColor Green
}
else {
    Write-Host "[ERREUR] Échec de connexion avec l'utilisateur 'postgres'" -ForegroundColor Red
}

# Test de connexion avec l'utilisateur de l'application
$env:PGPASSWORD = $DB_PASSWORD
$testApp = & "$PG_BIN_DIR\psql" -U $DB_USER -h localhost -p 5432 -d $DB_NAME -c "SELECT current_user, current_database();" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Connexion réussie avec l'utilisateur '$DB_USER'" -ForegroundColor Green
}
else {
    Write-Host "[ERREUR] Échec de connexion avec l'utilisateur '$DB_USER'" -ForegroundColor Red
}

# 10. Résumé final
Write-Host "`n[TERMINÉ] CONFIGURATION TERMINÉE" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "Base de données: $DB_NAME" -ForegroundColor White
Write-Host "Utilisateur application: $DB_USER / Mot de passe: $DB_PASSWORD" -ForegroundColor White
Write-Host "Utilisateur admin: postgres / Mot de passe: $POSTGRES_PASSWORD" -ForegroundColor White
Write-Host "Host: localhost:5432" -ForegroundColor White
Write-Host "URI de connexion: postgresql://$DB_USER`:$DB_PASSWORD@localhost`:5432/$DB_NAME" -ForegroundColor White

Write-Host "`n[ÉTAPES SUIVANTES]:" -ForegroundColor Yellow
Write-Host "1. Exécuter la migration: python src/migrate_to_postgis.py" -ForegroundColor Cyan
Write-Host "2. Démarrer l'API: python src/main_postgis.py" -ForegroundColor Cyan
Write-Host "3. Tester l'API: http://localhost:5000/api/health" -ForegroundColor Cyan

Write-Host "`n[OK] PostgreSQL/PostGIS prêt pour ODG Platform!" -ForegroundColor Green
