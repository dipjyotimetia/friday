# Browser Testing Agent Documentation

## Overview

FRIDAY's Browser Testing Agent provides AI-powered automated browser testing capabilities using natural language instructions. Built on top of the `browser-use` library and Playwright, it enables comprehensive UI testing without traditional test scripting.

## Features

### Core Capabilities
- **Natural Language Testing**: Describe test scenarios in plain English
- **Multi-Browser Support**: Chromium-based browsers with headless and visible modes
- **Visual Testing**: Automatic screenshot capture during test execution
- **Batch Testing**: Execute multiple test cases in sequence
- **Real-time Monitoring**: Live logs and progress tracking via WebSocket
- **Comprehensive Reporting**: Detailed test reports with success/failure analysis

### Test Types Supported
- **Functional Testing**: Core application functionality verification
- **UI/UX Testing**: User interface and experience validation
- **Integration Testing**: Component interaction testing
- **Accessibility Testing**: WCAG compliance and accessibility checks
- **Performance Testing**: Basic performance and responsiveness tests

## Architecture

### Components

```
Browser Testing Agent
├── backend/
│   ├── services/browser_agent.py      # Core browser testing logic
│   ├── api/routes/browser_test.py     # REST API endpoints
│   └── api/schemas/browser_test.py    # Pydantic models
├── frontend/
│   ├── components/features/browser-tester/   # React UI components
│   └── types/index.ts                 # TypeScript type definitions
└── cli/
    └── cli.py                         # Command-line interface
```

### Dependencies
- **browser-use**: AI agent framework for browser automation
- **playwright**: Browser automation engine
- **langchain**: LLM integration and prompt management
- **fastapi**: REST API framework
- **react**: Frontend user interface

## Quick Start

### CLI Commands (Recommended)

The Friday CLI provides streamlined access to browser testing functionality:

```bash
# Start the web UI for interactive test creation
friday webui

# Run browser tests from YAML scenarios
friday browser-test scenarios.yaml --provider openai

# Open web UI directly to browser testing
friday open --feature browser
```

For complete CLI documentation, see [CLI Reference](CLI_REFERENCE.md).

## Installation & Setup

### Prerequisites
```bash
# Install Python dependencies
uv sync

# Install Playwright browsers
uv run playwright install chromium --with-deps
```

### Environment Variables
Required environment variables for LLM providers:
```bash
OPENAI_API_KEY=your_openai_key        # For OpenAI GPT models
GOOGLE_API_KEY=your_google_key        # For Google Gemini models
MISTRAL_API_KEY=your_mistral_key      # For Mistral AI models
```

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Create a simple test scenario YAML file
cat > navigation_test.yaml << EOF
name: "Navigation Test Suite"
scenarios:
  - name: "Main Navigation Test"
    requirement: "Test the main navigation menu works correctly"
    url: "https://example.com"
    test_type: "functional"
EOF

# Run the test
uv run friday browser-test navigation_test.yaml

# Login flow test with context
cat > login_test.yaml << EOF
name: "Login Test Suite"
scenarios:
  - name: "User Login Test"
    requirement: "Test user login functionality"
    url: "https://app.example.com/login"
    test_type: "functional"
    context: "Use demo credentials: username 'demo', password 'demo123'"
EOF

uv run friday browser-test login_test.yaml --provider openai

# UI test with visible browser
cat > ui_test.yaml << EOF
name: "UI Test Suite"
scenarios:
  - name: "Responsive Design Test"
    requirement: "Verify responsive design on different screen sizes"
    url: "https://example.com"
    test_type: "ui"
EOF

uv run friday browser-test ui_test.yaml --no-headless --output ui_test_report.md
```

#### Advanced Options
```bash
uv run friday browser-test scenarios.yaml \
  --provider [openai|gemini|ollama|mistral] \
  --headless/--no-headless \
  --output report.md

# Example comprehensive YAML structure
cat > scenarios.yaml << EOF
name: "Comprehensive Test Suite"
scenarios:
  - name: "Test Name"
    requirement: "Test description"
    url: "https://example.com"
    test_type: "functional"
    context: "Additional context or instructions"
