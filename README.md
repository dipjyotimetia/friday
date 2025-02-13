# FRIDAY - AI Test Agent

An AI-powered test agent that uses Generative AI and LangChain to automatically create test cases from Jira/GitHub issues and execute API tests, for a streamlined testing experience.

[![License](https://img.shields.io/badge/license-MIT-orange.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <img src="docs/images/friday.png" alt="Friday Logo" width="700">
</p>

## ✨ Key Features

-   **AI-Powered Test Case Generation:** Leverage Google Gemini, OpenAI or mistral to generate test cases.
-   **Requirement Extraction:** Automatically extract requirements from Jira tickets or GitHub issues.
-   **Contextual Integration:** Incorporate relevant context from Confluence pages.
-   **LangChain Processing:** Utilize LangChain for advanced prompt engineering.
-   **Vectorized Storage:** Store and search documents efficiently using ChromaDB vectorization.
-   **Flexible Export:** Export test cases in JSON or Markdown format.
-   **Web Crawling:** Enhance context by creating embeddings using a web crawler.
-   **API Testing:** Execute API tests for comprehensive validation of functionalities.

## ⚙️ Setup

### Prerequisites

-   Python 3.12+
-   Gemini enabled or OpenAI API key 
-   Jira/GitHub and Confluence access credentials

### Installation

1.  **Install via Homebrew:**

    ```bash
    brew tap dipjyotimetia/friday
    brew install friday
    ```

2.  **Run setup:**

    ```bash
    friday setup
    ```

## ⚡️ Usage

### Generate Test Cases

```bash
# From Jira
friday generate --jira-key PROJ-123 --confluence-id 12345 -o test_cases.md

# From GitHub
friday generate --gh-issue 456 --gh-repo owner/repo --confluence-id 12345 -o test_cases.md
```

### Web Crawler

```bash
# Crawl single domain
friday crawl https://example.com --provider openai --persist-dir ./my_data/chroma --max-pages 5

# Crawl multiple domains
friday crawl https://example.com --provider openai --persist-dir ./my_data/chroma --max-pages 10 --same-domain false
```

### Command Reference

```bash
friday --help          # Show all commands
friday version         # Display version
friday generate --help # Show generation options
```

### Parameters

-   `--jira-key`: Jira issue key
-   `--confluence-id`: Confluence page ID (optional)
-   `--gh-issue`: GitHub issue number
-   `--gh-repo`: GitHub repository (format: owner/repo)
-   `--output`: Output file path (default: test_cases.md)
-   `--provider`: AI provider (gemini/openai)

## 🛠️ Development

1.  **Clone and setup:**

    ```bash
    git clone https://github.com/dipjyotimetia/friday.git
    cd friday
    chmod +x prerequisites.sh
    ./prerequisites.sh
    ```

2.  **Configure environment:**

    ```bash
    cp .env.example .env
    # Add your credentials to .env
    ```

3.  **Run Tests:**

    ```bash
    poetry run pytest tests/ -v
    ```

4.  **Format Code:**

    ```bash
    poetry run ruff format
    ```

5.  **Deploy to Google Cloud:**

    ```bash
    chmod +x deploy.sh
    PROJECT_ID="your-project" REGION="us-west1" ./deploy.sh
    ```

## 🐳 Development Container Setup

This project uses Visual Studio Code's Development Containers feature, providing a consistent development environment via Docker.

### Prerequisites

1.  [Visual Studio Code](https://code.visualstudio.com/)
2.  [Docker Desktop](https://www.docker.com/products/docker-desktop)
3.  [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Features

-   Python 3.12 with Poetry package management
-   Node.js 22 with npm
-   Docker-in-Docker support
-   Pre-configured VS Code extensions:
    -   Python and Pylance
    -   ESLint
    -   Prettier
    -   Docker
    -   Ruff (Python linter)

### Environment Variables

Required environment variables (set these before opening the dev container):

```sh
GOOGLE_CLOUD_PROJECT
GOOGLE_CLOUD_REGION
GITHUB_ACCESS_TOKEN
GITHUB_USERNAME
JIRA_URL
JIRA_USERNAME
JIRA_API_TOKEN
CONFLUENCE_URL
CONFLUENCE_USERNAME
CONFLUENCE_API_TOKEN
OPENAI_API_KEY
GOOGLE_API_KEY
```

### Services

The development environment includes three services:

-   `workspace`: Main development container
-   `api`: FastAPI backend service (port 8080)
-   app: Frontend application (port 3000)

### Getting Started

1.  Clone the repository
2.  Copy .env.example to .env and fill in your credentials
3.  Open in VS Code
4.  Click "Reopen in Container" when prompted
5.  The container will build and install all dependencies automatically

## 🗺️ Sequence Diagram

<details>
<summary>Expand Sequence diagram</summary>

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

</details>