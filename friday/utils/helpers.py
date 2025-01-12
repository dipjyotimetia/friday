import json
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List

from friday.models.test_case import TestCase, TestPriority, TestStep, TestType

logger = logging.getLogger(__name__)


def generate_test_id(prefix: str = "TC") -> str:
    """Generate a unique test case ID"""
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}-{unique_id}"


def parse_llm_response(response: str) -> List[Dict]:
    """Parse LLM generated test cases into structured format"""
    test_cases = []
    current_test = {}

    for line in response.split("\n"):
        line = line.strip()
        if line.startswith("Test ID:"):
            if current_test:
                test_cases.append(current_test)
            current_test = {"id": line.split("Test ID:")[1].strip()}
        elif line.startswith("Title:"):
            current_test["title"] = line.split("Title:")[1].strip()
        elif line.startswith("Preconditions:"):
            current_test["preconditions"] = [
                p.strip() for p in line.split("Preconditions:")[1].strip().split(",")
            ]
        elif line.startswith("Test Type:"):
            test_type = line.split("Test Type:")[1].strip().lower()
            current_test["test_type"] = test_type
        elif line.startswith("Priority:"):
            priority = line.split("Priority:")[1].strip().lower()
            current_test["priority"] = priority

    if current_test:
        test_cases.append(current_test)

    return test_cases


def create_test_case_from_dict(data: Dict) -> TestCase:
    """Create TestCase object from dictionary"""
    return TestCase(
        id=data.get("id", generate_test_id()),
        title=data["title"],
        description=data.get("description", ""),
        preconditions=data.get("preconditions", []),
        steps=[TestStep(**step) for step in data.get("steps", [])],
        priority=TestPriority(data.get("priority", "medium")),
        test_type=TestType(data.get("test_type", "functional")),
        jira_key=data.get("jira_key"),
        confluence_id=data.get("confluence_id"),
    )


def validate_test_case(test_case: TestCase) -> List[str]:
    """Validate test case data"""
    errors = []

    if not test_case.title:
        errors.append("Test case title is required")
    if not test_case.steps:
        errors.append("Test case must have at least one step")
    if len(test_case.title) > 200:
        errors.append("Test case title exceeds maximum length of 200 characters")

    return errors


def save_test_cases(test_cases: Dict[str, Any], output_path: str) -> None:
    """Save generated test cases to a JSON file."""
    logger.info("Saving test cases...")
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(test_cases, f, indent=2, ensure_ascii=False)
    logger.info(f"Test cases saved to {output_file}")


def save_test_cases_as_markdown(test_cases: str, output_path: str) -> None:
    """Save generated test cases to a Markdown file.

    Args:
        test_cases: String containing generated test cases
        output_path: Path to save the markdown file
    """
    from pathlib import Path

    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Add markdown header
    markdown_content = "# Generated Test Cases\n\n"
    markdown_content += test_cases

    # Write to file
    with open(output_file.with_suffix(".md"), "w", encoding="utf-8") as f:
        f.write(markdown_content)


def format_issue_data(issue):
    """Format the issue data for display."""
    return {
        "title": issue.title,
        "body": issue.body,
        "comments": issue.get_comments(),
        "labels": [label.name for label in issue.labels],
    }


def handle_api_response(response):
    """Handle the API response and return the JSON data."""
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
