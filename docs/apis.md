# API Documentation

FRIDAY provides a comprehensive REST API for test generation, web crawling, API testing, and browser automation.

## Server Configuration

### Local Development
```bash
uvicorn friday.api.app:app --host 0.0.0.0 --port 8080 --reload
```

### Production
```bash
uvicorn friday.api.app:app --host 0.0.0.0 --port 8080 --workers 4
```

### Health Check
```bash
curl http://localhost:8080/health
# Response: {"status": "healthy", "timestamp": "...", "version": "..."}
```


## Docker Run
```bash
# Build image
docker build -t friday-api .
# Interactive mode
docker run -p 8080:8080 friday-api
# Detached mode
docker run -d -p 8080:8080 friday-api
```

```bash
# Test with spec file path
curl -X POST "http://localhost:8000/api/v1/testapi" \
  -H "Content-Type: multipart/form-data" \
  -F "base_url=https://petstore.swagger.io/v2/pet" \
  -F "spec_file=./docs/specs/petstore.yaml" \
  -F "output=report.md"

# Test with file upload
curl -X POST "http://localhost:8000/api/v1/testapi" \
  -H "Content-Type: multipart/form-data" \
  -F "base_url=https://petstore.swagger.io/v2/pet" \
  -F "spec_upload=@./docs/specs/petstore.yaml" \
  -F "output=report.md"
```

# Get version
curl http://localhost:8000/version

# Generate test cases
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "jira_key": "PROJ-123",
    "confluence_id": "12345",
    "template": "test_case",
    "output": "test_cases.md"
  }'

# Crawl website
curl -X POST http://localhost:8080/api/v1/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "provider": "openai",
    "persist_dir": "./data/chroma",
    "max_pages": 5,
    "same_domain": true
  }'
```

## Browser Testing API ✅ Verified Working

The browser testing API provides AI-powered browser automation using natural language test descriptions.

### Upload YAML Test Suite
```bash
curl -X POST http://localhost:8080/api/v1/browser-test/yaml/upload \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test_suite.yaml",
    "content": "name: \"Test Suite\"\nscenarios:\n  - name: \"Page Load Test\"\n    requirement: \"Test page loads successfully\"\n    url: \"https://example.com\"\n    test_type: \"functional\""
  }'

# Response:
{
  "message": "Successfully uploaded test_suite.yaml",
  "file_id": "uuid-string",
  "parsed_suite": {
    "name": "Test Suite",
    "scenarios": [...]
  }
}
```

### Execute Browser Tests
```bash
curl -X POST http://localhost:8080/api/v1/browser-test/yaml/execute \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "uuid-from-upload",
    "provider": "openai",
    "headless": true,
    "output_format": "json"
  }'

# Response:
{
  "message": "Browser test execution started",
  "execution_id": "execution-uuid",
  "status": "running"
}
```

### Check Execution Status
```bash
curl http://localhost:8080/api/v1/browser-test/execution/execution-uuid

# Response:
{
  "status": "completed",
  "started_at": "2025-07-05T23:53:44.055637",
  "completed_at": "2025-07-05T23:54:32.123456",
  "report": {
    "total_tests": 2,
    "passed_tests": 2,
    "failed_tests": 0,
    "success_rate": 100.0,
    "results": [...]
  }
}
```

### Generate Test Report
```bash
curl -X POST http://localhost:8080/api/v1/browser-test/report/execution-uuid \
  -H "Content-Type: application/json" \
  -d '{"format": "markdown"}'

# Response:
{
  "report": "# Test Execution Report\n\n...",
  "format": "markdown"
}
```

### Browser Testing Health Check
```bash
curl http://localhost:8080/api/v1/browser-test/health

# Response:
{
  "status": "healthy",
  "browser_available": true,
  "playwright_version": "1.53.0",
  "browser_use_version": "0.4.4",
  "supported_providers": ["openai", "gemini", "ollama", "mistral"]
}
```

## WebSocket Endpoints ✅ Verified Working

Real-time communication for live updates and monitoring.

### General Application Logs
```bash
# WebSocket connection
ws://localhost:8080/api/v1/ws/logs

# Example message:
{
  "timestamp": "2025-07-05T23:53:44.055637",
  "level": "INFO",
  "message": "Test execution started",
  "source": "browser_agent"
}
```

### Browser Test Execution Logs
```bash
# Execution-specific WebSocket
ws://localhost:8080/api/v1/browser-test/ws/execution-uuid

# Example messages:
{
  "type": "progress",
  "message": "Starting test scenario: Page Load Test",
  "timestamp": "..."
}

{
  "type": "screenshot",
  "path": "/screenshots/test_001.png",
  "timestamp": "..."
}

{
  "type": "completion",
  "status": "success",
  "execution_time": 45.2,
  "timestamp": "..."
}
```

## Recent API Updates (2025-07-05)

### Fixed Issues
- ✅ **Frontend Integration**: Fixed API base URL configuration
- ✅ **WebSocket Connections**: Enhanced real-time monitoring
- ✅ **Error Handling**: Improved error responses and debugging
- ✅ **CORS Configuration**: Proper cross-origin support

### Verified Endpoints
All browser testing endpoints have been tested and confirmed working:
- ✅ YAML Upload: `POST /api/v1/browser-test/yaml/upload`
- ✅ Test Execution: `POST /api/v1/browser-test/yaml/execute`
- ✅ Status Check: `GET /api/v1/browser-test/execution/{id}`
- ✅ Report Generation: `POST /api/v1/browser-test/report/{id}`
- ✅ Health Check: `GET /api/v1/browser-test/health`
- ✅ WebSocket Logs: `WS /api/v1/ws/logs`
- ✅ WebSocket Browser: `WS /api/v1/browser-test/ws/{id}`