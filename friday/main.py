import argparse
import json
import logging
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from friday.config.config import GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_REGION
from friday.connectors.confluence_client import ConfluenceConnector
from friday.connectors.jira_client import JiraConnector
from friday.services.prompt_builder import PromptBuilder
from friday.services.test_generator import TestCaseGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@contextmanager
def error_handler(operation: str):
    """Context manager for handling operations with proper error logging."""
    try:
        yield
    except Exception as e:
        logger.error(f"Failed during {operation}: {str(e)}")
        raise


def validate_config() -> bool:
    """Validate required configuration settings."""
    if not GOOGLE_CLOUD_PROJECT or not GOOGLE_CLOUD_REGION:
        logger.error("Missing required Google Cloud configuration")
        return False
    return True


def setup_args() -> argparse.Namespace:
    """Set up and parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate test cases from Jira and Confluence"
    )
    parser.add_argument("--issue-key", type=str, required=True, help="Jira issue key")
    parser.add_argument("--confluence-id", type=str, help="Confluence page ID")
    parser.add_argument(
        "--output", type=str, default="test_cases.json", help="Output file path"
    )
    return parser.parse_args()


def initialize_services() -> Tuple[JiraConnector, TestCaseGenerator, PromptBuilder]:
    """Initialize all required services and connectors."""
    logger.info("Initializing services...")

    jira = JiraConnector()
    # confluence = ConfluenceConnector()
    test_gen = TestCaseGenerator()
    prompt = PromptBuilder()

    return (jira, test_gen, prompt)


def save_test_cases(test_cases: Dict[str, Any], output_path: str) -> None:
    """Save generated test cases to a JSON file."""
    logger.info("Saving test cases...")
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(test_cases, f, indent=2, ensure_ascii=False)
    logger.info(f"Test cases saved to {output_file}")


def get_confluence_content(
    confluence: ConfluenceConnector, page_id: Optional[str]
) -> str:
    """Retrieve content from Confluence if page ID is provided."""
    if not page_id:
        return ""

    logger.info(f"Fetching Confluence page: {page_id}")
    return confluence.get_page_content(page_id)


def main() -> int:
    """Main execution function."""
    if not validate_config():
        return 1

    args = setup_args()

    try:
        jira, test_generator, prompt_builder = initialize_services()

        with error_handler("fetching Jira details"):
            logger.info(f"Fetching Jira issue: {args.issue_key}")
            issue_details = jira.get_issue_details(args.issue_key)
            acceptance_criteria = jira.extract_acceptance_criteria(args.issue_key)

        # additional_context = get_confluence_content(confluence, args.confluence_id)

        variables = {
            "story_description": issue_details["fields"]["description"],
            "acceptance_criteria": acceptance_criteria,
            # "confluence_content": additional_context,
            "unique_id": args.issue_key,
        }

        with error_handler("building prompt"):
            _ = prompt_builder.build_prompt(
                template_key="test_case", variables=variables
            )

        with error_handler("generating test cases"):
            logger.info("Generating test cases...")
            test_cases = test_generator.generate_test_cases(
                requirement=issue_details["fields"]["description"],
                acceptance_criteria=acceptance_criteria,
            )

        save_test_cases(test_cases, args.output)
        return 0

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
