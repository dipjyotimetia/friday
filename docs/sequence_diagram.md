# Mermaid Sequence Diagram for FRIDAY Project

This document contains the mermaid sequence diagram for the FRIDAY project. The diagram illustrates the interaction between different components of the system during the process of generating test cases from Jira and Confluence.

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
    participant JiraConnector
    participant ConfluenceConnector
    participant TestCaseGenerator
    participant PromptBuilder
    end

    Note over User,PromptBuilder: Test Case Generation Flow

    User->>+Main: Run main.py with issue-key<br/>and confluence-id
    
    rect rgba(67, 160, 71, 0.1)
        Main->>+JiraConnector: Fetch issue details
        JiraConnector-->>-Main: Return issue details
        Main->>+JiraConnector: Extract acceptance criteria
        JiraConnector-->>-Main: Return acceptance criteria
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

## Diagram Description

1. **User**: Initiates the process by running the main script with the required parameters.
2. **Main**: The main script orchestrates the entire process.
3. **JiraConnector**: Fetches issue details and extracts acceptance criteria from Jira.
4. **ConfluenceConnector**: Retrieves additional context from Confluence pages.
5. **PromptBuilder**: Constructs the prompt for generating test cases.
6. **TestCaseGenerator**: Uses the prompt to generate detailed test cases.
7. **User**: Receives the generated test cases saved in the specified output file.

The sequence diagram provides a visual representation of the interactions and data flow between the components, helping to understand the overall process and identify potential areas for improvement.