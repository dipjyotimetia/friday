# Friday Architecture Diagrams

This document provides visual representations of Friday's architecture, workflows, and component interactions.

## System Overview

```mermaid
graph TB
    subgraph "User Interfaces"
        CLI[Friday CLI]
        WEB[Web Application]
        API_CLIENT[External API Clients]
    end
    
    subgraph "Core API Layer"
        API[FastAPI Server<br/>Port 8080]
        WS[WebSocket Server<br/>Real-time Logs]
    end
    
    subgraph "Service Layer"
        TG[Test Generator]
        BA[Browser Agent]
        WC[Web Crawler]
        ES[Embeddings Service]
        YS[YAML Scenarios]
    end
    
    subgraph "External Integrations"
        JIRA[Jira API]
        GH[GitHub API]
        CONF[Confluence API]
    end
    
    subgraph "AI/LLM Providers"
        OPENAI[OpenAI]
        GEMINI[Google Gemini]
        MISTRAL[Mistral AI]
        OLLAMA[Ollama]
    end
    
    subgraph "Storage & Data"
        CHROMA[ChromaDB<br/>Vector Store]
        SQLITE[SQLite<br/>LLM Cache]
        FS[File System<br/>Reports & Logs]
    end
    
    CLI --> API
    WEB --> API
    API_CLIENT --> API
    API --> WS
    
    API --> TG
    API --> BA
    API --> WC
    
    TG --> JIRA
    TG --> GH
    TG --> CONF
    
    TG --> OPENAI
    BA --> OPENAI
    WC --> GEMINI
    ES --> MISTRAL
    
    WC --> ES
    ES --> CHROMA
    TG --> SQLITE
    BA --> FS
    
    BA --> YS
    YS --> BA
```

## Component Architecture

```mermaid
graph TB
    subgraph "Frontend Architecture"
        subgraph "Next.js App Router"
            LAYOUT[Root Layout]
            MAIN[Main Page]
            API_ROUTES[API Routes]
        end
        
        subgraph "Feature Components"
            BT[Browser Tester]
            TGen[Test Generator]
            WCraw[Web Crawler]
            AT[API Tester]
        end
        
        subgraph "Shared Components"
            FU[File Uploader]
            LV[Log Viewer]
            OV[Output Viewer]
            RD[Result Display]
        end
        
        subgraph "Hooks & Services"
            API_HOOK[useApi]
            WS_HOOK[useWebSocket]
            FILE_HOOK[useFileUpload]
            API_SERVICE[API Service]
        end
    end
    
    subgraph "Backend Architecture"
        subgraph "API Layer"
            ROUTES[FastAPI Routes]
            MIDDLEWARE[Middleware]
            SCHEMAS[Pydantic Schemas]
        end
        
        subgraph "Business Logic"
            SERVICES[Service Classes]
            CONNECTORS[External Connectors]
            AGENTS[AI Agents]
        end
        
        subgraph "Data Layer"
            DB_SERVICES[Database Services]
            FILE_HANDLERS[File Handlers]
            CACHE[Cache Layer]
        end
    end
    
    LAYOUT --> MAIN
    MAIN --> BT
    MAIN --> TGen
    MAIN --> WCraw
    MAIN --> AT
    
    BT --> FU
    BT --> LV
    TGen --> OV
    AT --> RD
    
    BT --> API_HOOK
    LV --> WS_HOOK
    FU --> FILE_HOOK
    API_HOOK --> API_SERVICE
    
    API_SERVICE --> ROUTES
    ROUTES --> MIDDLEWARE
    ROUTES --> SCHEMAS
    SCHEMAS --> SERVICES
    SERVICES --> CONNECTORS
    SERVICES --> AGENTS
    AGENTS --> DB_SERVICES
```

## Test Generation Workflow

