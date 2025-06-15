# Friday Documentation

Welcome to the Friday AI-powered testing agent documentation. This guide provides comprehensive information about installation, usage, and development.

## Quick Navigation

### 🚀 Getting Started
- **[Quick Start Guide](CLI_QUICK_START.md)** - Get up and running in 5 minutes
- **[Installation & Setup](DEVELOPER_ONBOARDING.md)** - Complete installation guide
- **[System Requirements](DEVELOPER_ONBOARDING.md#prerequisites)** - What you need to run Friday

### 📚 Core Documentation
- **[CLI Reference](CLI_REFERENCE.md)** - Complete command-line interface documentation
- **[API Documentation](apis.md)** - REST API endpoints and usage
- **[Web Application Guide](WEBAPP_GUIDE.md)** - Frontend application documentation
- **[Architecture Diagrams](ARCHITECTURE_DIAGRAMS.md)** - Visual system overview

### 🎯 Feature Guides
- **[Browser Testing](BROWSER_TESTING.md)** - AI-powered browser automation testing
- **[System Architecture](SYSTEM_ARCHITECTURE.md)** - Technical architecture overview

### 🔧 Development
- **[Developer Onboarding](DEVELOPER_ONBOARDING.md)** - Contributing to Friday
- **[Architecture Diagrams](ARCHITECTURE_DIAGRAMS.md)** - System design and workflows

## What is Friday?

Friday is an AI-powered testing agent that helps you:

- **Generate Test Cases**: Create comprehensive test cases from Jira or GitHub issues
- **Browser Automation**: Run intelligent browser tests using natural language
- **Web Crawling**: Build context databases from documentation and websites
- **API Testing**: Test REST APIs using OpenAPI specifications
- **Visual Testing**: Interactive web interface for all testing operations

## Three Ways to Use Friday

### 1. Command Line Interface (CLI)
Perfect for developers and CI/CD integration:
```bash
# Generate test cases
friday generate --jira-key PROJ-123 --output tests.md

# Run browser tests
friday browser-test scenarios.yaml --provider openai

# Start web interface
friday webui
```

### 2. Web Application
Visual interface for interactive testing:
- Upload YAML test scenarios
- Monitor real-time test execution
- View results with screenshots
- Download comprehensive reports

### 3. REST API
Programmatic access for system integration:
```bash
# Generate tests via API
curl -X POST http://localhost:8080/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"jira_key": "PROJ-123", "output": "tests.md"}'
```

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Friday CLI    │    │  Web Interface  │    │  REST API       │
│   (Command)     │    │  (Next.js)      │    │  (FastAPI)      │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      Friday API Server    │
                    │       (Port 8080)         │
                    └─────────────┬─────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
  ┌─────▼──────┐        ┌────────▼────────┐      ┌─────────▼─────────┐
  │ Test Gen   │        │ Browser Agent   │      │ Web Crawler       │
  │ Service    │        │ (browser-use)   │      │ (Embeddings)      │
  └─────┬──────┘        └────────┬────────┘      └─────────┬─────────┘
        │                        │                         │
  ┌─────▼──────┐        ┌────────▼────────┐      ┌─────────▼─────────┐
  │ Jira/GitHub│        │   Playwright    │      │    ChromaDB       │
  │ Confluence │        │   Browsers      │      │ Vector Store      │
  └────────────┘        └─────────────────┘      └───────────────────┘
```

## Key Features

### 🤖 AI-Powered Testing
- **Natural Language**: Write test requirements in plain English
- **Multi-Modal Testing**: Functional, UI, integration, accessibility, performance
- **Smart Browser Automation**: AI agent navigates and tests web applications
- **Context-Aware**: Uses documentation and embeddings for better test generation

### 🔄 Multiple Integration Points
- **Jira Integration**: Generate tests from Jira issues
- **GitHub Integration**: Pull request and issue-based test generation
- **Confluence Integration**: Enhanced context from documentation
- **OpenAPI Integration**: Automated API testing from specifications

### 🎯 Flexible Execution
- **Multiple LLM Providers**: OpenAI, Google Gemini, Mistral, Ollama
- **Headless & Visual Modes**: Debug with visible browsers or run in CI/CD
- **Real-time Monitoring**: Live progress tracking and logging
- **Comprehensive Reporting**: Detailed test reports with screenshots

### 🛡️ Enterprise Ready
- **Environment Configuration**: Secure credential management
- **Docker Support**: Containerized deployment
- **CORS & Security**: Production-ready security configuration
- **Rate Limiting**: Built-in API rate limiting and error handling

## Quick Start Examples

### 1. Browser Testing Workflow
```bash
# Get started with browser testing
friday webui                                    # Start web interface
friday open --feature browser                  # Open browser testing tab
# Upload YAML scenarios or use the template
friday browser-test scenarios.yaml --provider openai
```

### 2. Test Generation Workflow
```bash
# Generate test cases from Jira
friday generate --jira-key PROJECT-123 --output tests.md

# Generate with additional context
friday crawl https://docs.myapp.com --max-pages 20
friday generate --jira-key PROJECT-123 --confluence-id 456789 --output comprehensive_tests.md
```

### 3. API Testing Workflow
```bash
# Test APIs from OpenAPI specs
curl -X POST http://localhost:8080/api/v1/testapi \
  -F "base_url=https://api.example.com" \
  -F "spec_upload=@openapi.yaml" \
  -F "output=api_test_report.md"
```

## Documentation Structure

### For Users
1. **[Quick Start](CLI_QUICK_START.md)** - Fastest way to get started
2. **[CLI Reference](CLI_REFERENCE.md)** - Complete command documentation
3. **[Browser Testing Guide](BROWSER_TESTING.md)** - Detailed browser testing guide

### For Developers
1. **[Developer Onboarding](DEVELOPER_ONBOARDING.md)** - Setup development environment
2. **[API Documentation](apis.md)** - REST API reference
3. **[Web App Guide](WEBAPP_GUIDE.md)** - Frontend development guide
4. **[Architecture Diagrams](ARCHITECTURE_DIAGRAMS.md)** - System design visuals

### For System Architects
1. **[System Architecture](SYSTEM_ARCHITECTURE.md)** - High-level architecture
2. **[Architecture Diagrams](ARCHITECTURE_DIAGRAMS.md)** - Detailed system diagrams

## Sample Files and Examples

### Browser Testing
- **[Sample YAML Scenarios](../examples/sample_browser_tests.yaml)** - Example browser test scenarios
- **[OpenAPI Specs](specs/)** - Sample API specifications for testing

### Reports and Output
- **[Sample Test Cases](test_cases.md)** - Example generated test cases
- **[API Test Report](api-test-report.md)** - Sample API testing report

## Support and Community

### Getting Help
- **GitHub Issues**: [Report bugs or request features](https://github.com/dipjyotimetia/friday/issues)
- **Documentation**: Browse this documentation for detailed guides
- **CLI Help**: Use `friday --help` for command-specific help

### Contributing
- **[Contributing Guidelines](../CONTRIBUTING.md)** - How to contribute to Friday
- **[Code of Conduct](../CODE_OF_CONDUCT.md)** - Community guidelines
- **[Security Policy](../SECURITY.md)** - Security vulnerability reporting

## Version Information

- **Current Version**: 0.1.47
- **Python Requirements**: 3.9+
- **Node.js Requirements**: 18+ (recommended: 22+)
- **Last Updated**: December 2024

## Environment Setup

### Minimum Configuration
```bash
# Required for basic functionality
OPENAI_API_KEY=your_openai_key
GITHUB_ACCESS_TOKEN=your_github_token
JIRA_URL=https://your-org.atlassian.net
JIRA_USERNAME=your_email
JIRA_API_TOKEN=your_jira_token
```

### Full Configuration
See the [CLI Reference](CLI_REFERENCE.md#configuration) for complete environment variable documentation.

---

**Need Help?** Start with the [Quick Start Guide](CLI_QUICK_START.md) or check the [CLI Reference](CLI_REFERENCE.md) for detailed command documentation.