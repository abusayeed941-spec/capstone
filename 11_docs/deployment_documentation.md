# Deployment Documentation — E-Commerce Capstone Project

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| AWS CLI | >= 2.x | `aws configure` |
| Terraform | >= 1.5 | `terraform init` |
| Ansible | >= 2.14 | `pip install ansible` |
| Docker | >= 24 | `yum install docker` / `apt install docker.io` |
| kubectl | >= 1.28 | Download from kubernetes.io |
| Python | >= 3.9 | Required for app + Ansible |
| Git | >= 2.40 | `yum install git` |
| tesseract | 5.x | For PDF extraction (capstone context only) |

---

## Phase 0: Initial Setup (Day 0)

### 0.1 Create AWS Account & Configure
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure
aws configure
# Access Key ID: <your-access-key>
# Secret Access Key: <your-secret-key>
# Default region: us-east-1
# Default output: json
```

### 0.2 Generate SSH Key Pair
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/ecommerce-key -C "ecommerce-capstone"
# Upload to AWS EC2 → Key Pairs, or via CLI:
aws ec2 import-key-pair --key-name ecommerce-key \
  --public-key-material file://~/.ssh/ecommerce-key.pub
```

### 0.3 Set Your IP in Terraform
```bash
# Find your public IP
curl -s ifconfig.me

# Update terraform.tfvars with your IP CIDR
# your_ip_cidr = "YOUR_IP/32"  (e.g., 203.0.113.5/32)
```

### 0.4 Initialize Git Repository
```bash
cd ~/CloudDevOpsCapstone
git init
git add -A
git commit -m "Initial commit: E-Commerce Capstone Project"

# Create repo on GitHub/GitLab and push
git remote add origin git@github.com:YOUR_USERNAME/ecommerce-capstone.git
git push -u origin main
```

---

## Phase 1: Linux Administration (Days 1-2)

### 1.1 Launch a RHEL/Rocky 9 VM

**Option A: On AWS EC2 (recommended for cloud exposure)**
```bash
aws ec2 run-instances \
  --image-id ami-053b53722f74e7eee \
  --instance-type t2.micro \
  --key-name ecommerce-key \
  --security-group-ids sg-xxxxxxxxx \
  --subnet-id subnet-xxxxxxxxx \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ecommerce-linux-vm}]' \
  --count 1
```

**Option B: Local VM (VirtualBox/VMware)**
- Download RHEL 9 / Rocky 9 ISO
- Install with minimal packages
- Configure static IP, enable SSH

### 1.2 Run Linux Setup Scripts
```bash
# Copy scripts to the VM
scp -i ~/.ssh/ecommerce-key -r 02_linux/setup_scripts/ ec2-user@<vm-ip>:/tmp/setup/

# SSH into VM
ssh -i ~/.ssh/ecommerce-key ec2-user@<vm-ip>

# Run scripts (as root via sudo)
sudo bash /tmp/setup/setup_user_accounts.sh
sudo bash /tmp/setup/setup_permissions.sh
sudo bash /tmp/setup/setup_storage_lvm.sh
sudo bash /tmp/setup/setup_ssh.sh
sudo bash /tmp/setup/setup_firewall.sh

# Install scripts as systemd services
sudo cp /tmp/setup/ecommerce-healthcheck.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/ecommerce-healthcheck.sh
sudo cp /tmp/setup/systemd/ecommerce-healthcheck.service /etc/systemd/system/
sudo cp /tmp/setup/systemd/ecommerce-healthcheck.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ecommerce-healthcheck.timer
```

### 1.3 Verify Linux Setup
```bash
# Check users
id devadmin
id dev1
id apprunner

# Check groups
getent group appadmin developer appuser

# Check file permissions
ls -la /opt/ecommerce/
getfacl /opt/ecommerce/app

# Check LVM
lvdisplay
vgdisplay
pvdisplay

# Check SSH
ss -tlnp | grep 2222
cat /etc/ssh/sshd_config | grep -E "Port|PermitRootLogin|PasswordAuthentication"

# Check firewall
firewall-cmd --list-all

# Check systemd timer
systemctl list-timers | grep ecommerce
```

### 1.4 Shell Script Validation
```bash
bash -n /tmp/setup/backup_script.sh && echo "backup_script.sh: syntax OK"
bash -n /tmp/setup/log_rotation.sh && echo "log_rotation.sh: syntax OK"
bash -n /usr/local/bin/ecommerce-healthcheck.sh && echo "healthcheck: syntax OK"
```

