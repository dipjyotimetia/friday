from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from connectors.github_client import GitHubClient


@pytest.fixture
def github_client():
    """Fixture that creates a GitHubClient instance with mock token"""
    with patch("github.Github"):
        client = GitHubClient("fake-token")
        return client


@pytest.fixture
def mock_issue():
    """Fixture that creates a mock GitHub issue"""
    issue = Mock()
    issue.number = 1
    issue.title = "Test Issue"
    issue.body = "Test Body"
    issue.state = "open"
    issue.created_at = datetime(2023, 1, 1)
    issue.updated_at = datetime(2023, 1, 2)
    issue.closed_at = None
    issue.user.login = "testuser"
    issue.assignees = [Mock(login="assignee1")]
    issue.labels = [Mock(name="bug")]
    issue.milestone = Mock(title="v1.0")

    comment = Mock()
    comment.id = 1
    comment.user.login = "commenter"
    comment.body = "Test comment"
    comment.created_at = datetime(2023, 1, 1)
    comment.updated_at = datetime(2023, 1, 1)
    issue.get_comments.return_value = [comment]

    return issue


class TestGitHubClient:
    def test_init(self, github_client):
        """Test GitHubClient initialization"""
        assert github_client is not None
        assert hasattr(github_client, "github")

    def test_get_issue_details(self, github_client, mock_issue):
        """Test getting issue details"""
        # Setup
        github_client.github.get_repo.return_value.get_issue.return_value = mock_issue

        # Execute
        result = github_client.get_issue_details("owner/repo", 1)

        # Verify
        assert result["number"] == 1
        assert result["title"] == "Test Issue"
        assert result["state"] == "open"
        assert result["user"] == "testuser"
        assert result["assignees"] == ["assignee1"]
        assert result["labels"] == ["bug"]
        assert result["milestone"] == "v1.0"
        assert len(result["comments"]) == 1
        assert result["comments"][0]["user"] == "commenter"

    def test_get_milestone_issues(self, github_client):
        """Test getting milestone issues"""
        # Setup
        mock_milestone = Mock()
        mock_issues = [
            Mock(
                number=1,
                title="Issue 1",
                state="open",
                created_at=datetime(2023, 1, 1),
                closed_at=None,
                assignees=[Mock(login="user1")],
                labels=[Mock(name="bug")],
            )
        ]

        repo_mock = github_client.github.get_repo.return_value
        repo_mock.get_milestone.return_value = mock_milestone
        repo_mock.get_issues.return_value = mock_issues

        # Execute
        result = github_client.get_milestone_issues("owner/repo", 1)

        # Verify
        assert len(result) == 1
        assert result[0]["number"] == 1
        assert result[0]["title"] == "Issue 1"
        assert result[0]["assignees"] == ["user1"]

    def test_get_pr_diff(self, github_client):
        """Test getting PR diff information"""
        # Setup
        mock_file = Mock(
            filename="test.py",
            status="modified",
            additions=10,
            deletions=5,
            changes=15,
            patch="@@ -1,5 +1,10 @@",
        )

        mock_pr = Mock(
            number=1,
            title="Test PR",
            state="open",
            created_at=datetime(2023, 1, 1),
            updated_at=datetime(2023, 1, 2),
            merged_at=None,
            additions=10,
            deletions=5,
            changed_files=1,
            diff_url="https://github.com/diff",
        )
        mock_pr.get_files.return_value = [mock_file]

        github_client.github.get_repo.return_value.get_pull.return_value = mock_pr

        # Execute
        result = github_client.get_pr_diff("owner/repo", 1)

        # Verify
        assert result["number"] == 1
        assert result["title"] == "Test PR"
        assert len(result["files"]) == 1
        assert result["files"][0]["filename"] == "test.py"
        assert result["additions"] == 10
        assert result["deletions"] == 5

    def test_get_linked_issues_from_pr(self, github_client):
        """Test getting linked issues from PR"""
        # Setup
        mock_pr = Mock()
        mock_pr.body = "Fixes #1"
        mock_pr.get_comments.return_value = [Mock(body="Related to #2")]
        mock_pr.get_review_comments.return_value = []

        mock_issue = Mock(
            number=1,
            title="Linked Issue",
            state="open",
            created_at=datetime(2023, 1, 1),
            closed_at=None,
            labels=[Mock(name="bug")],
        )

        github_client.github.get_repo.return_value.get_pull.return_value = mock_pr
        github_client.github.get_repo.return_value.get_issue.return_value = mock_issue

        # Execute
        result = github_client.get_linked_issues_from_pr("owner/repo", 1)

        # Verify
        assert len(result) == 1
        assert result[0]["number"] == 1
        assert result[0]["title"] == "Linked Issue"

    def test_error_handling(self, github_client):
        """Test error handling"""
        # Setup
        github_client.github.get_repo.side_effect = Exception("Not found")

        # Verify
        with pytest.raises(Exception) as exc_info:
            github_client.get_issue_details("owner/repo", 1)
        assert "Error fetching issue details" in str(exc_info.value)
