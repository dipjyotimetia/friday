# Friday API Documentation

## Overview

The Friday API is a FastAPI-based REST service that provides programmatic access to all Friday testing features. It runs on port 8080 by default and offers endpoints for test generation, web crawling, browser testing, and real-time logging via WebSocket.

## Base URL

```
http://localhost:8080
```

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`
- **OpenAPI Spec**: `http://localhost:8080/openapi.json`

## Quick Start

### Start the API Server

```bash
# Using Friday CLI
friday webui --api-only

# Using uvicorn directly
uv run uvicorn friday.api.app:app --reload --port 8080

# Using Docker
docker build -t friday-api .
docker run -p 8080:8080 friday-api
```

### Health Check

```bash
curl http://localhost:8080/health
```

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | API health check |
| GET | `/version` | Get API version |
| POST | `/api/v1/generate` | Generate test cases from issues |
| POST | `/api/v1/crawl` | Crawl websites and create embeddings |
| WebSocket | `/api/v1/ws/logs` | Real-time log streaming |

### Browser Testing Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/browser-test/health` | Browser testing service health |
| POST | `/api/v1/browser-test/yaml/upload` | Upload and execute YAML scenarios |
| POST | `/api/v1/browser-test/yaml/execute` | Execute YAML scenarios from content |
| GET | `/api/v1/browser-test/yaml/template` | Get sample YAML template |

### API Testing Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/testapi` | Test API endpoints from OpenAPI specs |

## Detailed Endpoint Reference

### 1. Health Check

Check if the API service is running properly.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "message": "Friday API is running",
  "timestamp": "2024-12-15T10:30:00Z",
  "version": "0.1.47"
}
```

**Example**:
```bash
curl http://localhost:8080/health
```

---

### 2. Version Information

Get the current API version.

**Endpoint**: `GET /version`

**Response**:
```json
{
  "version": "0.1.47",
  "build_date": "2024-12-15",
  "environment": "development"
}
```

**Example**:
```bash
curl http://localhost:8080/version
```

---

### 3. Generate Test Cases

Generate test cases from Jira or GitHub issues with optional Confluence context.

**Endpoint**: `POST /api/v1/generate`

**Request Body**:
```json
{
  "jira_key": "PROJECT-123",
  "gh_issue": "42",
  "gh_repo": "owner/repo",
  "confluence_id": "123456",
  "template": "test_case",
  "output": "test_cases.md"
}
```

**Parameters**:
- `jira_key` (optional): Jira issue key
- `gh_issue` (optional): GitHub issue number
- `gh_repo` (optional): GitHub repository (required with gh_issue)
- `confluence_id` (optional): Confluence page ID for context
- `template` (optional): Template name (default: "test_case")
- `output` (required): Output file path

**Response**:
```json
{
  "message": "Successfully generated test cases to test_cases.md",
  "test_cases_count": 15,
  "output_file": "test_cases.md"
}
```

**Examples**:
```bash
# Generate from Jira issue
curl -X POST http://localhost:8080/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "jira_key": "PROJ-123",
    "output": "test_cases.md"
  }'

# Generate from GitHub issue with Confluence context
curl -X POST http://localhost:8080/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "gh_repo": "owner/repo",
    "gh_issue": "42",
    "confluence_id": "123456",
    "output": "comprehensive_tests.md"
  }'
```

---

### 4. Web Crawling

Crawl websites and create vector embeddings for context enhancement.

**Endpoint**: `POST /api/v1/crawl`

**Request Body**:
```json
{
  "url": "https://example.com",
  "provider": "openai",
  "persist_dir": "./data/chroma",
  "max_pages": 10,
  "same_domain": true
}
```

**Parameters**:
- `url` (required): Starting URL to crawl
- `provider` (optional): Embedding provider (openai, gemini, ollama, mistral) - default: "openai"
- `persist_dir` (optional): ChromaDB storage directory - default: "./data/chroma"
- `max_pages` (optional): Maximum pages to crawl - default: 10
- `same_domain` (optional): Restrict to same domain - default: true

**Response**:
```json
{
  "pages_processed": 10,
  "total_documents": 45,
  "embedding_dimension": 1536,
  "collection_name": "crawl_1734264600",
  "storage_location": "./data/chroma"
}
```

**Example**:
```bash
curl -X POST http://localhost:8080/api/v1/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://docs.example.com",
    "provider": "gemini",
    "max_pages": 20,
    "same_domain": true
  }'
