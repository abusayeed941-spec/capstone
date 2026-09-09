# Demo Video Script — E-Commerce Capstone Project

**Video length:** ~5-7 minutes  
**Format:** Screen recording with voiceover

---

## Segment 1: Introduction (0:00-0:30)

**Visual:** Title slide / terminal with project name  
**Voiceover:**
"Hi, I'm [Your Name]. This is my Cloud & DevOps Capstone Project — a production-ready e-commerce platform built end-to-end using Linux, Ansible, AWS, Terraform, Docker, Kubernetes, Jenkins CI/CD, Prometheus, and Grafana. Over the next few minutes, I'll walk you through the architecture, each implementation phase, and a live demo of the application."

---

## Segment 2: Architecture Overview (0:30-1:00)

**Visual:** Show architecture_diagram.txt or draw on whiteboard  
**Voiceover:**
"The platform runs on AWS. A public-facing ALB handles SSL termination and routes traffic to our Kubernetes cluster running in private subnets. The cluster has a master node and two worker nodes. We have frontend pods serving the web UI, backend pods running the Flask REST API, and a MySQL StatefulSet with EBS-backed persistent storage. A bastion host in the public subnet provides secure SSH access. S3 stores product images, and CloudWatch monitors everything."

**Visual:** Point to each component as you mention it.

---

## Segment 3: Linux Administration Demo (1:00-1:45)

**Visual:** SSH into bastion, then to a Linux VM  
**Commands to show:**
```bash
# Show users and groups
id devadmin
id dev1
id apprunner
getent group appadmin developer appuser

# Show LVM
sudo lvdisplay
sudo vgdisplay

# Show ACLs
getfacl /opt/ecommerce/app

# Show systemd service
systemctl status ecommerce-healthcheck.timer
systemctl status ecommerce-healthcheck.service

# Show firewall
sudo firewall-cmd --list-all

# Show SSH config
grep -E "Port|PermitRootLogin|PasswordAuthentication" /etc/ssh/sshd_config

# Show backup script
cat /opt/ecommerce/backup_script.sh
```

**Voiceover:**
"Phase 1 is Linux Administration. I created three users across three groups, configured LVM with logical volumes for data, logs, and backups, hardened SSH with key-only authentication on port 2222, set up firewalld rules, and created a systemd timer that runs a healthcheck every minute. I also wrote backup and log rotation scripts that run via cron."

---

## Segment 4: Ansible Automation Demo (1:45-2:15)

**Visual:** Run ansible-playbook, show output  
**Commands:**
```bash
# Show inventory
cat 03_ansible/inventory/hosts.ini

# Run a specific role
ansible-playbook -i 03_ansible/inventory/hosts.ini \
  03_ansible/playbooks/site.yml --tags webserver --diff

# Verify
ansible webservers -a "nginx -v"
ansible dbservers -a "mysql --version"
```

**Voiceover:**
"Phase 2 is Ansible automation. I built five roles: bootstrap for base setup, webserver for Nginx, database for MySQL, app_deployment for the Flask app, and monitoring for Prometheus. The main site.yml playbook orchestrates all of them. When I run it, Ansible installs packages, configures services, deploys configs — all idempotent and version-controlled."

---

## Segment 5: AWS Infrastructure Demo (2:15-3:00)

**Visual:** AWS Console screenshots or Terraform output  
**Show:**
- VPC with public and private subnets
- EC2 instances (bastion, K8s master, workers)
- S3 bucket with encryption and versioning
- IAM users and groups
- Security Groups rules

**Voiceover:**
"Phase 3 is AWS. I used Terraform to provision everything — a VPC with public and private subnets across two availability zones, an internet gateway, a NAT gateway for private subnet outbound traffic, security groups that follow least-privilege, EC2 instances for the bastion and K8s nodes, an S3 bucket for product images with versioning and encryption enabled, and IAM users and roles with appropriate permissions. The Terraform code is fully modular — VPC, security groups, EC2, and IAM are all separate reusable modules."

**Visual:** Show `terraform apply` output with all resources created.

---

## Segment 6: Docker & CI/CD Demo (3:00-4:00)

