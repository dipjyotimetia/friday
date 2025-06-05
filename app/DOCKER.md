# Docker Configuration for FRIDAY Frontend

## Overview

The FRIDAY frontend is containerized using a multi-stage Docker build optimized for Next.js production deployment. The configuration supports both development and production environments with proper security measures and health monitoring.

## Docker Architecture

### Multi-Stage Build Process

1. **Base Stage** (`node:22-alpine`): Lightweight Alpine Linux base with Node.js 22
2. **Dependencies Stage**: Installs production dependencies only
3. **Builder Stage**: Builds the Next.js application with optimizations
4. **Runner Stage**: Final production image with minimal footprint

### Key Features

- ✅ **Security**: Non-root user execution (`nextjs:nodejs`)
- ✅ **Optimization**: Multi-stage build reduces image size
- ✅ **Performance**: Next.js standalone output for faster startup
- ✅ **Monitoring**: Built-in health checks
- ✅ **Production-Ready**: Environment variable support

## Files Overview

### Dockerfile
```dockerfile
FROM node:22-alpine AS base
# Multi-stage build with:
# - deps: Install dependencies
# - builder: Build Next.js app
# - runner: Production runtime
```

### docker-compose.yml
```yaml
services:
  friday-frontend:
    build: .
    ports: ["3000:3000"]
    healthcheck: node healthcheck.js
```

### .dockerignore
Excludes unnecessary files from Docker context:
- `node_modules/`, `.next/`, `.env*`
- Documentation, tests, development files
- Git and IDE files

### healthcheck.js
Custom health check script that validates the `/api/health` endpoint.

## Quick Start

### Development with Docker Compose

```bash
# Build and start the application
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f friday-frontend

# Stop services
docker-compose down
```

### Direct Docker Commands

```bash
# Build the image
docker build -t friday-frontend .

# Run the container
docker run -p 3000:3000 \
  --name friday-app \
  --health-cmd="node healthcheck.js" \
  --health-interval=30s \
  friday-frontend

# Check health status
docker inspect --format='{{json .State.Health}}' friday-app
```

## Environment Variables

### Build-time Variables
```bash
NODE_ENV=production          # Environment mode
NEXT_TELEMETRY_DISABLED=1   # Disable Next.js telemetry
```

### Runtime Variables
```bash
PORT=3000                   # Application port
HOSTNAME=0.0.0.0           # Bind address
NODE_ENV=production        # Runtime environment
```

### Custom Environment Variables
Add your own variables to `docker-compose.yml`:
```yaml
environment:
  - API_URL=http://backend:8080
  - CUSTOM_KEY=your_value
```

## Health Monitoring

### Health Check Endpoint
- **URL**: `http://localhost:3000/api/health`
- **Method**: GET
- **Response**: JSON with system status

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "uptime": 123.456,
  "environment": "production",
  "version": "1.0.0",
  "memory": {
    "used": 45.67,
    "total": 67.89
  },
  "pid": 1
}
```

### Docker Health Status
```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# View detailed health information
docker inspect friday-app | jq '.[].State.Health'
```

## Production Deployment

### Cloud Run (Google Cloud)
```bash
# Build for Cloud Run
docker build -t gcr.io/PROJECT_ID/friday-frontend .

# Push to registry
docker push gcr.io/PROJECT_ID/friday-frontend

# Deploy to Cloud Run
gcloud run deploy friday-frontend \
  --image gcr.io/PROJECT_ID/friday-frontend \
  --port 3000 \
  --allow-unauthenticated
```

### AWS ECS
```bash
# Build and tag for ECR
docker build -t friday-frontend .
docker tag friday-frontend:latest AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/friday-frontend:latest

# Push to ECR
docker push AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/friday-frontend:latest
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: friday-frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: friday-frontend
  template:
    metadata:
      labels:
        app: friday-frontend
    spec:
      containers:
      - name: friday-frontend
        image: friday-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
```

## Performance Optimizations

### Image Size Optimization
- **Alpine Linux**: Smaller base image (~5MB vs ~100MB)
- **Multi-stage Build**: Excludes build dependencies from final image
- **Standalone Output**: Only includes necessary runtime files
- **Layer Caching**: Optimized layer ordering for faster rebuilds

### Runtime Optimizations
- **Non-root User**: Security best practice
- **Console Removal**: Production builds exclude console.log statements
- **Static Optimization**: Pre-rendered pages for better performance
- **Compression**: Built-in Next.js optimizations

## Troubleshooting

### Common Issues

#### Build Failures
```bash
# Check build logs
docker build --no-cache -t friday-frontend .

# Debug with intermediate image
docker run -it $(docker build -q --target builder .) sh
```

#### Health Check Failures
```bash
# Test health endpoint manually
curl http://localhost:3000/api/health

# Check container logs
docker logs friday-app

# Execute health check manually
docker exec friday-app node healthcheck.js
```

#### Memory Issues
```bash
# Monitor memory usage
docker stats friday-app

# Increase memory limit
docker run --memory=2g friday-frontend
```

### Debug Mode
```bash
# Run with debug output
docker run -e DEBUG=* friday-frontend

# Access container shell
docker exec -it friday-app sh
```

## Best Practices

1. **Security**
   - Always run as non-root user
   - Use specific image tags, not `latest`
   - Scan images for vulnerabilities
   - Limit container capabilities

2. **Performance**
   - Use multi-stage builds
   - Optimize layer caching
   - Minimize image size
   - Enable health checks

3. **Monitoring**
   - Implement proper logging
   - Monitor resource usage
   - Set up alerts for health failures
   - Use structured logging

4. **Deployment**
   - Use environment-specific configurations
   - Implement rolling updates
   - Test in staging environment
   - Monitor deployment metrics