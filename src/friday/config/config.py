"""Production-grade configuration management with validation and type safety."""

from typing import Optional
from pydantic import field_validator, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation and type safety."""

    # Environment settings
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # JIRA configuration (required)
    jira_url: str = Field(..., env="JIRA_URL")
    jira_username: str = Field(..., env="JIRA_USERNAME")
    jira_api_token: str = Field(..., env="JIRA_API_TOKEN")

    # Confluence configuration (optional)
    confluence_url: Optional[str] = Field(default=None, env="CONFLUENCE_URL")
    confluence_username: Optional[str] = Field(default=None, env="CONFLUENCE_USERNAME")
    confluence_api_token: Optional[str] = Field(
        default=None, env="CONFLUENCE_API_TOKEN"
    )

    # GitHub configuration (optional)
    github_username: Optional[str] = Field(default=None, env="GITHUB_USERNAME")
    github_access_token: Optional[str] = Field(default=None, env="GITHUB_ACCESS_TOKEN")

    # LLM API keys (at least one required)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    mistral_api_key: Optional[str] = Field(default=None, env="MISTRAL_API_KEY")

    # Google Cloud configuration
    google_cloud_project: Optional[str] = Field(
        default=None, env="GOOGLE_CLOUD_PROJECT"
    )
    google_cloud_region: str = Field(default="us-central1", env="GOOGLE_CLOUD_REGION")

    # API configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8080, env="API_PORT")
    allowed_origins: str = Field(default="http://localhost:3000", env="ALLOWED_ORIGINS")

    # Database configuration
    database_url: str = Field(default="sqlite:///./friday.db", env="DATABASE_URL")

    @field_validator("jira_url")
    @classmethod
    def validate_jira_url(cls, v):
        """Ensure JIRA URL is secure."""
        if not v.startswith("https://"):
            raise ValueError("JIRA URL must use HTTPS")
        return v.rstrip("/")

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
        providers = [self.openai_api_key, self.google_api_key, self.mistral_api_key]
        if not any(providers):
            raise ValueError("At least one LLM provider API key must be configured")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

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

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Validate LLM providers on startup
settings.validate_llm_providers()


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
MISTRAL_API_KEY = settings.mistral_api_key
