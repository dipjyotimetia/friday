# API

`uvicorn friday.api.app:app --reload`

```json
# Get version
curl http://localhost:8000/version

# Generate test cases
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "jira_key": "PROJ-123",
    "confluence_id": "12345",
    "template": "test_case",
    "output": "test_cases.md"
  }'

# Crawl website
curl -X POST http://localhost:8000/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "provider": "vertex",
    "persist_dir": "./data/chroma",
    "max_pages": 5,
    "same_domain": true
  }'
```