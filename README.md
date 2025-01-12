# FRIDAY - AI Test Case Generator

<p align="center">
  <img src="docs/images/banner.svg" alt="Auto Test Case Generator Banner">
</p>


A Python-based tool that uses Google's Vertex AI and LangChain to automatically generate test cases from Jira and Confluence documentation.

## Features

- 🤖 Leverages Google Vertex AI for test case generation
- 📝 Pulls requirements from Jira tickets
- 📚 Extracts context from Confluence pages
- 🔄 Uses LangChain for prompt engineering and chain management
- 💾 Outputs structured test cases in JSON format

## Prerequisites

- Python 3.13+
- Google Cloud Platform account with Vertex AI enabled
- Jira and Confluence access credentials

## Sequence diagram 

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
poetry install
```

3. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your credentials
```

## Usage
Run the tool with:
```bash
poetry run python friday/main.py --issue-key PROJ-123 --confluence-id 12345 --output test_cases.json
```

Parameters
* `--issue-key`: Jira issue key (required)
* `--confluence-id`: Confluence page ID (optional)
* `--output`: Output file path for generated test cases (default: test_cases.json)

## Development
Run tests:

```bash
poetry run pytest
```

Format Code:

```bash
poetry run ruff format
```

