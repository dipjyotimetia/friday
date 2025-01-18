import re
from typing import Dict, List

from github import Github
from retrying import retry

from friday.config.config import GITHUB_ACCESS_TOKEN


class GitHubConnector:
    def __init__(self):
        """
        Initialize GitHub client

        Args:
            access_token (str): GitHub personal access token
        """
        self.github = Github(GITHUB_ACCESS_TOKEN)

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def get_issue_details(self, repo_name: str, issue_number: int) -> Dict:
        """
        Get detailed information about a specific GitHub issue

        Args:
            repo_name (str): Repository name in format 'owner/repo'
            issue_number (int): Issue number

        Returns:
            Dict: Issue details including comments and labels
        """
        try:
            repo = self.github.get_repo(repo_name)
            issue = repo.get_issue(issue_number)

            # Extract all comments
            comments = [
                {
                    "id": comment.id,
                    "user": comment.user.login,
                    "body": comment.body,
                    "created_at": comment.created_at,
                    "updated_at": comment.updated_at,
                }
                for comment in issue.get_comments()
            ]

            # Extract all labels
            labels = [label.name for label in issue.labels]

            # Build response
            return {
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "state": issue.state,
                "created_at": issue.created_at,
                "updated_at": issue.updated_at,
                "closed_at": issue.closed_at,
                "user": issue.user.login,
                "assignees": [assignee.login for assignee in issue.assignees],
                "labels": labels,
                "comments": comments,
                "milestone": issue.milestone.title if issue.milestone else None,
            }
        except Exception as e:
            raise Exception(f"Error fetching issue details: {str(e)}")

    def get_milestone_issues(self, repo_name: str, milestone_number: int) -> List[Dict]:
        """
        Get all issues linked to a specific milestone

        Args:
            repo_name (str): Repository name in format 'owner/repo'
            milestone_number (int): Milestone number

        Returns:
            List[Dict]: List of issues in the milestone
        """
        try:
            repo = self.github.get_repo(repo_name)
            milestone = repo.get_milestone(milestone_number)

            # Get all issues in the milestone
            issues = repo.get_issues(milestone=milestone, state="all")

            return [
                {
                    "number": issue.number,
                    "title": issue.title,
                    "state": issue.state,
                    "created_at": issue.created_at,
                    "closed_at": issue.closed_at,
                    "assignees": [assignee.login for assignee in issue.assignees],
                    "labels": [label.name for label in issue.labels],
                }
                for issue in issues
            ]
        except Exception as e:
            raise Exception(f"Error fetching milestone issues: {str(e)}")

    def get_pr_diff(self, repo_name: str, pr_number: int) -> Dict:
        """
        Get the diff information from a pull request

        Args:
            repo_name (str): Repository name in format 'owner/repo'
            pr_number (int): Pull request number

        Returns:
            Dict: Pull request diff information
        """
        try:
            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            # Get files changed in PR
            files_changed = [
                {
                    "filename": file.filename,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes,
                    "patch": file.patch if hasattr(file, "patch") else None,
                }
                for file in pr.get_files()
            ]

            return {
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "created_at": pr.created_at,
                "updated_at": pr.updated_at,
                "merged_at": pr.merged_at,
                "additions": pr.additions,
                "deletions": pr.deletions,
                "changed_files": pr.changed_files,
                "files": files_changed,
                "diff_url": pr.diff_url,
            }
        except Exception as e:
            raise Exception(
                f"Error fetching PR diff for {repo_name} PR #{pr_number}: {str(e)}"
            )

    def get_linked_issues_from_pr(self, repo_name: str, pr_number: int) -> List[Dict]:
        """
        Get issues linked to a pull request through various methods:
        1. Issues mentioned in PR description with #
        2. Issues mentioned in PR comments
        3. Issues linked through GitHub's UI

        Args:
            repo_name (str): Repository name in format 'owner/repo'
            pr_number (int): Pull request number

        Returns:
            List[Dict]: List of linked issues
        """
        try:
            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            # Set to store unique issue numbers
            issue_numbers = set()

            # Helper function to extract issue numbers from text
            def extract_issue_numbers(text: str) -> List[int]:
                if not text:
                    return []
                # Match #number patterns
                matches = re.findall(r"#(\d+)", text)
                return [int(num) for num in matches]

            # Get issues from PR description
            issue_numbers.update(extract_issue_numbers(pr.body))

            # Get issues from PR comments
            for comment in pr.get_comments():
                issue_numbers.update(extract_issue_numbers(comment.body))

            # Get issues from PR review comments
            for review_comment in pr.get_review_comments():
                issue_numbers.update(extract_issue_numbers(review_comment.body))

            # Get linked issues through GitHub's UI
            # Note: This requires appropriate permissions
            try:
                linked_issues = pr.as_issue().get_timeline()
                for event in linked_issues:
                    if event.event == "cross-referenced":
                        if hasattr(event, "source") and event.source.type == "issue":
                            issue_numbers.add(event.source.issue.number)
            except Exception:
                pass  # Skip if timeline events are not accessible

            # Fetch details for all found issues
            linked_issues = []
            for issue_num in issue_numbers:
                try:
                    issue = repo.get_issue(issue_num)
                    linked_issues.append(
                        {
                            "number": issue.number,
                            "title": issue.title,
                            "state": issue.state,
                            "created_at": issue.created_at,
                            "closed_at": issue.closed_at,
                            "labels": [label.name for label in issue.labels],
                        }
                    )
                except Exception:
                    continue  # Skip if issue is not accessible

            return linked_issues
        except Exception as e:
            raise Exception(
                f"Error fetching linked issues for repo '{repo_name}' and PR '{pr_number}': {str(e)}"
            )
