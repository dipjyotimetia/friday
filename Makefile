# Friday AI Testing Agent - Enhanced Makefile
# Commands for development, testing, and deployment

.PHONY: help install install-all update update-backend update-frontend upgrade upgrade-backend upgrade-frontend lock outdated add add-dev remove deps-info dev dev-backend dev-frontend

# Default target
help: ## Show this help message
	@echo "Friday AI Testing Agent - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation Commands
install: ## Install backend dependencies only
	uv sync
	cp .env.example .env

install-all: ## Install both backend and frontend dependencies
	@echo "Installing backend dependencies..."
	uv sync
	cp .env.example .env
	@echo "Installing frontend dependencies..."
	cd app && npm install
	@echo "✅ All dependencies installed"

# Dependency Management
.PHONY: update update-backend update-frontend upgrade upgrade-backend upgrade-frontend lock outdated
update: ## Update all dependencies (backend and frontend)
	@echo "🔄 Updating all dependencies..."
	@$(MAKE) update-backend
	@$(MAKE) update-frontend
	@echo "✅ All dependencies updated"

update-backend: ## Update backend Python dependencies
	@echo "🐍 Updating Python dependencies..."
	uv sync --upgrade
	@echo "✅ Backend dependencies updated"

update-frontend: ## Update frontend Node.js dependencies
	@echo "📦 Updating Node.js dependencies..."
	cd app && npm update
	@echo "✅ Frontend dependencies updated"

upgrade: ## Upgrade all dependencies to latest versions (potentially breaking)
	@echo "⚠️  Upgrading all dependencies to latest versions..."
	@echo "This might introduce breaking changes!"
	@read -p "Continue? [y/N] " confirm && [[ $$confirm == [yY] ]] || exit 1
	@$(MAKE) upgrade-backend
	@$(MAKE) upgrade-frontend
	@echo "✅ All dependencies upgraded"

upgrade-backend: ## Upgrade backend dependencies to latest versions
	@echo "🐍 Upgrading Python dependencies to latest versions..."
	uv sync --upgrade-package "*"
	@echo "✅ Backend dependencies upgraded"

upgrade-frontend: ## Upgrade frontend dependencies to latest versions
	@echo "📦 Upgrading Node.js dependencies to latest versions..."
	cd app && npm update --save
	cd app && npx npm-check-updates -u && npm install
	@echo "✅ Frontend dependencies upgraded"

lock: ## Update dependency lock files without upgrading
	@echo "🔒 Updating lock files..."
	uv lock
	cd app && npm install --package-lock-only
	@echo "✅ Lock files updated"

outdated: ## Check for outdated dependencies
	@echo "📊 Checking for outdated dependencies..."
	@echo "\n=== Backend (Python) ==="
	@echo "Current dependencies:"
	uv tree || echo "Unable to show dependency tree"
	@echo "\n=== Frontend (Node.js) ==="
	cd app && npm outdated || echo "No outdated Node.js packages found"

add: ## Add a new dependency (usage: make add PACKAGE=package-name)
	@if [ -z "$(PACKAGE)" ]; then \
		echo "❌ Please specify a package: make add PACKAGE=package-name"; \
		exit 1; \
	fi
	@echo "➕ Adding Python package: $(PACKAGE)"
	uv add $(PACKAGE)

add-dev: ## Add a new development dependency (usage: make add-dev PACKAGE=package-name)
	@if [ -z "$(PACKAGE)" ]; then \
		echo "❌ Please specify a package: make add-dev PACKAGE=package-name"; \
		exit 1; \
	fi
	@echo "➕ Adding Python dev package: $(PACKAGE)"
	uv add --dev $(PACKAGE)

remove: ## Remove a dependency (usage: make remove PACKAGE=package-name)
	@if [ -z "$(PACKAGE)" ]; then \
		echo "❌ Please specify a package: make remove PACKAGE=package-name"; \
		exit 1; \
	fi
	@echo "➖ Removing Python package: $(PACKAGE)"
	uv remove $(PACKAGE)

