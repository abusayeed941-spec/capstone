#!/bin/bash
# PHASE 1 (RHCSA): Linux Administration
# Run: sudo bash /home/ec2-user/phase1_build.sh

set -e

echo "============================================"
echo " PHASE 1 (RHCSA): Building from scratch"
echo " Host: $(hostname)"
echo "============================================"

# ── 1. USERS & GROUPS ──
echo ""
echo "[1/7] Users and Groups"
groupadd -f appadmin 2>/dev/null || echo "appadmin exists"
groupadd -f developer 2>/dev/null || echo "developer exists"
groupadd -f appuser 2>/dev/null || echo "appuser exists"

useradd -m -s /bin/bash -G appadmin devadmin 2>/dev/null || echo "devadmin exists"
useradd -m -s /bin/bash -G developer dev1 2>/dev/null || echo "dev1 exists"
useradd -m -s /bin/bash -G appuser apprunner 2>/dev/null || echo "apprunner exists"

echo "devadmin:DevAdmin123!" | chpasswd
echo "dev1:Dev1Pass123!" | chpasswd
echo "apprunner:AppRun123!" | chpasswd

echo "Users created:"
id devadmin | cut -d, -f1
id dev1 | cut -d, -f1
id apprunner | cut -d, -f1
echo ""
echo "Groups:"
getent group appadmin developer appuser

# ── 2. FILE PERMISSIONS & ACLs ──
echo ""
echo "[2/7] File Permissions and ACLs"
mkdir -p /opt/ecommerce/{app,static,logs,backups}
mkdir -p /var/log/ecommerce

chown -R devadmin:appadmin /opt/ecommerce
chown -R apprunner:appuser /var/log/ecommerce

chmod 750 /opt/ecommerce/app
chmod 755 /opt/ecommerce/static
chmod 750 /opt/ecommerce/logs
chmod 750 /opt/ecommerce/backups
chmod 755 /var/log/ecommerce

dnf install -y acl 2>&1 | tail -2
setfacl -m g:developer:rx /opt/ecommerce/app
setfacl -m g:developer:rx /opt/ecommerce/static

echo "Directory listing:"
ls -la /opt/ecommerce/
echo ""
echo "ACL on app dir:"
getfacl /opt/ecommerce/app 2>/dev/null | grep -E "^user:|^group:|^mask:|^other:" || true

# ── 3. SSH HARDENING ──
echo ""
echo "[3/7] SSH Configuration"
echo "Regenerating host keys..."
ssh-keygen -A 2>&1 | tail -2

# Idempotent SSH hardening
if ! grep -q "Capstone SSH Hardening" /etc/ssh/sshd_config; then
    cat >> /etc/ssh/sshd_config << 'SSHEOF'

# === Capstone SSH Hardening ===
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
X11Forwarding no
AllowUsers ec2-user devadmin dev1 apprunner
SSHEOF
    echo "SSH hardening appended"
fi

/usr/sbin/sshd -t 2>&1 && echo "SSH config: VALID" || echo "SSH config: INVALID"
systemctl restart sshd 2>&1 && echo "SSH restarted OK" || echo "SSH restart FAILED"
echo "SSH listening:"
ss -tlnp 2>/dev/null | grep sshd || netstat -tlnp 2>/dev/null | grep sshd || echo "ss/netstat unavailable"

# ── 4. FIREWALLD ──
echo ""
echo "[4/7] Firewall Configuration"
dnf install -y firewalld 2>&1 | tail -2
systemctl enable firewalld 2>&1 | tail -1
systemctl start firewalld 2>&1 | tail -1
sleep 2

firewall-cmd --permanent --remove-service=ssh 2>/dev/null || true
firewall-cmd --permanent --add-service=http 2>/dev/null || true
firewall-cmd --permanent --add-service=https 2>/dev/null || true
firewall-cmd --permanent --add-port=5000/tcp 2>/dev/null || true
firewall-cmd --permanent --add-port=3000/tcp 2>/dev/null || true
firewall-cmd --permanent --add-port=9090/tcp 2>/dev/null || true
firewall-cmd --permanent --add-port=8080/tcp 2>/dev/null || true
firewall-cmd --permanent --add-port=6443/tcp 2>/dev/null || true
firewall-cmd --permanent --add-port=10250/tcp 2>/dev/null || true
firewall-cmd --reload 2>&1 | tail -1

echo "Firewall status:"
systemctl is-active firewalld 2>/dev/null || echo "firewalld not active"
firewall-cmd --list-all 2>&1 | head -12

# ── 5. LOG MANAGEMENT & SHELL SCRIPTS ──
echo ""
echo "[5/7] Log Management and Shell Scripting"

# Healthcheck script
cat > /usr/local/bin/ecommerce-healthcheck.sh << 'HEOF'
#!/bin/bash
APP_URL="${APP_URL:-http://localhost:5000/api/health}"
LOG_DIR="/var/log/ecommerce"
LOG_FILE="$LOG_DIR/healthcheck.log"
mkdir -p "$LOG_DIR"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL" 2>/dev/null || echo "000")
echo "$(date '+%Y-%m-%d %H:%M:%S') - Health: HTTP $STATUS" >> "$LOG_FILE"