```

---

### 5. Browser Testing - Health Check

Check if browser testing service is operational.

**Endpoint**: `GET /api/v1/browser-test/health`

**Response**:
```json
{
  "status": "healthy",
  "message": "Browser testing service is operational",
  "service": "browser-testing",
  "version": "1.0.0"
}
```

**Example**:
```bash
curl http://localhost:8080/api/v1/browser-test/health
```

---

### 6. Upload and Execute YAML Scenarios

Upload a YAML file containing test scenarios and optionally execute them immediately.

**Endpoint**: `POST /api/v1/browser-test/yaml/upload`

**Request** (multipart/form-data):
- `file`: YAML file upload
- `provider`: LLM provider (default: "openai")
- `headless`: Run in headless mode (default: true)
- `execute_immediately`: Execute after upload (default: false)

**Response**:
```json
{
  "success": true,
  "message": "Successfully uploaded and executed 3 scenarios. 2/3 tests passed",
  "test_suite_name": "E2E Test Suite",
  "scenarios_count": 3,
  "scenarios": [...],
  "execution_results": [...],
  "report": "# Test Report...",
  "summary": {
    "total_tests": 3,
    "passed_tests": 2,
    "failed_tests": 1,
    "success_rate": 66.7
  }
}
```

**Example**:
```bash
curl -X POST http://localhost:8080/api/v1/browser-test/yaml/upload \
  -F "file=@scenarios.yaml" \
  -F "provider=openai" \
  -F "headless=true" \
  -F "execute_immediately=true"
```

---

### 7. Execute YAML Scenarios from Content

Execute test scenarios from YAML content without file upload.

**Endpoint**: `POST /api/v1/browser-test/yaml/execute`

**Request Body**:
```json
{
  "yaml_content": "name: Test Suite\nscenarios:\n  - name: Test 1\n    requirement: Test login\n    url: https://example.com",
  "provider": "openai",
  "headless": true
}
```

**Parameters**:
- `yaml_content` (required): YAML content as string
- `provider` (optional): LLM provider - default: "openai"
- `headless` (optional): Run in headless mode - default: true

**Response**:
```json
{
  "success": true,
  "message": "Successfully executed 1 scenarios. 1/1 tests passed",
  "test_suite_name": "Test Suite",
  "scenarios_count": 1,
  "results": [...],
  "report": "# Test Report...",
  "summary": {
    "total_tests": 1,
    "passed_tests": 1,
    "failed_tests": 0,
    "success_rate": 100.0
  }
}
```

**Example**:
```bash
curl -X POST http://localhost:8080/api/v1/browser-test/yaml/execute \
  -H "Content-Type: application/json" \
  -d '{
    "yaml_content": "name: Login Test\nscenarios:\n  - name: User Login\n    requirement: Test user can login successfully\n    url: https://example.com/login",
    "provider": "gemini",
    "headless": false
  }'
```

---

### 8. Get YAML Template

Download a sample YAML template for browser test scenarios.

**Endpoint**: `GET /api/v1/browser-test/yaml/template`

**Response**:
```json
{
  "template_content": "name: \"Sample Test Suite\"\ndescription: \"Sample browser test scenarios\"\n...",
  "description": "Sample YAML template for browser test scenarios with comprehensive examples"
}
```

**Example**:
```bash
curl http://localhost:8080/api/v1/browser-test/yaml/template
```

---

### 9. API Testing from OpenAPI Specs

Test API endpoints from OpenAPI specification files.

**Endpoint**: `POST /api/v1/testapi`

**Request** (multipart/form-data):
- `base_url`: Base URL for API testing
- `spec_file`: Path to OpenAPI spec file (optional)
- `spec_upload`: Upload OpenAPI spec file (optional)
- `output`: Output file for test report

**Response**:
```json
{
  "message": "API testing completed successfully",
  "tests_executed": 25,
  "tests_passed": 23,
  "tests_failed": 2,
  "report_file": "api_test_report.md"
}
```

**Examples**:
```bash
# Test with spec file path
curl -X POST http://localhost:8080/api/v1/testapi \
  -F "base_url=https://petstore.swagger.io/v2" \
  -F "spec_file=./docs/specs/petstore.yaml" \
  -F "output=report.md"

# Test with file upload
curl -X POST http://localhost:8080/api/v1/testapi \
  -F "base_url=https://api.example.com" \
  -F "spec_upload=@openapi.yaml" \
  -F "output=api_test_results.md"
```

---

### 10. WebSocket Logs

Real-time log streaming for monitoring API operations.

**Endpoint**: `WebSocket /api/v1/ws/logs`

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8080/api/v1/ws/logs');

ws.onmessage = function(event) {
  const logData = JSON.parse(event.data);
  console.log(logData);
};
```

