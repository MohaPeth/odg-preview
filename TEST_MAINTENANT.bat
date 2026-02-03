@echo off
echo ================================================
echo    GUIDE DE TEST - VERIFICATION DES CORRECTIONS
echo ================================================
echo.
echo 1. Les serveurs sont ACTIFS :
echo    - Backend Flask : http://localhost:5000
echo    - Frontend Vite : http://localhost:5173
echo.
echo 2. Base de donnees corrigee :
echo    - 3 couches visibles (is_visible=True)
echo.
echo 3. OUVREZ votre navigateur sur :
echo    http://localhost:5173
echo.
echo 4. APPUYEZ sur Ctrl+Shift+R (rechargement force)
echo.
echo 5. OUVREZ la console (F12) et cherchez :
echo    [fetchLayers] Nombre de couches: 3
echo    [DEBUG] Couches geospatiales: Array(3)
echo.
echo 6. VERIFIEZ l'interface :
echo    - Stats affichent "3 couches totales"
echo    - Carte montre 3 marqueurs
echo    - Toggle oeil fonctionne correctement
echo.
echo ================================================
pause
