import os

from dotenv import load_dotenv

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")


def validate_config() -> bool:
    """Validate required configuration settings."""
    required_vars = {
        "JIRA_URL": JIRA_URL,
        "JIRA_USERNAME": JIRA_USERNAME,
        "JIRA_API_TOKEN": JIRA_API_TOKEN,
        "CONFLUENCE_URL": CONFLUENCE_URL,
        "CONFLUENCE_USERNAME": CONFLUENCE_USERNAME,
        "CONFLUENCE_API_TOKEN": CONFLUENCE_API_TOKEN,
        "GOOGLE_CLOUD_PROJECT": GOOGLE_CLOUD_PROJECT,
        "GITHUB_ACCESS_TOKEN": GITHUB_ACCESS_TOKEN,
    }

    missing = [k for k, v in required_vars.items() if not v]
    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}")
        return False
    return True
