@echo off
REM Script de démarrage pour ODG WebGIS

cd /d %~dp0backend
echo ==========================================================
echo 🚀 DEMARRAGE BACKEND FLASK avec PostgreSQL
echo ==========================================================
python run_server.py
pause
