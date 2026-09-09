#!/bin/bash
# ============================================
# Firewall Configuration (firewalld)
# Run as root
# ============================================

echo "=== Firewall Configuration ==="

# Ensure firewalld is running
systemctl enable firewalld
systemctl start firewalld

# Remove default ssh service (we use custom port 2222)
firewall-cmd --remove-service=ssh --permanent 2>/dev/null

# Add custom SSH port
firewall-cmd --add-port=2222/tcp --permanent

# Allow HTTP and HTTPS
firewall-cmd --add-service=http --permanent
firewall-cmd --add-service=https --permanent

# Allow app ports
firewall-cmd --add-port=5000/tcp --permanent   # Flask backend
firewall-cmd --add-port=3000/tcp --permanent   # Grafana
firewall-cmd --add-port=9090/tcp --permanent   # Prometheus
firewall-cmd --add-port=6443/tcp --permanent   # Kubernetes API
firewall-cmd --add-port=8080/tcp --permanent   # Ingress/NodePort

# Allow MySQL only from internal (optional — restrict to subnet)
firewall-cmd --add-port=3306/tcp --permanent

# Add source IP restriction for SSH (example: only from VPC/CIDR)
# firewall-cmd --add-rich-rule='rule family="ipv4" source address="10.0.0.0/16" port port="2222" protocol="tcp" accept' --permanent

# Reload
firewall-cmd --reload

echo "Firewall rules active:"
firewall-cmd --list-all
