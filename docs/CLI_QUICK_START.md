# Friday CLI Quick Start Guide

Get up and running with Friday CLI in under 5 minutes.

## 🚀 Installation

```bash
# Clone and setup
git clone https://github.com/dipjyotimetia/friday.git
cd friday
uv sync

# Interactive configuration
uv run friday setup
```

## ⚡ Most Common Commands

### 1. Start Web UI (Recommended for Beginners)
```bash
friday webui
```
This starts both the API server and web interface, then opens your browser automatically.

### 2. Open Existing Web UI
```bash
friday open                    # Open main interface
friday open --feature browser  # Go directly to browser testing
```

### 3. Generate Test Cases
```bash
# From Jira issue
friday generate --jira-key PROJ-123 --output tests.md

# From GitHub issue  
friday generate --gh-repo owner/repo --gh-issue 42 --output tests.md
```

### 4. Browser Testing
```bash
# First, get a template
friday webui  # Use "Download Template" in browser testing section

# Then run tests
friday browser-test scenarios.yaml --provider openai
```

### 5. Web Crawling
```bash
friday crawl https://docs.example.com --max-pages 10
```

## 🆘 Getting Help

```bash
friday --help                 # All commands
friday generate --help        # Generate command options
friday browser-test --help    # Browser testing options
friday webui --help          # Web UI options
```

## 📚 Next Steps

- **Complete CLI Reference**: [CLI_REFERENCE.md](CLI_REFERENCE.md)
- **Browser Testing Guide**: [BROWSER_TESTING.md](BROWSER_TESTING.md)
- **API Documentation**: [apis.md](apis.md)
- **System Architecture**: [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)

## 🐛 Troubleshooting

### Command not found
```bash
# Make sure you're in the project directory
cd friday
uv run friday --help
```

### Authentication errors
```bash
# Run interactive setup
friday setup
```

### Web UI won't start
```bash
# Check if ports are in use
friday webui --port 4000 --api-port 9000
```

---

**Need more help?** See the [Complete CLI Reference](CLI_REFERENCE.md) or [open an issue](https://github.com/dipjyotimetia/friday/issues).