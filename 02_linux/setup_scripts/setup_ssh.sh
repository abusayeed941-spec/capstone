#!/bin/bash
# ============================================
# SSH Configuration — Hardening
# Run as root
# ============================================

echo "=== SSH Configuration ==="

# Generate host keys if missing
ssh-keygen -A 2>/dev/null

# Backup original config
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# Hardening settings
cat >> /etc/ssh/sshd_config << 'EOF'

# === Capstone Project SSH Hardening ===
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
Port 2222
AllowUsers devadmin dev1
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
Protocol 2
X11Forwarding no
EOF

# Restart SSH (on RHEL use sshd)
systemctl restart sshd 2>/dev/null || systemctl restart ssh 2>/dev/null

echo "SSH configured: Port 2222, key-only auth, root login disabled"
echo "Don't forget to add your public key to ~/.ssh/authorized_keys for allowed users!"
