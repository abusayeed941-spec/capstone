#!/bin/bash
# Health check script for the e-commerce app
# Called by systemd timer or cron every minute

APP_URL="${APP_URL:-http://localhost:5000/api/health}"
LOG_FILE="/var/log/ecommerce/healthcheck.log"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL" 2>/dev/null || echo "000")

echo "$(date '+%Y-%m-%d %H:%M:%S') - Health check: HTTP $STATUS" >> "$LOG_FILE"

if [ "$STATUS" = "200" ]; then
    echo "OK" > /var/run/ecommerce-healthy
    exit 0
else
    echo "FAIL" > /var/run/ecommerce-healthy
    # Alert via logger
    logger -t ecommerce-healthcheck "Application unhealthy! HTTP $STATUS"
    exit 1
fi
