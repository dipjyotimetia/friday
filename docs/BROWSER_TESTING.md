# Browser Testing Guide

This guide covers the browser testing capabilities of FRIDAY, including setup, usage, troubleshooting, and best practices.

## Overview

FRIDAY's browser testing feature provides AI-powered browser automation using natural language test descriptions. It combines the power of large language models with Playwright browser automation to execute complex user workflows.

### Key Features

- **Natural Language Testing**: Write test requirements in plain English
- **AI-Powered Automation**: Uses LLMs to intelligently interact with web pages
- **Multi-Modal Testing**: Supports functional, UI/UX, integration, accessibility, and performance testing
- **Visual Documentation**: Automatic screenshot capture for test evidence
- **Real-time Monitoring**: Live progress tracking via WebSocket connections
- **Multiple Execution Modes**: Sequential and parallel test execution
- **Comprehensive Reporting**: JSON, Markdown, and HTML report formats

## Architecture

### Components

1. **Browser Agent** (`src/friday/services/browser_agent.py`)
   - Core AI testing logic using browser-use library
   - LLM integration for natural language processing
   - Screenshot capture and test execution

2. **API Layer** (`src/friday/api/routes/browser_test.py`)
   - REST endpoints for YAML upload and test execution
   - WebSocket support for real-time updates
   - Background task management

3. **Frontend Interface** (`app/components/features/browser-tester/`)
   - Web UI for test management
   - File upload and execution control
   - Real-time monitoring and results display

4. **CLI Interface** (`src/friday/cli.py`)
   - Command-line test execution
   - Batch processing capabilities

## Quick Start

### 1. Environment Setup

```bash
# Install dependencies
uv sync

# Install Playwright browsers
uv run playwright install chromium --with-deps

# Set up environment variables
cp .env.example .env
# Configure OPENAI_API_KEY or other LLM provider keys
```

### 2. Verify Installation

```bash
# Check browser testing health
curl http://localhost:8080/api/v1/browser-test/health

# Expected response:
{
  "status": "healthy",
  "browser_available": true,
  "playwright_version": "1.53.0",
  "browser_use_version": "0.4.4",
  "supported_providers": ["openai", "gemini", "ollama", "mistral"]
}
```

### 3. Create a Test Suite

Create a YAML file with your test scenarios:

```yaml
name: "Example Test Suite"
description: "Demonstration of browser testing capabilities"
scenarios:
  - name: "Basic Page Load Test"
    requirement: "Verify that the homepage loads successfully"
    url: "https://example.com"
    test_type: "functional"
    context: "Check that the page loads and displays expected content"
    expected_outcome: "Page loads within 5 seconds with proper title"
    timeout: 30
    take_screenshots: true

  - name: "Search Functionality Test"
    requirement: "Test search functionality on DuckDuckGo"
    url: "https://duckduckgo.com"
    test_type: "functional"
    context: "Search for 'AI testing' and verify results appear"
    expected_outcome: "Search results are displayed with relevant links"
    timeout: 45
    take_screenshots: true
```

### 4. Execute Tests

#### Via CLI
```bash
uv run friday browser-test test_suite.yaml --provider openai --headless
```

#### Via Web Interface
1. Start the services:
   ```bash
   uv run friday webui
   ```
2. Open http://localhost:3000
3. Navigate to "Browser Tester" tab
4. Upload your YAML file
5. Configure execution settings
6. Monitor real-time progress

#### Via API
```bash
# Upload YAML
curl -X POST http://localhost:8080/api/v1/browser-test/yaml/upload \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.yaml", "content": "..."}'

# Execute tests
curl -X POST http://localhost:8080/api/v1/browser-test/yaml/execute \
  -H "Content-Type: application/json" \
  -d '{"file_id": "your-file-id", "provider": "openai", "headless": true}'
```

## YAML Configuration Reference

### Test Suite Structure

