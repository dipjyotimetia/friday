"""Tests for configuration management."""

import os

import pytest
from pydantic import ValidationError

from friday.config.config import Settings


class TestSettings:
    """Test Settings configuration class."""

    def test_default_values(self):
        """Test default configuration values."""
        # Set minimal required environment variables
        os.environ["JIRA_URL"] = "https://test.atlassian.net"
        os.environ["JIRA_USERNAME"] = "test@example.com"
        os.environ["JIRA_API_TOKEN"] = "test-token"

        settings = Settings()

        assert settings.environment == "development"
        assert settings.debug is False
        assert settings.log_level == "INFO"
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8080
        assert settings.google_cloud_region == "us-central1"
        assert settings.database_url == "sqlite:///./friday.db"

    def test_optional_jira_fields(self):
        """Test that JIRA fields are optional."""
        # Clear JIRA environment variables
        for key in ["JIRA_URL", "JIRA_USERNAME", "JIRA_API_TOKEN"]:
            if key in os.environ:
                del os.environ[key]

        # Should not raise an error since JIRA fields are optional
        settings = Settings()

        assert settings.jira_url is None
        assert settings.jira_username is None
        assert settings.jira_api_token is None
        assert settings.jira_enabled is False

    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        os.environ.update(
            {
                "JIRA_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
                "ENVIRONMENT": "production",
                "DEBUG": "true",
                "LOG_LEVEL": "DEBUG",
                "API_PORT": "9000",
            }
        )

        settings = Settings()

        assert settings.environment == "production"
        assert settings.debug is True
        assert settings.log_level == "DEBUG"
        assert settings.api_port == 9000

    def test_optional_fields(self):
        """Test optional configuration fields."""
        os.environ.update(
            {
                "JIRA_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
                "OPENAI_API_KEY": "sk-test-key",
                "GITHUB_USERNAME": "testuser",
                "CONFLUENCE_URL": "https://test.confluence.com",
            }
        )

        settings = Settings()

        assert settings.openai_api_key == "sk-test-key"
        assert settings.github_username == "testuser"
        assert settings.confluence_url == "https://test.confluence.com"
        assert settings.google_api_key is None  # Not set

    def test_type_validation(self):
        """Test type validation for configuration fields."""
        os.environ.update(
            {
                "JIRA_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
                "DEBUG": "invalid-boolean",
                "API_PORT": "not-a-number",
            }
        )

        with pytest.raises(ValidationError):
            Settings()

    def teardown_method(self):
        """Clean up environment variables after each test."""
        env_vars = [
            "JIRA_URL",
            "JIRA_USERNAME",
            "JIRA_API_TOKEN",
            "ENVIRONMENT",
            "DEBUG",
            "LOG_LEVEL",
            "API_PORT",
            "OPENAI_API_KEY",
            "GITHUB_USERNAME",
            "CONFLUENCE_URL",
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
