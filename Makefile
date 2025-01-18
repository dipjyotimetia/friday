.PHONY:install
install:
    poetry install
    poetry shell
    cp .env.example .env

.PHONY:clean
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    find . -type f -name "*.pyd" -delete
    find . -type f -name ".coverage" -delete
    find . -type d -name "*.egg-info" -exec rm -rf {} +
    find . -type d -name "*.egg" -exec rm -rf {} +
    find . -type d -name ".pytest_cache" -exec rm -rf {} +
    find . -type d -name ".tox" -exec rm -rf {} +
    find . -type d -name "build" -exec rm -rf {} +
    find . -type d -name "dist" -exec rm -rf {} +

.PHONY:test
test:
    poetry run pytest tests/ -v --cov=src

.PHONY:lint
lint:
    ruff format

.PHONY:format
format:
    poetry run black .

.PHONY:run
run:
    poetry run python main.py --gh-issue 5 --gh-repo dipjyotimetia/FRIDAY --confluence-id "1540097" --output test_cases.md
    poetry run python main.py --jira-key "FRID-1" --confluence-id "1540097" --output test_cases.md 
