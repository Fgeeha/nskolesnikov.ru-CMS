#!/usr/bin/env sh
set -eu

# Dump the production database and archive the media volume.
# Usage: infra/scripts/backup.sh [destination-directory]
#
# Reads POSTGRES_DB / POSTGRES_USER from the environment or from .env in the
# repository root. Existing backups are never removed by this script.

REPO_ROOT="$(CDPATH='' cd -- "$(dirname -- "$0")/../.." && pwd)"
DEST="${1:-${REPO_ROOT}/backups}"
COMPOSE_FILE="${REPO_ROOT}/infra/compose/compose.prod.yml"
PROJECT_NAME="nskolesnikov-prod"
STAMP="$(date +%F-%H%M)"

if [ -f "${REPO_ROOT}/.env" ]; then
    # shellcheck disable=SC1091  # path is resolved at runtime
    . "${REPO_ROOT}/.env"
fi

: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${POSTGRES_USER:?POSTGRES_USER is required}"

mkdir -p "${DEST}"

echo "Dumping database ${POSTGRES_DB}..."
docker compose -f "${COMPOSE_FILE}" exec -T db \
    pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" --clean --if-exists \
    | gzip > "${DEST}/db-${STAMP}.sql.gz"

echo "Archiving media volume..."
docker run --rm \
    -v "${PROJECT_NAME}_media_data:/data:ro" \
    -v "${DEST}:/backup" \
    alpine tar czf "/backup/media-${STAMP}.tar.gz" -C /data .

echo "Done:"
ls -lh "${DEST}/db-${STAMP}.sql.gz" "${DEST}/media-${STAMP}.tar.gz"
