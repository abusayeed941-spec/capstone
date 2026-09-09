#!/bin/bash
# ============================================
# Linux Administration — User & Group Setup
# Run as root on RHEL/Rocky 9
# ============================================

echo "=== User & Group Management ==="

# Create groups
groupadd -f appadmin
groupadd -f developer
groupadd -f appuser

# Create users
useradd -m -s /bin/bash -G appadmin devadmin 2>/dev/null || echo "devadmin exists"
useradd -m -s /bin/bash -G developer dev1 2>/dev/null || echo "dev1 exists"
useradd -m -s /bin/bash -G appuser apprunner 2>/dev/null || echo "apprunner exists"

# Set passwords (in production, use a secure method)
echo "devadmin:DevAdmin123!" | chpasswd
echo "dev1:Dev1Pass123!" | chpasswd
echo "apprunner:AppRun123!" | chpasswd

echo "Users created: devadmin, dev1, apprunner"
echo "Groups: appadmin, developer, appuser"
