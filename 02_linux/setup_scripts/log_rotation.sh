#!/bin/bash
# ============================================
# Log Rotation Script
# Alternatively, use logrotate config below
# ============================================

LOG_DIR="/var/log/ecommerce"
DATE=$(date +%Y%m%d)

mkdir -p "$LOG_DIR"

# Rotate logs
for logfile in "$LOG_DIR"/*.log; do
    if [ -f "$logfile" ] && [ -s "$logfile" ]; then
        mv "$logfile" "${logfile}.${DATE}"
        touch "$logfile"
        echo "Rotated: $(basename $logfile)"
    fi
done

# Compress old rotated logs
find "$LOG_DIR" -name "*.log.*" -mtime +1 -exec gzip {} \; 2>/dev/null || true

# Cleanup logs older than 30 days
find "$LOG_DIR" -name "*.log.*.gz" -mtime +30 -delete 2>/dev/null || true
echo "Log rotation complete."
