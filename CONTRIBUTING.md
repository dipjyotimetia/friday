# Contributing to FRIDAY

Thank you for considering contributing to FRIDAY! This document outlines the guidelines for contributing to this project.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you create a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include any error messages or logs

### Suggesting Enhancements

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Explain why this enhancement would be useful
* List some other tools or applications where this enhancement exists, if applicable

### Pull Requests

1. Fork the repo and create your branch from `main`
2. Install development dependencies:
   ```sh
   poetry install
   ```
3. Make sure the tests pass:
   ```sh
   poetry run pytest
   ```
4. Ensure your code follows the project style:
   ```sh
   poetry run ruff format
   ```
5. Make your changes and write clear commit messages
6. Add tests for any new functionality
7. Update documentation as needed
8. Submit your pull request

## Development Setup

1. Install Python 3.13+
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
4. Create a `.env` file with required credentials

## Project Structure

- [`friday/`](friday/): Main package source code
- [`tests/`](tests/): Test suite
- [`docs/`](docs/): Documentation 

## Testing

- Write tests for any new functionality
- Run tests with: `poetry run pytest`
- Ensure test coverage remains high

## Style Guide

- Follow PEP 8 style guide for Python code
- Use type hints 
- Format code using ruff
- Write docstrings for functions and classes

## Documentation

- Update README.md for user-facing changes
- Add docstrings for new functions, classes, and modules
- Keep inline comments clear and necessary

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
