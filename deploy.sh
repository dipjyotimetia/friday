#!/bin/bash

# Exit on any error and undefined variables
set -euo pipefail
IFS=$'\n\t'

# Configuration
readonly PROJECT_ID="${PROJECT_ID:-your-project-id}"
readonly REGION="${REGION:-us-central1}"
readonly SERVICE_NAME="${SERVICE_NAME:-friday-api}"
readonly IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
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
    # Check if .env.yaml exists
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "$ENV_FILE file not found"
        exit 1
    fi

    # Verify gcloud auth
    if ! gcloud auth print-access-token &>/dev/null; then
        log_error "Not authenticated with gcloud. Please run 'gcloud auth login'"
        exit 1
    }

    # Verify project ID
    if [[ "$PROJECT_ID" == "your-project-id" ]]; then
        log_error "Please set a valid PROJECT_ID"
        exit 1
    }
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
        # Skip empty lines and comments
        [[ -z "$key" || "$key" == \#* ]] && continue
        
        # Trim whitespace
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

# Build and deploy service
deploy_service() {
    # Build and push Docker image
    log_info "Building and pushing Docker image..."
    gcloud builds submit --tag "$IMAGE_NAME" --quiet

    # Prepare secrets string for deployment
    local secrets_str=""
    while IFS=': ' read -r key value || [[ -n "$key" ]]; do
        [[ -z "$key" || "$key" == \#* ]] && continue
        key="${key// /}"
        secrets_str+="${key}=${key}:latest,"
    done < "$ENV_FILE"
    secrets_str="${secrets_str%,}"  # Remove trailing comma

    # Deploy to Cloud Run
    log_info "Deploying to Cloud Run..."
    gcloud run deploy "$SERVICE_NAME" \
        --image "$IMAGE_NAME" \
        --platform managed \
        --region "$REGION" \
        --allow-unauthenticated \
        --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_REGION=$REGION" \
        --update-secrets="$secrets_str" \
        --quiet

    # Get the service URL
    local service_url
    service_url=$(gcloud run services describe "$SERVICE_NAME" \
        --region "$REGION" \
        --format='value(status.url)')

    log_info "✅ Deployment complete!"
    log_info "🌎 Service URL: $service_url"
}

main() {
    log_info "Starting deployment process..."
    check_dependencies
    validate_environment
    enable_apis
    create_secrets
    deploy_service
}

# Execute main function
main