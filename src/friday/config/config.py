"""Production-grade configuration management with validation and type safety."""

from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation and type safety."""

    # Environment settings
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # JIRA configuration (optional)
    jira_url: Optional[str] = Field(default=None, alias="JIRA_URL")
    jira_username: Optional[str] = Field(default=None, alias="JIRA_USERNAME")
    jira_api_token: Optional[str] = Field(default=None, alias="JIRA_API_TOKEN")

    # Confluence configuration (optional)
    confluence_url: Optional[str] = Field(default=None, alias="CONFLUENCE_URL")
    confluence_username: Optional[str] = Field(
        default=None, alias="CONFLUENCE_USERNAME"
    )
    confluence_api_token: Optional[str] = Field(
        default=None, alias="CONFLUENCE_API_TOKEN"
    )

    # GitHub configuration (optional)
    github_username: Optional[str] = Field(default=None, alias="GITHUB_USERNAME")
    github_access_token: Optional[str] = Field(
        default=None, alias="GITHUB_ACCESS_TOKEN"
    )

    # LLM API keys (at least one required)
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")

    # Google Cloud configuration
    google_cloud_project: Optional[str] = Field(
        default=None, alias="GOOGLE_CLOUD_PROJECT"
    )
    google_cloud_region: str = Field(default="us-central1", alias="GOOGLE_CLOUD_REGION")

    # API configuration
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8080, alias="API_PORT")
    allowed_origins: str = Field(
        default="http://localhost:3000", alias="ALLOWED_ORIGINS"
    )

    # Database configuration
    database_url: str = Field(default="sqlite:///./friday.db", alias="DATABASE_URL")

    @field_validator("jira_url")
    @classmethod
    def validate_jira_url(cls, v):
        """Ensure JIRA URL is secure."""
        if v and not v.startswith("https://"):
            raise ValueError("JIRA URL must use HTTPS")
        return v.rstrip("/") if v else v

    @field_validator("confluence_url")
    @classmethod
    def validate_confluence_url(cls, v):
        """Ensure Confluence URL is secure if provided."""
        if v and not v.startswith("https://"):
            raise ValueError("Confluence URL must use HTTPS")
        return v.rstrip("/") if v else v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Ensure log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    @field_validator("allowed_origins")
    @classmethod
    def validate_origins(cls, v):
        """Parse allowed origins."""
        return [origin.strip() for origin in v.split(",")]

    def validate_llm_providers(self):
        """Ensure at least one LLM provider is configured."""
        providers = [self.openai_api_key, self.google_api_key, self.openai_api_key]
        if not any(providers):
            raise ValueError("At least one LLM provider API key must be configured")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def jira_enabled(self) -> bool:
        """Check if JIRA integration is enabled."""
        return all([self.jira_url, self.jira_username, self.jira_api_token])

    @property
    def confluence_enabled(self) -> bool:
        """Check if Confluence integration is enabled."""
        return all(
            [self.confluence_url, self.confluence_username, self.confluence_api_token]
        )

    @property
    def github_enabled(self) -> bool:
        """Check if GitHub integration is enabled."""
        return all([self.github_username, self.github_access_token])

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore"
    )


# Global settings instance
settings = Settings()  # type: ignore

# Validate LLM providers on startup (skip in test environment)
import os
if os.getenv("PYTEST_CURRENT_TEST") is None:
    try:
        settings.validate_llm_providers()
    except ValueError:
        # Allow startup without LLM keys for testing/development
        pass


# Legacy compatibility - to be removed in future versions
JIRA_URL = settings.jira_url
JIRA_USERNAME = settings.jira_username
JIRA_API_TOKEN = settings.jira_api_token
CONFLUENCE_URL = settings.confluence_url
CONFLUENCE_USERNAME = settings.confluence_username
CONFLUENCE_API_TOKEN = settings.confluence_api_token
GOOGLE_CLOUD_PROJECT = settings.google_cloud_project
GOOGLE_CLOUD_REGION = settings.google_cloud_region
GITHUB_USERNAME = settings.github_username
GITHUB_ACCESS_TOKEN = settings.github_access_token
GOOGLE_API_KEY = settings.google_api_key
OPENAI_API_KEY = settings.openai_api_key
