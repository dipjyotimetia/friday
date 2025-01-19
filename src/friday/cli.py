import logging
from pathlib import Path
from typing import Optional

import typer
from rich import print

from friday.config.config import validate_config
from friday.connectors.confluence_client import ConfluenceConnector
from friday.connectors.github_client import GitHubConnector
from friday.connectors.jira_client import JiraConnector
from friday.services.embeddings import EmbeddingsService
from friday.services.parser import WebCrawler
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
        # for openai provider
        # test_generator = TestCaseGenerator(provider="openai")
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
def crawl(
    url: str = typer.Argument(..., help="URL to crawl"),
    provider: str = typer.Option(
        "vertex", help="Embedding provider (vertex or openai)"
    ),
    persist_dir: str = typer.Option(
        "./data/chroma", help="ChromaDB persistence directory"
    ),
    max_pages: int = typer.Option(10, help="Maximum number of pages to crawl"),
    same_domain: bool = typer.Option(
        True, help="Only crawl pages from the same domain"
    ),
):
    """Crawl webpage content and store embeddings in ChromaDB"""
    try:
        # Initialize crawler
        crawler = WebCrawler(max_pages=max_pages, same_domain_only=same_domain)

        # Crawl pages
        pages_data = crawler.crawl(url)

        # Initialize embeddings service
        embeddings_service = EmbeddingsService(
            provider=provider, persist_directory=persist_dir
        )

        # Create metadata and texts lists
        texts = []
        metadata = []

        for page in pages_data:
            texts.append(page["text"])
            metadata.append(
                {"source": page["url"], "type": "webpage", "title": page["title"]}
            )

        # Create database from texts
        embeddings_service.create_database(texts, metadata)

        # Get collection stats
        stats = embeddings_service.get_collection_stats()

        typer.echo(f"Successfully processed {len(pages_data)} pages")
        typer.echo(f"Total documents: {stats['total_documents']}")
        typer.echo(f"Embedding dimension: {stats['embedding_dimension']}")

    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
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
