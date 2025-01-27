from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from friday.api import app


async def error_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


app.add_exception_handler(HTTPException, error_handler)
