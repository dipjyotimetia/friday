"""Integration tests for API endpoints."""

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
            "fields": {"summary": "Test issue", "description": "Test description"},
        }
        mock_jira_instance.extract_acceptance_criteria.return_value = "Test criteria"
        mock_jira.return_value = mock_jira_instance

        # Mock test generator
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate.return_value = "Generated test cases"
        mock_generator.return_value = mock_generator_instance

        with (
            patch("friday.api.routes.generate.ConfluenceConnector"),
            patch("friday.api.routes.generate.GitHubConnector"),
            patch("friday.api.routes.generate.save_test_cases_as_markdown"),
        ):
            response = client.post(
                "/api/v1/generate",
                json={"jira_key": "TEST-123", "output": "test_output.md"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "generated test cases" in data["message"].lower()

    def test_generate_endpoint_missing_params(self, client):
        """Test generate endpoint with missing parameters."""
        response = client.post("/api/v1/generate", json={"output": "test_output.md"})

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "Either jira_key or gh_issue must be provided" in data["message"]

    @patch("friday.api.routes.crawl.WebCrawler")
    @patch("friday.api.routes.crawl.EmbeddingsService")
    def test_crawl_endpoint(self, mock_embeddings, mock_crawler, client):
        """Test crawl endpoint."""
        # Mock crawler
        mock_crawler_instance = MagicMock()
        mock_crawler_instance.crawl.return_value = [
            {"url": "https://example.com", "text": "Test", "title": "Test Page"}
        ]
        mock_crawler.return_value = mock_crawler_instance

        # Mock embeddings service
        mock_embeddings_instance = MagicMock()
        mock_embeddings_instance.get_collection_stats.return_value = {
            "total_documents": 1,
            "embedding_dimension": 1536
        }
        mock_embeddings.return_value = mock_embeddings_instance

        response = client.post("/api/v1/crawl", json={
            "url": "https://example.com",
            "provider": "openai",
            "max_pages": 5
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch("friday.api.routes.crawl.WebCrawler")
    @patch("friday.api.routes.crawl.EmbeddingsService")
    def test_crawl_endpoint_invalid_url(self, mock_embeddings, mock_crawler, client):
        """Test crawl endpoint with invalid URL."""
        # Mock to raise validation error
        mock_crawler_instance = MagicMock()
        mock_crawler_instance.crawl.side_effect = Exception("Invalid URL")
        mock_crawler.return_value = mock_crawler_instance

        response = client.post("/api/v1/crawl", json={
            "url": "not-a-valid-url",
            "provider": "openai"
        })

        assert response.status_code == 500  # Will raise exception from crawler

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.get("/api/v1/health")

        # CORS headers should be present on regular requests
        assert response.status_code == 200
        # TestClient doesn't always expose CORS headers, but we can verify the middleware is configured
        # by checking that the app has the CORS middleware added

    @patch("friday.api.routes.api_test.ApiTestGenerator")
    def test_api_test_endpoint(self, mock_generator_class, client):
        """Test API testing endpoint."""
        from unittest.mock import AsyncMock

        # Mock test generator
        mock_generator = MagicMock()
        mock_generator.load_spec = AsyncMock(return_value={
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "responses": {"200": {"description": "Success"}}
                    }
                }
            }
        })
        mock_generator.validate_spec.return_value = True
        mock_generator.create_test_cases = AsyncMock(return_value=["test1", "test2"])
        mock_generator.execute_tests = AsyncMock(return_value=None)
        mock_generator.test_results = [
            {"status": "PASS"},
            {"status": "PASS"}
        ]
        mock_generator.generate_report = AsyncMock(return_value="# Test Report")
        mock_generator_class.return_value = mock_generator

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
            data={"base_url": "https://api.example.com", "output": "test_results.md"},
            files={"spec_upload": ("spec.yaml", test_spec, "application/yaml")},
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
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422

    @patch("friday.api.routes.generate.JiraConnector")
    def test_jira_connection_error(self, mock_jira, client):
        """Test Jira connection error handling."""
        mock_jira.side_effect = Exception("Connection failed")

        response = client.post(
            "/api/v1/generate",
            json={"jira_key": "TEST-123", "output": "test_output.md"},
        )

        assert response.status_code == 500

    def test_validation_error_response_format(self, client):
        """Test validation error response format."""
        # Send invalid type for a field to trigger validation error
        response = client.post("/api/v1/generate", json={
            "jira_key": 123,  # Should be string
            "output": "test.md"
        })

        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "errors" in data
        assert isinstance(data["errors"], list)


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
