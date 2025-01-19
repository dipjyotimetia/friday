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

1. Install Python 3.12
2. Install poetry:
   ```sh 
   curl -sSL https://install.python-poetry.org | python3 -
   ```
3. Clone your fork and set up the environment:
   ```sh
   git clone https://github.com/dipjyotimetia/friday.git
   cd friday
   chmod +x prerequisites.sh
   ./prerequisites.sh
   poetry install
   ```
4. Create a `.env` file based on [.env.example](.env.example)

## Project Structure

- [src/friday/](src/friday/): Main package source code 
- [tests/](tests/): Test suite
- [docs/](docs/): Documentation including sequence diagrams
- [data/](data/): Data storage for chroma DB
