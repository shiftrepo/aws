#!/bin/bash
set -e

# Database Migration Script
# Handles schema migrations and data transformations

MIGRATIONS_DIR="${MIGRATIONS_DIR:-./migrations}"
DB_PATH="${DATABASE_PATH:-./data/schedule.db}"

echo "🔄 Starting database migration at $(date)"

# Check if database exists
if [ ! -f "${DB_PATH}" ]; then
    echo "📦 Database not found, will be created during migration"
fi

# Create migrations table if not exists
sqlite3 "${DB_PATH}" <<EOF
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);
EOF

echo "✅ Migrations table ready"

# Get current schema version
CURRENT_VERSION=$(sqlite3 "${DB_PATH}" "SELECT MAX(version) FROM migrations;" 2>/dev/null || echo "0")
echo "📊 Current schema version: ${CURRENT_VERSION}"

# Find and apply pending migrations
PENDING_COUNT=0

for migration_file in $(ls "${MIGRATIONS_DIR}"/*.sql 2>/dev/null | sort); do
    MIGRATION_VERSION=$(basename "${migration_file}" .sql)

    # Check if migration already applied
    APPLIED=$(sqlite3 "${DB_PATH}" "SELECT COUNT(*) FROM migrations WHERE version='${MIGRATION_VERSION}';" 2>/dev/null || echo "0")

    if [ "${APPLIED}" -eq "0" ]; then
        echo "⬆️  Applying migration: ${MIGRATION_VERSION}"

        # Begin transaction
        {
            echo "BEGIN TRANSACTION;"
            cat "${migration_file}"
            echo "INSERT INTO migrations (version, description) VALUES ('${MIGRATION_VERSION}', 'Applied from ${migration_file}');"
            echo "COMMIT;"
        } | sqlite3 "${DB_PATH}"

        if [ $? -eq 0 ]; then
            echo "✅ Migration ${MIGRATION_VERSION} applied successfully"
            PENDING_COUNT=$((PENDING_COUNT + 1))
        else
            echo "❌ Error: Migration ${MIGRATION_VERSION} failed"
            exit 1
        fi
    fi
done

if [ ${PENDING_COUNT} -eq 0 ]; then
    echo "✅ Database is up to date (no pending migrations)"
else
    echo "✅ Applied ${PENDING_COUNT} migration(s)"
fi

# Verify database integrity
echo "🔍 Verifying database integrity..."
sqlite3 "${DB_PATH}" "PRAGMA integrity_check;"

# Display schema version
NEW_VERSION=$(sqlite3 "${DB_PATH}" "SELECT MAX(version) FROM migrations;")
echo "📊 New schema version: ${NEW_VERSION}"

echo "✅ Migration completed successfully at $(date)"