deps-info: ## Show dependency information
	@echo "📋 Dependency Information:"
	@echo "\n=== Python Environment ==="
	@echo "uv version: $(shell uv --version 2>/dev/null || echo 'Not found')"
	@echo "Python version: $(shell uv run python --version 2>/dev/null || echo 'Not found')"
	@echo "Virtual environment: $(shell uv venv --show-path 2>/dev/null || echo 'Not found')"
	@echo "\n=== Node Environment ==="
	@echo "npm version: $(shell npm --version 2>/dev/null || echo 'Not found')"
	@echo "Node version: $(shell node --version 2>/dev/null || echo 'Not found')"
	@echo "\n=== Project Dependencies ==="
	@echo "Backend packages:"
	@uv tree --depth 1 2>/dev/null || echo "Unable to show dependency tree"
	@echo "\nFrontend packages:"
	@cd app && npm list --depth=0 2>/dev/null || echo "Unable to show npm packages"

browser-setup: ## Install Playwright browsers for browser testing
	@echo "Installing Playwright browsers..."
	uv run playwright install chromium --with-deps
	@echo "✅ Playwright browsers installed"

setup: install-all browser-setup ## Complete setup (install dependencies + browsers)
	@echo "✅ Setup complete! Run 'make dev' to start development servers"

# Development Commands
dev: ## Start both backend API and frontend in parallel
	@echo "🚀 Starting Friday development servers..."
	@echo "Backend API: http://localhost:8080"
	@echo "Frontend: http://localhost:3000"
	@echo "Press Ctrl+C to stop both servers"
	@$(MAKE) -j2 dev-backend dev-frontend

dev-backend: ## Start only the backend API server
	@echo "🔧 Starting backend API server on port 8080..."
	uv run uvicorn friday.api.app:app --reload --port 8080 --host 0.0.0.0

dev-frontend: ## Start only the frontend development server
	@echo "🎨 Starting frontend development server on port 3000..."
	cd app && npm run dev

webui: ## Start the Friday Web UI using CLI command
	@echo "🌐 Starting Friday Web UI..."
	uv run friday webui

open-browser: ## Open the Friday Web UI in browser
	uv run friday open

# Build Commands
.PHONY: build build-backend build-frontend
build: ## Build both backend and frontend for production
	@echo "🏗️ Building Friday for production..."
	@$(MAKE) build-backend
	@$(MAKE) build-frontend
	@echo "✅ Build complete"

build-backend: ## Build backend package
	@echo "Building backend..."
	uv build

build-frontend: ## Build frontend for production
	@echo "Building frontend..."
	cd app && npm run build

# Testing Commands
.PHONY: test test-backend test-frontend test-browser
test: ## Run all tests (backend and frontend)
	@echo "🧪 Running all tests..."
	@$(MAKE) test-backend
	@$(MAKE) test-frontend

test-backend: ## Run backend tests with coverage
	@echo "Running backend tests..."
	uv run pytest tests/ -v --cov=src --cov-report=term-missing

test-frontend: ## Run frontend tests
	@echo "Running frontend tests..."
	cd app && npm test

test-browser: ## Run browser automation tests
	@echo "Running browser tests..."
	uv run friday browser-test examples/sample_browser.yaml --provider openai --headless

# Code Quality
.PHONY: lint lint-backend lint-frontend format format-backend format-frontend
lint: ## Run linting for both backend and frontend
	@echo "🔍 Running linters..."
	@$(MAKE) lint-backend
	@$(MAKE) lint-frontend

lint-backend: ## Run backend linting (ruff)
	@echo "Linting backend Python code..."
	uv run ruff check src/ tests/

lint-frontend: ## Run frontend linting (ESLint)
	@echo "Linting frontend TypeScript/React code..."
	cd app && npm run lint

format: ## Format code for both backend and frontend
	@echo "✨ Formatting code..."
	@$(MAKE) format-backend
	@$(MAKE) format-frontend

