# CI/CD Pipeline — Jenkins

## Setup Instructions

1. **Install Jenkins on bastion EC2:**
   ```bash
   # On RHEL/Rocky 9
   sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
   sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.key
   sudo yum install -y jenkins
   sudo systemctl enable --now jenkins
   ```

2. **Install required Jenkins plugins:**
   - Docker Pipeline
   - Kubernetes CLI
   - AWS Credentials
   - Pipeline (already installed)
   - Slack Notification
   - Blue Ocean (optional)

3. **Configure credentials in Jenkins:**
   - `docker-registry-creds` — Docker Hub username/password
   - `aws-creds` — AWS Access Key ID + Secret Access Key

4. **Create a new Jenkins Pipeline job:**
   - Pipeline type: `Pipeline script from SCM`
   - SCM: Git, URL: your repository
   - Branch: `*/develop` or `*/main`
   - Script Path: `06_cicd/Jenkinsfile`

5. **Connect GitHub webhook:**
   - In your GitHub repo: Settings → Webhooks → Add webhook
   - Payload URL: `http://<jenkins-host>:8080/github-webhook/`
   - Events: Push

## Pipeline Stages

```
Checkout → Lint (Backend + Frontend) → Unit Tests
       → Build Backend Image → Build Frontend Image
       → Push Backend → Push Frontend → Deploy to K8s → Smoke Tests
       → Cleanup (old images)
```

## Rollback

On pipeline failure, the `post { failure }` block automatically triggers `kubectl rollout undo` for both deployments.
