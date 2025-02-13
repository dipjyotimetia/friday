# FRIDAY - AI Test Case Generator Documentation

This document provides an in-depth overview of the FRIDAY project, detailing its architecture, core components, development workflow, and deployment guidelines.

## Table of Contents
1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
   - [Main Orchestration](#main-orchestration)
   - [Connectors](#connectors)
   - [Test Case Generation](#test-case-generation)
   - [User Interface](#user-interface)
4. [Setup and Installation](#setup-and-installation)
5. [Development Workflow](#development-workflow)
6. [API and Deployment](#api-and-deployment)
7. [External Dependencies](#external-dependencies)

---

## Introduction

FRIDAY is an AI-powered CLI and web application that automatically generates test cases from Jira or GitHub issues and extracts additional context from Confluence. It leverages Google Gemini, LangChain, and ChromaDB for document embeddings and similarity search.

For a quick overview, see the [README.md](README.md).

---

## Architecture Overview

The project uses a modular architecture with clear separation of concerns:
- **Orchestration:** A main runner coordinates the flow by fetching issue details, retrieving Confluence context, and triggering test case generation.
- **Connectors:** Abstractions for interacting with Jira, GitHub, and Confluence.
- **Test Case Generation:** Uses vector databases (via ChromaDB) to search context and a prompt-based engine for generating test cases.
- **User Interface:** A web interface and CLI for end users.

For a visual sequence, refer to the [Sequence Diagram](docs/sequence_diagram.md).

---

## Core Components

### Main Orchestration
- **Main Runner:** Coordinates the overall process. It receives input parameters (issue key, confluence id, etc.), calls connectors, invokes the prompt builder, and outputs generated test cases.
  - This orchestration is evident in the web client ([app/src/components/App.tsx](app/src/components/App.tsx)) and the CLI script ([pyproject.toml](pyproject.toml) defines the `friday` script).

### Connectors
- **IssueConnector:** Abstracts Jira and GitHub interactions.
  - Jira-specific operations are managed via the [`JiraConnector`](#) (see [docs/sample_issue.md](docs/sample_issue.md) for reference use cases).
  - GitHub interactions follow a similar pattern.
- **ConfluenceConnector:** Fetches additional content from Confluence pages used to enrich context for test case generation.

### Test Case Generation
- **TestCaseGenerator:** Responsible for generating test cases using AI.
  - The service is defined in [src/friday/services/test_generator.py](src/friday/services/test_generator.py). It first retrieves relevant context by performing a similarity search.
  - The context is gathered using the [`EmbeddingsService`](src/friday/services/embeddings.py) which:
    - Splits texts into documents.
    - Creates and queries the ChromaDB vector database.
  - These methods ensure that the generated test cases are accurate and context-aware.

### User Interface
- **Web Interface:** Built with React in [app/src/components/App.tsx](app/src/components/App.tsx), it provides forms for input (Jira Key, GitHub issue number, repo, etc.) and displays output.
- **Electron App:** In [app/electron/main.ts](app/electron/main.ts), an Electron window loads the web interface to provide a desktop application experience.

---

## Setup and Installation

1. **Clone and Setup:**
   ```sh
   git clone https://github.com/dipjyotimetia/friday.git
   cd friday
   chmod +x prerequisites.sh
   ./prerequisites.sh
   ```
2. **Environment Configuration:**
   - Create a `.env` file based on [.env.example](.env.example) and add your credentials.
3. **Install Dependencies:**
   ```sh
   poetry install
   ```
4. **Running Locally:**
   - For the API:
     ```sh
     uvicorn friday.api.app:app --reload
     ```
   - For the web interface, check the `package.json` inside 

app

.

---

## Development Workflow

- **Running Tests:**
  ```sh
  poetry run pytest tests/ -v
  ```
- **Code Formatting:**
  ```sh
  poetry run ruff format
  ```
- **Development Guidelines:**
  - Please follow the guidelines in 

CONTRIBUTING.md

 when submitting pull requests.
  - Ensure that any new functionality is covered with tests (tests/) and documentation is updated accordingly.

---

## API and Deployment

- **API Endpoints:** Detailed in 

apis.md

. They include:
  - `/generate`: For test case generation.
  - `/crawl`: For crawling websites for additional context.
- **Docker Deployment:**
  - Build image:
    ```sh
    docker build -t friday-api .
    ```
  - Run container:
    ```sh
    docker run -p 8080:8080 friday-api
    ```
- **GitHub Actions Integration:**
  - The CI pipeline and GitHub action for generating test cases are defined in 

action.yml

.

---

## External Dependencies

The project relies on several key external libraries. Some notable ones include:
- **LangChain & Langchain-OpenAI/Google:** For prompt engineering and AI integrations (pyproject.toml).
- **ChromaDB:** Employed for vectorized document storage and similarity search (integrated within 

EmbeddingsService

).
- **Google Cloud & Gemini AI:** For test case generation processing.
- **Atlassian and GitHub APIs:** For fetching issue details.

Check 

poetry.lock

 for a full list of dependencies and their versions.

---
