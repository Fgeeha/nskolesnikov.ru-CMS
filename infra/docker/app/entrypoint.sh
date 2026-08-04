#!/usr/bin/env sh
set -eu

# Wait for PostgreSQL, apply migrations, collect static, then hand over PID 1
# to the real process so SIGTERM reaches it directly.

: "${POSTGRES_HOST:?POSTGRES_HOST is required}"
: "${POSTGRES_PORT:=5432}"
: "${DJANGO_SETTINGS_MODULE:?DJANGO_SETTINGS_MODULE is required}"

MANAGE="/app/src/manage.py"
WAIT_TIMEOUT="${DB_WAIT_TIMEOUT:-60}"

echo "Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
elapsed=0
while ! python -c "
import socket, sys
try:
    with socket.create_connection(('${POSTGRES_HOST}', ${POSTGRES_PORT}), timeout=2):
        pass
except OSError:
    sys.exit(1)
" 2>/dev/null; do
    elapsed=$((elapsed + 2))
    if [ "${elapsed}" -ge "${WAIT_TIMEOUT}" ]; then
        echo "PostgreSQL is unreachable after ${WAIT_TIMEOUT}s" >&2
        exit 1
    fi
    sleep 2
done
echo "PostgreSQL is available."

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
    echo "Applying migrations..."
    python "${MANAGE}" migrate --no-input
fi

if [ "${RUN_COLLECTSTATIC:-1}" = "1" ]; then
    echo "Collecting static files..."
    python "${MANAGE}" collectstatic --no-input --clear
fi

exec "$@"