```mermaid
sequenceDiagram
    participant User
    participant CLI/WebUI
    participant API
    participant TestGenerator
    participant JiraConnector
    participant ConfluenceConnector
    participant LLM
    participant FileSystem
    
    User->>CLI/WebUI: Request test generation
    CLI/WebUI->>API: POST /api/v1/generate
    API->>TestGenerator: Initialize generator
    
    alt Jira Issue
        TestGenerator->>JiraConnector: Get issue details
        JiraConnector->>TestGenerator: Return issue data
    else GitHub Issue
        TestGenerator->>GH: Get issue details
        GH->>TestGenerator: Return issue data
    end
    
    opt Additional Context
        TestGenerator->>ConfluenceConnector: Get page content
        ConfluenceConnector->>TestGenerator: Return context
    end
    
    TestGenerator->>LLM: Generate test cases
    LLM->>TestGenerator: Return generated tests
    TestGenerator->>FileSystem: Save test cases
    TestGenerator->>API: Return success response
    API->>CLI/WebUI: Return result
    CLI/WebUI->>User: Display success message
```

## Browser Testing Workflow

```mermaid
sequenceDiagram
    participant User
    participant WebUI
    participant API
    participant BrowserAgent
    participant YAMLParser
    participant Playwright
    participant LLM
    participant FileSystem
    
    User->>WebUI: Upload YAML scenarios
    WebUI->>API: POST /api/v1/browser-test/yaml/upload
    API->>YAMLParser: Parse YAML content
    YAMLParser->>API: Return test scenarios
    
    alt Execute Immediately
        API->>BrowserAgent: Initialize with provider
        BrowserAgent->>Playwright: Launch browser
        
        loop For each scenario
            BrowserAgent->>LLM: Get test instructions
            LLM->>BrowserAgent: Return instructions
            BrowserAgent->>Playwright: Execute browser actions
            Playwright->>BrowserAgent: Return results/screenshots
            BrowserAgent->>FileSystem: Save screenshots
        end
        
        BrowserAgent->>Playwright: Close browser
        BrowserAgent->>API: Return test results
    end
    
    API->>WebUI: Return response
    WebUI->>User: Display results
```

## Web Crawling Workflow

```mermaid
sequenceDiagram
    participant User
    participant CLI/API
    participant WebCrawler
    participant EmbeddingsService
    participant LLM_Provider
    participant ChromaDB
    participant WebSite
    
    User->>CLI/API: Start crawling
    CLI/API->>WebCrawler: Initialize crawler
    
    loop For each page
        WebCrawler->>WebSite: Fetch page content
        WebSite->>WebCrawler: Return HTML/text
        WebCrawler->>WebCrawler: Extract and clean text
    end
    
    WebCrawler->>EmbeddingsService: Send extracted texts
    EmbeddingsService->>LLM_Provider: Generate embeddings
    LLM_Provider->>EmbeddingsService: Return vectors
    EmbeddingsService->>ChromaDB: Store embeddings
    ChromaDB->>EmbeddingsService: Confirm storage
    EmbeddingsService->>CLI/API: Return statistics
    CLI/API->>User: Display results
```

## WebSocket Communication Flow

```mermaid
sequenceDiagram
    participant WebUI
    participant API_Server
    participant WebSocket_Manager
    participant Service_Layer
    participant Logger
    
    WebUI->>API_Server: Connect to /api/v1/ws/logs
    API_Server->>WebSocket_Manager: Establish connection
    WebSocket_Manager->>WebUI: Connection confirmed
    
    loop Real-time operations
        Service_Layer->>Logger: Log operation events
        Logger->>WebSocket_Manager: Send log message
        WebSocket_Manager->>WebUI: Forward log message
        WebUI->>WebUI: Display in log viewer
    end
    
    opt Connection lost
        WebSocket_Manager->>WebUI: Connection lost
        WebUI->>WebSocket_Manager: Auto-reconnect
        WebSocket_Manager->>WebUI: Reconnection successful
    end
```

## Data Flow Architecture

