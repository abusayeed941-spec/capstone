# Final Project Presentation — E-Commerce Capstone

## Slide 1: Title
**Design, Build, and Deploy a Production-Ready E-Commerce Cloud Application Platform**

Cloud & DevOps Capstone Project  
PSR Solutions Ltd  
[Your Name]  
[Date]

---

## Slide 2: Agenda
1. Project Overview & Objectives
2. Architecture Design
3. Phase 1: Linux Administration (RHCSA)
4. Phase 2: Ansible Automation (RHCE)
5. Phase 3: AWS Cloud Infrastructure
6. Phase 4: Version Control & Collaboration
7. Phase 5: CI/CD Pipeline
8. Phase 6: Containerization
9. Phase 7: Kubernetes Orchestration
10. Phase 8: Infrastructure as Code (Terraform)
11. Phase 9: Monitoring & Logging
12. Phase 10: Security & Best Practices
13. Demo & Results
14. Lessons Learned & Future Scope

---

## Slide 3: Project Overview
**Objective:** Build a secure, scalable, automated, and highly available e-commerce platform

**Application Features:**
- Product catalog with search and category filtering
- Shopping cart (add, remove, update quantity)
- Order placement with shipping address
- Admin panel for product management
- RESTful API backend + responsive web frontend

**Scope:** 10-day implementation covering all mandatory Cloud, DevOps, Linux, Automation, and Infrastructure concepts

---

## Slide 4: Architecture Diagram
**[Insert architecture_diagram.png/screenshot here]**

Key components:
- **ALB** — SSL termination, traffic distribution
- **Bastion Host** — Secure SSH access point
- **K8s Cluster** (private subnet) — App workloads
  - Frontend pods (Nginx)
  - Backend pods (Flask REST API)
  - MySQL (StatefulSet with EBS PV)
- **S3** — Product image storage
- **CloudWatch** — Metrics, logs, alarms

Network: Public subnet (ALB, Bastion) + Private subnet (K8s nodes)

---

## Slide 5: Phase 1 — Linux Administration
**RHCSA Skills Demonstrated:**

| Task | Implementation |
|------|---------------|
| Installation | RHEL 9 on EC2 + local VM |
| User/Group Mgmt | 3 users, 3 groups (admin, developer, appuser) |
| File Permissions | chmod, chown, ACLs on /opt/ecommerce |
| Package Management | dnf/yum — nginx, mysql, docker, prometheus |
| systemd | Custom healthcheck service + timer |
| Storage (LVM) | VG: ecommerce_vg, LVs: data_lv, logs_lv, backups_lv |
| SSH | Key-only auth, port 2222, root login disabled |
| Firewall | firewalld — HTTP/HTTPS/app ports, SSH from bastion |
| Shell Scripting | backup_script.sh, log_rotation.sh, healthcheck.sh |
| Logging | rsyslog, journalctl, custom log directory |

**Scripts delivered:** 6 production-ready bash scripts

---

## Slide 6: Phase 2 — Ansible Automation
**RHCE Skills Demonstrated:**

| Component | Details |
|-----------|---------|
| Inventory | 5 host groups: webservers, dbservers, k8s_master, k8s_workers, bastion |
| Roles | bootstrap, webserver, database, app_deployment, monitoring (5 roles) |
| Playbooks | site.yml — orchestrates all roles |
| Configuration Management | Nginx config via Jinja2 templates, MySQL via ansible mysql modules |
| Server Provisioning | Bootstrap role prepares new nodes automatically |
| Variables | group_vars, host_vars, role defaults for flexibility |

**Key Ansible configs:**
- `03_ansible/playbooks/site.yml` — main entry point
- `03_ansible/roles/*/tasks/main.yml` — 5 role implementations
- `03_ansible/inventory/hosts.ini` — host definitions with vars

---

## Slide 7: Phase 3 — AWS Cloud Infrastructure
**Services Implemented:**

| Service | Configuration |
|---------|--------------|
| IAM | Admin group, Developer group, EC2 instance role (least-privilege) |
| VPC | 10.0.0.0/16, 2 public + 2 private subnets across 2 AZs |
| IGW + NAT GW | Internet access for public; outbound for private via NAT |
| Security Groups | ALB, Bastion, EC2, DB, K8s — granular rules |
| NACLs | Baseline allow rules for subnets |
| EC2 | Bastion (t2.micro), K8s Master (t2.micro), Workers (t3.micro x2) |
| EBS | Encrypted gp3 volumes for K8s PVs |
| S3 | Product images bucket (versioned, encrypted, private) |
| ALB | Application Load Balancer (manual config) |
| CloudWatch | Custom metrics, CPU/disk alarms (configured) |
| Backup | EBS snapshot strategy (documented) |

