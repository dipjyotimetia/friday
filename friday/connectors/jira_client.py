import logging
from typing import Dict, List

from atlassian import Jira
from retrying import retry

from friday.config.config import JIRA_API_TOKEN, JIRA_URL, JIRA_USERNAME

logger = logging.getLogger(__name__)


class JiraConnector:
    def __init__(self):
        self.client = Jira(
            url=JIRA_URL, username=JIRA_USERNAME, password=JIRA_API_TOKEN
        )

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def get_issue_details(
        self, issue_key: str, expand: str = "changelog,renderedFields"
    ) -> Dict:
        """Get detailed issue information"""
        try:
            return self.client.issue(issue_key, expand=expand)
        except Exception as e:
            logger.error(f"Error fetching issue {issue_key}: {str(e)}")
            raise

    def get_acceptance_criteria(self, issue_key: str) -> str:
        """Get acceptance criteria from custom field"""
        try:
            issue = self.get_issue_details(issue_key)
            return issue.get("fields", {}).get("customfield_10016", "")
        except Exception as e:
            logger.error(
                f"Error fetching acceptance criteria for {issue_key}: {str(e)}"
            )
            raise

    def extract_acceptance_criteria(self, issue_key: str) -> List[str]:
        """
        Extract and parse acceptance criteria from Jira issue
        Args:
            issue_key: Jira issue key (e.g. 'PROJ-123')
        Returns:
            List of acceptance criteria items
        """
        try:
            # Get raw AC text from custom field
            ac_text = self.get_acceptance_criteria(issue_key)
            if not ac_text:
                logger.warning(f"No acceptance criteria found for {issue_key}")
                return []

            # Split into lines and clean up
            criteria = []
            for line in ac_text.split("\n"):
                # Remove common bullet points and whitespace
                line = line.strip().lstrip("•-*").strip()
                if line:
                    criteria.append(line)

            return criteria

        except Exception as e:
            logger.error(
                f"Error extracting acceptance criteria from {issue_key}: {str(e)}"
            )
            raise

    def search_issues(
        self, jql_query: str, max_results: int = 50, fields: str = "*all"
    ) -> List[Dict]:
        """Search issues using JQL"""
        try:
            return self.client.jql(jql_query, limit=max_results, fields=fields)
        except Exception as e:
            logger.error(f"Error searching issues with JQL {jql_query}: {str(e)}")
            raise
