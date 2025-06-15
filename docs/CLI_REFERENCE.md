# Friday CLI Reference

Comprehensive documentation for the Friday CLI commands and usage.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Global Options](#global-options)
- [Commands](#commands)
  - [generate](#generate)
  - [crawl](#crawl)
  - [browser-test](#browser-test)
  - [webui](#webui)
  - [open](#open)
  - [version](#version)
  - [setup](#setup)
- [Configuration](#configuration)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

The Friday CLI is a powerful command-line interface for the AI-powered testing agent. It provides commands for test generation, web crawling, browser automation testing, and web UI management.

```bash
friday --help
```

## Installation

### Prerequisites

- Python 3.13+
- Node.js 22+ (for web UI)
- UV package manager

### Install from Source

```bash
git clone https://github.com/dipjyotimetia/friday.git
cd friday
uv sync
```

### Verify Installation

```bash
uv run friday --help
uv run friday version
```

## Global Options

All Friday commands support these global options:

- `--help` - Show help message and exit
- `--install-completion` - Install shell completion
- `--show-completion` - Show completion script

## Commands

### generate

Generate test cases from Jira or GitHub issues with optional Confluence context.

#### Syntax

```bash
friday generate [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--jira-key` | | TEXT | None | Jira issue key (e.g., PROJECT-123) |
| `--gh-issue` | | TEXT | None | GitHub issue number |
| `--gh-repo` | | TEXT | None | GitHub repository (owner/repo) |
| `--confluence-id` | | TEXT | None | Confluence page ID for additional context |
| `--template` | | TEXT | test_case | Prompt template key |
| `--output` | `-o` | PATH | test_cases.md | Output file path |

#### Examples

```bash
# Generate from Jira issue
friday generate --jira-key PROJECT-123 --output tests.md

# Generate from GitHub issue
friday generate --gh-repo owner/repo --gh-issue 42

# Generate with Confluence context
friday generate --jira-key PROJECT-123 --confluence-id 123456 --output comprehensive_tests.md

# Use custom template
friday generate --jira-key PROJECT-123 --template custom_template --output custom_tests.md
```

#### Requirements

- Either `--jira-key` or both `--gh-issue` and `--gh-repo` must be provided
- Requires appropriate environment variables for authentication (see [Configuration](#configuration))

---

### crawl

Crawl webpage content and store embeddings in ChromaDB for context enhancement.

#### Syntax

```bash
friday crawl URL [OPTIONS]
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `URL` | TEXT | Yes | Starting URL to crawl |

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--provider` | | TEXT | openai | Embedding provider (gemini, openai, ollama, mistral) |
| `--persist-dir` | | TEXT | ./data/chroma | ChromaDB persistence directory |
| `--max-pages` | | INTEGER | 10 | Maximum number of pages to crawl |
| `--same-domain` | | BOOLEAN | True | Only crawl pages from the same domain |

#### Examples

```bash
# Basic crawling
friday crawl https://example.com

# Crawl with custom settings
friday crawl https://example.com --provider gemini --max-pages 20

# Crawl with custom storage location
friday crawl https://docs.example.com --persist-dir ./embeddings --max-pages 50

# Allow cross-domain crawling
friday crawl https://example.com --same-domain false
```

#### Output

- Creates vector embeddings in ChromaDB
- Displays crawling statistics (pages processed, documents created)

---

### browser-test

Run AI-powered browser automation tests from YAML scenario files.

#### Syntax

```bash
friday browser-test YAML_FILE [OPTIONS]
```

#### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `YAML_FILE` | PATH | Yes | Path to YAML file containing test scenarios |

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--provider` | `-p` | TEXT | openai | LLM provider (openai, gemini, ollama, mistral) |
| `--headless` / `--no-headless` | | BOOLEAN | True | Run browser in headless mode |
| `--output` | `-o` | PATH | None | Output file for test report |

#### Examples

```bash
# Run tests from YAML file
friday browser-test scenarios.yaml

# Use custom provider and visible browser
friday browser-test tests.yaml --provider gemini --no-headless

# Generate test report
friday browser-test scenarios.yaml --output test_report.md

# Run with different provider
friday browser-test e2e_tests.yaml --provider ollama
```

#### YAML Format

Test scenarios must be defined in YAML format:

```yaml
name: "Test Suite Name"
description: "Test suite description"
version: "1.0"
provider: "openai"
headless: true
base_url: "https://example.com"
global_context: "Global test context"

scenarios:
  - name: "Test Name"
    requirement: "What to test"
    url: "https://example.com/page"
    test_type: "functional"  # functional, ui, integration, accessibility, performance
    context: "Additional context"
    take_screenshots: true
    steps:
      - "Step 1"
      - "Step 2"
    expected_outcomes:
      - "Expected result 1"
      - "Expected result 2"
    tags: ["tag1", "tag2"]
```

#### Download Template

```bash
# Use the web UI to download a sample YAML template
friday webui
# Then use the "Download Template" button in the browser testing section
```

---

### webui

Start the Friday Web UI for interactive testing and management.

#### Syntax

```bash
friday webui [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--port` | `-p` | INTEGER | 3000 | Port to run the web UI on |
| `--api-port` | | INTEGER | 8080 | Port for the API server |
| `--open` / `--no-open` | | BOOLEAN | True | Open browser automatically |
| `--api-only` | | BOOLEAN | False | Start only the API server |
| `--frontend-only` | | BOOLEAN | False | Start only the frontend |

#### Examples

```bash
# Start both API and frontend
friday webui

# Start on custom ports
friday webui --port 4000 --api-port 9000

# Start only API server
friday webui --api-only

# Start only frontend (API must be running separately)
friday webui --frontend-only

# Start without opening browser
friday webui --no-open
```

#### Services Started

When running `friday webui`, the following services are available:

- **Web UI**: `http://localhost:3000` (or custom port)
- **API Server**: `http://localhost:8080` (or custom port)
- **API Documentation**: `http://localhost:8080/docs`
- **WebSocket Logs**: `ws://localhost:8080/api/v1/ws/logs`

#### Shutdown

Press `Ctrl+C` to gracefully stop all services.

---

### open

Open the Friday Web UI in your default browser.

#### Syntax

```bash
friday open [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--port` | `-p` | INTEGER | 3000 | Port where the web UI is running |
| `--feature` | `-f` | TEXT | None | Open specific feature directly |

#### Available Features

- `browser` - Browser testing interface
- `generator` - Test case generator
- `crawler` - Web crawler interface
- `api` - API testing interface

#### Examples

```bash
# Open main web UI
friday open

# Open on custom port
friday open --port 4000

# Open directly to browser testing
friday open --feature browser

# Open directly to test generator
friday open --feature generator
```

#### Error Handling

If the web UI is not running, the command will:
1. Display an error message
2. Provide instructions to start the web UI
3. Exit with code 1

---

### version

Display the current version of Friday.

#### Syntax

```bash
friday version
```

#### Example

```bash
friday version
# Output: Friday v0.1.47
```

---

### setup

Interactive environment configuration wizard for setting up Friday.

#### Syntax

```bash
friday setup
```

#### Configuration Parameters

The setup wizard will prompt for:

| Parameter | Description | Required |
|-----------|-------------|----------|
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | No |
| `GOOGLE_CLOUD_REGION` | Google Cloud region | No (default: us-central1) |
| `GITHUB_ACCESS_TOKEN` | GitHub personal access token | Yes |
| `GITHUB_USERNAME` | GitHub username | Yes |
| `JIRA_URL` | Jira URL (e.g., https://org.atlassian.net) | Yes |
| `JIRA_USERNAME` | Jira username/email | Yes |
| `JIRA_API_TOKEN` | Jira API token | Yes |
| `CONFLUENCE_URL` | Confluence URL | Yes |
| `CONFLUENCE_USERNAME` | Confluence username/email | Yes |
| `CONFLUENCE_API_TOKEN` | Confluence API token | Yes |
| `OPENAI_API_KEY` | OpenAI API key for GPT models | Yes |
| `GOOGLE_API_KEY` | Google API key for Gemini models | No |
| `MISTRAL_API_KEY` | Mistral AI API key | No |

#### Example

```bash
friday setup
# Interactive prompts will guide you through configuration
```

#### Output

Creates or updates `.env` file with your configuration.

## Configuration

### Environment Variables

Friday requires several environment variables for proper operation. Use `friday setup` for interactive configuration, or manually create a `.env` file:

```bash
# LLM Providers
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
MISTRAL_API_KEY=your_mistral_key

# Google Cloud
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_REGION=us-central1

# GitHub Integration
GITHUB_ACCESS_TOKEN=your_github_token
GITHUB_USERNAME=your_username

# Jira Integration
JIRA_URL=https://your-org.atlassian.net
JIRA_USERNAME=your_email
JIRA_API_TOKEN=your_jira_token

# Confluence Integration
CONFLUENCE_URL=https://your-org.atlassian.net/wiki
CONFLUENCE_USERNAME=your_email
CONFLUENCE_API_TOKEN=your_confluence_token

# API Configuration (for web UI)
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Configuration Files

- `.env` - Environment variables
- `pyproject.toml` - Python dependencies and project configuration
- `app/package.json` - Frontend dependencies

## Examples

### Complete Workflow Examples

#### 1. Generate Tests from Jira with Context

```bash
# Step 1: Crawl documentation for context
friday crawl https://docs.myapp.com --max-pages 20

# Step 2: Generate test cases with Confluence context
friday generate --jira-key PROJ-123 --confluence-id 456789 --output comprehensive_tests.md
```

#### 2. Browser Testing Workflow

```bash
# Step 1: Start web UI to create/download YAML scenarios
friday webui

# Step 2: Run browser tests
friday browser-test my_scenarios.yaml --provider gemini --output test_report.md
```

#### 3. Development Workflow

```bash
# Start API and frontend for development
friday webui

# In another terminal, open specific feature
friday open --feature browser
```

### Integration Examples

#### CI/CD Pipeline

```yaml
# .github/workflows/friday.yml
name: Friday Test Generation
on: [push]
jobs:
  test-generation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Friday
        run: |
          pip install -r requirements.txt
          friday setup  # Configure via environment variables
      - name: Generate Tests
        run: friday generate --jira-key ${{ github.event.issue.number }} --output tests.md
```

#### Docker Integration

```bash
# Build and run with Friday CLI
docker build -t friday .
docker run -it friday friday --help
```

## Troubleshooting

### Common Issues

#### 1. Command Not Found

**Problem**: `friday: command not found`

**Solution**:
```bash
# Ensure UV is installed and Friday is available
uv --version
uv run friday --help

# Or activate the virtual environment
source .venv/bin/activate
friday --help
```

#### 2. API Connection Errors

**Problem**: Web UI commands fail with connection errors

**Solution**:
```bash
# Check if API server is running
curl http://localhost:8080/health

# Start API server
friday webui --api-only
```

#### 3. Authentication Errors

**Problem**: Jira/GitHub/Confluence authentication fails

**Solution**:
```bash
# Run setup to reconfigure credentials
friday setup

# Verify environment variables
echo $JIRA_API_TOKEN
echo $GITHUB_ACCESS_TOKEN
```

#### 4. Browser Testing Issues

**Problem**: Browser tests fail to run

**Solution**:
```bash
# Install Playwright browsers
uv run playwright install chromium --with-deps

# Test with visible browser for debugging
friday browser-test scenarios.yaml --no-headless
```

#### 5. YAML Parsing Errors

**Problem**: YAML scenario file parsing fails

**Solution**:
```bash
# Download a fresh template from web UI
friday webui
# Use "Download Template" button

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('scenarios.yaml'))"
```

### Debug Mode

For detailed logging, set the log level:

```bash
export LOG_LEVEL=DEBUG
friday browser-test scenarios.yaml
```

### Getting Help

- **GitHub Issues**: [Report bugs](https://github.com/dipjyotimetia/friday/issues)
- **Documentation**: [Browse docs](https://github.com/dipjyotimetia/friday/tree/main/docs)
- **Discussions**: [Ask questions](https://github.com/dipjyotimetia/friday/discussions)

### Version Compatibility

| Friday Version | Python Version | Node.js Version |
|---------------|----------------|-----------------|
| 0.1.47+ | 3.9+ | 18+ |
| 0.1.40-0.1.46 | 3.9+ | 16+ |

---

## Quick Reference Card

### Most Common Commands

```bash
# Setup (first time)
friday setup

# Start web UI
friday webui

# Generate tests from Jira
friday generate --jira-key PROJ-123 --output tests.md

# Run browser tests
friday browser-test scenarios.yaml

# Open web UI
friday open --feature browser
```

### Key Locations

- **Config**: `.env` file in project root
- **Templates**: Download from web UI
- **Outputs**: Current directory (unless specified)
- **Logs**: Console output (set LOG_LEVEL=DEBUG for verbose)

---

**Last Updated**: December 2024  
**Version**: 0.1.47

For the most up-to-date information, run `friday --help` or visit the [GitHub repository](https://github.com/dipjyotimetia/friday).