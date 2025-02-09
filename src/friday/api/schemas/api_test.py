from typing import Optional

from openai import BaseModel


class ApiTestRequest(BaseModel):
    spec_file: Optional[str] = None
    base_url: str
    output: str = "api_test_report.md"

    class Config:
        arbitrary_types_allowed = True


class ApiTestResponse(BaseModel):
    message: str
    total_tests: int
    paths_tested: int
