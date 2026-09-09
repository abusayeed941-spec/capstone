#!/bin/bash
# ============================================
# Backup Script — Daily Database + App Files
# Run as a cron job: 0 2 * * * /opt/ecommerce/backup_script.sh
# ============================================

set -e

BACKUP_DIR="/opt/ecommerce/backups"
DATA_DIR="/data"
LOG_DIR="/logs"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting backup..." >> "$LOG_DIR/backup.log"

# Backup app data
if [ -d "$DATA_DIR" ]; then
    tar -czf "$BACKUP_DIR/app_data_$DATE.tar.gz" -C / "$(dirname $DATA_DIR)" 2>/dev/null || true
    echo "App data backed up: app_data_$DATE.tar.gz" >> "$LOG_DIR/backup.log"
fi

# Backup logs
if [ -d "$LOG_DIR" ]; then
    tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" -C / "$(dirname $LOG_DIR)" 2>/dev/null || true
    echo "Logs backed up: logs_$DATE.tar.gz" >> "$LOG_DIR/backup.log"
fi

# MySQL dump (if mysql client is available)
if command -v mysqldump &> /dev/null; then
    mysqldump -u ecommerce -pecommerce123 ecommerce_db > "$BACKUP_DIR/ecommerce_db_$DATE.sql" 2>> "$LOG_DIR/backup.log" || echo "DB dump failed" >> "$LOG_DIR/backup.log"
fi

# Cleanup old backups
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "*.sql" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

echo "[$(date)] Backup complete." >> "$LOG_DIR/backup.log"
