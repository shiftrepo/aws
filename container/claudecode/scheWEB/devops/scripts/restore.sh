#!/bin/bash
set -e

# SQLite Database Restore Script
# Restores database from backup with verification

BACKUP_FILE="$1"
DB_PATH="${DATABASE_PATH:-/app/data/schedule.db}"
BACKUP_DIR="${BACKUP_DIR:-/app/backups}"

if [ -z "${BACKUP_FILE}" ]; then
    echo "Usage: $0 <backup_file>"
    echo ""
    echo "Available backups:"
    ls -lh "${BACKUP_DIR}"/schedule_*.db.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

echo "🔄 Starting restore at $(date)"

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    # Try with backup directory prefix
    BACKUP_FILE="${BACKUP_DIR}/${BACKUP_FILE}"
    if [ ! -f "${BACKUP_FILE}" ]; then
        echo "❌ Error: Backup file not found"
        exit 1
    fi
fi

# Create backup of current database
if [ -f "${DB_PATH}" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    CURRENT_BACKUP="${DB_PATH}.before_restore_${TIMESTAMP}"
    echo "💾 Backing up current database to: ${CURRENT_BACKUP}"
    cp "${DB_PATH}" "${CURRENT_BACKUP}"
fi

# Decompress if needed
TEMP_FILE="${BACKUP_FILE}"
if [[ "${BACKUP_FILE}" == *.gz ]]; then
    echo "🗜️  Decompressing backup..."
    TEMP_FILE="${BACKUP_DIR}/temp_restore.db"
    gunzip -c "${BACKUP_FILE}" > "${TEMP_FILE}"
fi

# Verify backup integrity
echo "🔍 Verifying backup integrity..."
sqlite3 "${TEMP_FILE}" "PRAGMA integrity_check;" > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "❌ Error: Backup file is corrupted"
    rm -f "${TEMP_FILE}"
    exit 1
fi

# Restore database
echo "📦 Restoring database..."
cp "${TEMP_FILE}" "${DB_PATH}"

# Clean up temp file
if [[ "${BACKUP_FILE}" == *.gz ]]; then
    rm "${TEMP_FILE}"
fi

# Verify restored database
echo "🔍 Verifying restored database..."
sqlite3 "${DB_PATH}" "PRAGMA integrity_check;" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Database restored successfully"
else
    echo "❌ Error: Restored database verification failed"
    if [ -f "${CURRENT_BACKUP}" ]; then
        echo "🔄 Rolling back to previous database..."
        cp "${CURRENT_BACKUP}" "${DB_PATH}"
    fi
    exit 1
fi

echo "✅ Restore completed successfully at $(date)"
echo "📍 Database location: ${DB_PATH}"

# Log restore event
echo "[$(date)] Database restored from: ${BACKUP_FILE}" >> "${BACKUP_DIR}/restore.log"
