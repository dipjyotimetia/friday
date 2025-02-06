#!/bin/bash

# Exit on any error and undefined variables
set -euo pipefail
IFS=$'\n\t'

# Configuration
readonly PROJECT_ID="${PROJECT_ID:-your-project-id}"
readonly REGION="${REGION:-us-central1}"
readonly API_SERVICE_NAME="${API_SERVICE_NAME:-friday-api}"
readonly APP_SERVICE_NAME="${APP_SERVICE_NAME:-friday-app}"
readonly API_IMAGE_NAME="gcr.io/${PROJECT_ID}/${API_SERVICE_NAME}"
readonly APP_IMAGE_NAME="gcr.io/${PROJECT_ID}/${APP_SERVICE_NAME}"
readonly ENV_FILE=".env.yaml"
readonly REQUIRED_APIS=(
    "run.googleapis.com"
    "cloudbuild.googleapis.com"
    "artifactregistry.googleapis.com"
    "secretmanager.googleapis.com"
)

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

# Logger functions
log_info() { echo -e "${GREEN}INFO: ${NC}$1"; }
log_warn() { echo -e "${YELLOW}WARN: ${NC}$1"; }
log_error() { echo -e "${RED}ERROR: ${NC}$1" >&2; }

# Error handler
trap 'log_error "An error occurred on line $LINENO. Exit code: $?"' ERR

# Check if required commands exist
check_dependencies() {
    local deps=("gcloud" "docker")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "$dep is required but not installed."
            exit 1
        fi
    done
}

# Validate environment
validate_environment() {
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "$ENV_FILE file not found"
        exit 1
    fi

    if ! gcloud auth print-access-token &>/dev/null; then
        log_error "Not authenticated with gcloud. Please run 'gcloud auth login'"
        exit 1
    fi

    if [[ "$PROJECT_ID" == "your-project-id" ]]; then
        log_error "Please set a valid PROJECT_ID"
        exit 1
    fi
}

# Enable required APIs
enable_apis() {
    log_info "Enabling required APIs..."
    local apis_to_enable=""
    for api in "${REQUIRED_APIS[@]}"; do
        if ! gcloud services list --enabled --filter="name:$api" --quiet | grep -q "$api"; then
            apis_to_enable+="$api "
        fi
    done

    if [[ -n "$apis_to_enable" ]]; then
        gcloud services enable $apis_to_enable
    fi
}

# Create secrets from .env.yaml
create_secrets() {
    log_info "Creating secrets in Secret Manager..."
    local service_account="${PROJECT_ID}@appspot.gserviceaccount.com"

    while IFS=': ' read -r key value || [[ -n "$key" ]]; do
        [[ -z "$key" || "$key" == \#* ]] && continue
        key="${key// /}"
        value="${value// /}"
        
        if [[ -n "$key" && -n "$value" ]]; then
            log_info "Processing secret: $key"
            if ! gcloud secrets describe "$key" --project="$PROJECT_ID" &>/dev/null; then
                echo -n "$value" | gcloud secrets create "$key" \
                    --replication-policy="automatic" \
                    --data-file=- \
                    --project="$PROJECT_ID"
            fi
        fi
    done < "$ENV_FILE"

    # Add Secret Manager role to Cloud Run service account
    log_info "Granting Secret Manager access..."
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$service_account" \
        --role="roles/secretmanager.secretAccessor" \
        --condition=None \
        --quiet
}

# Deploy API service
deploy_api() {
    log_info "Building and pushing API image..."
    gcloud builds submit --tag "$API_IMAGE_NAME" --quiet

    local secrets_str=""
    while IFS=': ' read -r key value || [[ -n "$key" ]]; do
        [[ -z "$key" || "$key" == \#* ]] && continue
        key="${key// /}"
        secrets_str+="${key}=${key}:latest,"
    done < "$ENV_FILE"
    secrets_str="${secrets_str%,}"

    log_info "Deploying API to Cloud Run..."
    gcloud run deploy "$API_SERVICE_NAME" \
        --image "$API_IMAGE_NAME" \
        --platform managed \
        --region "$REGION" \
        --allow-unauthenticated \
        --memory 512Mi \
        --cpu 1 \
        --concurrency 10 \
        --timeout 30s \
        --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_REGION=$REGION,WORKERS=2,MAX_WORKERS=4,WEB_CONCURRENCY=2" \
        --update-secrets="$secrets_str" \
        --quiet

    API_URL=$(gcloud run services describe "$API_SERVICE_NAME" \
        --region "$REGION" \
        --format='value(status.url)')
    
    log_info "API deployed at: $API_URL"
    return "$API_URL"
}

# Deploy Web App service
deploy_webapp() {
    local api_url="$1"
    log_info "Building and pushing Web App image..."
    
    # Build with API URL configuration
    gcloud builds submit ./app --tag "$APP_IMAGE_NAME" \
        --substitutions=_API_URL="$api_url" \
        --quiet

    log_info "Deploying Web App to Cloud Run..."
    gcloud run deploy "$APP_SERVICE_NAME" \
        --image "$APP_IMAGE_NAME" \
        --platform managed \
        --region "$REGION" \
        --memory 512Mi \
        --cpu 1 \
        --concurrency 10 \
        --timeout 30s \
        --allow-unauthenticated \
        --set-env-vars="API_URL=$api_url" \
        --quiet

    local webapp_url
    webapp_url=$(gcloud run services describe "$APP_SERVICE_NAME" \
        --region "$REGION" \
        --format='value(status.url)')

    log_info "Web App deployed at: $webapp_url"
}

main() {
    log_info "Starting deployment process..."
    check_dependencies
    validate_environment
    enable_apis
    create_secrets
    
    # Deploy API first
    api_url=$(deploy_api)
    
    # Then deploy webapp with API URL
    deploy_webapp "$api_url"
    
    log_info "✅ Deployment complete!"
}

# Execute main function
# PROJECT_ID="your-project" REGION="us-west1" ./deploy.sh
main