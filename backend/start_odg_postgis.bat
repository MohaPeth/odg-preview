# Démarrer l'API ODG avec PostgreSQL

@echo off
echo ======================================================
echo    DÉMARRAGE DE L'API ODG AVEC POSTGIS
echo ======================================================
echo.

echo [1] Vérification de l'environnement Python...
if exist ..\.venv\Scripts\activate.bat (
    echo [OK] Environnement virtuel trouvé
    call ..\.venv\Scripts\activate.bat
) else (
    echo [ATTENTION] Environnement virtuel non trouvé
    echo Création d'un nouvel environnement virtuel...
    python -m venv ..\.venv
    call ..\.venv\Scripts\activate.bat
    echo [OK] Environnement virtuel créé et activé
)

echo.
echo [2] Installation des dépendances...
pip install -r requirements.txt
echo [OK] Dépendances installées

echo.
echo [3] Migration des données vers PostGIS...
python src/migrate_to_postgis.py
echo [OK] Migration terminée

echo.
echo [4] Démarrage de l'API ODG avec PostgreSQL...
echo.
echo L'API sera accessible à l'adresse: http://localhost:5000
echo.
echo Appuyez sur CTRL+C pour arrêter le serveur
echo.
python src/main_postgis.py

pause
