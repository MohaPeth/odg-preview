@echo off
REM Script de démarrage pour ODG WebGIS Frontend

cd /d %~dp0frontend
echo ==========================================================
echo 🚀 DEMARRAGE FRONTEND VITE
echo ==========================================================
npm run dev
pause
