#!/bin/bash
# ===== VM SETUP SCRIPT - Debian 13 =====
set -e
LOGFILE="/var/log/vm_setup.log"
exec > >(tee -a "$LOGFILE") 2>&1

echo "=== $(date) - Starting VM setup ==="

# 1. Fix sources.list
cat > /etc/apt/sources.list << 'EOF'
deb http://deb.debian.org/debian trixie main contrib non-free non-free-firmware
deb http://deb.debian.org/debian trixie-updates main contrib non-free non-free-firmware
deb http://deb.debian.org/debian trixie-security main contrib non-free non-free-firmware
EOF
rm -f /etc/apt/sources.list.d/docker.list 2>/dev/null || true
echo "[1/8] Fixed apt sources"

# 2. Fix clock
date -s "2026-07-26 12:00:00" 2>/dev/null || true
echo "[2/8] Clock set to $(date)"

# 3. apt update (allow failure - clock may be slightly off)
apt-get update -qq 2>&1 | tail -1 || true
echo "[3/8] apt update done"

# 4. Install packages
apt-get install -y git acl lvm2 python3-pip python3-venv curl wget 2>&1 | tail -3
echo "[4/8] Packages installed"

# 5. Set up Flask venv
python3 -m venv /opt/ecommerce/venv 2>/dev/null || true
/opt/ecommerce/venv/bin/pip install --upgrade pip > /dev/null 2>&1
/opt/ecommerce/venv/bin/pip install flask flask-cors pymysql flask-sqlalchemy requests 2>&1 | tail -2
/opt/ecommerce/venv/bin/python3 -c "import flask; print('Flask version:', flask.__version__)" 2>&1
echo "[5/8] Flask venv ready"

# 6. Verify tools
echo "--- Tools check ---"
echo "git: $(which git 2>/dev/null || echo MISSING)"
echo "python3: $(which python3 2>/dev/null || echo MISSING)"
echo "venv python: $(ls /opt/ecommerce/venv/bin/python 2>/dev/null || echo MISSING)"
echo "acl: $(which setfacl 2>/dev/null || echo MISSING)"
echo "lvm2: $(which pvcreate 2>/dev/null || echo MISSING)"
echo "[6/8] Tools verified"

# 7. LVM check
echo "--- LVM status ---"
vgs --noheadings -o vg_name 2>/dev/null || echo "No VGs"
lvs --noheadings -o lv_name,lv_size 2>/dev/null || echo "No LVs"
df -h /data 2>/dev/null | tail -1 || echo "/data not mounted"
echo "[7/8] LVM checked"

# 8. Users check
echo "--- Users ---"
id devadmin | cut -d, -f1
id dev1 | cut -d, -f1
id apprunner | cut -d, -f1
echo "[8/8] Users verified"

echo "=== SETUP COMPLETE ==="
