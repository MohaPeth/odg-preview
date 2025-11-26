@echo off
echo Redemarrage du service PostgreSQL...
net stop postgresql-x64-17
net start postgresql-x64-17
echo Service PostgreSQL redemarre.
pause