**Visual:** Docker Compose running locally, then Jenkins pipeline  
**Commands:**
```bash
# Local docker-compose
cd eCommerceApp
docker-compose up -d
curl http://localhost/api/products
curl http://localhost:5000/api/health
docker-compose down

# Show Docker images
docker images | grep ecommerce

# Show Jenkins pipeline running
# (Navigate to Jenkins in browser)
```

**Voiceover:**
"Phase 4 and 5 — Docker and CI/CD. I containerized both the frontend and backend with multi-stage Dockerfiles that produce small, secure images. For local development, docker-compose brings up the full stack — backend, database, frontend, plus Prometheus and Grafana. The Jenkins pipeline automates everything: on every git push, it lints the code, runs unit tests with pytest, builds Docker images tagged with the commit hash, pushes them to Docker Hub, deploys to Kubernetes, and runs smoke tests. If anything fails, Jenkins automatically rolls back the deployment."

**Visual:** Show Jenkins pipeline stages passing in green.

---

## Segment 7: Kubernetes Demo (4:00-5:00)

**Visual:** kubectl commands, Kubernetes Dashboard or terminal  
**Commands:**
```bash
# Show cluster
kubectl cluster-info
kubectl get nodes

# Show workloads
kubectl get pods -n ecommerce -o wide
kubectl get svc -n ecommerce
kubectl get ingress -n ecommerce
kubectl get hpa -n ecommerce

# Show app running
kubectl port-forward svc/frontend-service 8080:80 -n ecommerce &
sleep 2
curl http://localhost:8080/api/health
curl http://localhost:8080/api/products

# Show logs
kubectl logs -f deployment/ecommerce-backend -n ecommerce --tail=20

# Show scaling
kubectl scale deployment ecommerce-backend --replicas=4 -n ecommerce
kubectl get pods -n ecommerce -w
kubectl scale deployment ecommerce-backend --replicas=2 -n ecommerce
```

**Voiceover:**
"Phase 7 is Kubernetes. I bootstrapped a self-hosted cluster on EC2 using kubeadm — one master and two workers. I deployed the entire application: frontend and backend deployments with health probes, a MySQL StatefulSet with EBS persistent storage, ClusterIP services, an Nginx Ingress for routing, and a HorizontalPodAutoscaler that scales the backend based on CPU and memory usage. ConfigMaps and Secrets manage configuration and credentials."

**Visual:** Show pods scaling up and down in real-time.

---

## Segment 8: Monitoring Demo (5:00-5:45)

**Visual:** Grafana dashboards  
**Show:**
- Cluster Health dashboard (node status, CPU, memory, disk)
- App Performance dashboard (request rate, latency, error rate)
- Business Metrics dashboard (orders, revenue)

**Voiceover:**
"Phase 9 is monitoring. I set up Prometheus to scrape metrics from the cluster and application, and Grafana with three dashboards: cluster health showing node status and resource usage, application performance showing request rates and latency, and business metrics showing orders and revenue. I also configured AlertManager with rules for high CPU, low disk space, and pod failures."

---

## Segment 9: Security & Conclusion (5:45-6:30)

**Visual:** Security checklist, architecture recap  
**Voiceover:**
"Finally, security. I implemented least-privilege IAM, stored all secrets as Kubernetes Secrets and Ansible Vault, enabled SSL/TLS with cert-manager, hardened security groups to restrict all unnecessary traffic, used non-root Docker containers, and applied Kubernetes RBAC. All of this is documented in my security best practices guide."

**Visual:** Summary slide with all phases checked off.

**Voiceover:**
"This project demonstrates proficiency in all ten mandatory phases of the Cloud & DevOps program: Linux administration, Ansible automation, AWS cloud infrastructure, version control, CI/CD, containerization, Kubernetes orchestration, infrastructure as code with Terraform, monitoring and logging, and security best practices. Thank you for watching."

---

## Recording Tips

1. **Use OBS Studio or SimpleScreenRecorder** for screen capture
2. **Zoom in** on terminal text (150-200% zoom) for readability
3. **Speak clearly** and pause between segments
4. **Show the actual application** in a browser at least once
5. **Keep it under 7 minutes** — evaluators have limited time
6. **Add subtitles** if possible (auto-generated is fine)

---

*End of Video Script*