---

## Phase 2: Ansible Automation (Day 3)

### 2.1 Install Ansible
```bash
# On control node (your machine or bastion)
pip install ansible

# Or on RHEL/Rocky
sudo dnf install -y ansible
```

### 2.2 Configure Ansible
```bash
# Create ansible.cfg
cat > ansible.cfg << 'EOF'
[defaults]
inventory = ./03_ansible/inventory/hosts.ini
remote_user = devadmin
private_key_file = ~/.ssh/ecommerce-key
host_key_checking = False
retry_files_enabled = False
vault_password_file = ~/.ansible_vault_pass
EOF

# Create vault password file
echo "your-vault-password" > ~/.ansible_vault_pass
chmod 600 ~/.ansible_vault_pass
```

### 2.3 Test Connectivity
```bash
ansible all -i 03_ansible/inventory/hosts.ini -m ping
```

### 2.4 Run Playbooks
```bash
# Bootstrap all servers
ansible-playbook -i 03_ansible/inventory/hosts.ini 03_ansible/playbooks/site.yml --tags bootstrap

# Configure web servers
ansible-playbook -i 03_ansible/inventory/hosts.ini 03_ansible/playbooks/site.yml --tags webserver

# Configure database
ansible-playbook -i 03_ansible/inventory/hosts.ini 03_ansible/playbooks/site.yml --tags database

# Deploy application
ansible-playbook -i 03_ansible/inventory/hosts.ini 03_ansible/playbooks/site.yml --tags app_deployment

# Setup monitoring
ansible-playbook -i 03_ansible/inventory/hosts.ini 03_ansible/playbooks/site.yml --tags monitoring
```

### 2.5 Verify Ansible
```bash
# Check nginx is running
ansible webservers -a "systemctl is-active nginx"

# Check mysql is running
ansible dbservers -a "systemctl is-active mysqld"

# Check app is listening
ansible k8s_master -a "curl -s http://localhost:5000/api/health"
```

---

## Phase 3: Terraform — AWS Infrastructure (Day 4)

### 3.1 Initialize and Plan
```bash
cd 04_terraform

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan infrastructure
terraform plan -out=tfplan -var-file=terraform.tfvars
```

### 3.2 Apply Infrastructure
```bash
terraform apply tfplan
```

### 3.3 Verify AWS Resources
```bash
# Check VPC
aws ec2 describe-vpcs --filters "Name=tag:Project,Values=E-Commerce Capstone"

# Check EC2 instances
aws ec2 describe-instances --filters "Name=tag:Project,Values=E-Commerce Capstone" \
  --query "Reservations[*].Instances[*].[InstanceId,State.Name,Tags[?Key=='Name'].Value]" \
  --output table

# Check S3
aws s3 ls | grep ecommerce

# Check IAM
aws iam list-users --query "Users[?contains(UserName, 'ecommerce')]"
```

### 3.4 Get Connection Info
```bash
# Output bastion IP
BASTION_IP=$(terraform output -raw bastion_public_ip)
ssh -i ~/.ssh/ecommerce-key ec2-user@$BASTION_IP

# From bastion, access K8s master via private IP
MASTER_IP=$(terraform output -raw k8s_master_private_ip)
ssh -i ~/.ssh/ecommerce-key ec2-user@$MASTER_IP
```

---

## Phase 4: Docker & Containers (Day 5)

### 4.1 Build and Test Locally (on your dev machine)
```bash
cd eCommerceApp

# Build backend
docker build -t ecommerce-backend:latest ./backend

# Build frontend
docker build -t ecommerce-frontend:latest ./frontend

# Run with docker-compose
docker-compose up -d

# Test
curl http://localhost:5000/api/health
curl http://localhost/api/products
```

### 4.2 Push to Registry
```bash
# Login
docker login

# Tag and push
docker tag ecommerce-backend:latest docker.io/YOUR_USERNAME/ecommerce-backend:latest
docker tag ecommerce-frontend:latest docker.io/YOUR_USERNAME/ecommerce-frontend:latest

docker push docker.io/YOUR_USERNAME/ecommerce-backend:latest
docker push docker.io/YOUR_USERNAME/ecommerce-frontend:latest
```

### 4.3 Local Test with Docker Compose + Prometheus
```bash
# Start the full stack
docker-compose up -d

# Access:
# Frontend: http://localhost
# Backend API: http://localhost:5000/api/products
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin123)

# Stop
docker-compose down
```