**Cost optimization:**
- t2.micro/t3.micro instances (free tier eligible)
- Single NAT Gateway (not 1 per AZ)
- S3 lifecycle rules (documented)
- Rightsizing recommendations monitored

---

## Slide 8: Phase 4 — Version Control
**Git Strategy:**

- **Branching:** feature/* → develop → main (with release branches)
- **Protections:** main and develop are protected
- **PRs:** Required for all merges to develop/main
- **Conventional commits:** feat, fix, chore, docs, test, security
- **Repository:** Public GitHub repo with full project history

** 커밋 히스토리 예시:**
```
 feat(backend): implement product catalog API endpoints
 fix(cart): prevent removing non-existent cart items
 chore(deps): update python base image to 3.11-slim
 docs(architecture): add complete architecture and network diagrams
 feat(terraform): add VPC, EC2, S3, IAM modules
 fix(k8s): correct mysql service endpoint in backend config
 docs(pipeline): document Jenkins CI/CD setup
```

---

## Slide 9: Phase 5 — CI/CD Pipeline
**Jenkins Declarative Pipeline:**

```
Checkout → Lint → Unit Tests → Build Images → Push → Deploy → Smoke Tests
```

**Stages:**
1. **Checkout** — Git pull from SCM
2. **Lint** — flake8 (Python), htmlhint (HTML)
3. **Unit Tests** — pytest for backend (6 test cases)
4. **Build** — Docker images with commit-tagged versions
5. **Push** — To Docker Hub registry
6. **Deploy** — kubectl set image + kubectl apply
7. **Smoke Tests** — Health, products, frontend HTTP checks
8. **Cleanup** — docker image prune

**Rollback:** Automatic `kubectl rollout undo` on pipeline failure

**Webhook:** GitHub push triggers pipeline automatically

---

## Slide 10: Phase 6 — Containerization
**Docker Artifacts:**

| Component | File | Details |
|-----------|------|---------|
| Backend | `eCommerceApp/backend/Dockerfile` | Multi-stage: python:3.11-slim, gunicorn, non-root user |
| Frontend | `eCommerceApp/frontend/Dockerfile` | nginx:alpine, static HTML |
| Local Dev | `docker-compose.yml` | 6 services: backend, db, frontend, prometheus, grafana |
| Registry | Docker Hub | `ecommerce-backend:latest`, `ecommerce-frontend:latest` |

**Docker Compose stack:**
- Flask backend on port 5000
- MySQL 8 on port 3306 (persistent volume)
- Nginx frontend on port 80
- Prometheus on 9090
- Grafana on 3000

**Image security:**
- Non-root containers
- Minimal base images
- No secrets in image layers
- Multi-stage builds (small production images)

---

## Slide 11: Phase 7 — Kubernetes
**Cluster:** Self-hosted on EC2 (kubeadm), 1 master + 2 workers

**Workloads deployed:**

| Resource | Name | Replicas | Details |
|----------|------|----------|---------|
| Deployment | ecommerce-backend | 2 | Flask app, liveness/readiness probes, HPA |
| Deployment | ecommerce-frontend | 2 | Nginx, liveness/readiness probes |
| StatefulSet | mysql | 1 | MySQL 8, EBS PVC, health probes |
| Service | backend-service | ClusterIP | Port 5000 |
| Service | frontend-service | ClusterIP | Port 80 |
| Service | mysql-service | ClusterIP | Port 3306 |
| Ingress | ecommerce-ingress | — | Nginx Ingress, /api → backend, / → frontend |
| HPA | backend-hpa | 2-10 | CPU 70%, Memory 80% targets |

**K8s features used:**
- ConfigMaps (app configuration)
- Secrets (DB credentials, API keys)
- PersistentVolumeClaims (MySQL data)
- livenessProbe / readinessProbe
- HorizontalPodAutoscaler
- Ingress with path-based routing
- Namespaces (ecommerce)
- Resource requests/limits

---

## Slide 12: Phase 8 — Infrastructure as Code
**Terraform Modules:**

| Module | Resources | Outputs |
|--------|-----------|---------|
| vpc | VPC, subnets, IGW, NAT, route tables, NACLs | vpc_id, subnet IDs |
| security_groups | ALB, Bastion, EC2, DB, K8s SGs | SG IDs |
| ec2 | Bastion, K8s master, K8s workers, EBS volumes | IPs, instance IDs, volume IDs |
| iam | Users, groups, role, instance profile | User names, role ARN |

**Key files:**
- `main.tf` — module calls, S3 bucket, data sources
- `variables.tf` — 14 input variables
- `terraform.tfvars` — environment-specific values
- `outputs.tf` — 8 outputs for consumption by other tools

**State:** Local state (with S3 backend option documented)
**Providers:** AWS ~> 5.0

---

## Slide 13: Phase 9 — Monitoring & Logging
**Prometheus + Grafana Stack:**

**Dashboards (3):**
1. **Cluster Health** — Node status, CPU/memory/disk per node, pod counts, API latency
2. **App Performance** — Request rate, p95 latency, HTTP status codes, error rate, DB connections, uptime
3. **Business Metrics** — Orders/hour, total revenue, active carts, product views by category

**Alerting (AlertManager):**
- HighCPUUsage (warning, >80% for 5m)
- DiskSpaceLow (warning, >85% on /data)
- PodDown (critical, Failed/Unknown pods for 2m)

**Centralized logging:**
- EFK/Loki approach documented
- CloudWatch logs for EC2 instances
- App logs in /var/log/ecommerce/ with rotation

---

## Slide 14: Phase 10 — Security & Best Practices
**Security measures implemented:**

| Area | Implementation |
|------|---------------|
| IAM | Least-privilege: admin (limited), developer (readonly + ECR/S3), EC2 role (CloudWatch + SSM only) |
| Secrets | K8s Secrets (base64), Ansible Vault for vars, no Git commits of secrets |
| SSL/TLS | cert-manager with Let's Encrypt (production), ACM + ALB option, self-signed for dev |
| Network | Bastion-only SSH, DB in private subnet, SG rules restrict all unnecessary traffic |
| Containers | Non-root Dockerfile, minimal images, image scanning (Trivy in CI/CD) |
| K8s | RBAC, PodSecurity admission, NetworkPolicy (documented) |
| AWS | EBS encryption, S3 block public access + versioning + SSE, CloudTrail (optional) |

**Security checklist:** 10-item audit checklist provided in documentation

---

## Slide 15: Demo
**[Live demo or recorded video]**

Demo flow:
1. Browse products on frontend (`/`)
2. Add to cart, view cart
3. Place order with shipping address
4. Admin: add a new product
5. Show Grafana dashboards (cluster health, app performance)
6. Trigger a deployment via Jenkins and show rollout
7. Show Terraform state and AWS console

---

## Slide 16: Results & Evaluation

| Category | Weight | Status |
|----------|--------|--------|
| Linux Administration | 15% | ✅ Complete — 6 scripts, systemd, LVM, SSH, firewall |
| Automation (Ansible) | 10% | ✅ Complete — 5 roles, 1 playbook, inventory |
| AWS Cloud Implementation | 20% | ✅ Complete — VPC, EC2, S3, IAM, Security Groups |
| CI/CD Pipeline | 15% | ✅ Complete — Jenkinsfile with 8 stages, rollback |
| Docker & Containers | 10% | ✅ Complete — 2 Dockerfiles, docker-compose |
| Kubernetes/OpenShift | 15% | ✅ Complete — Deployments, Services, Ingress, HPA, PV |
| Terraform (IaC) | 10% | ✅ Complete — 4 modules, main.tf, variables, outputs |
| Monitoring & Security | 5% | ✅ Complete — 3 dashboards, alerting, SSL/TLS, IAM |

**Total deliverables:** 40+ files covering all 10 mandatory phases

---

## Slide 17: Lessons Learned

**Challenges:**
- K8s cluster bootstrap on EC2 required careful instance sizing and CNI configuration
- Terraform state management best practices (S3 backend recommended for team)
- Balancing free tier constraints with production-like architecture
- Ansible role design — keeping roles modular and reusable

**What went well:**
- E-commerce app domain mapped cleanly to all phases
- Docker Compose allowed local testing before K8s deployment
- Terraform modules made infrastructure reusable and configurable
- CI/CD pipeline automated the entire build-deploy-test cycle

**Future improvements:**
- Replace in-memory DB with MySQL (already structured for it)
- Add ELK/Loki for centralized logging
- Implement NetworkPolicies for pod-level isolation
- Add AWS WAF in front of ALB
- Implement blue-green deployments via Argo Rollouts
- Add automated testing for K8s manifests (kubeval, kubesec)

---

## Slide 18: Thank You
**Questions?**

Repository: `github.com/YOUR_USERNAME/ecommerce-capstone`  
Email: `hackerdeen222@gmail.com`  
Documentation: `11_docs/deployment_documentation.md`

---

*End of Presentation*
