#!/bin/bash
# Daily backup script for Talent Solutions
# Recommended: add to crontab → 0 2 * * * /root/talent_solutions/Talent-Solutions/backup.sh

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p "$BACKUP_DIR"

# ── Backup SQLite DB ──────────────────────────────────────────────────────────
DB_SRC="$PROJECT_DIR/data/db/db.sqlite3"

if [ -f "$DB_SRC" ]; then
    cp "$DB_SRC" "$BACKUP_DIR/db_$TIMESTAMP.sqlite3"
    echo "DB backed up → backups/db_$TIMESTAMP.sqlite3"
else
    echo "WARNING: DB file not found at $DB_SRC"
fi

# ── Backup media files ────────────────────────────────────────────────────────
MEDIA_SRC="$PROJECT_DIR/data/media"

if [ -d "$MEDIA_SRC" ]; then
    tar -czf "$BACKUP_DIR/media_$TIMESTAMP.tar.gz" -C "$PROJECT_DIR/data" media
    echo "Media backed up → backups/media_$TIMESTAMP.tar.gz"
else
    echo "WARNING: Media directory not found at $MEDIA_SRC"
fi

# ── Prune backups older than 14 days ─────────────────────────────────────────
find "$BACKUP_DIR" -name "db_*.sqlite3" -mtime +14 -delete
find "$BACKUP_DIR" -name "media_*.tar.gz" -mtime +14 -delete
echo "Old backups pruned (kept last 14 days)."
