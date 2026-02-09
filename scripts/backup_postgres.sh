#!/bin/bash
# Sauvegarde PostgreSQL ODG (pg_dump)
# Usage : ./backup_postgres.sh [répertoire_de_sortie]
# Définir DATABASE_URL dans l'environnement ou dans .env (source depuis backend)

set -e

BACKUP_DIR="${1:-./backups}"
mkdir -p "$BACKUP_DIR"

# Charger .env du backend si présent
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
if [ -f "$PROJECT_ROOT/backend/.env" ]; then
  set -a
  source "$PROJECT_ROOT/backend/.env"
  set +a
fi

if [ -z "$DATABASE_URL" ]; then
  echo "Erreur : DATABASE_URL non définie. Exportez-la ou configurez backend/.env"
  exit 1
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="$BACKUP_DIR/odg_backup_${TIMESTAMP}.sql"

echo "Sauvegarde vers $OUTPUT_FILE ..."
pg_dump -d "$DATABASE_URL" -F p -f "$OUTPUT_FILE"

echo "Sauvegarde terminée : $OUTPUT_FILE"
echo "Taille : $(du -h "$OUTPUT_FILE" | cut -f1)"
