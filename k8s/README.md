# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the Agent Marketplace Platform.

## Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl configured
- Helm (optional, for cert-manager)
- Container registry access

## Quick Start

### 1. Create Namespace

```bash
kubectl apply -f namespace.yaml
```

### 2. Create Secrets

**Important**: Update the secrets with your actual values before applying.

```bash
# Create secrets from file
kubectl apply -f secrets.yaml

# Or create from command line
kubectl create secret generic agent-marketplace-secrets \
  --from-literal=DATABASE_URL="postgresql://user:pass@postgres:5432/db" \
  --from-literal=REDIS_URL="redis://redis:6379/0" \
  --from-literal=SECRET_KEY="your-secret-key" \
  --from-literal=OPENAI_API_KEY="sk-..." \
  --from-literal=ANTHROPIC_API_KEY="sk-ant-..." \
  --from-literal=GROQ_API_KEY="gsk_..." \
  --namespace agent-marketplace
```

### 3. Apply ConfigMap

```bash
kubectl apply -f configmap.yaml
```

### 4. Deploy Infrastructure

```bash
# PostgreSQL
kubectl apply -f postgres.yaml

# Redis
kubectl apply -f redis.yaml

# Qdrant
kubectl apply -f qdrant.yaml
```

Wait for all pods to be ready:

```bash
kubectl wait --for=condition=ready pod -l app=postgres -n agent-marketplace --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n agent-marketplace --timeout=300s
kubectl wait --for=condition=ready pod -l app=qdrant -n agent-marketplace --timeout=300s
```

### 5. Run Database Migrations

```bash
# Create a job to run migrations
kubectl run migrations --image=your-registry/agent-marketplace-backend:latest \
  --restart=Never \
  --namespace=agent-marketplace \
  --env-from=configmap/agent-marketplace-config \
  --env-from=secret/agent-marketplace-secrets \
  --command -- alembic upgrade head

# Check logs
kubectl logs migrations -n agent-marketplace

# Clean up
kubectl delete pod migrations -n agent-marketplace
```

### 6. Deploy Backend

```bash
kubectl apply -f backend.yaml
```

### 7. Deploy Ingress (Optional)

```bash
# Install cert-manager first (if not already installed)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Apply ingress
kubectl apply -f ingress.yaml
```

## Verify Deployment

```bash
# Check all pods
kubectl get pods -n agent-marketplace

# Check services
kubectl get svc -n agent-marketplace

# Check ingress
kubectl get ingress -n agent-marketplace

# View logs
kubectl logs -f deployment/backend -n agent-marketplace

# Test health endpoint
kubectl port-forward svc/backend 8000:8000 -n agent-marketplace
curl http://localhost:8000/api/v1/health
```

## Scaling

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment backend --replicas=5 -n agent-marketplace
```

### Auto-scaling

The HPA (Horizontal Pod Autoscaler) is already configured in `backend.yaml`:
- Min replicas: 3
- Max replicas: 10
- Target CPU: 70%
- Target Memory: 80%

View HPA status:

```bash
kubectl get hpa -n agent-marketplace
```

## Monitoring

### View Metrics

```bash
# Pod metrics
kubectl top pods -n agent-marketplace

# Node metrics
kubectl top nodes
```

### View Events

```bash
kubectl get events -n agent-marketplace --sort-by='.lastTimestamp'
```

## Troubleshooting

### Pod Not Starting

```bash
# Describe pod
kubectl describe pod <pod-name> -n agent-marketplace

# View logs
kubectl logs <pod-name> -n agent-marketplace

# Get previous logs (if pod restarted)
kubectl logs <pod-name> -n agent-marketplace --previous
```

### Database Connection Issues

```bash
# Test database connectivity
kubectl run -it --rm debug --image=postgres:16-alpine --restart=Never -n agent-marketplace -- \
  psql postgresql://user:pass@postgres:5432/agentic_db
```

### Redis Connection Issues

```bash
# Test Redis connectivity
kubectl run -it --rm debug --image=redis:7-alpine --restart=Never -n agent-marketplace -- \
  redis-cli -h redis ping
```

## Backup and Restore

### Backup PostgreSQL

```bash
# Create backup
kubectl exec -it deployment/postgres -n agent-marketplace -- \
  pg_dump -U agentic agentic_db > backup.sql

# Or use a CronJob for automated backups
```

### Restore PostgreSQL

```bash
# Restore from backup
kubectl exec -i deployment/postgres -n agent-marketplace -- \
  psql -U agentic agentic_db < backup.sql
```

## Updates and Rollouts

### Update Backend Image

```bash
# Update image
kubectl set image deployment/backend backend=your-registry/agent-marketplace-backend:v2.0.0 \
  -n agent-marketplace

# Check rollout status
kubectl rollout status deployment/backend -n agent-marketplace

# View rollout history
kubectl rollout history deployment/backend -n agent-marketplace
```

### Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/backend -n agent-marketplace

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n agent-marketplace
```

## Clean Up

```bash
# Delete all resources
kubectl delete namespace agent-marketplace

# Or delete individual resources
kubectl delete -f backend.yaml
kubectl delete -f postgres.yaml
kubectl delete -f redis.yaml
kubectl delete -f qdrant.yaml
kubectl delete -f configmap.yaml
kubectl delete -f secrets.yaml
kubectl delete -f namespace.yaml
```

## Production Considerations

### Security

1. **Use Secrets Management**: Consider using external secrets management (Vault, AWS Secrets Manager)
2. **Network Policies**: Implement network policies to restrict pod-to-pod communication
3. **RBAC**: Configure proper Role-Based Access Control
4. **Pod Security**: Use Pod Security Standards/Policies

### High Availability

1. **Multi-Zone Deployment**: Deploy across multiple availability zones
2. **Database Replication**: Set up PostgreSQL replication
3. **Redis Sentinel**: Use Redis Sentinel for HA
4. **Backup Strategy**: Implement automated backup and disaster recovery

### Monitoring

1. **Prometheus**: Set up Prometheus for metrics collection
2. **Grafana**: Create dashboards for visualization
3. **Alerting**: Configure alerts for critical issues
4. **Logging**: Use ELK/EFK stack or cloud logging

### Performance

1. **Resource Limits**: Fine-tune CPU and memory limits
2. **Connection Pooling**: Configure database connection pooling
3. **Caching**: Optimize Redis caching strategy
4. **CDN**: Use CDN for static assets

## Support

For issues or questions:
- Check logs: `kubectl logs -f deployment/backend -n agent-marketplace`
- View events: `kubectl get events -n agent-marketplace`
- Describe resources: `kubectl describe <resource> -n agent-marketplace`

