# Cloud & DevOps Capstone Project Proposal

## Project Title
**Design, Build, and Deploy a Production-Ready E-Commerce Cloud Application Platform**

---

## Submitted By
**Name:** [Your Name]  
**Email:** [Your Email]  
**Course:** Cloud & DevOps Program — PSR Solutions Ltd  
**Date:** [Submission Date]

---

## 1. Executive Summary

This capstone project demonstrates a complete end-to-end Cloud and DevOps implementation for a production-ready **E-Commerce Platform**. The platform includes a product catalog, shopping cart, and order management system delivered as a RESTful API with a web frontend.

Every Cloud, Linux, DevOps, Automation, and Infrastructure concept from the course is incorporated:
- **Linux Administration (RHCSA):** System installation, user management, permissions, LVM, systemd services, firewall, shell scripting
- **Advanced Linux (RHCE):** Ansible automation, playbooks, roles, configuration management
- **AWS Cloud:** VPC, EC2, EBS, S3, IAM, ELB, Auto Scaling, CloudWatch
- **Version Control:** Git branching strategy, pull requests, repository management
- **CI/CD:** Jenkins pipelines for automated build, test, and deployment with rollback
- **Containerization:** Docker images, Docker Compose, container registry
- **Kubernetes:** Self-hosted cluster on EC2 with deployments, services, ingress, ConfigMaps, Secrets, PVs
- **Infrastructure as Code:** Terraform modules for AWS resource provisioning
- **Monitoring & Security:** Prometheus, Grafana, centralized logging, alerting, SSL/TLS, least-privilege IAM

---

## 2. Application Overview

### Business Use Case
An e-commerce platform enabling customers to:
- Browse and search products from a catalog
- Add/remove items from a shopping cart
- Place and track orders
- Administer products and orders via an admin panel

### Technology Stack
| Layer | Technology |
|-------|-----------|
| Backend | Python Flask REST API |
| Frontend | HTML/CSS/JS (simple web UI) |
| Database | MySQL 8 |
| Container Runtime | Docker + Docker Compose |
| Orchestration | Kubernetes (self-hosted on EC2) |
| CI/CD | Jenkins |
| IaC | Terraform (AWS) |
| Config Management | Ansible |
| Monitoring | Prometheus + Grafana |
| Cloud Provider | AWS (Free Tier) |

### Application Architecture (Logical)
```
┌─────────────────────────────────────────────────────┐
│                    Load Balancer (ELB)              │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
   │  K8s    │  │  K8s    │  │  K8s    │
   │ Node 1  │  │ Node 2  │  │ Node 3  │
   │ (EC2)   │  │ (EC2)   │  │ (EC2)   │
   └────┬────┘  └────┬────┘  └────┬────┘
        │             │             │
   ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
   │ Pod:    │  │ Pod:    │  │ Pod:    │
   │ Frontend│  │ Backend │  │ MySQL   │
   │ (Nginx) │  │ (Flask) │  │ (Stateful│
   │         │  │         │  │  Set)    │
   └─────────┘  └─────────┘  └─────────┘
                      │
               ┌──────▼──────┐
               │   S3 Store  │
               │ (Product    │
               │  Images)    │
               └─────────────┘
```

---

## 3. Scope and Deliverables

### Phase 1 — Linux Administration (RHCSA)
- [ ] RHEL/Rocky 9 installation and configuration
- [ ] User and group management (create roles: admin, developer, appuser)
- [ ] File permissions and ACLs (restrict app directories)
- [ ] Package management (yum/dnf — install nginx, mysql, docker)
- [ ] Service management using systemd (custom service for app health checks)
- [ ] Storage management (LVM: create logical volumes for /data, /logs)
- [ ] SSH configuration (key-based auth, disable root login, custom port)
- [ ] Firewall configuration (firewalld — open HTTP/HTTPS, block unnecessary ports)
- [ ] Basic shell scripting (backup script, log rotation script)
- [ ] Log management and troubleshooting (rsyslog, journalctl)

### Phase 2 — Ansible Automation (RHCE)
- [ ] Ansible installation and configuration
- [ ] Inventory file (group hosts: webservers, dbservers, k8s_nodes)
- [ ] Role: `webserver` — installs and configures Nginx
- [ ] Role: `database` — installs and configures MySQL
- [ ] Role: `app_deployment` — deploys the Flask application
- [ ] Role: `monitoring` — installs Prometheus node exporter
- [ ] Playbook: `site.yml` — orchestrates all roles
- [ ] Server provisioning using Ansible (bootstrap new nodes)

### Phase 3 — AWS Cloud Infrastructure
- [ ] IAM users, groups, and roles (least-privilege: Admin, Developer, AppUser)
- [ ] VPC design: public subnet (load balancer, bastion), private subnet (app nodes, DB)
- [ ] Security Groups and NACLs (web traffic, SSH from bastion only)
- [ ] EC2 instances (bastion host, K8s control plane, K8s worker nodes)
- [ ] EBS volumes (attach to K8s nodes for PVs)
- [ ] S3 bucket (product images, static assets)
- [ ] Application Load Balancer (ALB) targeting K8s ingress
- [ ] Auto Scaling Group for worker nodes (optional — scale based on CPU)
- [ ] CloudWatch monitoring (CPU, memory, disk, custom app metrics via agent)
- [ ] AWS Backup strategy (EBS snapshots, S3 versioning)
- [ ] Cost optimization (Rightsizing, spot instances for workers, free tier usage)

