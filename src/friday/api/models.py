"""Standardized API response models and error handling."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime


class APIResponse(BaseModel):
    """Standard API response format for all endpoints."""

    success: bool = Field(..., description="Whether the request was successful")
    message: Optional[str] = Field(None, description="Human-readable message")
    data: Optional[Union[Dict[str, Any], List[Any], str, int, bool]] = Field(
        None, description="Response data payload"
    )
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Response timestamp"
    )

    @classmethod
    def success_response(
        cls,
        data: Any = None,
        message: str = "Request completed successfully",
        request_id: Optional[str] = None,
    ) -> "APIResponse":
        """Create a successful response."""
        return cls(success=True, message=message, data=data, request_id=request_id)

    @classmethod
    def error_response(
        cls,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> "APIResponse":
        """Create an error response."""
        error_data = {"error_code": error_code} if error_code else {}
        if details:
            error_data.update(details)

        return cls(
            success=False,
            message=message,
            data=error_data if error_data else None,
            request_id=request_id,
        )


class ErrorDetail(BaseModel):
    """Detailed error information."""

    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    field: Optional[str] = Field(None, description="Field that caused the error")
    context: Optional[Dict[str, Any]] = Field(
        None, description="Additional error context"
    )


class ValidationErrorResponse(BaseModel):
    """Response format for validation errors."""

    success: bool = Field(default=False)
    message: str = Field(default="Validation failed")
    errors: List[ErrorDetail] = Field(..., description="List of validation errors")
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Health check response format."""

    status: str = Field(..., description="Overall health status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, str] = Field(
        default_factory=dict, description="Service health status"
    )
    uptime_seconds: Optional[float] = Field(
        None, description="Application uptime in seconds"
    )


class TestGenerationRequest(BaseModel):
    """Request model for test generation."""

    jira_key: Optional[str] = Field(None, description="JIRA issue key")
    github_issue: Optional[str] = Field(None, description="GitHub issue URL or number")
    custom_requirements: Optional[str] = Field(
        None, description="Custom requirements text"
    )
    test_type: str = Field(default="api", description="Type of tests to generate")
    provider: str = Field(default="openai", description="LLM provider to use")
    include_confluence: bool = Field(
        default=False, description="Include Confluence context"
    )


class TestGenerationResponse(BaseModel):
    """Response model for test generation."""

    success: bool = Field(..., description="Whether generation was successful")
    test_content: Optional[str] = Field(None, description="Generated test content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Generation metadata")
    request_id: Optional[str] = Field(None, description="Request identifier")
    timestamp: datetime = Field(default_factory=datetime.now)


class CrawlRequest(BaseModel):
    """Request model for web crawling."""

    url: str = Field(..., description="URL to crawl")
    max_pages: int = Field(
        default=10, ge=1, le=100, description="Maximum pages to crawl"
    )
    provider: str = Field(
        default="openai", description="LLM provider for content analysis"
    )
    include_external: bool = Field(default=False, description="Include external links")


class CrawlResponse(BaseModel):
    """Response model for web crawling."""

    success: bool = Field(..., description="Whether crawling was successful")
    pages_crawled: int = Field(..., description="Number of pages successfully crawled")
    content_summary: Optional[str] = Field(
        None, description="Summary of crawled content"
    )
    embeddings_created: int = Field(
        default=0, description="Number of embeddings created"
    )
    request_id: Optional[str] = Field(None, description="Request identifier")
    timestamp: datetime = Field(default_factory=datetime.now)


class APITestRequest(BaseModel):
    """Request model for API testing."""

    spec_content: str = Field(..., description="OpenAPI specification content")
    base_url: Optional[str] = Field(None, description="Base URL for testing")
    auth_config: Optional[Dict[str, Any]] = Field(
        None, description="Authentication configuration"
    )


class APITestResponse(BaseModel):
    """Response model for API testing."""

    success: bool = Field(..., description="Whether testing was successful")
    test_results: Optional[Dict[str, Any]] = Field(
        None, description="Test execution results"
    )
    total_tests: int = Field(default=0, description="Total number of tests executed")
    passed_tests: int = Field(default=0, description="Number of tests that passed")
    failed_tests: int = Field(default=0, description="Number of tests that failed")
    request_id: Optional[str] = Field(None, description="Request identifier")
    timestamp: datetime = Field(default_factory=datetime.now)
