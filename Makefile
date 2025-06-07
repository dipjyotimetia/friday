.PHONY: install
install:
	uv sync
	cp .env.example .env

.PHONY: clean
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
	rm -rf .venv uv.lock

.PHONY: test
test:
	uv run pytest tests/ -v --cov=src

.PHONY: lint
lint:
	uv run ruff format

.PHONY: format
format:
	uv run ruff format

.PHONY: run
run:
	uv run python main.py --gh-issue 5 --gh-repo dipjyotimetia/FRIDAY --confluence-id "1540097" --output test_cases.md
	uv run python main.py --jira-key "FRID-1" --confluence-id "1540097" --output test_cases.md

.PHONY: api-spec
api-spec:
	@echo "Generating OpenAPI specification..."
	uv run python -c "from friday.api.app import app; import json; json.dump(app.openapi(), open('openapi.json', 'w'), indent=2)"
	@echo "OpenAPI spec generated at openapi.json"

.PHONY: api-types
api-types: api-spec
	@echo "Installing openapi-typescript if not present..."
	cd app && npm list openapi-typescript >/dev/null 2>&1 || npm install --save-dev openapi-typescript
	@echo "Generating TypeScript types from OpenAPI spec..."
	npx openapi-typescript openapi.json --output app/types/api.ts
	@echo "TypeScript types generated at app/types/api.ts"

.PHONY: types
types: api-types