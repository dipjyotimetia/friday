# API

## Local Run
`uvicorn friday.api.app:app --host 0.0.0.0 --port 8080 --reload`


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
curl -X POST http://localhost:8000/api/v1/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "provider": "openai",
    "persist_dir": "./data/chroma",
    "max_pages": 5,
    "same_domain": true
  }'
```