```yaml
name: "Test Suite Name"                    # Required: Suite identifier
description: "Suite description"           # Optional: Suite description
version: "1.0"                            # Optional: Schema version
global_timeout: 300                       # Optional: Global timeout in seconds
global_take_screenshots: true            # Optional: Global screenshot setting

scenarios:                                # Required: List of test scenarios
  - name: "Test Name"                     # Required: Scenario identifier
    requirement: "What to test"           # Required: Natural language requirement
    url: "https://example.com"            # Required: Target URL
    test_type: "functional"               # Required: Type of test
    context: "Additional context"         # Optional: Extra context for AI
    expected_outcome: "Expected result"   # Optional: Success criteria
    timeout: 30                          # Optional: Scenario timeout
    take_screenshots: true               # Optional: Screenshot setting
    steps:                               # Optional: Specific test steps
      - "Navigate to login page"
      - "Enter valid credentials"
      - "Click login button"
    expected_outcomes:                   # Optional: Multiple success criteria
      - "User is logged in successfully"
      - "Dashboard is displayed"
```

### Test Types

- **functional**: Core application workflows and user interactions
- **ui**: Visual elements, layout, and responsive design
- **integration**: Component interactions and API integrations
- **accessibility**: WCAG compliance and screen reader support
- **performance**: Page load times and responsiveness

### Advanced Configuration

```yaml
# Enhanced scenario with all options
scenarios:
  - name: "Complex Login Test"
    requirement: "Test user authentication workflow"
    url: "https://app.example.com/login"
    test_type: "functional"
    context: |
      Use test credentials:
      Username: test@example.com
      Password: TestPass123
      Verify redirect to dashboard after login
    expected_outcome: "Successfully logged in and redirected to dashboard"
    timeout: 60
    take_screenshots: true
    steps:
      - "Click on email input field"
      - "Type test@example.com"
      - "Click on password field"
      - "Type TestPass123"
      - "Click login button"
      - "Wait for dashboard to load"
    expected_outcomes:
      - "Login form accepts credentials"
      - "No error messages are displayed"
      - "Dashboard loads with user information"
      - "Navigation menu is visible"
```

## Web Interface Guide

### Upload Tab
- **Single File Upload**: Drag and drop or select YAML files
- **Multiple File Upload**: Upload multiple test suites simultaneously
- **File Validation**: Real-time YAML syntax checking
- **Preview**: View parsed test suite structure

### Preview Tab
- **Suite Overview**: Test suite metadata and configuration
- **Scenario List**: Individual test scenario details
- **Validation Status**: Checks for required fields and syntax

### Execution Tab
- **Provider Selection**: Choose LLM provider (OpenAI, Gemini, etc.)
- **Execution Mode**: Sequential or parallel execution
- **Headless Toggle**: Visible or headless browser mode
- **Real-time Logs**: Live execution progress via WebSocket
- **Status Monitoring**: Track individual scenario progress

### Results Tab
- **Execution Summary**: Overall test statistics
- **Individual Results**: Detailed scenario outcomes
- **Screenshots**: Captured evidence from test execution
- **Report Generation**: Export results in multiple formats

## API Reference

### Endpoints

#### Upload YAML File
```
POST /api/v1/browser-test/yaml/upload
Content-Type: application/json

{
  "filename": "test_suite.yaml",
  "content": "yaml content as string"
}

Response:
{
  "message": "Successfully uploaded test_suite.yaml",
  "file_id": "uuid",
  "parsed_suite": { ... }
}
```

#### Execute Tests
```
POST /api/v1/browser-test/yaml/execute
Content-Type: application/json

{
  "file_id": "uuid",
  "provider": "openai",
  "headless": true,
  "output_format": "json"
}

Response:
{
  "message": "Browser test execution started",
  "execution_id": "uuid",
  "status": "running"
}
```

#### Check Execution Status
```
GET /api/v1/browser-test/execution/{execution_id}

Response:
{
  "status": "completed",
  "started_at": "2025-07-05T23:53:44.055637",
  "completed_at": "2025-07-05T23:54:32.123456",
  "report": { ... }
}
```

#### Generate Report
```
POST /api/v1/browser-test/report/{execution_id}
Content-Type: application/json

{
  "format": "markdown"
}

Response:
{
  "report": "markdown content",
  "format": "markdown"
}
```

