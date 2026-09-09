# Git Branching Strategy — E-Commerce Capstone

## Branching Model

```
main (production-ready, protected)
  │
  └── develop (integration branch, protected)
        │
        ├── feature/ecommerce-backend-api
        ├── feature/ecommerce-frontend-ui
        ├── feature/ansible-automation
        ├── feature/terraform-infra
        ├── feature/k8s-cluster
        ├── feature/ci-cd-pipeline
        ├── feature/prometheus-monitoring
        ├── feature/security-hardening
        │
        └── release/v1.0.0 (release candidate)
```

## Branch Naming Convention

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/<short-desc>` | `feature/ecommerce-backend-api` |
| Bug fix | `fix/<short-desc>` | `fix/cart-stock-check` |
| Hotfix | `hotfix/<short-desc>` | `hotfix/prod-db-connection` |
| Release | `release/v<major>.<minor>.<patch>` | `release/v1.0.0` |
| Documentation | `docs/<short-desc>` | `docs/pipeline-guide` |

## Workflow

### Feature Development
```bash
# 1. Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/ecommerce-backend-api

# 2. Work on feature, commit regularly
git add .
git commit -m "feat: implement product catalog endpoint"

# 3. Push and create Pull Request
git push origin feature/ecommerce-backend-api
# → Create PR on GitHub: feature/ecommerce-backend-api → develop

# 4. After review and merge, delete branch
git checkout develop
git pull origin develop
git branch -d feature/ecommerce-backend-api
```

### Release
```bash
# 1. Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0

# 2. Bump version, update changelog
# 3. Test release branch thoroughly
# 4. Merge to main AND develop
git checkout main
git merge --no-ff release/v1.0.0
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin main --tags

git checkout develop
git merge --no-ff release/v1.0.0
git push origin develop

# 5. Delete release branch
git branch -d release/v1.0.0
git push origin --delete release/v1.0.0
```

## Pull Request Guidelines

- **Title:** Use conventional commit format: `feat:`, `fix:`, `chore:`, `docs:`
- **Description:** What changed, why, testing done
- **Reviewers:** At least 1 reviewer (self-review if solo)
- **Merge:** Squash merge for feature branches, merge commit for releases
- **CI:** All checks must pass before merge

## Repository Structure

```
ecommerce-capstone/
├── 01_proposal/           # Project proposal
├── 02_linux/              # Linux scripts & configs
│   ├── setup_scripts/
│   └── systemd/
├── 03_ansible/            # Ansible playbooks & roles
│   ├── inventory/
│   ├── playbooks/
│   └── roles/
├── 04_terraform/          # Terraform AWS infrastructure
│   ├── modules/
│   └── environments/
├── 05_git/               # Git documentation
├── 06_cicd/              # Jenkins pipeline
│   └── Jenkinsfile
├── 07_docker/            # Docker configs (in eCommerceApp/)
├── 08_kubernetes/        # K8s manifests
│   ├── deployments/
│   ├── services/
│   ├── configmaps/
│   ├── secrets/
│   ├── ingress/
│   └── pv/
├── 09_monitoring/        # Prometheus, Grafana, Alerting
│   ├── prometheus/
│   ├── grafana/
│   └── alerting/
├── 10_security/          # Security configs & docs
│   ├── ssl/
│   ├── secrets/
│   └── iam/
├── 11_docs/              # Documentation
│   ├── architecture_diagram.txt
│   ├── deployment_documentation.md
│   └── presentation/
├── eCommerceApp/         # Application source code
│   ├── backend/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── test_app.py
│   └── frontend/
│       ├── index.html
│       ├── Dockerfile
│       └── nginx.conf
└── docker-compose.yml    # Local dev orchestration
```

## Commit Message Convention

```
type(scope): description

Types:
  feat     - New feature
  fix      - Bug fix
  chore    - Maintenance (dependencies, config)
  docs     - Documentation only
  refactor - Code restructure (no behavior change)
  test     - Add/update tests
  security - Security-related changes

Examples:
  feat(products): add category filter to GET /api/products
  fix(cart): prevent negative quantity in cart
  chore(deps): update flask to 3.0.0
  docs(deploy): add kubernetes deployment steps
  test(backend): add integration tests for orders endpoint
  security(ssl): add TLS configuration for ingress
```