```mermaid
graph LR
    subgraph "Input Sources"
        JIRA_IN[Jira Issues]
        GH_IN[GitHub Issues]
        CONF_IN[Confluence Pages]
        WEB_IN[Web Pages]
        YAML_IN[YAML Scenarios]
        API_SPEC[OpenAPI Specs]
    end
    
    subgraph "Processing Layer"
        CONNECTORS[External Connectors]
        PARSERS[Content Parsers]
        GENERATORS[Test Generators]
        CRAWLERS[Web Crawlers]
        AGENTS[Browser Agents]
    end
    
    subgraph "AI/LLM Layer"
        LLM_ROUTER[LLM Router]
        OPENAI_LLM[OpenAI]
        GEMINI_LLM[Gemini]
        MISTRAL_LLM[Mistral]
        OLLAMA_LLM[Ollama]
    end
    
    subgraph "Storage Layer"
        VECTOR_DB[ChromaDB<br/>Vector Store]
        CACHE_DB[SQLite<br/>Cache]
        FILE_STORE[File System<br/>Reports]
    end
    
    subgraph "Output Layer"
        MD_FILES[Markdown Reports]
        JSON_RESULTS[JSON Results]
        SCREENSHOTS[Screenshots]
        LOGS[Log Files]
    end
    
    JIRA_IN --> CONNECTORS
    GH_IN --> CONNECTORS
    CONF_IN --> CONNECTORS
    WEB_IN --> CRAWLERS
    YAML_IN --> PARSERS
    API_SPEC --> PARSERS
    
    CONNECTORS --> GENERATORS
    PARSERS --> AGENTS
    CRAWLERS --> GENERATORS
    
    GENERATORS --> LLM_ROUTER
    AGENTS --> LLM_ROUTER
    
    LLM_ROUTER --> OPENAI_LLM
    LLM_ROUTER --> GEMINI_LLM
    LLM_ROUTER --> MISTRAL_LLM
    LLM_ROUTER --> OLLAMA_LLM
    
    GENERATORS --> VECTOR_DB
    GENERATORS --> CACHE_DB
    AGENTS --> FILE_STORE
    
    GENERATORS --> MD_FILES
    AGENTS --> JSON_RESULTS
    AGENTS --> SCREENSHOTS
    GENERATORS --> LOGS
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV_CLI[Friday CLI]
        DEV_API[API Server<br/>Port 8080]
        DEV_WEB[Web App<br/>Port 3000]
        DEV_DB[Local ChromaDB]
    end
    
    subgraph "Docker Environment"
        DOCKER_API[Friday API<br/>Container]
        DOCKER_WEB[Web App<br/>Container]
        DOCKER_DB[ChromaDB<br/>Volume]
        DOCKER_COMPOSE[Docker Compose]
    end
    
    subgraph "Production Environment"
        LB[Load Balancer]
        API_CLUSTER[API Server<br/>Cluster]
        WEB_CLUSTER[Web App<br/>Cluster]
        SHARED_DB[Shared ChromaDB]
        REDIS[Redis Cache]
    end
    
    subgraph "External Services"
        JIRA_PROD[Jira Cloud]
        GH_PROD[GitHub]
        CONF_PROD[Confluence]
        LLM_APIS[LLM APIs]
    end
    
    DEV_CLI --> DEV_API
    DEV_API --> DEV_WEB
    DEV_API --> DEV_DB
    
    DOCKER_COMPOSE --> DOCKER_API
    DOCKER_COMPOSE --> DOCKER_WEB
    DOCKER_API --> DOCKER_DB
    
    LB --> API_CLUSTER
    LB --> WEB_CLUSTER
    API_CLUSTER --> SHARED_DB
    API_CLUSTER --> REDIS
    
    API_CLUSTER --> JIRA_PROD
    API_CLUSTER --> GH_PROD
    API_CLUSTER --> CONF_PROD
    API_CLUSTER --> LLM_APIS
```

## Security Model

```mermaid
graph TB
    subgraph "Authentication Layer"
        ENV_VARS[Environment Variables]
        API_KEYS[API Keys Management]
        TOKENS[Access Tokens]
    end
    
    subgraph "Authorization Layer"
        CORS[CORS Policy]
        RATE_LIMIT[Rate Limiting]
        INPUT_VAL[Input Validation]
    end
    
    subgraph "Data Protection"
        ENCRYPT[Data Encryption]
        SANITIZE[Data Sanitization]
        AUDIT[Audit Logging]
    end
    
    subgraph "Network Security"
        HTTPS[HTTPS/TLS]
        CSP[Content Security Policy]
        FIREWALL[Firewall Rules]
    end
    
    ENV_VARS --> API_KEYS
    API_KEYS --> TOKENS
    
    CORS --> RATE_LIMIT
    RATE_LIMIT --> INPUT_VAL
    
    ENCRYPT --> SANITIZE
    SANITIZE --> AUDIT
    
    HTTPS --> CSP
    CSP --> FIREWALL
    
    TOKENS --> CORS
    INPUT_VAL --> ENCRYPT
    AUDIT --> HTTPS
```