---

## Phase 5: Kubernetes Cluster (Days 6-7)

### 5.1 Bootstrap K8s on EC2 Instances

**On K8s Master:**
```bash
# Install container runtime
sudo yum install -y docker
sudo systemctl enable --now docker

# Install kubeadm, kubelet, kubectl
cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v1.28/rpm/
enabled=1
gpgcheck=1
gpgkey=https://pkgs.k8s.io/core:/stable:/v1.28/rpm/repodata/repomd.xml.key
exclude=kubelet kubeadm kubectl cri-tools kubernetes-cni
EOF

sudo yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes
sudo systemctl enable --now kubelet

# Disable swap
sudo swapoff -a
sudo sed -i '/swap/d' /etc/fstab

# Initialize cluster
sudo kubeadm init --pod-network-cidr=10.244.0.0/16

# Configure kubectl
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Install CNI (Flannel)
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml

# Install metrics-server (required for HPA)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Install Ingress Controller (Nginx)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/aws/deploy.yaml

# Get join command
kubeadm token create --print-join-command
```

**On K8s Workers:**
```bash
# Run the join command from master (paste the output above)
sudo kubeadm join ... --token ... --discovery-token-ca-cert-hash ...
```

### 5.2 Deploy Application to K8s

```bash
# From master or any node with kubeconfig

# Create namespace
kubectl create namespace ecommerce

# Apply all manifests
kubectl apply -f 08_kubernetes/namespace.yml
kubectl apply -f 08_kubernetes/configmaps/app-config.yml
kubectl apply -f 08_kubernetes/secrets/db-credentials.yml
kubectl apply -f 08_kubernetes/pv/mysql-pvc.yml
kubectl apply -f 08_kubernetes/deployments/mysql-statefulset.yml
kubectl apply -f 08_kubernetes/services/mysql-service.yml
kubectl apply -f 08_kubernetes/services/backend-service.yml
kubectl apply -f 08_kubernetes/services/frontend-service.yml
kubectl apply -f 08_kubernetes/deployments/backend-deployment.yml
kubectl apply -f 08_kubernetes/deployments/frontend-deployment.yml
kubectl apply -f 08_kubernetes/deployments/backend-hpa.yml
kubectl apply -f 08_kubernetes/ingress/ecommerce-ingress.yml
```

### 5.3 Verify K8s Deployment
```bash
# Check all pods
kubectl get pods -n ecommerce -w

# Check services
kubectl get svc -n ecommerce

# Check ingress
kubectl get ingress -n ecommerce

# Check HPA
kubectl get hpa -n ecommerce

# Test from within cluster
kubectl run test --rm -it --image=curlimages/curl --restart=Never -- \
  curl http://backend-service.ecommerce.svc.cluster.local:5000/api/health

# Port-forward for local testing
kubectl port-forward svc/frontend-service 8080:80 -n ecommerce
# Then open http://localhost:8080
```

---

## Phase 6: CI/CD — Jenkins (Day 7)

### 6.1 Install Jenkins
```bash
# On bastion or dedicated EC2
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.key
sudo yum install -y jenkins java-17-amazon-corretto-headless
sudo systemctl enable --now jenkins

# Get initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

### 6.2 Configure Jenkins
1. Access `http://<jenkins-ip>:8080`
2. Enter initial admin password
3. Install suggested plugins
4. Create admin user
5. Configure credentials:
   - **Docker Registry:** `docker-registry-creds` (username/password)
   - **AWS Credentials:** `aws-creds` (access key + secret key)

### 6.3 Create Pipeline
1. New Item → Pipeline
2. Pipeline script from SCM → Git
3. Repository URL: your GitHub repo
4. Branch: `*/main`
5. Script Path: `06_cicd/Jenkinsfile`
6. Save and run

### 6.4 Connect GitHub Webhook
```
Payload URL: http://<jenkins-ip>:8080/github-webhook/
Content type: application/json
Events: Push
```

---

## Phase 7: Monitoring (Day 8)

### 7.1 Deploy Grafana Dashboards
```bash
# Import dashboards via Grafana UI or kubectl
kubectl create configmap grafana-dashboards \
  --from-file=09_monitoring/grafana/dashboards/ \
  -n ecommerce
```

### 7.2 Create Grafana Data Sources
- **Prometheus:** `http://prometheus:9090` (if in same cluster)
- **CloudWatch:** AWS credentials for EC2 metrics

