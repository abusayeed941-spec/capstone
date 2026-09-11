#!/bin/bash
# =============================================
# CLOUD & DEVOPS CAPSTONE - FULL BUILD SCRIPT
# Target: Debian 13 VM, root access
# =============================================
set -e

LOG="/tmp/capstone-build.log"
exec > >(tee -a "$LOG") 2>&1

echo "============================================"
echo " CLOUD & DEVOPS CAPSTONE BUILD"
echo " Host: $(hostname) | $(cat /etc/debian_version)"
echo " Started: $(date)"
echo "============================================"

# =============================================
# PHASE 0: INSTALL BASE TOOLS
# =============================================
echo ""
echo "[PHASE 0] Installing base tools..."

apt-get update -qq 2>&1 | tail -1

echo "Installing Python, pip, venv..."
apt-get install -y python3-pip python3-venv python3-dev git curl wget jq 2>&1 | tail -3

echo "Installing ACL, LVM tools, UFW..."
apt-get install -y acl lvm2 ufw iptables 2>&1 | tail -3

echo "Installing Docker..."
install -m 0755 -d /etc/apt/keyrings 2>/dev/null || true
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc 2>&1
chmod a+r /etc/apt/keyrings/docker.asc 2>&1
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null 2>&1
apt-get update -qq 2>&1 | tail -1
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin 2>&1 | tail -5
systemctl enable docker 2>&1 | tail -1
systemctl start docker 2>&1 | tail -1
echo "Docker: $(docker --version 2>&1 | head -1)"

echo "Installing kubectl..."
curl -sL https://dl.k8s.io/release/v1.28.4/bin/linux/amd64/kubectl -o /usr/local/bin/kubectl 2>&1
chmod +x /usr/local/bin/kubectl 2>&1
echo "kubectl: $(kubectl version --client 2>&1 | head -1)"

echo "Installing Ansible..."
apt-get install -y ansible 2>&1 | tail -3
echo "Ansible: $(ansible --version 2>&1 | head -1)"

echo "Installing Jenkins..."
apt-get install -y fontconfig 2>&1 | tail -1
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key -o /usr/share/keyrings/jenkins-keyring.asc 2>&1
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" > /etc/apt/sources.list.d/jenkins.list 2>&1
apt-get update -qq 2>&1 | tail -1
apt-get install -y jenkins 2>&1 | tail -5
systemctl enable jenkins 2>&1 | tail -1
systemctl start jenkins 2>&1 | tail -1
echo "Jenkins: $(systemctl is-active jenkins 2>&1)"

echo "Installing Prometheus..."
useradd -r -s /sbin/nologin prometheus 2>/dev/null || true
cd /tmp
curl -sL https://github.com/prometheus/prometheus/releases/download/v2.47.0/prometheus-2.47.0.linux-amd64.tar.gz -o /tmp/prometheus.tar.gz 2>&1
tar xzf /tmp/prometheus.tar.gz -C /opt 2>&1
mv /opt/prometheus-2.47.0.linux-amd64 /opt/prometheus 2>&1
ln -sf /opt/prometheus/prometheus /usr/local/bin/prometheus 2>&1
cd /home/ec2-user
mkdir -p /opt/prometheus/data
chown -R prometheus:prometheus /opt/prometheus 2>&1 || true

cat > /etc/systemd/system/prometheus.service << 'PEOF'
[Unit]
Description=Prometheus Monitoring
After=network.target
[Service]
Type=simple
User=prometheus
Group=prometheus
ExecStart=/opt/prometheus/prometheus \
    --config.file=/opt/prometheus/prometheus.yml \
    --storage.tsdb.path=/opt/prometheus/data \
    --web.listen-address=:9090
Restart=on-failure
[Install]
WantedBy=multi-user.target
PEOF

systemctl daemon-reload
systemctl enable prometheus 2>&1 | tail -1
systemctl start prometheus 2>&1 | tail -1
echo "Prometheus: $(systemctl is-active prometheus 2>&1)"

echo "Installing Grafana..."
apt-get install -y apt-transport-https software-properties-common 2>&1 | tail -2
mkdir -p /etc/apt/keyrings 2>/dev/null || true
curl -sL https://apt.grafana.com/gpg.key -o /etc/apt/keyrings/grafana.asc 2>&1
echo "deb [signed-by=/etc/apt/keyrings/grafana.asc] https://apt.grafana.com stable main" > /etc/apt/sources.list.d/grafana.list 2>&1
apt-get update -qq 2>&1 | tail -1
apt-get install -y grafana 2>&1 | tail -5
systemctl enable grafana-server 2>&1 | tail -1
systemctl start grafana-server 2>&1 | tail -1
echo "Grafana: $(systemctl is-active grafana-server 2>&1)"

# Install Terraform
echo "Installing Terraform..."
curl -sL https://releases.hashicorp.com/terraform/1.8.5/terraform_1.8.5_linux_amd64.zip -o /tmp/terraform.zip 2>&1
apt-get install -y unzip 2>&1 | tail -1
unzip -o /tmp/terraform.zip -d /usr/local/bin 2>&1
echo "Terraform: $(terraform version 2>&1 | head -1)"

# Install AWS CLI
echo "Installing AWS CLI..."
pip3 install awscli 2>&1 | tail -3

echo ""
echo "Phase 0 complete. Tools installed."