## Error Handling Flow

```mermaid
graph TB
    subgraph "Error Sources"
        API_ERR[API Errors]
        LLM_ERR[LLM Provider Errors]
        NETWORK_ERR[Network Errors]
        VALIDATION_ERR[Validation Errors]
        BROWSER_ERR[Browser Errors]
    end
    
    subgraph "Error Handling"
        CATCH[Error Catcher]
        CLASSIFY[Error Classifier]
        RETRY[Retry Logic]
        FALLBACK[Fallback Mechanisms]
    end
    
    subgraph "Error Response"
        LOG[Error Logging]
        NOTIFY[User Notification]
        RECOVERY[Recovery Actions]
        REPORT[Error Reporting]
    end
    
    API_ERR --> CATCH
    LLM_ERR --> CATCH
    NETWORK_ERR --> CATCH
    VALIDATION_ERR --> CATCH
    BROWSER_ERR --> CATCH
    
    CATCH --> CLASSIFY
    CLASSIFY --> RETRY
    RETRY --> FALLBACK
    
    FALLBACK --> LOG
    LOG --> NOTIFY
    NOTIFY --> RECOVERY
    RECOVERY --> REPORT
```

## CLI Command Flow

```mermaid
graph LR
    subgraph "CLI Commands"
        SETUP[friday setup]
        GENERATE[friday generate]
        CRAWL[friday crawl]
        BROWSER[friday browser-test]
        WEBUI[friday webui]
        OPEN[friday open]
        VERSION[friday version]
    end
    
    subgraph "Command Processing"
        PARSER[Argument Parser]
        VALIDATOR[Input Validator]
        EXECUTOR[Command Executor]
    end
    
    subgraph "Service Integration"
        API_CLIENT[API Client]
        DIRECT_SERVICE[Direct Service Calls]
        UI_LAUNCHER[UI Launcher]
    end
    
    subgraph "Output"
        CONSOLE[Console Output]
        FILES[File Output]
        BROWSER_OPEN[Browser Opening]
    end
    
    SETUP --> PARSER
    GENERATE --> PARSER
    CRAWL --> PARSER
    BROWSER --> PARSER
    WEBUI --> PARSER
    OPEN --> PARSER
    VERSION --> PARSER
    
    PARSER --> VALIDATOR
    VALIDATOR --> EXECUTOR
    
    EXECUTOR --> API_CLIENT
    EXECUTOR --> DIRECT_SERVICE
    EXECUTOR --> UI_LAUNCHER
    
    API_CLIENT --> CONSOLE
    DIRECT_SERVICE --> FILES
    UI_LAUNCHER --> BROWSER_OPEN
```

## Monitoring and Observability

```mermaid
graph TB
    subgraph "Application Metrics"
        API_METRICS[API Response Times]
        TEST_METRICS[Test Execution Stats]
        ERROR_METRICS[Error Rates]
        USAGE_METRICS[Feature Usage]
    end
    
    subgraph "Infrastructure Metrics"
        CPU_METRICS[CPU Usage]
        MEMORY_METRICS[Memory Usage]
        DISK_METRICS[Disk Usage]
        NETWORK_METRICS[Network I/O]
    end
    
    subgraph "Logging"
        APP_LOGS[Application Logs]
        ACCESS_LOGS[Access Logs]
        ERROR_LOGS[Error Logs]
        AUDIT_LOGS[Audit Logs]
    end
    
    subgraph "Alerting"
        HEALTH_ALERTS[Health Check Alerts]
        PERFORMANCE_ALERTS[Performance Alerts]
        ERROR_ALERTS[Error Threshold Alerts]
        RESOURCE_ALERTS[Resource Usage Alerts]
    end
    
    API_METRICS --> HEALTH_ALERTS
    TEST_METRICS --> PERFORMANCE_ALERTS
    ERROR_METRICS --> ERROR_ALERTS
    
    CPU_METRICS --> RESOURCE_ALERTS
    MEMORY_METRICS --> RESOURCE_ALERTS
    
    APP_LOGS --> ERROR_ALERTS
    ERROR_LOGS --> ERROR_ALERTS
```

These diagrams provide a comprehensive visual overview of Friday's architecture, helping developers understand the system's structure, data flow, and component interactions.