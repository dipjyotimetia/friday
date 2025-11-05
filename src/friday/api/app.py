"""
Friday API - Production-grade FastAPI application.

This module provides the main FastAPI service for Friday's REST API services
with production-grade error handling, logging, and middleware.
"""

import json
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from friday.api.models import APIResponse, ErrorDetail, ValidationErrorResponse
from friday.api.routes import api_test, browser_test, crawl, generate, health, ws
from friday.config.config import settings
from friday.exceptions import FridayError

logger = logging.getLogger(__name__)
from friday.version import __version__


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    print(f"Starting Friday API version {__version__}")
    yield
    print("Shutting down Friday API")


app = FastAPI(
    title="Friday API",
    version=__version__,
    description="AI-powered testing agent with production-grade reliability",
    lifespan=lifespan,
)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    """Add request ID and context to all requests."""
    request_id = str(uuid.uuid4())
    # Simplified for now

    # Add request ID to request state for access in routes
    request.state.request_id = request_id

    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        # Simplified for now - add proper cleanup if needed
        pass


@app.exception_handler(FridayError)
async def friday_error_handler(request: Request, exc: FridayError):
    """Handle Friday application errors."""
    print(f"Friday application error: {exc.message}")

    return JSONResponse(
        status_code=400,
        content=APIResponse.error_response(
            message=exc.message,
            error_code=exc.error_code,
            details=exc.context,
            request_id=getattr(request.state, "request_id", None),
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    errors = []
    for error in exc.errors():
        errors.append(
            ErrorDetail(
                error_code="VALIDATION_ERROR",
                message=error["msg"],
                field=".".join(str(loc) for loc in error["loc"])
                if error["loc"]
                else None,
                context={"type": error["type"], "input": error.get("input")},
            )
        )

    print(f"Request validation failed: {len(errors)} errors")

    return JSONResponse(
        status_code=422,
        content=ValidationErrorResponse(
            errors=errors, request_id=getattr(request.state, "request_id", None)
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    print(f"HTTP exception: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error_response(
            message=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            request_id=getattr(request.state, "request_id", None),
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    print(f"Unexpected error: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content=APIResponse.error_response(
            message="An unexpected error occurred",
            error_code="INTERNAL_ERROR",
            request_id=getattr(request.state, "request_id", None),
        ).model_dump(),
    )


# Add CORS middleware with WebSocket support
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Friday - AI-powered Testing Agent",
        "version": __version__,
        "docs": "/docs",
    }


app.include_router(generate.router, prefix="/api/v1", tags=["Test Generation"])
app.include_router(crawl.router, prefix="/api/v1", tags=["Web Crawling"])
app.include_router(health.router, prefix="/api/v1", tags=["Health Check"])
app.include_router(api_test.router, prefix="/api/v1", tags=["API Testing"])
app.include_router(browser_test.router, tags=["Browser Testing"])
app.include_router(ws.router, prefix="/api/v1", tags=["WebSocket"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=not settings.is_production,
        log_level=settings.log_level.lower(),
    )
