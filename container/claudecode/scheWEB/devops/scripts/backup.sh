#!/bin/bash
set -e

# SQLite Database Backup Script
# Performs online backup of SQLite database with optional S3 upload

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_PATH="${DATABASE_PATH:-/app/data/schedule.db}"
BACKUP_DIR="${BACKUP_DIR:-/app/backups}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
S3_BUCKET="${S3_BUCKET}"

BACKUP_FILE="${BACKUP_DIR}/schedule_${TIMESTAMP}.db"
BACKUP_SQL="${BACKUP_DIR}/schedule_${TIMESTAMP}.sql"
BACKUP_COMPRESSED="${BACKUP_DIR}/schedule_${TIMESTAMP}.db.gz"

echo "🔄 Starting backup at $(date)"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Check if database exists
if [ ! -f "${DB_PATH}" ]; then
    echo "❌ Error: Database not found at ${DB_PATH}"
    exit 1
fi

# Perform online backup using SQLite backup API
echo "📦 Creating database backup..."
sqlite3 "${DB_PATH}" ".backup '${BACKUP_FILE}'"

if [ $? -eq 0 ]; then
    echo "✅ Database backup created: ${BACKUP_FILE}"
else
    echo "❌ Error: Backup failed"
    exit 1
fi

# Export SQL dump for disaster recovery
echo "📝 Creating SQL dump..."
sqlite3 "${DB_PATH}" .dump > "${BACKUP_SQL}"

# Compress backups
echo "🗜️  Compressing backups..."
gzip -c "${BACKUP_FILE}" > "${BACKUP_COMPRESSED}"
gzip "${BACKUP_SQL}"

# Remove uncompressed database backup (keep SQL uncompressed for viewing)
rm "${BACKUP_FILE}"

# Calculate file sizes
BACKUP_SIZE=$(du -h "${BACKUP_COMPRESSED}" | cut -f1)
echo "📊 Backup size: ${BACKUP_SIZE}"

# Upload to S3 if configured
if [ -n "${S3_BUCKET}" ]; then
    echo "☁️  Uploading to S3..."
    aws s3 cp "${BACKUP_COMPRESSED}" "s3://${S3_BUCKET}/backups/schedule_${TIMESTAMP}.db.gz"
    aws s3 cp "${BACKUP_SQL}.gz" "s3://${S3_BUCKET}/backups/schedule_${TIMESTAMP}.sql.gz"

    if [ $? -eq 0 ]; then
        echo "✅ Uploaded to S3: s3://${S3_BUCKET}/backups/"
    else
        echo "⚠️  Warning: S3 upload failed, backup retained locally"
    fi
fi

# Clean up old backups (local)
echo "🧹 Cleaning up old backups (older than ${RETENTION_DAYS} days)..."
find "${BACKUP_DIR}" -name "schedule_*.db.gz" -mtime +${RETENTION_DAYS} -delete
find "${BACKUP_DIR}" -name "schedule_*.sql.gz" -mtime +${RETENTION_DAYS} -delete

# Clean up S3 backups if configured
if [ -n "${S3_BUCKET}" ]; then
    CUTOFF_DATE=$(date -d "${RETENTION_DAYS} days ago" +%Y%m%d)
    aws s3 ls "s3://${S3_BUCKET}/backups/" | while read -r line; do
        BACKUP_DATE=$(echo $line | awk '{print $4}' | grep -oP '\d{8}' | head -1)
        if [ -n "${BACKUP_DATE}" ] && [ "${BACKUP_DATE}" -lt "${CUTOFF_DATE}" ]; then
            FILE_NAME=$(echo $line | awk '{print $4}')
            aws s3 rm "s3://${S3_BUCKET}/backups/${FILE_NAME}"
            echo "🗑️  Deleted old S3 backup: ${FILE_NAME}"
        fi
    done
fi

# Verify backup integrity
echo "🔍 Verifying backup integrity..."
sqlite3 "${BACKUP_COMPRESSED%.*}" "PRAGMA integrity_check;" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Backup verification successful"
else
    echo "⚠️  Warning: Backup verification failed"
fi

echo "✅ Backup completed successfully at $(date)"
echo "📍 Backup location: ${BACKUP_COMPRESSED}"

# Log backup event
echo "[$(date)] Backup completed: ${BACKUP_COMPRESSED} (${BACKUP_SIZE})" >> "${BACKUP_DIR}/backup.log"
