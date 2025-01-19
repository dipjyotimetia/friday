# FRIDAY - AI Test Case Generator

<p align="center">
  <img src="docs/images/banner.svg" alt="Auto Test Case Generator Banner" width="1000">
</p>


A Python-based tool that uses Google's Vertex AI and LangChain to automatically generate test cases from Jira/Github and Confluence documentation.

## Features

- 🤖 Leverages Google Vertex AI for test case generation
- 📝 Pulls requirements from Jira tickets or github issue
- 📚 Extracts additional context from Confluence pages
- 🔄 Uses LangChain for prompt engineering and chain management
- 💾 Use ChromaDb for Embeddings, vector search, document storage
- { } Outputs structured test cases in JSON/MarkDown format

## Prerequisites

- Python 3.12
- Google Cloud Platform account with Vertex AI enabled
- Jira and Confluence access credentials

## Sequence diagram 

![Sequence Diagram](docs/images/sequence.png)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dipjyotimetia/friday.git
cd friday
```
2. Install dependencies:

```bash
chmod +x prerequisites.sh
./prerequisites.sh
```

3. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your credentials
```

## Usage
Run the tool with:
```bash
# Install the cli
brew tap dipjyotimetia/friday https://github.com/dipjyotimetia/FRIDAY 
brew install friday

# Run interactive setup
friday setup

# Generate test cases from a Jira issue
friday generate --jira-key PROJ-123 --confluence-id 12345 -o test_cases.md

# Generate test cases from a GitHub issue 
friday generate --gh-issue 456 --gh-repo owner/repo --confluence-id 12345 -o test_cases.md

# Crawl multiple pages from same domain
friday crawl https://example.com --provider vertex --persist-dir ./my_data/chroma --max-pages 5

# # Crawl across different domains
friday crawl https://example.com --provider vertex --persist-dir ./my_data/chroma --max-pages 10 --same-domain false

# Show version
friday version

# Show help
friday --help
friday generate --help
```

Parameters
* `--jira-key`: Jira issue key (required)
* `--confluence-id`: Confluence page ID (optional)
* `--gh-issue`: Github Issue key
* `--gh-repo`: Github User/Repo
* `--output`: Output file path for generated test cases (default: test_cases.json)

## Example other repo

```yaml
- uses: dipjyotimetia/friday@v1
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    confluence_id: "optional-confluence-id" 
```
## Development
Run tests:

```bash
poetry run pytest tests/ -v
```

Format Code:

```bash
poetry run ruff format
```

