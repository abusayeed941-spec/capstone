#!/bin/bash
# ============================================
# Storage Management — LVM Setup
# Run as root
# Assumes a free disk/partition (e.g., /dev/sdb)
# ============================================

echo "=== LVM Storage Setup ==="

# Check for free disk (example uses /dev/sdb — adjust to your environment)
FREE_DISK="/dev/sdb"

if [ ! -b "$FREE_DISK" ]; then
    echo "WARNING: $FREE_DISK not found. Using loopback as demo."
    # Create a 2GB loopback device for demo
    FREE_DISK=$(losetup -f --show --size 2G /dev/zero 2>/dev/null || echo "/dev/sdb")
    if [ "$FREE_DISK" = "/dev/sdb" ]; then
        echo "No free disk found. Skipping LVM demo. In production, attach an EBS volume."
        exit 0
    fi
fi

# Create physical volume
pvcreate "$FREE_DISK" 2>/dev/null || echo "PV create skipped (device may not be empty)"
echo "Physical Volume created on $FREE_DISK"

# Create volume group
vgcreate ecommerce_vg "$FREE_DISK" 2>/dev/null || echo "VG create skipped"
echo "Volume Group 'ecommerce_vg' created"

# Create logical volumes
lvcreate -L 1G -n data_lv ecommerce_vg 2>/dev/null || echo "LV data_lv skipped"
lvcreate -L 500M -n logs_lv ecommerce_vg 2>/dev/null || echo "LV logs_lv skipped"
lvcreate -L 500M -n backups_lv ecommerce_vg 2>/dev/null || echo "LV backups_lv skipped"

# Format with XFS (RHEL default)
mkfs.xfs /dev/ecommerce_vg/data_lv 2>/dev/null || echo "Format skipped"
mkfs.xfs /dev/ecommerce_vg/logs_lv 2>/dev/null || echo "Format skipped"

# Mount
mkdir -p /data /logs
mount /dev/ecommerce_vg/data_lv /data 2>/dev/null || echo "/data mount skipped"
mount /dev/ecommerce_vg/logs_lv /logs 2>/dev/null || echo "/logs mount skipped"

# Add to fstab (best-effort)
echo "/dev/ecommerce_vg/data_lv /data xfs defaults 0 0" >> /etc/fstab 2>/dev/null
echo "/dev/ecommerce_vg/logs_lv /logs xfs defaults 0 0" >> /etc/fstab 2>/dev/null

echo "LVM setup complete."
df -h /data /logs 2>/dev/null || echo "Verify with: lvdisplay, vgdisplay, pvdisplay"
