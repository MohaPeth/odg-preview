@echo off
title ODG WebGIS API avec PostGIS
echo.
echo ==========================================
echo    ODG WebGIS API - PostGIS Version
echo ==========================================
echo.

cd /d "%~dp0"

echo 🔄 Vérification de l'environnement Python...

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo 📥 Installez Python depuis https://python.org
    pause
    exit /b 1
)

echo ✅ Python détecté

REM Vérifier si l'environnement virtuel existe
if not exist "venv\" (
    echo 🔄 Création de l'environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Erreur lors de la création de l'environnement virtuel
        pause
        exit /b 1
    )
)

echo 🔄 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo 🔄 Installation/mise à jour des dépendances...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Erreur lors de l'installation des dépendances
    pause
    exit /b 1
)

echo.
echo 🚀 Démarrage du serveur ODG WebGIS API...
echo    Choisissez votre méthode de démarrage :
echo.
echo    [1] Méthode simple (sans auto-reload)
echo    [2] Méthode avancée (avec auto-reload)
echo    [3] Démarrage direct depuis src/
echo.

set /p choice="Votre choix (1-3) : "

if "%choice%"=="1" (
    echo 🔄 Démarrage simple...
    python start_odg_api.py
) else if "%choice%"=="2" (
    echo 🔄 Démarrage avec auto-reload...
    python run_postgis.py
) else if "%choice%"=="3" (
    echo 🔄 Démarrage direct...
    python launch_api.py
) else (
    echo ⚠️ Choix invalide, utilisation de la méthode par défaut...
    python start_odg_api.py
)

echo.
echo 🛑 Serveur arrêté
pause
