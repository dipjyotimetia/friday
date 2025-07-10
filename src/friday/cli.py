"""
Friday CLI Module

This module provides the command-line interface for Friday, an AI-powered testing agent.
It supports various commands for test case generation, web crawling, and environment setup.

Features:
- Test case generation from Jira or GitHub issues
- Web crawling with multiple LLM provider support
- Environment configuration management
- Version information
- Rich console output with colored formatting

Commands:
    generate: Generate test cases from Jira or GitHub issues
    crawl: Crawl webpage content and store embeddings
    version: Display Friday version
    setup: Configure environment parameters

Example:
    ```bash
    # Generate test cases from a Jira issue
    friday generate --jira-key PROJECT-123 --output tests.md

    # Crawl a website and store embeddings
    friday crawl https://example.com --provider openai --max-pages 20

    # Set up environment configuration
    friday setup
    ```
"""

import asyncio
import logging
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich import print

from friday.connectors.confluence_client import ConfluenceConnector
from friday.connectors.github_client import GitHubConnector
from friday.connectors.jira_client import JiraConnector
from friday.services.browser_agent import execute_yaml_file
from friday.services.crawler import WebCrawler
from friday.services.embeddings import EmbeddingsService
from friday.services.test_generator import TestCaseGenerator
from friday.utils.helpers import save_test_cases_as_markdown
from friday.version import __version__

app = typer.Typer(name="friday", help="AI-powered testing agent")
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
    """
    Generate test cases from Jira or GitHub issues.

    This command fetches issue details from either Jira or GitHub and generates
    test cases using AI. Additional context can be provided from Confluence pages.

    Args:
        jira_key: Jira issue key (e.g., PROJECT-123)
        gh_issue: GitHub issue number
        gh_repo: GitHub repository in owner/repo format
        confluence_id: Confluence page ID for additional context
        template: Template key for test case generation
        output: Output file path for generated test cases

    Example:
        ```bash
        # Generate from Jira issue
        friday generate --jira-key PROJECT-123 --output tests.md

        # Generate from GitHub issue with Confluence context
        friday generate --gh-repo owner/repo --gh-issue 42 --confluence-id 123456
        ```

    Raises:
        typer.Exit: If required parameters are missing or an error occurs
    """

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

        if jira_key:
            issue_details = jira.get_issue_details(jira_key)
        else:
            issue_details = github.get_issue_details(gh_repo, int(gh_issue))

        additional_context = ""
        if confluence_id:
            additional_context = confluence.get_page_content(confluence_id)

        test_generator.initialize_context(additional_context)

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
        "openai", help="Embedding provider (gemini, openai, ollama, mistral)"
    ),
    persist_dir: str = typer.Option(
        "./data/chroma", help="ChromaDB persistence directory"
    ),
    max_pages: int = typer.Option(10, help="Maximum number of pages to crawl"),
    same_domain: bool = typer.Option(
        True, help="Only crawl pages from the same domain"
    ),
):
    """
    Crawl webpage content and store embeddings in ChromaDB.

    This command crawls web pages starting from the provided URL and stores
    the extracted content as embeddings in a ChromaDB database.

    Args:
        url: Starting URL to crawl
        provider: LLM provider for generating embeddings
        persist_dir: Directory to store ChromaDB files
        max_pages: Maximum number of pages to crawl
        same_domain: Whether to restrict crawling to the same domain

    Example:
        ```bash
        # Crawl with default settings
        friday crawl https://example.com

        # Crawl with custom settings
        friday crawl https://example.com --provider gemini --max-pages 20 --persist-dir ./embeddings
        ```

    Raises:
        typer.Exit: If crawling or embedding generation fails
    """
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
    """
    Show the version of Friday.

    Displays the current version number of the Friday CLI tool.

    Example:
        ```bash
        friday version
        ```
    """
    print(f"Friday v{__version__}")


