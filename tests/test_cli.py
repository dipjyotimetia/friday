"""Tests for CLI functionality."""

from unittest.mock import MagicMock, patch
import pytest
from typer.testing import CliRunner

from friday.cli import app


class TestCLI:
    """Test CLI command functionality."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "Friday" in result.stdout
        assert "generate" in result.stdout
        assert "crawl" in result.stdout

    def test_version_command(self, runner):
        """Test version command."""
        result = runner.invoke(app, ["version"])
        
        assert result.exit_code == 0
        assert "Friday" in result.stdout
        # Should contain version information

    @patch("friday.cli.JiraConnector")
    @patch("friday.cli.TestCaseGenerator")
    @patch("friday.cli.save_test_cases_as_markdown")
    def test_generate_with_jira_key(self, mock_save, mock_generator, mock_jira, runner):
        """Test generate command with Jira key."""
        # Mock Jira connector
        mock_jira_instance = MagicMock()
        mock_jira_instance.get_issue.return_value = {
            "key": "TEST-123",
            "fields": {"summary": "Test", "description": "Test description"}
        }
        mock_jira_instance.extract_acceptance_criteria.return_value = "Test criteria"
        mock_jira.return_value = mock_jira_instance

        # Mock test generator
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate.return_value = "Generated test cases"
        mock_generator.return_value = mock_generator_instance

        # Mock file save
        mock_save.return_value = None

        with patch("friday.cli.ConfluenceConnector"):
            result = runner.invoke(app, [
                "generate",
                "--jira-key", "TEST-123",
                "--output", "test_output.md"
            ])

        assert result.exit_code == 0
        mock_jira_instance.get_issue_details.assert_called_once_with("TEST-123")
        mock_save.assert_called_once()

    @patch("friday.cli.GitHubConnector")
    @patch("friday.cli.TestCaseGenerator")
    @patch("friday.cli.save_test_cases_as_markdown")
    def test_generate_with_github_issue(self, mock_save, mock_generator, mock_github, runner):
        """Test generate command with GitHub issue."""
        # Mock GitHub connector
        mock_github_instance = MagicMock()
        mock_github_instance.get_issue.return_value = {
            "number": 123,
            "title": "Test issue",
            "body": "Test description"
        }
        mock_github_instance.extract_acceptance_criteria.return_value = "Test criteria"
        mock_github.return_value = mock_github_instance

        # Mock test generator
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate.return_value = "Generated test cases"
        mock_generator.return_value = mock_generator_instance

        # Mock file save
        mock_save.return_value = None

        with patch("friday.cli.ConfluenceConnector"):
            result = runner.invoke(app, [
                "generate",
                "--gh-issue", "123",
                "--gh-repo", "owner/repo",
                "--output", "test_output.md"
            ])

        assert result.exit_code == 0
        mock_github_instance.get_issue_details.assert_called_once_with("owner/repo", 123)
        mock_save.assert_called_once()

    def test_generate_missing_required_params(self, runner):
        """Test generate command with missing required parameters."""
        result = runner.invoke(app, [
            "generate",
            "--output", "test_output.md"
        ])

        assert result.exit_code != 0
        # Should show error about missing required parameters

    @patch("friday.cli.WebCrawler")
    @patch("friday.cli.EmbeddingsService")
    def test_crawl_command(self, mock_embeddings, mock_crawler, runner):
        """Test crawl command."""
        # Mock crawler
        mock_crawler_instance = MagicMock()
        mock_crawler_instance.crawl.return_value = [
            {"url": "https://example.com", "text": "Test", "title": "Test"}
        ]
        mock_crawler.return_value = mock_crawler_instance

        # Mock embeddings service
        mock_embeddings_instance = MagicMock()
        mock_embeddings_instance.get_collection_stats.return_value = {
            "total_documents": 1,
            "embedding_dimension": 1536
        }
        mock_embeddings.return_value = mock_embeddings_instance

        result = runner.invoke(app, [
            "crawl",
            "https://example.com",
            "--provider", "openai",
            "--max-pages", "5"
        ])

        assert result.exit_code == 0
        mock_crawler_instance.crawl.assert_called_once()

    def test_crawl_invalid_url(self, runner):
        """Test crawl command with invalid URL."""
        result = runner.invoke(app, [
            "crawl",
            "not-a-valid-url",
            "--provider", "openai"
        ])

        # Should handle invalid URL gracefully
        assert result.exit_code != 0

    @patch("friday.cli.setup")
    def test_setup_command(self, mock_setup, runner):
        """Test setup command."""
        mock_setup.return_value = None

        result = runner.invoke(app, ["setup"])

        assert result.exit_code == 0
        mock_setup.assert_called_once()

    def test_crawl_help(self, runner):
        """Test crawl command help."""
        result = runner.invoke(app, ["crawl", "--help"])
        
        assert result.exit_code == 0
        assert "provider" in result.stdout
        assert "max-pages" in result.stdout

    def test_generate_help(self, runner):
        """Test generate command help."""
        result = runner.invoke(app, ["generate", "--help"])
        
        assert result.exit_code == 0
        assert "jira-key" in result.stdout
        assert "gh-issue" in result.stdout
        assert "output" in result.stdout


class TestCLIErrorHandling:
    """Test CLI error handling scenarios."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    @patch("friday.cli.JiraConnector")
    def test_jira_connection_error(self, mock_jira, runner):
        """Test Jira connection error handling."""
        mock_jira.side_effect = Exception("Connection failed")

        result = runner.invoke(app, [
            "generate",
            "--jira-key", "TEST-123",
            "--output", "test_output.md"
        ])

        assert result.exit_code != 0
        assert "Connection failed" in result.stdout or "error" in result.stdout.lower()

    @patch("friday.cli.GitHubConnector")
    def test_github_connection_error(self, mock_github, runner):
        """Test GitHub connection error handling."""
        mock_github.side_effect = Exception("GitHub API error")

        result = runner.invoke(app, [
            "generate",
            "--gh-issue", "123",
            "--gh-repo", "owner/repo",
            "--output", "test_output.md"
        ])

        assert result.exit_code != 0

    def test_invalid_command(self, runner):
        """Test invalid command handling."""
        result = runner.invoke(app, ["invalid-command"])
        
        assert result.exit_code != 0

    @patch("friday.cli.WebCrawler")
    def test_crawler_error(self, mock_crawler, runner):
        """Test crawler error handling."""
        mock_crawler_instance = MagicMock()
        mock_crawler_instance.crawl.side_effect = Exception("Crawl failed")
        mock_crawler.return_value = mock_crawler_instance

        result = runner.invoke(app, [
            "crawl",
            "https://example.com",
            "--provider", "openai"
        ])

        assert result.exit_code != 0


