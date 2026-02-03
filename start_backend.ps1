# Script PowerShell pour demarrer le backend ODG
$BackendDir = "C:\Users\LENOVO\Downloads\odg-preview-main\odg-preview-main\backend"
Set-Location $BackendDir

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "DEMARRAGE BACKEND FLASK ODG" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Repertoire: $BackendDir" -ForegroundColor Yellow
Write-Host ""

# Lancer le serveur
python run_server.py