### Phase 4 — Version Control & Collaboration
- [ ] Git repository initialized
- [ ] Branching strategy: `main`, `develop`, `feature/*`, `release/*`
- [ ] Pull Requests for code review
- [ ] Repository structure organized by component

### Phase 5 — CI/CD Pipeline
- [ ] Jenkins installation and configuration (on bastion or dedicated EC2)
- [ ] Pipeline stages: Checkout → Lint → Unit Test → Build Docker Image → Push to Registry → Deploy to K8s → Smoke Test
- [ ] Automated testing (pytest for backend)
- [ ] Rollback strategy (kubectl rollout undo on failure)
- [ ] Jenkinsfile (declarative pipeline)

### Phase 6 — Containerization
- [ ] Dockerfile for backend (Flask app)
- [ ] Dockerfile for frontend (Nginx serving static files)
- [ ] docker-compose.yml for local development
- [ ] Multi-container setup (app + db + nginx)
- [ ] Container registry integration (Docker Hub or AWS ECR)

### Phase 7 — Kubernetes
- [ ] Self-hosted Kubernetes cluster (kubeadm or k3s on EC2)
- [ ] Pod management (frontend, backend, database pods)
- [ ] Deployments (frontend-deployment, backend-deployment)
- [ ] Services (ClusterIP for DB, NodePort/LoadBalancer for app)
- [ ] ConfigMaps (app config, log levels)
- [ ] Secrets (DB password, API keys — base64 encoded)
- [ ] Persistent Volumes (EBS-backed PVs for MySQL data)
- [ ] Ingress (Nginx Ingress Controller routing /api and / to services)
- [ ] Application scaling (HorizontalPodAutoscaler)

### Phase 8 — Infrastructure as Code (Terraform)
- [ ] `main.tf` — Terraform AWS provider and module calls
- [ ] `variables.tf` — input variables (region, instance types, counts)
- [ ] `terraform.tfvars` — environment-specific values
- [ ] `outputs.tf` — VPC ID, subnet IDs, instance IPs, bucket name
- [ ] Module: `vpc` — VPC, subnets, IGW, route tables, NACLs
- [ ] Module: `security_groups` — web SG, DB SG, SSH SG
- [ ] Module: `ec2` — bastion, K8s master, K8s workers
- [ ] Module: `iam` — users, groups, roles, policies
- [ ] Modular infrastructure design (reusable, parameterized)
- [ ] Terraform state management (local + S3 backend option)

### Phase 9 — Monitoring & Logging
- [ ] Prometheus (scrape K8s nodes, pods, API server metrics)
- [ ] Grafana (dashboards: cluster health, app latency, DB connections, EC2 metrics)
- [ ] Centralized logging (EFK stack — Elasticsearch, Fluentd/Fluent Bit, Kibana — or Loki + Promtail)
- [ ] Alerting mechanism (AlertManager: pod down, high CPU, DB unreachable, disk full)
- [ ] Dashboard creation (at least 3 Grafana dashboards)

### Phase 10 — Security & Best Practices
- [ ] Least-privilege IAM access (no AdministratorAccess for app role)
- [ ] Secret management (K8s Secrets, Ansible Vault for sensitive vars)
- [ ] SSL/TLS implementation (Let's Encrypt cert-manager on K8s, or ALB HTTPS)
- [ ] Security Group hardening (least exposure)
- [ ] Container security (non-root Dockerfile, image scanning)

---

## 4. Project Timeline (10 Days)

| Day | Focus Area | Key Tasks |
|-----|-----------|-----------|
| 1 | Setup & Linux | Install RHEL on VM/EC2, configure users, LVM, SSH, firewalld |
| 2 | Linux continued | Shell scripts, systemd service, log configuration |
| 3 | Ansible | Install Ansible, write inventory, build 4 roles, run site.yml |
| 4 | Terraform (AWS) | Write modules, apply VPC + EC2 + IAM + S3 |
| 5 | Docker | Write Dockerfiles, docker-compose, build and test locally |
| 6 | Kubernetes | Bootstrap cluster on EC2, deploy apps, ingress, PVs |
| 7 | CI/CD | Install Jenkins, create Jenkinsfile, connect to Git |
| 8 | Monitoring | Install Prometheus/Grafana, create dashboards, alerting |
| 9 | Security & Docs | SSL/TLS, IAM hardening, deployment documentation |
| 10 | Finalize | Demo video, presentation, final submission |

---

## 5. Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| AWS costs exceeding free tier | Medium | Use t2.micro/t3.micro, monitor Billing Dashboard, set budget alerts |
| K8s cluster complexity | Medium | Use k3s (lightweight) or kubeadm; start with 1 master + 1 worker, scale later |
| Time overrun | High | Prioritize mandatory items; submit partial work on Day 10 with completed sections |
| DNS/SSL delays | Low | Use ALB HTTPS or self-signed certs initially; cert-manager for production |

---

## 6. Conclusion

This project will deliver a production-grade e-commerce platform demonstrating mastery of Cloud, Linux, DevOps, Automation, and Infrastructure skills. All mandatory learning outcomes are addressed, and the implementation is structured to be progressively enhanced as new technologies are learned.

---

*End of Proposal*
