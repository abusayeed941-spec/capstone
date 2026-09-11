#!/bin/bash
# Deploy all K8s manifests for ecommerce namespace

NAMESPACE_FILE="/opt/ecommerce/k8s/namespaces/ecommerce-namespace.yml"
CONFIGMAP_FILE="/opt/ecommerce/k8s/configmaps/app-config.yml"
SECRET_FILE="/opt/ecommerce/k8s/secrets/db-secret.yml"
BACKEND_DEPLOY="/opt/ecommerce/k8s/deployments/backend-deployment.yml"
FRONTEND_DEPLOY="/opt/ecommerce/k8s/deployments/frontend-deployment.yml"
BACKEND_SVC="/opt/ecommerce/k8s/services/backend-service.yml"
FRONTEND_SVC="/opt/ecommerce/k8s/services/frontend-service.yml"
INGRESS_FILE="/opt/ecommerce/k8s/ingress/ecommerce-ingress.yml"
PVC_FILE="/opt/ecommerce/k8s/persistent/db-pvc.yml"

KUBECTL="/usr/local/bin/k3s kubectl"

echo "=== Deploying to K8s ==="
echo ""

# 1. Namespace
echo "1. Creating namespace..."
$KUBECTL apply -f $NAMESPACE_FILE
echo ""

# 2. ConfigMap
echo "2. Creating configmap..."
$KUBECTL apply -f $CONFIGMAP_FILE
echo ""

# 3. Secret
echo "3. Creating secret..."
$KUBECTL apply -f $SECRET_FILE
echo ""

# 4. PVC
echo "4. Creating PVC..."
$KUBECTL apply -f $PVC_FILE
echo ""

# 5. Backend deployment
echo "5. Deploying backend..."
$KUBECTL apply -f $BACKEND_DEPLOY
echo ""

# 6. Frontend deployment
echo "6. Deploying frontend..."
$KUBECTL apply -f $FRONTEND_DEPLOY
echo ""

# 7. Services
echo "7. Creating services..."
$KUBECTL apply -f $BACKEND_SVC
$KUBECTL apply -f $FRONTEND_SVC
echo ""

# 8. Ingress
echo "8. Creating ingress..."
$KUBECTL apply -f $INGRESS_FILE
echo ""

echo "=== All manifests applied ==="
echo ""
echo "=== Verification ==="
$KUBECTL get all -n ecommerce
echo ""
echo "=== END ==="