### 7.3 Alerting
```bash
# Configure AlertManager with Slack/Email/PagerDuty
# Edit 09_monitoring/alerting/alertmanager.yml
```

### 7.4 Dashboard URLs
| Dashboard | URL |
|-----------|-----|
| Cluster Health | Grafana → Import → cluster-health.json |
| App Performance | Grafana → Import → app-performance.json |
| Business Metrics | Grafana → Import → ecommerce-business.json |

---

## Phase 8: Security Hardening (Day 9)

### 8.1 IAM Review
- Ensure admin user has MFA
- Delete any unused IAM users/keys
- Verify EC2 instance profile is attached

### 8.2 SSL/TLS
- Request ACM certificate for your domain
- Attach to ALB
- Update Ingress to use TLS

### 8.3 Secrets
- Replace dummy secrets with real values
- Use Ansible Vault for sensitive variables
- Rotate DB passwords periodically

### 8.4 Network Policies
- Apply network policies to restrict pod-to-pod traffic
- Restrict database access to backend pods only

---

## Phase 9: Documentation & Submission (Day 10)

### 9.1 Final Verification Checklist
```bash
# All phases verified?
echo "=== Phase 1: Linux ==="
systemctl is-active sshd
systemctl is-active firewalld
id devadmin && id dev1 && id apprunner
ls /opt/ecommerce/

echo "=== Phase 2: Ansible ==="
ansible all -i 03_ansible/inventory/hosts.ini -m ping

echo "=== Phase 3: AWS ==="
aws ec2 describe-instances --filters "Name=tag:Project,Values=E-Commerce Capstone" | jq '.Reservations[].Instances[].State.Name'

echo "=== Phase 4: Docker ==="
docker images | grep ecommerce

echo "=== Phase 5: K8s ==="
kubectl get pods -n ecommerce
kubectl get svc -n ecommerce
kubectl get ingress -n ecommerce

echo "=== Phase 6: CI/CD ==="
curl -s http://<jenkins-ip>:8080/api/json | jq '.jobs[].name'

echo "=== Phase 7: Monitoring ==="
curl -s http://<grafana-ip>:3000/api/health

echo "=== Phase 8: Security ==="
aws sts get-caller-identity
```

### 9.2 Prepare Submission Package
```bash
# Create submission archive
cd ~/CloudDevOpsCapstone

zip -r ecommerce-capstone-submission.zip \
  01_proposal/project_proposal.md \
  11_docs/architecture_diagram.txt \
  02_linux/ \
  03_ansible/ \
  04_terraform/ \
  05_git/ \
  06_cicd/Jenkinsfile \
  06_cicd/README.md \
  07_docker/ \
  08_kubernetes/ \
  09_monitoring/ \
  10_security/ \
  eCommerceApp/ \
  11_docs/deployment_documentation.md

# Or tar.gz
tar -czvf ecommerce-capstone-submission.tar.gz \
  01_proposal/ 11_docs/ 02_linux/ 03_ansible/ \
  04_terraform/ 05_git/ 06_cicd/ 07_docker/ \
  08_kubernetes/ 09_monitoring/ 10_security/ \
  eCommerceApp/
```

### 9.3 Submit
```bash
# Email to hackerdeen222@gmail.com
# Subject: Cloud & DevOps Capstone Project — [Your Name]
#
# Attach: ecommerce-capstone-submission.zip
# Plus: demo video, presentation slides
```

---

## Quick Reference Commands

```bash
# Terraform
cd 04_terraform && terraform init && terraform plan -var-file=terraform.tfvars && terraform apply

# Ansible
ansible-playbook -i 03_ansible/inventory/hosts.ini 03_ansible/playbooks/site.yml

# Kubernetes
kubectl get pods -n ecommerce -o wide
kubectl logs -f deployment/ecommerce-backend -n ecommerce
kubectl describe ingress ecommerce-ingress -n ecommerce
kubectl top pods -n ecommerce

# Docker
docker-compose -f eCommerceApp/docker-compose.yml up -d
docker-compose -f eCommerceApp/docker-compose.yml logs -f

# AWS
aws ec2 describe-instances --filters "Name=tag:Project,Values=E-Commerce Capstone"
aws s3 ls | grep ecommerce
aws iam list-users

# Jenkins
# http://<jenkins>:8080
```

---

*End of Deployment Documentation*
