#!/bin/bash
# ============================================
# File Permissions & ACLs
# ============================================

echo "=== Setting up file permissions and ACLs ==="

# Create application directory structure
mkdir -p /opt/ecommerce/{app,static,logs,backups}
mkdir -p /var/log/ecommerce

# Set ownership
chown -R devadmin:appadmin /opt/ecommerce
chown -R apprunner:appuser /var/log/ecommerce

# Base permissions
chmod 750 /opt/ecommerce/app
chmod 755 /opt/ecommerce/static
chmod 750 /opt/ecommerce/logs
chmod 750 /opt/ecommerce/backups
chmod 755 /var/log/ecommerce

# ACLs — grant developer group read access to app dir
setfacl -m g:developer:rx /opt/ecommerce/app
setfacl -m g:developer:rx /opt/ecommerce/static

echo "Permissions configured:"
ls -la /opt/ecommerce/
getfacl /opt/ecommerce/app
