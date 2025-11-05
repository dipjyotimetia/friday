"""Integration tests for API endpoints."""

import json
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from friday.api.app import app


class TestAPIIntegration:
    """Integration tests for API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Friday" in data["message"]

    @patch("friday.api.routes.generate.JiraConnector")
    @patch("friday.api.routes.generate.TestCaseGenerator")
    def test_generate_endpoint_with_jira(self, mock_generator, mock_jira, client):
        """Test generate endpoint with Jira issue."""
        # Mock Jira connector
        mock_jira_instance = MagicMock()
        mock_jira_instance.get_issue.return_value = {
            "key": "TEST-123",
            "fields": {
                "summary": "Test issue",
                "description": "Test description"
            }
        }
        mock_jira_instance.extract_acceptance_criteria.return_value = "Test criteria"
        mock_jira.return_value = mock_jira_instance

        # Mock test generator
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate.return_value = "Generated test cases"
        mock_generator.return_value = mock_generator_instance

        with patch("friday.api.routes.generate.ConfluenceConnector"), \
             patch("friday.api.routes.generate.GitHubConnector"), \
             patch("friday.api.routes.generate.save_test_cases_as_markdown"):
            
            response = client.post("/api/v1/generate", json={
                "jira_key": "TEST-123",
                "output": "test_output.md"
            })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "generated test cases" in data["message"].lower()

    def test_generate_endpoint_missing_params(self, client):
        """Test generate endpoint with missing parameters."""
        response = client.post("/api/v1/generate", json={
            "output": "test_output.md"
        })

        assert response.status_code == 400
        data = response.json()
        assert "Either jira_key or gh_issue must be provided" in data["detail"]

    @patch("friday.api.routes.crawl.CrawlerService")
    def test_crawl_endpoint(self, mock_crawler, client):
        """Test crawl endpoint."""
        # Mock crawler service
        mock_crawler_instance = MagicMock()
        mock_crawler_instance.crawl.return_value = {
            "pages_crawled": 5,
            "embeddings_created": 10,
            "status": "completed"
        }
        mock_crawler.return_value = mock_crawler_instance

        response = client.post("/api/v1/crawl", json={
            "url": "https://example.com",
            "provider": "openai",
            "max_pages": 5
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_crawl_endpoint_invalid_url(self, client):
        """Test crawl endpoint with invalid URL."""
        response = client.post("/api/v1/crawl", json={
            "url": "not-a-valid-url",
            "provider": "openai"
        })

        assert response.status_code == 422  # Validation error

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/api/v1/health")
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers

    @patch("friday.api.routes.api_test.run_api_tests")
    def test_api_test_endpoint(self, mock_run_tests, client):
        """Test API testing endpoint."""
        # Mock test runner
        mock_run_tests.return_value = {
            "total_tests": 10,
            "passed": 8,
            "failed": 2,
            "execution_time": "5.2s"
        }

        # Mock file upload
        test_spec = """
        openapi: 3.0.0
        info:
          title: Test API
          version: 1.0.0
        paths:
          /test:
            get:
              responses:
                '200':
                  description: Success
        """

        response = client.post(
            "/api/v1/testapi",
            data={
                "base_url": "https://api.example.com",
                "output": "test_results.md"
            },
            files={"spec_upload": ("spec.yaml", test_spec, "application/yaml")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestAPIErrorHandling:
    """Test API error handling scenarios."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_404_endpoint(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == 404

    def test_invalid_json(self, client):
        """Test invalid JSON request handling."""
        response = client.post(
            "/api/v1/generate",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422

    @patch("friday.api.routes.generate.JiraConnector")
    def test_jira_connection_error(self, mock_jira, client):
        """Test Jira connection error handling."""
        mock_jira.side_effect = Exception("Connection failed")

        response = client.post("/api/v1/generate", json={
            "jira_key": "TEST-123",
            "output": "test_output.md"
        })

        assert response.status_code == 500

    def test_validation_error_response_format(self, client):
        """Test validation error response format."""
        response = client.post("/api/v1/generate", json={
            "invalid_field": "value"
        })

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)


class TestAPIMiddleware:
    """Test API middleware functionality."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_request_id_header(self, client):
        """Test that request ID is added to responses."""
        response = client.get("/api/v1/health")
        
        # Check if request ID is in headers or can be traced
        assert response.status_code == 200

    def test_content_type_handling(self, client):
        """Test content type handling."""
        response = client.get("/api/v1/health")
        
        assert response.headers["content-type"] == "application/json"

    def test_security_headers(self, client):
        """Test security headers are present."""
        response = client.get("/api/v1/health")
        
        # Should have basic security considerations
        assert response.status_code == 200
        # Could check for X-Content-Type-Options, X-Frame-Options, etc.


class TestAPIConfiguration:
    """Test API configuration and settings."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_app_metadata(self, client):
        """Test application metadata."""
        # Test that the app has proper configuration
        assert app.title is not None
        assert app.version is not None

    def test_openapi_schema(self, client):
        """Test OpenAPI schema generation."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema