import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from friday.api.routes import api_test, crawl, generate, health, ws
from friday.version import __version__

app = FastAPI(
    title="Friday API",
    version=__version__,
    description="AI-powered test case generation API",
)


# Get allowed origins from environment variable
def get_allowed_origins() -> List[str]:
    origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
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

    uvicorn.run(app, host="0.0.0.0", port=8080)
