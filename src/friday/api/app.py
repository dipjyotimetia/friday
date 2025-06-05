"""
Friday API

This module provides the main FastAPI service for Friday's REST API services.
It handles routing, CORS configuration, and serves as the entry point for the API.

Features:
- RESTful API endpoints for test generation
- WebSocket support for real-time updates
- CORS configuration with environment-based origins
- Health check endpoints
- OpenAPI documentation
- API versioning

Available Routes:
- /api/v1/generate: Test case generation endpoints
- /api/v1/crawl: Web crawling and embedding endpoints
- /api/v1/health: Health check endpoints
- /api/v1/test: API testing endpoints
- /api/v1/ws: WebSocket endpoints

Environment Variables:
    ALLOWED_ORIGINS: Comma-separated list of allowed CORS origins
                    Default: "http://localhost:3000"

Example:
    ```bash
    # Run the API server
    uvicorn friday.api.app:app --host 0.0.0.0 --port 8080 --reload
    ```
"""

import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from friday.api.routes import api_test, crawl, generate, health, ws
from friday.version import __version__

app = FastAPI(
    title="Friday API",
    version=__version__,
    description="AI-powered testing agent",
)


# Get allowed origins from environment variable
def get_allowed_origins() -> List[str]:
    origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://192.168.1.40:3000")
    return origins_env.split(",")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router, prefix="/api/v1", tags=["Test Generation"])
app.include_router(crawl.router, prefix="/api/v1", tags=["Web Crawling"])
app.include_router(health.router, prefix="/api/v1", tags=["Health Check"])
app.include_router(api_test.router, prefix="/api/v1", tags=["API Testing"])
app.include_router(ws.router, prefix="/api/v1", tags=["WebSocket"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info",
    )
