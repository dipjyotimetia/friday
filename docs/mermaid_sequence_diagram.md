# Mermaid Sequence Diagram for FRIDAY Project

This document contains the mermaid sequence diagram for the FRIDAY project. The diagram illustrates the interaction between different components of the system during the process of generating test cases from Jira and Confluence.

```mermaid
sequenceDiagram
    participant User
    participant Main
    participant JiraConnector
    participant ConfluenceConnector
    participant TestCaseGenerator
    participant PromptBuilder

    User->>Main: Run main.py with issue-key and confluence-id
    Main->>JiraConnector: Fetch issue details
    JiraConnector-->>Main: Return issue details
    Main->>JiraConnector: Extract acceptance criteria
    JiraConnector-->>Main: Return acceptance criteria
    Main->>ConfluenceConnector: Fetch Confluence page content
    ConfluenceConnector-->>Main: Return page content
    Main->>PromptBuilder: Build prompt with details
    PromptBuilder-->>Main: Return prompt
    Main->>TestCaseGenerator: Generate test cases
    TestCaseGenerator-->>Main: Return test cases
    Main->>User: Save test cases to output file
```

## Diagram Description

1. **User**: Initiates the process by running the main script with the required parameters.
2. **Main**: The main script orchestrates the entire process.
3. **JiraConnector**: Fetches issue details and extracts acceptance criteria from Jira.
4. **ConfluenceConnector**: Retrieves additional context from Confluence pages.
5. **PromptBuilder**: Constructs the prompt for generating test cases.
6. **TestCaseGenerator**: Uses the prompt to generate detailed test cases.
7. **User**: Receives the generated test cases saved in the specified output file.

The sequence diagram provides a visual representation of the interactions and data flow between the components, helping to understand the overall process and identify potential areas for improvement.