EOF
```

### REST API

#### YAML Scenario Upload and Execute
```bash
# Upload and execute YAML scenarios
curl -X POST "http://localhost:8080/api/v1/browser-test/yaml/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_scenarios.yaml" \
  -F "provider=openai" \
  -F "headless=true" \
  -F "execute_immediately=true"
```

#### Execute YAML Content Directly
```bash
curl -X POST "http://localhost:8080/api/v1/browser-test/yaml/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "yaml_content": "name: \"Test Suite\"\nscenarios:\n  - name: \"Homepage Test\"\n    requirement: \"Test homepage loads correctly\"\n    url: \"https://example.com\"\n    test_type: \"functional\"\n  - name: \"Contact Form Test\"\n    requirement: \"Test contact form submission\"\n    url: \"https://example.com/contact\"\n    test_type: \"functional\"\n    context: \"Fill out form with test data\"",
    "provider": "openai",
    "headless": true
  }'
```

### Web Interface

Access the browser testing interface at `http://localhost:3000` and navigate to the "Browser Tests" tab.

#### YAML Scenario Testing
1. Upload a YAML file with test scenarios or write YAML content directly
2. Select LLM provider (OpenAI, Gemini, Ollama, Mistral)
3. Configure execution settings (headless mode, immediate execution)
4. Execute all tests and monitor real-time progress
5. View comprehensive results, reports, and screenshots

## API Reference

### Endpoints

#### POST /api/v1/browser-test/yaml/upload
Upload and optionally execute YAML test scenarios.

**Request:** Multipart form data
- `file`: YAML file containing test scenarios
- `provider`: LLM provider (openai, gemini, ollama, mistral)
- `headless`: Boolean for headless mode
- `execute_immediately`: Boolean to execute after upload

**Response:**
```json
{
  "success": true,
  "message": "Successfully uploaded YAML file with 3 scenarios",
  "test_suite_name": "Test Suite",
  "scenarios_count": 3,
  "scenarios": [...],
  "execution_results": [...],
  "report": "# Test Report\n...",
  "summary": {
    "total_tests": 3,
    "passed_tests": 2,
    "failed_tests": 1,
    "success_rate": 66.7
  }
}
```

#### POST /api/v1/browser-test/yaml/execute
Execute test scenarios from YAML content.

**Request Body:**
```json
{
  "yaml_content": "name: \"Test Suite\"\nscenarios:\n  - name: \"Test\"\n    requirement: \"Test description\"\n    url: \"https://example.com\"\n    test_type: \"functional\"",
  "provider": "openai",
  "headless": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully executed 3 scenarios. 2/3 tests passed",
  "test_suite_name": "Test Suite",
  "scenarios_count": 3,
  "results": [...],
  "report": "# Test Report\n...",
  "summary": {
    "total_tests": 3,
    "passed_tests": 2,
    "failed_tests": 1,
    "success_rate": 66.7
  }
}
```

#### GET /api/v1/browser-test/health
Health check for browser testing service.

## Best Practices

### Writing Effective Test Requirements

#### Good Examples
```
✅ "Test user login with valid credentials and verify redirection to dashboard"
✅ "Verify the shopping cart updates correctly when adding/removing items"
✅ "Test form validation by submitting invalid data and checking error messages"
✅ "Verify responsive navigation menu works on mobile screen sizes"
```

#### Avoid These
```
❌ "Test the website"  # Too vague
❌ "Click button"      # Too specific, not goal-oriented
❌ "Check everything"  # Unclear scope
```

### Test Context Guidelines
- Provide specific test data when needed
- Include expected outcomes
- Mention any prerequisites or setup requirements
- Specify user roles or permissions if relevant

### Performance Considerations
- Use headless mode for faster execution in CI/CD
- Add delays between batch tests to avoid overwhelming target sites
- Consider rate limiting for external websites
- Monitor resource usage during test execution

## Troubleshooting

### Common Issues

#### Browser Installation Problems
```bash
# Reinstall Playwright browsers
uv run playwright install chromium --with-deps --force
```

#### LLM Provider Errors
- Verify API keys are correctly set in environment variables
- Check API rate limits and quotas
- Ensure network connectivity to LLM providers

