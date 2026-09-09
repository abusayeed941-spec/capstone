# Security & Best Practices Documentation

## 1. IAM — Least-Privilege Access

| Role | Permissions | Purpose |
|------|------------|---------|
| Admin | AdministratorAccess (temp) + custom limited policies | Terraform apply, AWS console access |
| Developer | ReadOnlyAccess + ECR read + S3 read (specific buckets) | Code deployment, log viewing |
| EC2 Instance Role | CloudWatchAgent, SSM, ECR pull only | App instances — no broad AWS access |
| AppUser | No AWS console access | Service account, no IAM policies needed |

### IAM Policy Example (Developer — restricted)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::ecommerce-dev-product-images-*",
        "arn:aws:s3:::ecommerce-dev-product-images-*/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:Get*",
        "cloudwatch:List*"
      ],
      "Resource": "*"
    }
  ]
}
```

## 2. Secret Management

### K8s Secrets
- All passwords, API keys stored as K8s Secrets (base64 encoded)
- Secrets mounted as environment variables or files
- **Production:** Use External Secrets Operator with AWS Secrets Manager
- **Dev:** K8s Secrets are sufficient

### Ansible Vault
```bash
# Encrypt sensitive variables
ansible-vault encrypt 03_ansible/playbooks/vault.yml

# Run playbook with vault password
ansible-playbook site.yml --ask-vault-pass

# Edit encrypted file
ansible-vault edit 03_ansible/playbooks/vault.yml
```

### Never commit secrets to Git
- `.gitignore` includes `.env`, `vault.yml`, `*.key`, `*.pem`
- Use CI/CD credential stores (Jenkins credentials, GitHub secrets)

## 3. SSL/TLS Implementation

### Option A: Let's Encrypt via cert-manager (recommended for K8s)
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
      - http01:
          ingress:
            class: nginx
```

### Option B: ALB TLS Termination
- ALB handles SSL termination with ACM certificate
- Traffic between ALB and K8s nodes on private network (no public exposure)
- Cost: ACM certificates are free

### Option C: Self-signed (for internal/testing)
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt \
  -subj "/CN=shop.example.com"
kubectl create secret tls ecommerce-tls-secret \
  --cert=tls.crt --key=tls.key -n ecommerce
```

## 4. Container Security

### Dockerfile Best Practices (already implemented)
- Multi-stage builds (smaller production images)
- Non-root user (appuser)
- Minimal base images (python:3.11-slim, nginx:alpine)
- No secrets in image layers
- Pin base image versions

### Image Scanning
```bash
# Manifest — integrate Trivy in CI/CD
trivy image --severity HIGH,CRITICAL ecommerce-backend:latest
```

## 5. Network Security

### Security Group Rules (implemented in Terraform)
- **ALB SG:** 80, 443 from 0.0.0.0/0; SSH from bastion only
- **Bastion SG:** SSH from your IP (set `your_ip_cidr` in tfvars)
- **EC2 SG:** SSH from bastion subnet; app ports accessible
- **DB SG:** MySQL 3306 from private subnet only — NOT from internet
- **K8s SG:** Node-to-node communication only

### NACL Rules (baseline)
- Allow inbound/outbound for standard ports
- Deny by default (AWS default)

### Private Subnet Architecture
- K8s master and workers in **private subnets** (no public IPs)
- Bastion host in **public subnet** for SSH access
- NAT Gateway for outbound from private subnet (updates, package downloads)

## 6. Kubernetes Security

### Pod Security Standards
- Use `PodSecurity` admission controller
- Set namespace labels: `pod-security.kubernetes.io/enforce: restricted`

### RBAC
- ServiceAccounts per application
- No `cluster-admin` for app ServiceAccounts
- Minimal permissions in ClusterRole/Role

### Network Policies (recommended — add after baseline works)
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
  namespace: ecommerce
spec:
  podSelector:
    matchLabels:
      app: ecommerce-backend
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: ecommerce-frontend
      ports:
        - protocol: TCP
          port: 5000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: mysql
      ports:
        - protocol: TCP
          port: 3306
```

## 7. AWS Security Best Practices

- **Encryption at rest:** EBS volumes encrypted (gp3 with encryption enabled)
- **Encryption in transit:** TLS for all public endpoints
- **S3:** Block public access, versioning enabled, SSE (AES-256)
- **CloudWatch Logs:** Centralized log aggregation for all instances
- **AWS Config:** Rules for compliance checking (optional)
- **GuardDuty:** Threat detection (free trial available)

## 8. Audit Checklist

- [ ] IAM users have MFA enabled
- [ ] Root account has MFA and is not used for daily operations
- [ ] Security groups follow least-privilege
- [ ] Secrets not hard-coded in source code
- [ ] Container images scanned before deployment
- [ ] TLS enabled on all public endpoints
- [ ] CloudTrail enabled for API audit logging
- [ ] CloudWatch alarms for security events
- [ ] Regular patching of EC2 instances (via Ansible)
- [ ] Kubernetes RBAC reviewed quarterly