**Message Format**:
```json
{
  "timestamp": "2024-12-15T10:30:00Z",
  "level": "INFO",
  "logger": "friday.services.browser_agent",
  "message": "Starting browser test execution",
  "context": {
    "operation": "browser_test",
    "provider": "openai"
  }
}
```

## Error Handling

### Standard Error Response

All endpoints return errors in a consistent format:

```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-12-15T10:30:00Z"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Authentication required |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Invalid request body |
| 500 | Internal Server Error |
| 503 | Service Unavailable - External service down |

### Common Error Scenarios

#### 1. Authentication Errors
```json
{
  "detail": "Invalid Jira credentials",
  "error_code": "AUTH_ERROR"
}
```

#### 2. Validation Errors
```json
{
  "detail": "Either jira_key or gh_issue must be provided",
  "error_code": "VALIDATION_ERROR"
}
```

#### 3. Service Errors
```json
{
  "detail": "Browser testing service is not operational",
  "error_code": "SERVICE_ERROR"
}
```

## Authentication

The API uses environment variables for authentication with external services:

```bash
# Required for test generation
JIRA_URL=https://your-org.atlassian.net
JIRA_USERNAME=your-email
JIRA_API_TOKEN=your-jira-token

GITHUB_ACCESS_TOKEN=your-github-token
GITHUB_USERNAME=your-username

CONFLUENCE_URL=https://your-org.atlassian.net/wiki
CONFLUENCE_USERNAME=your-email
CONFLUENCE_API_TOKEN=your-confluence-token

# Required for AI features
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key
MISTRAL_API_KEY=your-mistral-key

# Required for web UI integration
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Rate Limiting

The API implements basic rate limiting:
- 100 requests per minute for browser testing endpoints
- 500 requests per minute for other endpoints
- WebSocket connections limited to 10 concurrent per client

## CORS Configuration

CORS is configured to allow requests from the web UI. Configure allowed origins via the `ALLOWED_ORIGINS` environment variable.

## Integration Examples

### Python Client

```python
import requests
import json

# Generate test cases
response = requests.post(
    "http://localhost:8080/api/v1/generate",
    json={
        "jira_key": "PROJ-123",
        "output": "tests.md"
    }
)
print(response.json())

# Run browser tests
with open("scenarios.yaml", "rb") as f:
    response = requests.post(
        "http://localhost:8080/api/v1/browser-test/yaml/upload",
        files={"file": f},
        data={
            "provider": "openai",
            "execute_immediately": "true"
        }
    )
print(response.json())
```

### JavaScript/TypeScript Client

```typescript
// Using fetch API
async function generateTests() {
  const response = await fetch('http://localhost:8080/api/v1/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      jira_key: 'PROJ-123',
      output: 'tests.md'
    })
  });
  
  return await response.json();
}

// WebSocket connection for logs
const ws = new WebSocket('ws://localhost:8080/api/v1/ws/logs');
ws.onmessage = (event) => {
  const logData = JSON.parse(event.data);
  console.log(`[${logData.level}] ${logData.message}`);
};
```

### cURL Examples

```bash
# Health check
curl http://localhost:8080/health

# Generate tests from Jira
curl -X POST http://localhost:8080/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"jira_key": "PROJ-123", "output": "tests.md"}'

# Crawl website
curl -X POST http://localhost:8080/api/v1/crawl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "max_pages": 5}'

# Upload and execute browser tests
curl -X POST http://localhost:8080/api/v1/browser-test/yaml/upload \
  -F "file=@test_scenarios.yaml" \
  -F "execute_immediately=true"
```

## Development and Testing

### Local Development

```bash
# Start API server in development mode
uv run uvicorn friday.api.app:app --reload --port 8080

# Run API tests
uv run pytest tests/test_api_integration.py -v

# Check API documentation
open http://localhost:8080/docs
```

### Docker Development

```bash
# Build API image
docker build -t friday-api .

# Run API container
docker run -p 8080:8080 -e OPENAI_API_KEY=your-key friday-api

# Run with docker-compose
docker-compose up friday-api
```

## Monitoring and Debugging

### Health Monitoring

```bash
# Basic health check
curl http://localhost:8080/health

# Browser testing service health
curl http://localhost:8080/api/v1/browser-test/health

# Check API version
curl http://localhost:8080/version
```

### Debug Logging

Set the log level for detailed debugging:

```bash
export LOG_LEVEL=DEBUG
uv run uvicorn friday.api.app:app --reload --port 8080
```

### Performance Monitoring

The API provides performance metrics through structured logging. Enable debug logging to see detailed timing information for each request.

---

**Last Updated**: December 2024  
**API Version**: 0.1.47

For the most up-to-date API documentation, visit `http://localhost:8080/docs` when the API server is running.