format-backend: ## Format backend Python code
	@echo "Formatting backend code..."
	uv run ruff format src/ tests/

format-frontend: ## Format frontend code
	@echo "Formatting frontend code..."
	cd app && npm run format

# CLI Commands
.PHONY: generate crawl browser-test-yaml
generate: ## Generate test cases from Jira (example: make generate JIRA_KEY=PROJ-123)
	uv run friday generate --jira-key $(JIRA_KEY) --output test_cases.md

crawl: ## Crawl website (example: make crawl URL=https://example.com)
	uv run friday crawl $(URL) --provider openai --max-pages 10

browser-test-yaml: ## Run browser tests (example: make browser-test-yaml FILE=scenarios.yaml)
	uv run friday browser-test $(FILE) --provider openai --headless

# Utility Commands
.PHONY: clean reset-db version health
clean: ## Clean build artifacts and caches
	@echo "🧹 Cleaning build artifacts..."
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
	rm -rf app/.next/ app/out/ app/node_modules/.cache/
	@echo "✅ Cleaned"

reset-db: ## Reset database and clear embeddings
	@echo "🗄️ Resetting database..."
	rm -rf data/chroma/ data/friday/ app/data/cache/
	@echo "✅ Database reset"

version: ## Show Friday version
	uv run friday version

health: ## Check health of all services
	@echo "🏥 Checking service health..."
	@echo "Backend API:"
	@curl -s http://localhost:8080/health || echo "❌ Backend not responding"
	@echo "\nFrontend:"
	@curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend responding" || echo "❌ Frontend not responding"

# API and Type Generation
.PHONY: api-spec api-types types
api-spec: ## Generate OpenAPI specification
	@echo "Generating OpenAPI specification..."
	uv run python -c "from friday.api.app import app; import json; json.dump(app.openapi(), open('openapi.json', 'w'), indent=2)"
	@echo "OpenAPI spec generated at openapi.json"

api-types: api-spec ## Generate TypeScript types from OpenAPI spec
	@echo "Installing openapi-typescript if not present..."
	cd app && npm list openapi-typescript >/dev/null 2>&1 || npm install --save-dev openapi-typescript
	@echo "Generating TypeScript types from OpenAPI spec..."
	npx openapi-typescript openapi.json --output app/types/api.ts
	@echo "TypeScript types generated at app/types/api.ts"

types: api-types ## Alias for api-types

# Docker Commands
.PHONY: docker-build docker-up docker-down
docker-build: ## Build Docker images
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-up: ## Start services with Docker Compose
	@echo "🐳 Starting services with Docker..."
	docker-compose up

docker-down: ## Stop Docker services
	docker-compose down

# Environment Commands
.PHONY: env-check
env-check: ## Check environment variables and dependencies
	@echo "🔍 Environment Check:"
	@echo "Python version: $(shell python --version 2>/dev/null || echo 'Not found')"
	@echo "Node version: $(shell node --version 2>/dev/null || echo 'Not found')"
	@echo "uv version: $(shell uv --version 2>/dev/null || echo 'Not found')"
	@echo "Docker version: $(shell docker --version 2>/dev/null || echo 'Not found')"
	@echo ""
	@echo "Required environment variables:"
	@echo "OPENAI_API_KEY: $(if $(OPENAI_API_KEY),✅ Set,❌ Not set)"
	@echo "JIRA_URL: $(if $(JIRA_URL),✅ Set,❌ Not set)"
	@echo "GITHUB_ACCESS_TOKEN: $(if $(GITHUB_ACCESS_TOKEN),✅ Set,❌ Not set)"

# Legacy Commands (for compatibility)
.PHONY: run
run: ## Legacy command - generate test cases
	uv run python main.py --gh-issue 5 --gh-repo dipjyotimetia/FRIDAY --confluence-id "1540097" --output test_cases.md
	uv run python main.py --jira-key "FRID-1" --confluence-id "1540097" --output test_cases.md