if [ "$STATUS" = "200" ]; then
    echo "OK" > /var/run/ecommerce-healthy
    exit 0
else
    echo "FAIL" > /var/run/ecommerce-healthy
    logger -t ecommerce-hc "Unhealthy! HTTP $STATUS"
    exit 1
fi
HEOF
chmod +x /usr/local/bin/ecommerce-healthcheck.sh

# Backup script
cat > /opt/ecommerce/backup_script.sh << 'BEOF'
#!/bin/bash
set -e
BACKUP_DIR="/opt/ecommerce/backups"
LOG_DIR="/var/log/ecommerce"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION=7
mkdir -p "$BACKUP_DIR"
echo "[$(date)] Backup start" >> "$LOG_DIR/backup.log"
if [ -d /data ]; then
    tar -czf "$BACKUP_DIR/data_$DATE.tar.gz" -C / data 2>/dev/null || true
    echo "Data: data_$DATE.tar.gz" >> "$LOG_DIR/backup.log"
fi
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" -C / var/log/ecommerce 2>/dev/null || true
echo "Logs: logs_$DATE.tar.gz" >> "$LOG_DIR/backup.log"
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION -delete 2>/dev/null || true
echo "[$(date)] Backup done" >> "$LOG_DIR/backup.log"
BEOF
chmod +x /opt/ecommerce/backup_script.sh

# Log rotation script
cat > /opt/ecommerce/log_rotation.sh << 'LEOF'
#!/bin/bash
LOG_DIR="/var/log/ecommerce"
DATE=$(date +%Y%m%d)
mkdir -p "$LOG_DIR"
for f in "$LOG_DIR"/*.log; do
    [ -f "$f" ] && [ -s "$f" ] && mv "$f" "${f}.${DATE}" && touch "$f"
done
find "$LOG_DIR" -name "*.log.*" -mtime +1 -exec gzip {} \; 2>/dev/null || true
find "$LOG_DIR" -name "*.log.*.gz" -mtime +30 -delete 2>/dev/null || true
echo "Log rotation done: $(date)"
LEOF
chmod +x /opt/ecommerce/log_rotation.sh

echo "Script syntax:"
bash -n /usr/local/bin/ecommerce-healthcheck.sh && echo "  healthcheck.sh: OK" || echo "  healthcheck.sh: FAIL"
bash -n /opt/ecommerce/backup_script.sh && echo "  backup_script.sh: OK" || echo "  backup_script.sh: FAIL"
bash -n /opt/ecommerce/log_rotation.sh && echo "  log_rotation.sh: OK" || echo "  log_rotation.sh: FAIL"

# ── 6. SYSTEMD SERVICE ──
echo ""
echo "[6/7] Systemd Healthcheck Service"
cat > /etc/systemd/system/ecommerce-healthcheck.service << 'SEOF'
[Unit]
Description=E-Commerce App Health Check
After=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/ecommerce-healthcheck.sh
User=apprunner
Group=appuser
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SEOF

cat > /etc/systemd/system/ecommerce-healthcheck.timer << 'TEOF'
[Unit]
Description=Run health check every minute

[Timer]
OnBootSec=1min
OnUnitActiveSec=1min
Unit=ecommerce-healthcheck.service

[Install]
WantedBy=timers.target
TEOF

systemctl daemon-reload
systemctl enable ecommerce-healthcheck.timer 2>&1 | tail -1
systemctl start ecommerce-healthcheck.timer 2>&1 | tail -1
echo "Timer status:"
systemctl list-timers --all 2>&1 | grep ecommerce || echo "Timer not active"

# ── 7. LVM ──
echo ""
echo "[7/7] LVM Storage"
if vgs --noheadings -o vg_name 2>/dev/null | grep -q ecommerce_vg; then
    echo "LVM already configured, skipping."
    vgs --noheadings -o vg_name,lv_count 2>&1 | tr -d " "
    lvs --noheadings -o lv_name,lv_size 2>&1 | tr -d " "
    df -h /data 2>/dev/null | tail -1 || echo "/data not mounted"
else
    echo "Creating LVM on loop device..."
    dd if=/dev/zero of=/root/lvm_disk.img bs=1M count=512 oflag=direct 2>&1 | tail -1
    /sbin/losetup /dev/loop0 /root/lvm_disk.img 2>&1
    pvcreate /dev/loop0 2>&1 | tail -1
    vgcreate ecommerce_vg /dev/loop0 2>&1 | tail -1
    lvcreate -L 200M -n data_lv ecommerce_vg 2>&1 | tail -1
    echo ""
    echo "LVM structure (PV/VG/LV) created."
    echo "Run manually: mkfs.ext4 /dev/ecommerce_vg/data_lv && mount /dev/ecommerce_vg/data_lv /data"
    echo ""
    vgs --noheadings -o vg_name 2>&1 | tr -d " "
    lvs --noheadings -o lv_name,lv_size 2>&1 | tr -d " "
fi

echo ""
echo "============================================"
echo " PHASE 1 COMPLETE"
echo "============================================"
