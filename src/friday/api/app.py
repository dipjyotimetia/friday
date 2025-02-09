import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from friday.api.routes import api_test, crawl, generate, health, perf_test, ws
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

app.include_router(generate.router, tags=["Test Generation"])
app.include_router(crawl.router, tags=["Web Crawling"])
app.include_router(health.router, tags=["System"])
app.include_router(api_test.router, tags=["API Testing"])
app.include_router(ws.router, tags=["WebSocket"])
app.include_router(perf_test.router, tags=["Performance Testing"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