@app.command()
def setup():
    """
    Verify and configure required environment parameters.

    This command helps set up the required environment variables for Friday.
    It creates or updates a .env file with necessary configuration parameters.

    Configuration includes:
    - Google Cloud settings
    - GitHub credentials
    - Jira/Confluence credentials
    - API keys for various LLM providers

    Example:
        ```bash
        friday setup
        ```

    Note:
        Existing values in .env file will be preserved unless new values are provided.
    """
    required_params = {
        "GOOGLE_CLOUD_PROJECT": "Google Cloud project ID",
        "GOOGLE_CLOUD_REGION": "Google Cloud region (default: us-central1)",
        "GITHUB_ACCESS_TOKEN": "GitHub personal access token",
        "GITHUB_USERNAME": "GitHub username",
        "JIRA_URL": "Jira URL (e.g. https://your-org.atlassian.net)",
        "JIRA_USERNAME": "Jira username/email",
        "JIRA_API_TOKEN": "Jira API token",
        "CONFLUENCE_URL": "Confluence URL (e.g. https://your-org.atlassian.net/wiki)",
        "CONFLUENCE_USERNAME": "Confluence username/email",
        "CONFLUENCE_API_TOKEN": "Confluence API token",
        "OPENAI_API_KEY": "OpenAI API key",
        "MISTRAL_API_KEY": "Mistral AI API key",
    }

    env_file = Path(".env")
    if not env_file.exists():
        print("[yellow]No .env file found, creating new one...[/yellow]")
        env_file.touch()

    current_env = {}
    if env_file.stat().st_size > 0:
        with open(env_file) as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    current_env[key] = value

    new_env = {}
    print("\n[bold blue]Friday Environment Setup[/bold blue]")
    print(
        "Fill in the following required parameters (press Enter to skip/keep existing):\n"
    )

    for key, description in required_params.items():
        current = current_env.get(key, "")
        if current:
            prompt = f"{description} [current: {current}]: "
        else:
            prompt = f"{description}: "

        value = typer.prompt(prompt, default="", show_default=False)
        if value:
            new_env[key] = value
        elif current:
            new_env[key] = current

    # Write to .env file
    with open(env_file, "w") as f:
        for key, value in new_env.items():
            f.write(f"{key}={value}\n")

    print("\n[green]Environment configuration saved to .env file[/green]")
    print("[green]✓ Environment setup complete[/green]")


@app.command("browser-test")
def browser_test(
    yaml_file: Path = typer.Argument(..., help="YAML file containing test scenarios"),
    provider: str = typer.Option(
        "openai", help="LLM provider (openai, gemini, ollama, mistral)"
    ),
    headless: bool = typer.Option(True, "--headless/--no-headless", help="Run in headless mode"),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file for test report"
    ),
):
    """
    Execute browser tests from YAML file using AI-powered automation.
    
    This command loads test scenarios from a YAML file and executes them using
    natural language instructions with the browser-use library.
    
    Args:
        yaml_file: Path to YAML file containing test scenarios
        provider: LLM provider for AI-powered browser automation
        headless: Whether to run browser in headless mode
        output: Optional output file for test report
    
    Example:
        ```bash
        # Run tests with default settings
        friday browser-test scenarios.yaml
        
        # Run with custom provider and visible browser
        friday browser-test scenarios.yaml --provider gemini --no-headless
        
        # Save report to file
        friday browser-test scenarios.yaml --output report.json
        ```
    """
    try:
        if not yaml_file.exists():
            typer.echo(f"Error: YAML file not found: {yaml_file}", err=True)
            raise typer.Exit(code=1)
        
        print(f"[blue]Starting browser tests from {yaml_file}[/blue]")
        print(f"[blue]Provider: {provider}, Headless: {headless}[/blue]")
        
        # Run the async function
        report = asyncio.run(execute_yaml_file(
            yaml_file_path=str(yaml_file),
            provider=provider,
            headless=headless,
            output_file=str(output) if output else None,
        ))
        
        # Print summary
        print(f"[green]✓ Browser tests completed[/green]")
        print(f"[green]Total tests: {report.total_tests}[/green]")
        print(f"[green]Passed: {report.passed_tests}[/green]")
        print(f"[green]Failed: {report.failed_tests}[/green]")
        print(f"[green]Success rate: {report.success_rate:.1f}%[/green]")
        
        if output:
            print(f"[green]Report saved to: {output}[/green]")
        
    except Exception as e:
        logger.error(f"Browser test execution failed: {str(e)}")
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(code=1)