#### Health Check
```
GET /api/v1/browser-test/health

Response:
{
  "status": "healthy",
  "browser_available": true,
  "playwright_version": "1.53.0",
  "browser_use_version": "0.4.4",
  "supported_providers": ["openai", "gemini", "ollama", "mistral"]
}
```

### WebSocket Endpoints

#### General Logs
```
WS /api/v1/ws/logs
```
Streams general application logs for debugging and monitoring.

#### Execution-Specific Logs
```
WS /api/v1/browser-test/ws/{execution_id}
```
Streams real-time updates for specific test execution:
- Test progress updates
- Screenshot notifications
- Error messages
- Completion status

## Troubleshooting

### Common Issues

#### "Upload failed: Not Found" Error
**Cause**: Frontend API calls not using proper base URL  
**Solution**: Fixed in v2025.07.05 - frontend now uses `${API_CONFIG.BASE_URL}${endpoint}`

#### Browser Health Check Fails
**Cause**: Playwright browsers not installed or corrupted  
**Solution**:
```bash
uv run playwright install chromium --with-deps --force
```

#### WebSocket Connection Issues
**Cause**: Incorrect endpoint configuration or CORS settings  
**Solutions**:
- Verify backend server is running on port 8080
- Check CORS configuration includes frontend origins
- Ensure `.env` has proper `ALLOWED_ORIGINS` setting

#### Test Execution Hangs
**Causes**: Network issues, target site blocking, or browser crashes  
**Solutions**:
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Use headless mode for stability
uv run friday browser-test test.yaml --headless

# Check target site accessibility
curl -I https://target-site.com
```

#### Memory Issues with Large Test Suites
**Solutions**:
- Use headless mode: `--headless`
- Run tests sequentially instead of parallel
- Reduce timeout values
- Split large suites into smaller ones

### Debug Mode

Enable detailed logging for troubleshooting:
```bash
export LOG_LEVEL=DEBUG
uv run friday browser-test test.yaml --provider openai --headless
```

### Network Diagnostics

Test network connectivity:
```bash
# Check API server
curl http://localhost:8080/api/v1/browser-test/health

# Check WebSocket connectivity
websocat ws://localhost:8080/api/v1/ws/logs

# Test target site accessibility
curl -I https://example.com
```

## Best Practices

### Writing Effective Tests

#### 1. Clear Requirements
```yaml
# Good
requirement: "Test user login with valid credentials and verify dashboard redirect"

# Avoid
requirement: "Test login"
```

#### 2. Provide Context
```yaml
context: |
  Use test account: user@test.com / password123
  Expected behavior: Login should redirect to /dashboard
  Check for welcome message and navigation menu
```

#### 3. Specific Expected Outcomes
```yaml
expected_outcomes:
  - "Login form accepts credentials without errors"
  - "Page redirects to dashboard URL"
  - "Welcome message displays user name"
  - "Navigation menu is visible and functional"
```

### Performance Optimization

#### 1. Use Headless Mode
```bash
# For CI/CD and batch testing
uv run friday browser-test suite.yaml --headless
```

#### 2. Optimize Timeouts
```yaml
# Scenario-specific timeouts
scenarios:
  - name: "Quick Test"
    timeout: 15  # Short timeout for simple tests
  - name: "Complex Workflow"
    timeout: 120  # Longer timeout for complex interactions
```

#### 3. Batch Processing
```bash
# Process multiple suites efficiently
for suite in *.yaml; do
  uv run friday browser-test "$suite" --headless
done
```

### Security Considerations

#### 1. Use Test Environments
- Never test against production systems
- Use dedicated test environments with mock data
- Implement proper access controls

#### 2. Secure Credentials
```yaml
# Avoid hardcoded credentials
context: "Use environment test credentials"

