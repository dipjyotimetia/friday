import logging
from pathlib import Path
from typing import Optional

import typer
from rich import print

from friday.config.config import validate_config
from friday.connectors.confluence_client import ConfluenceConnector
from friday.connectors.github_client import GitHubConnector
from friday.connectors.jira_client import JiraConnector
from friday.services.prompt_builder import PromptBuilder
from friday.services.test_generator import TestCaseGenerator
from friday.utils.helpers import save_test_cases_as_markdown

app = typer.Typer(name="friday", help="AI-powered test case generator CLI")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.command()
def generate(
    jira_key: Optional[str] = typer.Option(None, "--jira-key", help="Jira issue key"),
    gh_issue: Optional[str] = typer.Option(
        None, "--gh-issue", help="GitHub issue number"
    ),
    gh_repo: Optional[str] = typer.Option(
        None, "--gh-repo", help="GitHub repository (owner/repo)"
    ),
    confluence_id: Optional[str] = typer.Option(
        None, "--confluence-id", help="Confluence page ID"
    ),
    template: str = typer.Option("test_case", "--template", help="Prompt template key"),
    output: Path = typer.Option(
        Path("test_cases.md"), "--output", "-o", help="Output file path"
    ),
):
    """Generate test cases from Jira or GitHub issues"""

    if not validate_config():
        raise typer.Exit(code=1)

    if gh_issue and not gh_repo:
        typer.echo("Error: --gh-repo is required when using --gh-issue", err=True)
        raise typer.Exit(code=1)

    if not jira_key and not gh_issue:
        typer.echo("Error: Either --jira-key or --gh-issue must be provided", err=True)
        raise typer.Exit(code=1)

    try:
        jira = JiraConnector()
        confluence = ConfluenceConnector()
        github = GitHubConnector()
        test_generator = TestCaseGenerator()
        prompt_builder = PromptBuilder()

        # Initialize test generator context
        test_generator.initialize_context(
            [
                "Test case generation guidelines",
                "Best practices for testing",
                "Common test scenarios",
            ]
        )

        # Get issue details
        if jira_key:
            issue_details = jira.get_issue_details(jira_key)
        else:
            issue_details = github.get_issue_details(gh_repo, int(gh_issue))

        # Get additional context from Confluence
        additional_context = ""
        if confluence_id:
            additional_context = confluence.get_page_content(confluence_id)

        variables = {
            "story_description": issue_details["fields"]["description"],
            "confluence_content": additional_context,
            "unique_id": jira_key or f"{gh_repo}#{gh_issue}",
        }

        # Build prompt and generate test cases
        _ = prompt_builder.build_prompt(template_key=template, variables=variables)
        test_cases = test_generator.generate_test_cases(
            requirement=issue_details["fields"]["description"]
        )

        # Save output
        save_test_cases_as_markdown(test_cases, str(output))
        print(f"[green]Successfully generated test cases to {output}[/green]")

    except Exception as e:
        logger.error(f"Error generating test cases: {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def version():
    """Show the version of Friday"""
    from importlib.metadata import version

    try:
        friday_version = version("friday")
        print(f"Friday v{friday_version}")
    except:  # noqa: E722
        print("Friday version unknown")


def main():
    app()


if __name__ == "__main__":
    main()
