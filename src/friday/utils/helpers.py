import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def save_test_cases_as_markdown(test_cases: str, output_path: str) -> None:
    """Save generated test cases to a Markdown file.

    Args:
        test_cases: String containing generated test cases
        output_path: Path to save the markdown file
    """

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