# Better: Reference external configuration
context: "Login with TEST_USER_EMAIL and TEST_USER_PASSWORD from env"
```

#### 3. Screenshot Review
- Review screenshots for sensitive information
- Implement automatic PII detection
- Store screenshots securely

### Reliability Guidelines

#### 1. Implement Retry Logic
```yaml
# Design tests to be idempotent
requirement: "Test login functionality (should work on retry)"
```

#### 2. Handle Dynamic Content
```yaml
context: |
  Page may have loading spinners or dynamic content
  Wait for elements to be fully loaded before interaction
```

#### 3. Cross-Browser Testing
```bash
# Test with different browser configurations
uv run friday browser-test suite.yaml --headless  # Chromium default
```

## Integration Patterns

### CI/CD Integration

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
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install uv
          uv sync
          uv run playwright install chromium --with-deps
      - name: Run browser tests
        run: |
          uv run friday browser-test tests/browser/*.yaml --headless
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Docker Integration

```dockerfile
# Dockerfile for browser testing
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install uv and dependencies
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync

# Install Playwright browsers
RUN uv run playwright install chromium --with-deps

# Copy application
COPY . .

# Run tests
CMD ["uv", "run", "friday", "browser-test", "tests/", "--headless"]
```

## Advanced Usage

### Custom Test Steps

```yaml
scenarios:
  - name: "Advanced E-commerce Test"
    requirement: "Test complete purchase workflow"
    url: "https://shop.example.com"
    test_type: "functional"
    steps:
      - "Navigate to product catalog"
      - "Filter products by category 'Electronics'"
      - "Select first product from results"
      - "Add product to cart"
      - "Proceed to checkout"
      - "Fill shipping information"
      - "Select payment method"
      - "Complete purchase"
    expected_outcomes:
      - "Product is added to cart successfully"
      - "Checkout process completes without errors"
      - "Order confirmation is displayed"
```

### Multi-Page Workflows

```yaml
scenarios:
  - name: "Multi-Page User Journey"
    requirement: "Test user registration and profile setup"
    url: "https://app.example.com"
    test_type: "functional"
    context: |
      Complete user journey:
      1. Register new account
      2. Verify email (simulate)
      3. Complete profile setup
      4. Navigate to dashboard
    steps:
      - "Click 'Sign Up' button"
      - "Fill registration form with valid data"
      - "Submit registration"
      - "Navigate to profile setup"
      - "Upload profile picture"
      - "Fill profile information"
      - "Save profile"
      - "Navigate to dashboard"
```

### Accessibility Testing

```yaml
scenarios:
  - name: "Accessibility Compliance Test"
    requirement: "Verify WCAG 2.1 AA compliance"
    url: "https://example.com"
    test_type: "accessibility"
    context: |
      Check for:
      - Proper heading structure
      - Alt text for images
      - Keyboard navigation
      - Color contrast ratios
      - Screen reader compatibility
    expected_outcomes:
      - "All images have descriptive alt text"
      - "Page structure uses proper heading hierarchy"
      - "All interactive elements are keyboard accessible"
      - "Color contrast meets WCAG AA standards"
```

## Recent Updates (2025-07-05)

### Fixed Issues
- ✅ **API Integration**: Fixed "Upload failed: Not Found" error
- ✅ **WebSocket Connections**: Enhanced real-time monitoring
- ✅ **Frontend Updates**: Proper base URL configuration
- ✅ **Error Handling**: Improved error messages and debugging

### New Features
- ✅ **Execution-Specific WebSockets**: Real-time updates per test execution
- ✅ **Enhanced UI**: Improved browser testing interface
- ✅ **API Verification**: All endpoints tested and confirmed working
- ✅ **Documentation**: Comprehensive troubleshooting guide

### Breaking Changes
None in this update - all changes are backward compatible.

## Support and Resources

### Documentation
- [System Architecture](SYSTEM_ARCHITECTURE.md)
- [API Documentation](apis.md)
- [Developer Onboarding](DEVELOPER_ONBOARDING.md)

### Community
- GitHub Issues: Report bugs and feature requests
- Discussions: Ask questions and share experiences

### Contributing
- Follow the development setup in [DEVELOPER_ONBOARDING.md](DEVELOPER_ONBOARDING.md)
- Submit pull requests with comprehensive tests
- Update documentation for new features