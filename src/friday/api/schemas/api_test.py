from openai import BaseModel


class ApiTestRequest(BaseModel):
    spec_file: str
    base_url: str
    output: str = "api_test_report.md"


class ApiTestResponse(BaseModel):
    message: str
    total_tests: int
    paths_tested: int
