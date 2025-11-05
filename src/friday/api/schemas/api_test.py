from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel


class ApiTestRequest(BaseModel):
    base_url: str
    output: str = "api_test_report.md"
    spec_file: Optional[str] = None
    spec_upload: Optional[UploadFile] = None
    provider: str = "vertex"


class ApiTestResponse(BaseModel):
    success: bool = True
    message: str
    total_tests: int
    paths_tested: int
    passed_tests: int
    failed_tests: int
    error_tests: int
    success_rate: float
