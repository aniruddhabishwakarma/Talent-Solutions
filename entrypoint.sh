#!/bin/sh
set -e

DB_DIR="/app/db_data"
MEDIA_DIR="/app/media"

# ── Volume safety checks ──────────────────────────────────────────────────────
# If these dirs aren't writable, the volume isn't mounted correctly.
# Fail loud immediately rather than silently creating an in-container DB.

if [ ! -w "$DB_DIR" ]; then
    echo "FATAL: $DB_DIR is not writable — is the db_data volume mounted?"
    exit 1
fi

if [ ! -w "$MEDIA_DIR" ]; then
    echo "FATAL: $MEDIA_DIR is not writable — is the media volume mounted?"
    exit 1
fi

echo "Volume check passed."
echo "  DB   → $DB_DIR/db.sqlite3"
echo "  Media→ $MEDIA_DIR"

# ── Run migrations ────────────────────────────────────────────────────────────
python manage.py migrate --noinput

# ── Start Gunicorn ────────────────────────────────────────────────────────────
exec gunicorn --bind 0.0.0.0:8000 --workers 3 talent_solutions.wsgi:application
