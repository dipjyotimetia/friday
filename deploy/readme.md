# Cloud Deployment Script

A deployment script for deploying the FRIDAY services to Google Cloud Run.

## Description

This script automates the deployment of both the API and web application components to Google Cloud Run. It handles:

- Enabling required Google Cloud APIs
- Setting up secrets from environment files
- Building and deploying Docker images 
- Configuring Cloud Run services

## Prerequisites

- Google Cloud SDK (`gcloud`)
- Docker
- A .env.yaml file with configurations
- Authenticated `gcloud` session
- Project ID and region configuration

## Usage

```bash
# Set required environment variables
export PROJECT_ID="your-project-id"
export REGION="your-region"

# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

## Configuration

- `API_SERVICE_NAME`: Name for the API service (default: `friday-api`)
- `APP_SERVICE_NAME`: Name for the web app service (default: `friday-app`)
- `ENV_FILE`: Environment file path (default: .env.yaml)

## Features

- Error handling and logging
- Dependency checking
- Automatic API enablement
- Secret Manager integration
- Configurable resource allocation
- Unauthenticated access setup
- Environment variable configuration
- Service URL output

## Service Configuration

The script configures both services with:
- 512Mi memory
- 1 CPU
- 10 concurrent requests
- 30s timeout
- Automatic scaling

## Environment Variables

Required in .env.yaml:
```yaml
# API configuration variables
# Add your environment variables here
```

## Error Codes

The script will exit with non-zero status if:
- Required dependencies are missing
- Environment file is not found
- Not authenticated with `gcloud`
- Invalid project ID
- Deployment failures occur

## Notes

- All secrets are stored in Google Cloud Secret Manager
- Services are deployed with public access
- API URL is automatically configured in the web app
