# Configuration PostgreSQL avec pgAdmin4
# Ce script guide l'utilisateur pour configurer PostgreSQL via l'interface graphique

# Couleurs pour meilleure lisibilité
$Green = [ConsoleColor]::Green
$Yellow = [ConsoleColor]::Yellow
$Cyan = [ConsoleColor]::Cyan
$Red = [ConsoleColor]::Red
$White = [ConsoleColor]::White

# Informations de configuration
$DB_NAME = "odg_database"
$DB_USER = "odg_user"
$DB_PASSWORD = "root"
$POSTGRES_USER = "postgres"
$POSTGRES_PASSWORD = "root"

# Titre du script
Write-Host "Guide de configuration PostgreSQL pour ODG Platform" -ForegroundColor $Green
Write-Host "==============================================" -ForegroundColor $Cyan
Write-Host

# 1. Vérifier si pgAdmin est installé
Write-Host "[1] Vérification de pgAdmin..." -ForegroundColor $Yellow
$pgAdminPath = "C:\Program Files\PostgreSQL\*\pgAdmin*\bin\pgAdmin*.exe"
$pgAdminExecutable = Get-ChildItem -Path $pgAdminPath -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1

if ($pgAdminExecutable) {
    Write-Host "[OK] pgAdmin trouvé: $($pgAdminExecutable.FullName)" -ForegroundColor $Green
} else {
    Write-Host "[INFO] pgAdmin non trouvé dans le chemin standard." -ForegroundColor $Cyan
    Write-Host "       Recherchez pgAdmin dans votre menu démarrer ou dans C:\Program Files\PostgreSQL\" -ForegroundColor $White
}

# 2. Vérifier si le service PostgreSQL est en cours d'exécution
Write-Host "`n[2] Vérification du service PostgreSQL..." -ForegroundColor $Yellow
$pgService = Get-Service -Name "*postgresql*" -ErrorAction SilentlyContinue

if ($pgService -and $pgService.Status -eq 'Running') {
    Write-Host "[OK] Le service PostgreSQL est en cours d'exécution: $($pgService.DisplayName)" -ForegroundColor $Green
} else {
    Write-Host "[ATTENTION] Le service PostgreSQL n'est pas en cours d'exécution." -ForegroundColor $Yellow
    
    $startService = Read-Host "Voulez-vous démarrer le service PostgreSQL? (O/N)"
    if ($startService -eq "O" -or $startService -eq "o") {
        try {
            Start-Service -Name $pgService.Name
            Write-Host "[OK] Service PostgreSQL démarré" -ForegroundColor $Green
        } catch {
            Write-Host "[ERREUR] Impossible de démarrer le service. Veuillez le démarrer manuellement:" -ForegroundColor $Red
            Write-Host "         net start $($pgService.Name)" -ForegroundColor $Cyan
        }
    } else {
        Write-Host "[INFO] Veuillez démarrer le service manuellement avant de continuer" -ForegroundColor $Cyan
    }
}

# 3. Instructions pgAdmin
Write-Host "`n[3] Configuration via pgAdmin - Instructions:" -ForegroundColor $Yellow
Write-Host @"
ÉTAPE 1: Démarrer pgAdmin 4
---------------------------------------
1. Lancez pgAdmin 4 depuis votre menu démarrer
2. Connectez-vous avec votre mot de passe pgAdmin (si demandé)

ÉTAPE 2: Configurer le serveur
---------------------------------------
1. Dans le panneau de gauche, faites un clic droit sur 'Servers'
2. Sélectionnez 'Register > Server'
3. Dans l'onglet 'General':
   - Name: PostgreSQL ODG

4. Dans l'onglet 'Connection':
   - Host: localhost
   - Port: 5432
   - Maintenance database: postgres
   - Username: $POSTGRES_USER
   - Password: $POSTGRES_PASSWORD
   - Cochez 'Save password'
5. Cliquez sur 'Save'

ÉTAPE 3: Créer la base de données
---------------------------------------
1. Connectez-vous au serveur PostgreSQL
2. Faites un clic droit sur 'Databases'
3. Sélectionnez 'Create > Database'
4. Dans l'onglet 'General':
   - Database: $DB_NAME
   - Owner: $POSTGRES_USER
5. Cliquez sur 'Save'

ÉTAPE 4: Créer l'utilisateur ODG
---------------------------------------
1. Faites un clic droit sur 'Login/Group Roles'
2. Sélectionnez 'Create > Login/Group Role'
3. Dans l'onglet 'General':
   - Name: $DB_USER
4. Dans l'onglet 'Definition':
   - Password: $DB_PASSWORD
5. Dans l'onglet 'Privileges':
   - Cochez 'Can login'
   - Cochez 'Create databases'
6. Cliquez sur 'Save'

ÉTAPE 5: Installer l'extension PostGIS
---------------------------------------
1. Connectez-vous à la base de données '$DB_NAME'
2. Faites un clic droit sur 'Extensions'
3. Sélectionnez 'Create > Extension'
4. Dans la liste déroulante, sélectionnez 'postgis'
5. Cliquez sur 'Save'
6. Répétez pour les extensions:
   - postgis_topology
   - fuzzystrmatch
   - postgis_tiger_geocoder

ÉTAPE 6: Configurer les permissions
---------------------------------------
1. Faites un clic droit sur la base de données '$DB_NAME'
2. Sélectionnez 'Properties'
3. Allez dans l'onglet 'Security'
4. Dans la section 'Privileges', ajoutez:
   - Role: $DB_USER
   - Privileges: ALL
5. Cliquez sur 'Save'
"@ -ForegroundColor $White

# 4. Lancer pgAdmin si trouvé
if ($pgAdminExecutable) {
    $launchPgAdmin = Read-Host "`nVoulez-vous lancer pgAdmin maintenant? (O/N)"
    if ($launchPgAdmin -eq "O" -or $launchPgAdmin -eq "o") {
        Write-Host "[INFO] Lancement de pgAdmin..." -ForegroundColor $Cyan
        Start-Process -FilePath $pgAdminExecutable.FullName
    }
}

# 5. Informations finales
Write-Host "`n[INFO] Informations de connexion pour référence:" -ForegroundColor $Yellow
Write-Host @"
Base de données: $DB_NAME
Utilisateur: $DB_USER
Mot de passe: $DB_PASSWORD
Hôte: localhost:5432
URI de connexion: postgresql://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}
"@ -ForegroundColor $White

Write-Host "`n[ÉTAPES SUIVANTES]:" -ForegroundColor $Yellow
Write-Host "1. Après avoir configuré PostgreSQL via pgAdmin, revenez à ce terminal" -ForegroundColor $Cyan
Write-Host "2. Exécutez la migration: python src/migrate_to_postgis.py" -ForegroundColor $Cyan
Write-Host "3. Démarrez l'API: python src/main_postgis.py" -ForegroundColor $Cyan

Write-Host "`n[INFO] Suivez ce guide pour configurer PostgreSQL pour ODG Platform" -ForegroundColor $Green

# Attendre l'entrée de l'utilisateur avant de fermer
Write-Host "`nAppuyez sur une touche pour continuer..." -ForegroundColor $Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
