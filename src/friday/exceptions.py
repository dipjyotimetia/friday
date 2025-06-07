"""Production-grade exception hierarchy for Friday application."""

from typing import Dict, Any, Optional
import traceback


class FridayError(Exception):
    """Base exception for Friday application with structured error context."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.context = context or {}
        self.cause = cause
        self.traceback_str = traceback.format_exc() if cause else None

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON serialization."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
        }


class ValidationError(FridayError):
    """Data validation and input validation errors."""

    def __init__(
        self, message: str, field: Optional[str] = None, value: Any = None, **kwargs
    ):
        context = kwargs.get("context", {})
        if field:
            context["field"] = field
        if value is not None:
            context["invalid_value"] = str(value)[:100]  # Truncate for safety
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class ConfigurationError(FridayError):
    """Configuration and environment setup errors."""

    pass


class ConnectorError(FridayError):
    """Errors related to external service connections."""

    def __init__(self, message: str, service: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if service:
            context["service"] = service
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class JiraError(ConnectorError):
    """JIRA-specific connection and API errors."""

    def __init__(self, message: str, issue_key: Optional[str] = None, **kwargs):
        kwargs["service"] = "jira"
        context = kwargs.get("context", {})
        if issue_key:
            context["issue_key"] = issue_key
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class GitHubError(ConnectorError):
    """GitHub-specific connection and API errors."""

    def __init__(self, message: str, repo: Optional[str] = None, **kwargs):
        kwargs["service"] = "github"
        context = kwargs.get("context", {})
        if repo:
            context["repository"] = repo
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class ConfluenceError(ConnectorError):
    """Confluence-specific connection and API errors."""

    def __init__(self, message: str, page_id: Optional[str] = None, **kwargs):
        kwargs["service"] = "confluence"
        context = kwargs.get("context", {})
        if page_id:
            context["page_id"] = page_id
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class LLMError(FridayError):
    """Large Language Model related errors."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        if provider:
            context["provider"] = provider
        if model:
            context["model"] = model
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class TestGenerationError(FridayError):
    """Test generation and processing errors."""

    def __init__(self, message: str, test_type: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if test_type:
            context["test_type"] = test_type
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class CrawlerError(FridayError):
    """Web crawling and content extraction errors."""

    def __init__(self, message: str, url: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if url:
            context["url"] = url
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class EmbeddingError(FridayError):
    """Vector embedding and similarity search errors."""

    def __init__(self, message: str, collection: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if collection:
            context["collection"] = collection
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class APIError(FridayError):
    """API-related errors for HTTP responses."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        endpoint: Optional[str] = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        if status_code:
            context["status_code"] = status_code
        if endpoint:
            context["endpoint"] = endpoint
        kwargs["context"] = context
        super().__init__(message, **kwargs)


class RateLimitError(APIError):
    """Rate limiting and throttling errors."""

    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        context = kwargs.get("context", {})
        if retry_after:
            context["retry_after_seconds"] = retry_after
        kwargs["context"] = context
        super().__init__(message, status_code=429, **kwargs)


class AuthenticationError(APIError):
    """Authentication and authorization errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class NotFoundError(APIError):
    """Resource not found errors."""

    def __init__(self, message: str, resource_id: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if resource_id:
            context["resource_id"] = resource_id
        kwargs["context"] = context
        super().__init__(message, status_code=404, **kwargs)
