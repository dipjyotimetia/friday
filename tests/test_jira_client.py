"""Tests for Jira client functionality."""

from unittest.mock import MagicMock, patch

import pytest

from friday.connectors.jira_client import JiraConnector


class TestJiraConnector:
    """Test JiraConnector class functionality."""

    @patch("friday.connectors.jira_client.Jira")
    def test_init(self, mock_jira_class):
        """Test JiraConnector initialization."""
        mock_jira_instance = MagicMock()
        mock_jira_class.return_value = mock_jira_instance

        with patch.dict(
            "os.environ",
            {
                "JIRA_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
            },
        ):
            connector = JiraConnector()

            mock_jira_class.assert_called_once_with(
                url="https://test.atlassian.net",
                username="test@example.com",
                password="test-token",
            )
            assert connector.jira == mock_jira_instance

    @patch("friday.connectors.jira_client.Jira")
    def test_get_issue_success(self, mock_jira_class):
        """Test successful issue retrieval."""
        mock_jira_instance = MagicMock()
        mock_jira_class.return_value = mock_jira_instance

        # Mock issue data
        mock_issue = {
            "key": "TEST-123",
            "fields": {
                "summary": "Test issue",
                "description": "Test description",
                "status": {"name": "Open"},
                "priority": {"name": "High"},
                "issuetype": {"name": "Story"},
                "assignee": {"displayName": "Test User"},
                "reporter": {"displayName": "Reporter User"},
                "created": "2023-01-01T00:00:00.000+0000",
                "updated": "2023-01-02T00:00:00.000+0000",
            },
        }
        mock_jira_instance.issue.return_value = mock_issue

        with patch.dict(
            "os.environ",
            {
                "JIRA_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
            },
        ):
            connector = JiraConnector()
            result = connector.get_issue("TEST-123")

            mock_jira_instance.issue.assert_called_once_with("TEST-123")
            assert result == mock_issue

    @patch("friday.connectors.jira_client.Jira")
    def test_get_issue_not_found(self, mock_jira_class):
        """Test issue not found scenario."""
        mock_jira_instance = MagicMock()
        mock_jira_class.return_value = mock_jira_instance
        mock_jira_instance.issue.side_effect = Exception("Issue not found")

        with patch.dict(
            "os.environ",
            {
                "JIRA_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
            },
        ):
            connector = JiraConnector()

            with pytest.raises(Exception, match="Issue not found"):
                connector.get_issue("NONEXISTENT-123")

    @patch("friday.connectors.jira_client.Jira")
    def test_extract_acceptance_criteria(self, mock_jira_class):
        """Test acceptance criteria extraction."""
        mock_jira_instance = MagicMock()
        mock_jira_class.return_value = mock_jira_instance

        # Mock issue with acceptance criteria in description
        mock_issue = {
            "fields": {
                "description": """
                User Story: As a user, I want to login to the system
                
                Acceptance Criteria:
                1. User can enter username and password
                2. System validates credentials
                3. User is redirected to dashboard on success
                4. Error message shown on failure
                """
            }
        }

        with patch.dict(
            "os.environ",
            {
                "JIRA_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
            },
        ):
            connector = JiraConnector()
            criteria = connector.extract_acceptance_criteria(mock_issue)

            assert "User can enter username and password" in criteria
            assert "System validates credentials" in criteria
            assert "Error message shown on failure" in criteria

    @patch("friday.connectors.jira_client.Jira")
    def test_extract_acceptance_criteria_no_criteria(self, mock_jira_class):
        """Test acceptance criteria extraction when none exist."""
        mock_jira_instance = MagicMock()
        mock_jira_class.return_value = mock_jira_instance

        # Mock issue without acceptance criteria
        mock_issue = {
            "fields": {"description": "Simple description without acceptance criteria"}
        }

        with patch.dict(
            "os.environ",
            {
                "JIRA_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
            },
        ):
            connector = JiraConnector()
            criteria = connector.extract_acceptance_criteria(mock_issue)

            # Should return the description or empty string
            assert isinstance(criteria, str)

    @patch("friday.connectors.jira_client.Jira")
    def test_extract_acceptance_criteria_empty_description(self, mock_jira_class):
        """Test acceptance criteria extraction with empty description."""
        mock_jira_instance = MagicMock()
        mock_jira_class.return_value = mock_jira_instance

        # Mock issue with empty description
        mock_issue = {"fields": {"description": None}}

        with patch.dict(
            "os.environ",
            {
                "JIRA_URL": "https://test.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "test-token",
            },
        ):
            connector = JiraConnector()
            criteria = connector.extract_acceptance_criteria(mock_issue)

            # Should handle None description gracefully
            assert criteria == ""


class TestJiraConnectorConfiguration:
    """Test Jira connector configuration scenarios."""

    @patch("friday.connectors.jira_client.Jira")
    def test_missing_environment_variables(self, mock_jira_class):
        """Test behavior when environment variables are missing."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises((KeyError, ValueError)):
                JiraConnector()

    @patch("friday.connectors.jira_client.Jira")
    def test_connection_error(self, mock_jira_class):
        """Test connection error handling."""
        mock_jira_class.side_effect = Exception("Connection failed")

        with patch.dict(
            "os.environ",
            {
                "JIRA_URL": "https://invalid.atlassian.net",
                "JIRA_USERNAME": "test@example.com",
                "JIRA_API_TOKEN": "invalid-token",
            },
        ):
            with pytest.raises(Exception, match="Connection failed"):
                JiraConnector()
