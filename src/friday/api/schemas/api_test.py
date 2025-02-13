from typing import Optional

from fastapi import UploadFile
from openai import BaseModel


class ApiTestRequest(BaseModel):
    base_url: str
    output: str = "api_test_report.md"
    spec_file: Optional[str] = None
    spec_upload: Optional[UploadFile] = None
    provider: str = "vertex"


class ApiTestResponse(BaseModel):
    message: str
    total_tests: int
    paths_tested: int
