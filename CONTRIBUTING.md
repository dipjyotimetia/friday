# Contributing to FRIDAY

Thank you for considering contributing to FRIDAY! This document outlines the guidelines for contributing to this project.

## Code of Conduct

By participating in this project, you are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). Please report unacceptable behavior via GitHub issues.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include any error messages or logs
* Include Python version and environment details

### Suggesting Enhancements

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Explain why this enhancement would be useful to FRIDAY's AI test case generation
* List similar implementations in other test automation tools, if applicable

### Pull Requests

1. Fork the repo and create your branch from `main`
2. Install development dependencies:
   ```sh
   poetry install
   ```
3. Run tests:
   ```sh
   poetry run pytest tests/ -v
   ```
4. Format code:
   ```sh
   poetry run ruff format
   ```
5. Make your changes and write clear commit messages
6. Add tests in [tests/](tests/) directory for new functionality
7. Update documentation in [docs/](docs/) as needed
8. Submit your pull request

## Development Setup

### Quick Start
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/friday.git
cd friday

# Set up environment
uv sync
cp .env.example .env
# Edit .env with your credentials

# Install frontend dependencies
cd app && npm install && cd ..

# Verify setup
uv run pytest tests/ -v
cd app && npm test && cd ..
```

### Development Environment Options

#### Option 1: VS Code Dev Container (Recommended)
- Install Docker Desktop and VS Code Dev Containers extension
- Open project in VS Code and click "Reopen in Container"
- All dependencies are pre-installed

#### Option 2: Local Development
- Python 3.12+ with uv package manager
- Node.js 18+ with npm
- Docker (for ChromaDB and testing)

### Environment Configuration
Required environment variables in `.env`:
```bash
# AI Providers (at least one required)
GOOGLE_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key

# Issue Tracking
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your_username
JIRA_API_TOKEN=your_token

GITHUB_ACCESS_TOKEN=your_github_token
GITHUB_USERNAME=your_username

# Documentation
CONFLUENCE_URL=https://your-company.atlassian.net/wiki
CONFLUENCE_USERNAME=your_username
CONFLUENCE_API_TOKEN=your_token
```

## Development Workflow

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/description-of-feature

# Make changes following our coding standards
# Add comprehensive tests
# Update documentation

# Run quality checks
uv run ruff format          # Format Python code
uv run ruff check           # Lint Python code
uv run pytest tests/ -v    # Run backend tests
cd app && npm run lint && npm test  # Frontend checks

# Commit with conventional commit format
git commit -m "feat: add description of feature"
```

### 2. Bug Fix Workflow
```bash
# Create bugfix branch
git checkout -b fix/issue-123-description

# Write failing test first (TDD approach)
# Fix the bug
# Ensure all tests pass
# Update documentation if needed

git commit -m "fix: resolve issue with specific component"
```

### 3. Code Quality Standards

#### Python Standards
- **Formatting**: Use Ruff formatter (`uv run ruff format`)
- **Linting**: Follow Ruff rules (`uv run ruff check`)
- **Type Hints**: Use type annotations for all functions
- **Docstrings**: Google-style docstrings for all public methods
- **Testing**: Minimum 80% code coverage

#### TypeScript Standards
- **Formatting**: Prettier configuration (`npm run format`)
- **Linting**: ESLint rules (`npm run lint`)
- **Type Safety**: Strict TypeScript configuration
- **Components**: Functional components with TypeScript
- **Testing**: Jest with React Testing Library

### 4. Testing Requirements

#### Backend Testing
```bash
# Unit tests
uv run pytest tests/unit/ -v

# Integration tests
uv run pytest tests/integration/ -v

# Test coverage
uv run pytest --cov=src/friday tests/ --cov-report=html
```

#### Frontend Testing
```bash
cd app

# Unit tests
npm run test:unit

# Component tests
npm run test:components

# End-to-end tests
npm run test:e2e

# Coverage report
npm run test:coverage
```

#### Test Writing Guidelines
- Write tests before implementing features (TDD)
- Test both happy paths and edge cases
- Mock external dependencies
- Use descriptive test names
- Group related tests in classes/describe blocks

## Submitting Changes

### 1. Pre-submission Checklist
- [ ] Feature branch created from latest `main`
- [ ] All tests pass locally
- [ ] Code follows project style guidelines
- [ ] Documentation updated (if applicable)
- [ ] Commit messages follow conventional format
- [ ] No sensitive data in commits
- [ ] Pull request description is clear and detailed

### 2. Pull Request Process
1. **Push to your fork**: `git push origin your-branch-name`
2. **Create pull request** on GitHub
3. **Fill out PR template** completely
4. **Wait for code review** from maintainers
5. **Address feedback** promptly
6. **Squash commits** if requested
7. **Wait for approval** and merge

### 3. Pull Request Guidelines

#### Title Format
Follow conventional commit format:
```
feat: add support for new LLM provider
fix: resolve authentication issue with Jira
docs: update API documentation
test: add integration tests for crawler
```

#### Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added for new functionality
```

### 4. Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(api): add endpoint for batch test generation
fix(crawler): handle timeout errors gracefully
docs: update installation instructions
test(llm): add unit tests for OpenAI provider
```

## Project Structure

- [app](app): Friday desktop application
- [src/friday/](src/friday/): Main package source code 
- [tests/](tests/): Test suite
- [docs/](docs/): Documentation including sequence diagrams
- [data/](data/): Data storage for chroma DB
- [scripts/](scripts/): Utility scripts
- [friday/](friday/): CLI entry point
- [pyproject.toml](pyproject.toml): Poetry configuration
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md): Code of Conduct
- [CONTRIBUTING.md](CONTRIBUTING.md): Contribution guidelines
- [LICENSE](LICENSE): MIT License
- [README.md](README.md): Project overview