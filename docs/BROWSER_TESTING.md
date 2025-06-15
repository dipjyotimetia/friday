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
# Simple functional test
uv run friday browser-test https://example.com \
  --requirement "Test the main navigation menu works correctly"

# Login flow test with context
uv run friday browser-test https://app.example.com/login \
  --requirement "Test user login functionality" \
  --test-type functional \
  --context "Use demo credentials: username 'demo', password 'demo123'"

# UI test with visible browser
uv run friday browser-test https://example.com \
  --requirement "Verify responsive design on different screen sizes" \
  --test-type ui \
  --no-headless \
  --output ui_test_report.md
```

#### Advanced Options
```bash
uv run friday browser-test <URL> \
  --requirement "Test description" \
  --test-type [functional|ui|integration|accessibility|performance] \
  --context "Additional context or instructions" \
  --provider [openai|gemini|ollama|mistral] \
  --headless/--no-headless \
  --output report.md
```

### REST API

#### Single Browser Test
```bash
curl -X POST "http://localhost:8080/api/v1/browser-test/single" \
  -H "Content-Type: application/json" \
  -d '{
    "requirement": "Test user registration form",
    "url": "https://example.com/register",
    "test_type": "functional",
    "context": "Fill out form with valid data and verify success message",
    "headless": true,
    "take_screenshots": true
  }'
```

#### Multiple Browser Tests
```bash
curl -X POST "http://localhost:8080/api/v1/browser-test/multiple" \
  -H "Content-Type: application/json" \
  -d '{
    "test_cases": [
      {
        "requirement": "Test homepage loads correctly",
        "url": "https://example.com",
        "test_type": "functional"
      },
      {
        "requirement": "Test contact form submission",
        "url": "https://example.com/contact",
        "test_type": "functional",
        "context": "Fill out form with test data"
      }
    ],
    "headless": true
  }'
```

### Web Interface

Access the browser testing interface at `http://localhost:3000` and navigate to the "Browser Tests" tab.

#### Single Test Mode
1. Enter test requirement in natural language
2. Specify target URL
3. Select test type
4. Add optional context
5. Configure execution settings
6. Run test and monitor progress

#### Multiple Test Mode
1. Add multiple test cases
2. Configure global settings (headless mode)
3. Execute all tests in sequence
4. View aggregated results and reports

## API Reference

### Endpoints

#### POST /api/v1/browser-test/single
Execute a single browser test.

**Request Body:**
```json
{
  "requirement": "string",
  "url": "string",
  "test_type": "functional|ui|integration|accessibility|performance",
  "context": "string",
  "headless": true,
  "take_screenshots": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Browser test completed successfully",
  "data": {
    "status": "completed",
    "requirement": "Test requirement",
    "url": "https://example.com",
    "test_type": "functional",
    "execution_result": "Detailed test execution results...",
    "screenshots": ["screenshot1.png", "screenshot2.png"],
    "timestamp": 1640995200.0,
    "success": true,
    "errors": []
  }
}
```

#### POST /api/v1/browser-test/multiple
Execute multiple browser tests in sequence.

**Request Body:**
```json
{
  "test_cases": [
    {
      "requirement": "string",
      "url": "string",
      "test_type": "functional",
      "context": "string",
      "take_screenshots": true
    }
  ],
  "headless": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Multiple browser tests completed",
  "data": [...],
  "report": "# Test Report\n...",
  "summary": {
    "total_tests": 5,
    "passed_tests": 4,
    "failed_tests": 1,
    "success_rate": 80.0
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
uv run friday browser-test <url> --requirement "test"
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
          uv run friday browser-test ${{ env.TEST_URL }} \
            --requirement "Verify homepage loads and navigation works" \
            --output browser-test-results.md
```

### Custom Test Scripts
```python
import asyncio
from friday.services.browser_agent import BrowserTestingAgent

async def run_custom_tests():
    agent = BrowserTestingAgent(provider="openai")
    
    test_cases = [
        {
            "requirement": "Test user registration flow",
            "url": "https://example.com/register",
            "test_type": "functional",
            "context": "Use test email and verify confirmation"
        },
        {
            "requirement": "Test product search functionality", 
            "url": "https://example.com/shop",
            "test_type": "functional",
            "context": "Search for 'laptop' and verify results"
        }
    ]
    
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