@app.command("webui")
def webui(
    api_only: bool = typer.Option(False, "--api-only", help="Start only API server"),
    frontend_only: bool = typer.Option(False, "--frontend-only", help="Start only frontend"),
    port: int = typer.Option(8080, "--port", help="API server port"),
    frontend_port: int = typer.Option(3000, "--frontend-port", help="Frontend port"),
):
    """
    Start the Friday Web UI (API server and/or frontend).
    
    This command starts the FastAPI server and/or Next.js frontend for
    the Friday web interface.
    
    Args:
        api_only: Start only the API server
        frontend_only: Start only the frontend
        port: API server port
        frontend_port: Frontend port
    
    Example:
        ```bash
        # Start both API and frontend
        friday webui
        
        # Start only API server
        friday webui --api-only
        
        # Start only frontend
        friday webui --frontend-only
        
        # Custom ports
        friday webui --port 8081 --frontend-port 3001
        ```
    """
    try:
        if api_only:
            print(f"[blue]Starting Friday API server on port {port}[/blue]")
            subprocess.run([
                sys.executable, "-m", "uvicorn", 
                "friday.api.app:app",
                "--host", "0.0.0.0",
                "--port", str(port),
                "--reload"
            ])
        elif frontend_only:
            print(f"[blue]Starting Friday frontend on port {frontend_port}[/blue]")
            subprocess.run([
                "npm", "run", "dev", "--", "--port", str(frontend_port)
            ], cwd="app")
        else:
            print(f"[blue]Starting Friday API server on port {port}[/blue]")
            print(f"[blue]Starting Friday frontend on port {frontend_port}[/blue]")
            print("[yellow]Starting both services... Press Ctrl+C to stop[/yellow]")
            
            # Start API server in background
            api_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", 
                "friday.api.app:app",
                "--host", "0.0.0.0",
                "--port", str(port),
                "--reload"
            ])
            
            # Start frontend
            try:
                subprocess.run([
                    "npm", "run", "dev", "--", "--port", str(frontend_port)
                ], cwd="app")
            except KeyboardInterrupt:
                print("\n[yellow]Stopping services...[/yellow]")
            finally:
                api_process.terminate()
                api_process.wait()
                
    except Exception as e:
        logger.error(f"Failed to start web UI: {str(e)}")
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(code=1)


@app.command("open")
def open_browser(
    feature: Optional[str] = typer.Option(None, "--feature", help="Open specific feature (browser, api, crawl)"),
    port: int = typer.Option(3000, "--port", help="Frontend port"),
):
    """
    Open Friday Web UI in default browser.
    
    This command opens the Friday web interface in your default browser.
    
    Args:
        feature: Specific feature to open (browser, api, crawl)
        port: Frontend port
    
    Example:
        ```bash
        # Open main UI
        friday open
        
        # Open browser testing feature
        friday open --feature browser
        
        # Open API testing feature
        friday open --feature api
        ```
    """
    try:
        import webbrowser
        
        base_url = f"http://localhost:{port}"
        
        if feature == "browser":
            url = f"{base_url}?tab=browser"
        elif feature == "api":
            url = f"{base_url}?tab=api"
        elif feature == "crawl":
            url = f"{base_url}?tab=crawl"
        else:
            url = base_url
        
        print(f"[blue]Opening Friday Web UI: {url}[/blue]")
        webbrowser.open(url)
        
    except Exception as e:
        logger.error(f"Failed to open browser: {str(e)}")
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(code=1)


def main():
    """
    Main entry point for the Friday CLI application.
    """
    app()


if __name__ == "__main__":
    main()