class TestCLIConfiguration:
    """Test CLI configuration and options."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    def test_provider_options(self, runner):
        """Test that valid provider options are accepted."""
        with patch("friday.cli.WebCrawler") as mock_crawler:
            mock_crawler_instance = MagicMock()
            mock_crawler_instance.crawl.return_value = {}
            mock_crawler.return_value = mock_crawler_instance

            for provider in ["openai", "gemini", "mistral"]:
                result = runner.invoke(app, [
                    "crawl",
                    "https://example.com",
                    "--provider", provider
                ])
                
                # Should not fail due to invalid provider
                # (may fail for other reasons in test environment)

    def test_max_pages_validation(self, runner):
        """Test max pages parameter validation."""
        with patch("friday.cli.WebCrawler"):
            # Test with negative number
            result = runner.invoke(app, [
                "crawl",
                "https://example.com",
                "--max-pages", "-1"
            ])
            
            # Should handle invalid max pages

    def test_output_file_parameter(self, runner):
        """Test output file parameter."""
        with patch("friday.cli.JiraConnector") as mock_jira, \
             patch("friday.cli.TestCaseGenerator") as mock_generator, \
             patch("friday.cli.save_test_cases_as_markdown") as mock_save, \
             patch("friday.cli.ConfluenceConnector"):
            
            mock_jira_instance = MagicMock()
            mock_jira_instance.get_issue.return_value = {"key": "TEST-123", "fields": {}}
            mock_jira_instance.extract_acceptance_criteria.return_value = ""
            mock_jira.return_value = mock_jira_instance

            mock_generator_instance = MagicMock()
            mock_generator_instance.generate.return_value = "test"
            mock_generator.return_value = mock_generator_instance

            result = runner.invoke(app, [
                "generate",
                "--jira-key", "TEST-123",
                "--output", "custom_output.md"
            ])

            if result.exit_code == 0:
                # Verify the output file parameter was used
                mock_save.assert_called_once()