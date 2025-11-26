# Script de réinitialisation de la connexion PostgreSQL pour ODG
# Ce script ne nécessite pas d'arrêter le service PostgreSQL

# Variables
$DB_NAME = "odg_database"
$DB_USER = "odg_user"
$DB_PASSWORD = "root"
$POSTGRES_USER = "postgres"
$POSTGRES_PASSWORD = "root"

Write-Host "Configuration de la connexion PostgreSQL pour ODG Platform" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan

# 1. Vérifier la présence de psql
Write-Host "`n[1] Vérification de psql..." -ForegroundColor Yellow
$psqlPath = $null
$possiblePaths = @(
    "C:\Program Files\PostgreSQL\17\bin\psql.exe",
    "C:\Program Files\PostgreSQL\16\bin\psql.exe",
    "C:\Program Files\PostgreSQL\15\bin\psql.exe",
    "C:\Program Files\PostgreSQL\14\bin\psql.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $psqlPath = $path
        break
    }
}

if ($psqlPath) {
    Write-Host "[OK] psql trouvé à: $psqlPath" -ForegroundColor Green
    # Définir un alias pour faciliter l'utilisation
    Set-Alias -Name psql -Value $psqlPath -Scope Script
} else {
    Write-Host "[ATTENTION] psql non trouvé dans les chemins standards." -ForegroundColor Yellow
    Write-Host "Tentative d'utilisation de psql depuis le PATH..." -ForegroundColor Cyan
    
    try {
        $psqlVersion = psql --version
        Write-Host "[OK] psql trouvé dans le PATH: $psqlVersion" -ForegroundColor Green
    } catch {
        Write-Host "[ERREUR] psql non trouvé. Vérifiez l'installation PostgreSQL." -ForegroundColor Red
        exit 1
    }
}

# 2. Tester la connexion actuelle
Write-Host "`n[2] Test de la connexion actuelle..." -ForegroundColor Yellow
$env:PGPASSWORD = $POSTGRES_PASSWORD
try {
    & psql -U $POSTGRES_USER -h localhost -p 5432 -c "SELECT version();" -w 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Connexion PostgreSQL réussie avec le mot de passe actuel" -ForegroundColor Green
    } else {
        Write-Host "[ATTENTION] Échec de connexion avec le mot de passe actuel" -ForegroundColor Yellow
        Write-Host "Nous allons essayer la connexion via PgAdmin ou l'interface graphique" -ForegroundColor Cyan
    }
} catch {
    Write-Host "[ATTENTION] Problème de connexion à PostgreSQL" -ForegroundColor Yellow
}

# 3. Instructions pour la réinitialisation manuelle
Write-Host "`n[3] Instructions pour configurer la connexion..." -ForegroundColor Yellow
Write-Host @"
Pour configurer la connexion PostgreSQL:

1. Ouvrez pgAdmin 4 (installé avec PostgreSQL)
2. Cliquez-droit sur le serveur et sélectionnez "Propriétés"
3. Dans l'onglet "Connexion", vérifiez:
   - Hôte: localhost
   - Port: 5432
   - Base de données de maintenance: postgres
   - Nom d'utilisateur: postgres
   - Mot de passe: $POSTGRES_PASSWORD (ou définissez-le)

4. Pour réinitialiser manuellement le mot de passe (si nécessaire):
   a. Ouvrez l'invite de commande en tant qu'administrateur
   b. Arrêtez le service PostgreSQL:
      > net stop postgresql-x64-17
   c. Exécutez en tant qu'utilisateur postgres:
      > runas /user:postgres "cmd.exe"
   d. Puis exécutez:
      > psql -c "ALTER USER postgres WITH PASSWORD '$POSTGRES_PASSWORD';"
   e. Redémarrez le service:
      > net start postgresql-x64-17

5. Pour créer la base de données ODG:
   - Ouvrez pgAdmin
   - Cliquez-droit sur "Bases de données" et sélectionnez "Créer > Base de données"
   - Nom: $DB_NAME
   - Propriétaire: $POSTGRES_USER (créez cet utilisateur si nécessaire)
"@ -ForegroundColor Cyan

# 4. Mise à jour du fichier de configuration ODG
Write-Host "`n[4] Mise à jour du fichier de configuration..." -ForegroundColor Yellow
$configPath = "src\config.py"

if (Test-Path $configPath) {
    Write-Host "[INFO] Mise à jour du fichier $configPath avec les nouvelles informations de connexion" -ForegroundColor Cyan
    
    # Lire le contenu du fichier
    $configContent = Get-Content -Path $configPath -Raw
    
    # Remplacer la chaîne de connexion
    $oldConnectionString = "SQLALCHEMY_DATABASE_URI = os.environ.get\('DATABASE_URL'\) or \\'[^']*\\'"
    $newConnectionString = "SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \\
        'postgresql://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}'"
    
    $updatedConfig = $configContent -replace $oldConnectionString, $newConnectionString
    
    # Écrire le contenu mis à jour
    $updatedConfig | Set-Content -Path $configPath -Force
    
    Write-Host "[OK] Fichier de configuration mis à jour" -ForegroundColor Green
} else {
    Write-Host "[ATTENTION] Fichier de configuration non trouvé: $configPath" -ForegroundColor Yellow
}

# 5. Afficher les chaînes de connexion pour référence
Write-Host "`n[5] Informations de connexion pour ODG Platform:" -ForegroundColor Yellow
Write-Host @"
Base de données: $DB_NAME
Utilisateur: $DB_USER
Mot de passe: $DB_PASSWORD
Hôte: localhost:5432
URI de connexion: postgresql://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}

Pour tester manuellement la connexion:
> psql -U $DB_USER -h localhost -p 5432 -d $DB_NAME -W
"@ -ForegroundColor White

Write-Host "`n[ÉTAPES SUIVANTES]:" -ForegroundColor Yellow
Write-Host "1. Vérifiez/créez l'utilisateur et la base de données via pgAdmin" -ForegroundColor Cyan
Write-Host "2. Exécutez la migration: python src/migrate_to_postgis.py" -ForegroundColor Cyan
Write-Host "3. Démarrez l'API: python src/main_postgis.py" -ForegroundColor Cyan

Write-Host "`n[INFO] Ce guide vous aide à configurer PostgreSQL pour ODG Platform" -ForegroundColor Green
