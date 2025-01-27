from fastapi import FastAPI

from friday.api.routes import crawl, generate, health
from friday.version import __version__

app = FastAPI(
    title="Friday API",
    version=__version__,
    description="AI-powered test case generation API",
)


app.include_router(generate.router, tags=["Test Generation"])
app.include_router(crawl.router, tags=["Web Crawling"])
app.include_router(health.router, tags=["System"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
