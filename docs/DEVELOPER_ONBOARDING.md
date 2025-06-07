# Developer Onboarding Guide

Welcome to the FRIDAY AI Test Agent project! This guide will help you get up and running quickly as a contributor.

## 🎯 Quick Start (5 minutes)

### Prerequisites Checklist
- [ ] Python 3.12+
- [ ] Node.js 18+
- [ ] [uv](https://docs.astral.sh/uv/) package manager
- [ ] Git
- [ ] VS Code (recommended)

### One-Line Setup
```bash
git clone https://github.com/dipjyotimetia/friday.git && cd friday && uv sync && cp .env.example .env
```

## 🚀 Environment Setup

### 1. Development Environment Options

#### Option A: VS Code Dev Container (Recommended)
```bash
# Install Docker Desktop and VS Code Dev Containers extension
code --install-extension ms-vscode-remote.remote-containers

# Open in container
code .
# Click "Reopen in Container" when prompted
```

#### Option B: Local Development
```bash
# Install Python dependencies
uv sync

# Install frontend dependencies
cd app && npm install && cd ..

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials
```

### 2. Required Environment Variables

Create your `.env` file with these variables:

```bash
# AI Providers (at least one required)
GOOGLE_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here

# Issue Tracking
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your_username
JIRA_API_TOKEN=your_jira_token

GITHUB_ACCESS_TOKEN=your_github_token
GITHUB_USERNAME=your_username

# Documentation
CONFLUENCE_URL=https://your-company.atlassian.net/wiki
CONFLUENCE_USERNAME=your_username
CONFLUENCE_API_TOKEN=your_confluence_token

# Optional: Google Cloud (for deployment)
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_REGION=us-west1
```

## 🧪 Verify Your Setup

### Run the Health Check
```bash
# Test CLI
uv run friday --help

# Test API
uv run uvicorn src.friday.api.main:app --reload --port 8080
curl http://localhost:8080/health

# Test Web App
cd app && npm run dev
# Visit http://localhost:3000
```

### Run Tests
```bash
# Backend tests
uv run pytest tests/ -v

# Frontend tests
cd app && npm test

# Integration tests
uv run pytest tests/integration/ -v
```

## 🏗️ Project Structure Deep Dive

### Backend Architecture (`src/friday/`)
```
src/friday/
├── cli.py              # CLI entry point
├── api/                # FastAPI REST API
│   ├── main.py         # FastAPI app
│   ├── routes/         # API endpoints
│   └── middleware/     # Request middleware
├── agents/             # AI agents
│   ├── test_agent.py   # Test generation
│   └── web_agent.py    # Web crawling
├── connectors/         # External integrations
│   ├── jira.py         # Jira API client
│   ├── github.py       # GitHub API client
│   └── confluence.py   # Confluence API client
├── llm/                # LLM providers
│   ├── gemini.py       # Google Gemini
│   ├── openai.py       # OpenAI GPT
│   └── mistral.py      # Mistral AI
└── services/           # Business logic
    ├── generator.py    # Test case generation
    ├── crawler.py      # Web crawling
    └── embeddings.py   # Vector embeddings
```

### Frontend Architecture (`app/`)
```
app/
├── app/                # Next.js App Router
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Home page
│   └── api/            # API routes
├── components/         # React components
│   ├── features/       # Feature components
│   ├── shared/         # Reusable components
│   └── ui/             # UI primitives
├── hooks/              # Custom React hooks
├── services/           # API client
└── types/              # TypeScript types
```

## 🛠️ Development Workflow

### 1. Choose Your Development Style

#### Feature Development
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes
# Add tests
# Update documentation

# Run quality checks
uv run ruff check
uv run pytest
cd app && npm run lint && npm test

# Commit and push
git commit -m "feat: add your feature"
git push origin feature/your-feature-name
```

#### Bug Fix
```bash
# Create bugfix branch
git checkout -b fix/issue-number

# Write failing test first
# Fix the bug
# Ensure test passes

# Run full test suite
uv run pytest tests/ -v
```

### 2. Code Quality Standards

#### Python Code Style
```bash
# Format code
uv run ruff format

# Check linting
uv run ruff check

# Type checking
uv run mypy src/

# Test coverage
uv run pytest --cov=src/friday tests/
```

#### TypeScript Code Style
```bash
cd app

# Format code
npm run format

# Check linting
npm run lint

# Type checking
npm run type-check

# Test with coverage
npm run test:coverage
```

## 🧩 Common Development Tasks

### Adding a New LLM Provider

1. Create provider class in `src/friday/llm/`:
```python
# src/friday/llm/new_provider.py
from .base import LLMProvider

class NewProvider(LLMProvider):
    def generate(self, prompt: str) -> str:
        # Implementation
        pass
```

2. Register in configuration:
```python
# src/friday/config/llm.py
LLM_PROVIDERS = {
    "new_provider": NewProvider,
    # ... existing providers
}
```

3. Add tests:
```python
# tests/test_new_provider.py
def test_new_provider_generation():
    # Test implementation
    pass
```

### Adding a New API Endpoint

1. Create route handler:
```python
# src/friday/api/routes/new_endpoint.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/new-endpoint")
async def new_endpoint():
    # Implementation
    pass
```

2. Register route:
```python
# src/friday/api/main.py
from .routes.new_endpoint import router as new_router

app.include_router(new_router, prefix="/api/v1")
```

3. Add frontend integration:
```typescript
// app/services/api.ts
export const newEndpoint = async (data: any) => {
  const response = await fetch('/api/new-endpoint', {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return response.json();
};
```

### Adding a New Frontend Feature

1. Create feature component:
```typescript
// app/components/features/new-feature/new-feature.tsx
export function NewFeature() {
  // Implementation
  return <div>New Feature</div>;
}
```

2. Add to main export:
```typescript
// app/components/features/index.ts
export { NewFeature } from './new-feature';
```

3. Integrate in pages:
```typescript
// app/app/page.tsx
import { NewFeature } from '@/components/features';

export default function HomePage() {
  return (
    <div>
      <NewFeature />
    </div>
  );
}
```

## 🚦 Testing Strategy

### Unit Tests
```bash
# Backend unit tests
uv run pytest tests/unit/ -v

# Frontend unit tests
cd app && npm run test:unit
```

### Integration Tests
```bash
# API integration tests
uv run pytest tests/integration/ -v

# End-to-end tests
cd app && npm run test:e2e
```

### Test Coverage Goals
- Backend: > 80%
- Frontend: > 75%
- Critical paths: > 95%

## 📚 Documentation Standards

### Code Documentation
- Python: Use Google-style docstrings
- TypeScript: Use JSDoc comments
- API: OpenAPI/Swagger specifications

### Documentation Updates
When adding features, update:
- [ ] README.md (if user-facing)
- [ ] API documentation
- [ ] Architecture diagrams
- [ ] Sequence diagrams (if workflow changes)

## 🐛 Debugging Guide

### Common Issues

#### Python Environment Issues
```bash
# Reset Python environment
rm -rf .venv
uv sync
```

#### Frontend Build Issues
```bash
# Clear npm cache
cd app
rm -rf node_modules package-lock.json
npm install
```

#### Vector Database Issues
```bash
# Reset ChromaDB
rm -rf data/chroma/
# Restart the application
```

### Debug Tools

#### Backend Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debugger
import pdb; pdb.set_trace()
```

#### Frontend Debugging
```typescript
// React Developer Tools
// Network tab for API calls
// Console for errors

// Add debug logs
console.log('Debug:', data);
```

## 🚀 Ready to Contribute?

1. Check out [good first issues](https://github.com/dipjyotimetia/friday/labels/good%20first%20issue)
2. Read our [Contributing Guidelines](CONTRIBUTING.md)
3. Join our [Discord community](#) (if applicable)
4. Ask questions in GitHub Discussions

## 📞 Getting Help

- **Documentation**: Check [docs/](docs/) folder
- **Issues**: Search existing GitHub issues
- **Architecture**: See [docs/SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md)
- **API Reference**: Visit `/docs` when API is running

Welcome to the team! 🎉
