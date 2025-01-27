# FRIDAY - AI Test Case Generator

<p align="center">
  <img src="docs/images/banner.svg" alt="Auto Test Case Generator Banner" width="1000">
</p>

An AI-powered test case generator that leverages Google Vertex AI and LangChain to automatically create test cases from Jira/GitHub issues and Confluence documentation.

## 🚀 Features

- Generate test cases using Google Vertex AI or OpenAI
- Extract requirements from Jira tickets or GitHub issues 
- Integrate context from Confluence pages
- Process data using LangChain's prompt engineering
- Store and search documents using ChromaDB vectorization
- Export test cases in JSON or Markdown format
- Create embeddings using web crawler for additional context

## 📋 Prerequisites

- Python 3.12+
- Google Cloud Platform account with Vertex AI enabled or OpenAI
- Jira/GitHub and Confluence access credentials

## 🔄 Sequence Diagram

```mermaid
%%{init: {
    'theme': 'base',
    'themeVariables': {
        'primaryColor': '#1a1a1a',
        'primaryTextColor': '#fff',
        'primaryBorderColor': '#4285f4',
        'lineColor': '#4285f4',
        'secondaryColor': '#2d2d2d',
        'tertiaryColor': '#2d2d2d',
        'actorBkg': '#4285f4',
        'actorTextColor': '#fff',
        'actorLineColor': '#4285f4',
        'signalColor': '#6c757d',
        'signalTextColor': '#fff',
        'labelBoxBkgColor': '#2d2d2d',
        'labelBoxBorderColor': '#4285f4',
        'labelTextColor': '#fff',
        'loopTextColor': '#fff',
        'noteBorderColor': '#43a047',
        'noteBkgColor': '#43a047',
        'noteTextColor': '#fff',
        'activationBorderColor': '#4285f4',
        'activationBkgColor': '#2d2d2d',
        'sequenceNumberColor': '#fff'
    }
}}%%

sequenceDiagram
    box rgba(66, 133, 244, 0.1) External Components
    participant User
    end
    
    box rgba(66, 133, 244, 0.1) Core System
    participant Main
    participant IssueConnector
    participant JiraConnector
    participant GitHubConnector
    participant ConfluenceConnector
    participant TestCaseGenerator
    participant PromptBuilder
    end

    Note over User,PromptBuilder: Test Case Generation Flow

    User->>+Main: Run main.py with issue-key/number<br/>and confluence-id
    
    alt Jira Issue
        rect rgba(67, 160, 71, 0.1)
            Main->>+IssueConnector: Get issue details
            IssueConnector->>+JiraConnector: Fetch Jira issue
            JiraConnector-->>-IssueConnector: Return issue details
            IssueConnector-->>-Main: Return issue details
            Main->>+IssueConnector: Extract acceptance criteria
            IssueConnector->>JiraConnector: Extract from Jira
            JiraConnector-->>IssueConnector: Return criteria
            IssueConnector-->>-Main: Return acceptance criteria
        end
    else GitHub Issue
        rect rgba(67, 160, 71, 0.1)
            Main->>+IssueConnector: Get issue details
            IssueConnector->>+GitHubConnector: Fetch GitHub issue
            GitHubConnector-->>-IssueConnector: Return issue details
            IssueConnector-->>-Main: Return issue details
            Main->>+IssueConnector: Extract acceptance criteria
            IssueConnector->>GitHubConnector: Extract from GitHub
            GitHubConnector-->>IssueConnector: Return criteria
            IssueConnector-->>-Main: Return acceptance criteria
        end
    end
    
    rect rgba(255, 152, 0, 0.1)
        Main->>+ConfluenceConnector: Fetch Confluence<br/>page content
        ConfluenceConnector-->>-Main: Return page content
    end
    
    rect rgba(66, 133, 244, 0.1)
        Main->>+PromptBuilder: Build prompt with details
        PromptBuilder-->>-Main: Return prompt
        Main->>+TestCaseGenerator: Generate test cases
        TestCaseGenerator-->>-Main: Return test cases
    end
    
    Main->>-User: Save test cases to<br/>output file

    Note over User,PromptBuilder: Process Complete
```

## ⚡️ Quick Start

1. Install via Homebrew:
```bash
brew tap dipjyotimetia/friday
brew install friday
```

2. Run setup:
```bash 
friday setup
```

3. Generate test cases:
```bash
# From Jira
friday generate --jira-key PROJ-123 --confluence-id 12345 -o test_cases.md

# From GitHub
friday generate --gh-issue 456 --gh-repo owner/repo --confluence-id 12345 -o test_cases.md
```

## 📖 Usage Options

### Web Crawler
```bash
# Crawl single domain
friday crawl https://example.com --provider vertex --persist-dir ./my_data/chroma --max-pages 5

# Crawl multiple domains
friday crawl https://example.com --provider vertex --persist-dir ./my_data/chroma --max-pages 10 --same-domain false
```

### Command Reference
```bash
friday --help          # Show all commands
friday version         # Display version
friday generate --help # Show generation options
```

### Parameters
- `--jira-key`: Jira issue key
- `--confluence-id`: Confluence page ID (optional)
- `--gh-issue`: GitHub issue number
- `--gh-repo`: GitHub repository (format: owner/repo)
- `--output`: Output file path (default: test_cases.json)

## 🔧 GitHub Action

```yaml
name: Friday Test Generator

on:
  pull_request:
    types: [opened, synchronize]
  workflow_dispatch:
    inputs:
      confluence_id:
        description: 'Confluence Page ID'
        required: true
      jira_id:
        description: 'Jira Issue ID'
        required: false

jobs:
  generate-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate Test Cases
        uses: dipjyotimetia/friday@main
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          confluence_url: ${{ secrets.CONFLUENCE_URL }}
          confluence_user: ${{ secrets.CONFLUENCE_USERNAME }}
          confluence_token: ${{ secrets.CONFLUENCE_API_TOKEN }}
          jira_url: ${{ secrets.JIRA_URL }}
          jira_user: ${{ secrets.JIRA_USERNAME }}
          jira_token: ${{ secrets.JIRA_API_TOKEN }}
          confluence_id: ${{ inputs.confluence_id || '12345' }}
          jira_id: ${{ inputs.jira_id || github.event.pull_request.number }}
          google_cloud_project: ${{ secrets.GOOGLE_CLOUD_PROJECT }}
          google_cloud_region: ${{ secrets.GOOGLE_CLOUD_REGION }}
          model_provider: 'vertex'
          persist_dir: './data/chroma'

      - name: Upload Test Cases
        uses: actions/upload-artifact@v4
        with:
          name: test-cases
          path: test_cases.md
```

## 💻 Development

1. Clone and setup:
```bash
git clone https://github.com/dipjyotimetia/friday.git
cd friday
chmod +x prerequisites.sh
./prerequisites.sh
```

2. Configure environment:
```bash
cp .env.example .env
# Add your credentials to .env
```

3. Run Tests:
```bash
# Run tests
poetry run pytest tests/ -v
```

4. Format Code:
```bash
# Format code
poetry run ruff format
```

6. Deploy to google cloud
```bash
chmod +x deploy.sh
PROJECT_ID="your-project" REGION="us-west1" ./deploy.sh
```