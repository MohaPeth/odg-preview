@echo off
REM Script de lancement ODG Platform avec PostGIS

TITLE ODG Platform - PostGIS Edition

echo ===============================================
echo      ODG WebGIS Platform - PostGIS Edition
echo ===============================================
echo.

REM Vérifier que Python est disponible
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [31mX Python n'a pas été trouvé. Assurez-vous qu'il est installé et dans le PATH.[0m
    goto :end
)

echo [92m✓[0m Python trouvé

REM Options disponibles
echo.
echo [96m1[0m - Configurer PostgreSQL/PostGIS
echo [96m2[0m - Corriger les configurations
echo [96m3[0m - Migrer les données SQLite vers PostGIS
echo [96m4[0m - Démarrer le serveur API PostGIS
echo [96m5[0m - Quitter
echo.

:menu
set /p choix="Entrez votre choix (1-5): "

if "%choix%"=="1" (
    echo.
    echo [93mConfiguration de PostgreSQL/PostGIS...[0m
    powershell -ExecutionPolicy Bypass -File setup_postgresql.ps1
    echo.
    echo Appuyez sur une touche pour continuer...
    pause > nul
    cls
    goto :start
) else if "%choix%"=="2" (
    echo.
    echo [93mCorrection des configurations...[0m
    python fix_postgis.py
    echo.
    echo Appuyez sur une touche pour continuer...
    pause > nul
    cls
    goto :start
) else if "%choix%"=="3" (
    echo.
    echo [93mMigration des données SQLite vers PostGIS...[0m
    python src/migrate_to_postgis.py
    echo.
    echo Appuyez sur une touche pour continuer...
    pause > nul
    cls
    goto :start
) else if "%choix%"=="4" (
    echo.
    echo [93mDémarrage du serveur API PostGIS...[0m
    echo [92mServeur accessible sur http://localhost:5000[0m
    echo [33mUtilisez Ctrl+C pour arrêter le serveur[0m
    echo.
    python src/main_postgis.py
    echo.
    echo Appuyez sur une touche pour continuer...
    pause > nul
    cls
    goto :start
) else if "%choix%"=="5" (
    goto :end
) else (
    echo.
    echo [91mChoix invalide, veuillez réessayer.[0m
    echo.
    goto :menu
)

:start
echo ===============================================
echo      ODG WebGIS Platform - PostGIS Edition
echo ===============================================
echo.
echo [92m✓[0m Python trouvé
echo.
echo [96m1[0m - Configurer PostgreSQL/PostGIS
echo [96m2[0m - Corriger les configurations
echo [96m3[0m - Migrer les données SQLite vers PostGIS
echo [96m4[0m - Démarrer le serveur API PostGIS
echo [96m5[0m - Quitter
echo.
goto :menu

:end
echo.
echo [92mMerci d'avoir utilisé ODG Platform![0m
echo.
