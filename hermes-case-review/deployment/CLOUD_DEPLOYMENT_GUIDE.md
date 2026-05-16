# ============================================================
# HERMES Case Review System - Cloud Deployment Guide
# Production-Grade Deployment for AWS/GCP/Azure
# ============================================================

# ============================================================
# SECTION 1: Deployment Overview
# ============================================================

## Architecture Overview

The HERMES Case Review System uses a microservices architecture designed for cloud-native deployment:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Load Balancer                                │
│                    (ALB/Cloud Load Balancer)                        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  API Server   │    │  API Server   │    │  API Server   │
│   (Node 1)    │    │   (Node 2)    │    │   (Node 3)    │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│     Redis     │    │  PostgreSQL   │    │  Object Store │
│   (ElastiCache│    │   (RDS)      │    │   (S3/GCS)    │
└───────────────┘    └───────────────┘    └───────────────┘
```

## Deployment Strategy

- **High Availability**: Multi-AZ deployment with automatic failover
- **Scalability**: Auto-scaling based on CPU/memory utilization
- **Security**: IAM roles, security groups, encryption at rest and in transit
- **Monitoring**: CloudWatch/Stackdriver + Prometheus + Grafana

# ============================================================
# SECTION 2: AWS Deployment (Amazon EKS)
# ============================================================

## Prerequisites

- AWS CLI configured with appropriate credentials
- eksctl installed
- kubectl installed
- Docker installed for image building

## Step 1: Build and Push Docker Image

```bash
# Login to Amazon ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Create ECR repository
aws ecr create-repository --repository-name hermes-case-review --region us-east-1

# Build image
cd hermes-case-review
docker build -f deployment/production/Dockerfile -t hermes-case-review:latest .

# Tag and push
docker tag hermes-case-review:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/hermes-case-review:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/hermes-case-review:latest
```

## Step 2: Create EKS Cluster

```bash
# Create EKS cluster with managed node group
eksctl create cluster \
  --name hermes-review-prod \
  --region us-east-1 \
  --version 1.28 \
  --nodegroup-name linux-nodes \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 10 \
  --managed \
  --with-oidc \
  --ssh-access \
  --asg-access
```

## Step 3: Deploy Application

```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-east-1 --name hermes-review-prod

# Apply Kubernetes configurations
kubectl apply -f deployment/kubernetes/
```

## Step 4: Verify Deployment

```bash
# Check pods status
kubectl get pods -n hermes-review

# Check services
kubectl get services -n hermes-review

# Get external IP
kubectl get ingress -n hermes-review
```

# ============================================================
# SECTION 3: GCP Deployment (Google Kubernetes Engine)
# ============================================================

## Prerequisites

- Google Cloud SDK installed
- kubectl installed
- Docker installed

## Step 1: Build and Push to Google Container Registry

```bash
# Set project
gcloud config set project <project-id>

# Build and push image
cd hermes-case-review
docker build -f deployment/production/Dockerfile -t gcr.io/<project-id>/hermes-case-review:latest .
docker push gcr.io/<project-id>/hermes-case-review:latest
```

## Step 2: Create GKE Cluster

```bash
# Create standard cluster
gcloud container clusters create hermes-review-prod \
  --region us-central1 \
  --num-nodes=3 \
  --machine-type=n2-standard-2 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10
```

## Step 3: Deploy Application

```bash
# Update kubectl
gcloud container clusters get-credentials hermes-review-prod --region us-central1

# Apply configurations
kubectl apply -f deployment/kubernetes/
```

# ============================================================
# SECTION 4: Azure Deployment (AKS)
# ============================================================

## Prerequisites

- Azure CLI installed
- kubectl installed
- Docker installed

## Step 1: Build and Push to Azure Container Registry

```bash
# Login to ACR
az acr login --name <acr-name>

# Build and push
cd hermes-case-review
az acr build --registry <acr-name> --image hermes-case-review:latest -f deployment/production/Dockerfile .
```

## Step 2: Create AKS Cluster

```bash
# Create resource group
az group create --name hermes-review-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group hermes-review-rg \
  --name hermes-review-prod \
  --node-count 3 \
  --enable-autoscaling \
  --min-count 1 \
  --max-count 10 \
  --vm-set-type VirtualMachineScaleSets \
  --load-balancer-sku standard
```

## Step 3: Deploy Application

```bash
# Get credentials
az aks get-credentials --resource-group hermes-review-rg --name hermes-review-prod

# Apply configurations
kubectl apply -f deployment/kubernetes/
```

# ============================================================
# SECTION 5: Kubernetes Configuration
# ============================================================

## Kubernetes Manifest Files

The following files are required for Kubernetes deployment:

1. **namespace.yaml** - Namespace for the application
2. **deployment.yaml** - Application deployment configuration
3. **service.yaml** - Service configuration
4. **ingress.yaml** - Ingress configuration (with TLS)
5. **configmap.yaml** - Configuration as code
6. **secret.yaml** - Sensitive data (encrypted)
7. **hpa.yaml** - Horizontal Pod Autoscaler
8. **pdb.yaml** - Pod Disruption Budget

## Key Configuration Options

### Resource Limits

```yaml
resources:
  requests:
    cpu: 250m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 2Gi
```

### Autoscaling Configuration

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: hermes-review-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: hermes-review
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

# ============================================================
# SECTION 6: Load Testing
# ============================================================

## Load Test Configuration

### Test Scenarios

1. **Light Load**: 50 concurrent users for 5 minutes
2. **Medium Load**: 200 concurrent users for 10 minutes
3. **Heavy Load**: 500 concurrent users for 15 minutes
4. **Stress Test**: 1000+ concurrent users until system failure
5. **Soak Test**: 100 concurrent users for 1 hour

### Running Load Tests

```bash
# Install dependencies
pip install locust

# Light load test
locust -f deployment/production/load_test/locustfile.py \
  --host=https://your-api-endpoint.com \
  --users 50 --spawn-rate 10 --run-time 5m \
  --headless --html report_light.html

# Medium load test
locust -f deployment/production/load_test/locustfile.py \
  --host=https://your-api-endpoint.com \
  --users 200 --spawn-rate 20 --run-time 10m \
  --headless --html report_medium.html

# Heavy load test
locust -f deployment/production/load_test/locustfile.py \
  --host=https://your-api-endpoint.com \
  --users 500 --spawn-rate 50 --run-time 15m \
  --headless --html report_heavy.html
```

### Distributed Load Testing

```bash
# Master node
locust -f deployment/production/load_test/locustfile.py \
  --host=https://your-api-endpoint.com \
  --master --expect-workers 4

# Worker nodes (run on 4 separate machines)
locust -f deployment/production/load_test/locustfile.py \
  --host=https://your-api-endpoint.com \
  --worker --master-host <master-ip>
```

# ============================================================
# SECTION 7: Monitoring & Alerting
# ============================================================

## CloudWatch Metrics (AWS)

```yaml
# CloudWatch Dashboard Configuration
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["hermes-review", "Requests", "Service", "hermes-review"],
          [".", "Latency", ".", "."],
          [".", "Errors", ".", "."]
        ],
        "period": 60,
        "stat": "Average"
      }
    }
  ]
}
```

## Alert Rules

| Alert | Condition | Action |
|-------|-----------|--------|
| High Latency | p99 > 2s | Notify on-call |
| Error Rate | > 5% | Page on-call |
| High CPU | > 80% for 5min | Auto-scale |
| High Memory | > 90% | Alert + scale |

# ============================================================
# SECTION 8: Security Configuration
# ============================================================

## IAM Roles (AWS)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::hermes-review-data/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Resource": "*"
    }
  ]
}
```

## Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: hermes-review-network-policy
spec:
  podSelector:
    matchLabels:
      app: hermes-review
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

# ============================================================
# SECTION 9: Backup & Disaster Recovery
# ============================================================

## Backup Strategy

| Component | Backup Frequency | Retention | Recovery Time |
|-----------|-----------------|-----------|---------------|
| PostgreSQL | Hourly | 7 days | < 1 hour |
| Redis | Every 5 min | 1 day | < 5 min |
| File Storage | Daily | 30 days | < 2 hours |
| Configuration | On change | Indefinite | < 10 min |

## Disaster Recovery Plan

1. **RTO (Recovery Time Objective)**: 4 hours
2. **RPO (Recovery Point Objective)**: 1 hour
3. **DR Site**: Cross-region deployment
4. **Failover**: Automatic with Route 53

# ============================================================
# SECTION 10: Deployment Checklist
# ============================================================

## Pre-Deployment Checklist

- [ ] All tests passing in CI/CD pipeline
- [ ] Security scan completed (no critical vulnerabilities)
- [ ] Performance benchmarks met
- [ ] Rollback plan prepared
- [ ] Monitoring dashboards configured
- [ ] Alerting rules verified
- [ ] Runbook documented
- [ ] Team trained on deployment process

## Post-Deployment Checklist

- [ ] Smoke tests passed
- [ ] Health checks green
- [ ] Error rates normal
- [ ] Latency within SLA
- [ ] Logs being collected
- [ ] Backups verified
- [ ] Documentation updated

# ============================================================
# SECTION 11: Troubleshooting
# ============================================================

## Common Issues

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n hermes-review

# Check events
kubectl get events -n hermes-review --sort-by='.lastTimestamp'

# Common fixes:
# - Check image pull policy
# - Verify resource limits
# - Check init container logs
```

### High Latency

```bash
# Check pod resource usage
kubectl top pods -n hermes-review

# Check HPA status
kubectl describe hpa hermes-review -n hermes-review

# Check service endpoints
kubectl get endpoints hermes-review -n hermes-review
```

### Database Connection Issues

```bash
# Check secrets
kubectl get secrets -n hermes-review

# Verify connection string format
kubectl get configmap hermes-review-config -n hermes-review -o yaml

# Test connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  wget -qO- http://hermes-review:8000/health
```

# ============================================================
# Contact & Support
# ============================================================

For deployment support, contact:
- DevOps Team: devops@example.com
- On-Call: oncall@example.com
- Documentation: https://docs.example.com/hermes-review