#### Test Execution Failures
- Check target website accessibility
- Verify test requirements are clear and specific
- Review browser console logs for JavaScript errors
- Increase timeout values for slow-loading pages

#### Memory Issues
- Use headless mode for resource-intensive test suites
- Limit concurrent test execution
- Monitor system resources during batch testing

### Debug Mode
Enable verbose logging for troubleshooting:
```bash
export LOG_LEVEL=DEBUG

# Create a simple debug YAML scenario
cat > debug_test.yaml << EOF
name: "Debug Test"
scenarios:
  - name: "Simple Debug Test"
    requirement: "test"
    url: "<url>"
    test_type: "functional"
EOF

uv run friday browser-test debug_test.yaml
```

## Integration Examples

### CI/CD Pipeline
```yaml
# .github/workflows/browser-tests.yml
name: Browser Tests
on: [push, pull_request]

jobs:
  browser-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install uv
          uv sync
          uv run playwright install chromium --with-deps
      - name: Run browser tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          echo 'name: "CI Test Suite"
          scenarios:
            - name: "Homepage Test"
              requirement: "Verify homepage loads and navigation works"
              url: "${{ env.TEST_URL }}"
              test_type: "functional"' > ci_test.yaml
          uv run friday browser-test ci_test.yaml --output browser-test-results.md
```

### Custom Test Scripts
```python
import asyncio
from friday.services.browser_agent import BrowserTestingAgent
from friday.services.yaml_scenarios import YamlScenariosParser

async def run_custom_tests():
    agent = BrowserTestingAgent(provider="openai")
    parser = YamlScenariosParser()
    
    # Define YAML content
    yaml_content = """
name: "Custom Test Suite"
scenarios:
  - name: "User Registration Test"
    requirement: "Test user registration flow"
    url: "https://example.com/register"
    test_type: "functional"
    context: "Use test email and verify confirmation"
  - name: "Product Search Test"
    requirement: "Test product search functionality"
    url: "https://example.com/shop"
    test_type: "functional"
    context: "Search for 'laptop' and verify results"
"""
    
    # Parse YAML and convert to test cases
    test_suite = parser.parse_yaml_content(yaml_content)
    test_cases = parser.convert_to_browser_test_cases(test_suite)
    
    # Execute tests
    results = await agent.run_multiple_tests(test_cases)
    report = agent.generate_test_report(results)
    
    print(report)

if __name__ == "__main__":
    asyncio.run(run_custom_tests())
```

## Limitations

### Current Limitations
- **Browser Support**: Currently limited to Chromium-based browsers
- **Complex Interactions**: May struggle with complex drag-and-drop or advanced UI patterns
- **Dynamic Content**: Challenges with heavily dynamic or real-time updating content
- **Authentication**: Limited support for complex authentication flows (OAuth, 2FA)
- **File Operations**: Restricted file upload/download capabilities

### Future Enhancements
- Multi-browser support (Firefox, Safari)
- Enhanced mobile testing capabilities
- Integration with visual regression testing tools
- Advanced authentication handling
- Performance metrics collection
- Test recording and playback features

## Security Considerations

### Data Privacy
- Browser tests may capture sensitive information in screenshots
- Avoid testing with real user credentials
- Use test environments and mock data when possible
- Review generated screenshots before sharing

### Network Security
- Tests make real HTTP requests to target websites
- Consider using VPN or isolated networks for sensitive testing
- Be mindful of rate limiting and respectful testing practices

### API Key Management
- Store LLM provider API keys securely
- Use environment variables, not hardcoded values
- Implement key rotation policies
- Monitor API usage and costs

## Support

### Getting Help
- Check the troubleshooting section for common issues
- Review browser console logs for JavaScript errors
- Enable debug logging for detailed execution traces
- Create issues on the project repository with detailed reproduction steps

### Community Resources
- Project documentation: [docs/](../docs/)
- Example test cases: [examples/](../examples/)
- API reference: [OpenAPI spec](../openapi.json)
- Development guide: [DEVELOPER_ONBOARDING.md](DEVELOPER_ONBOARDING.md)