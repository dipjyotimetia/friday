from pydantic import BaseModel


class PerfTestRequest(BaseModel):
    spec_file: str
    base_url: str
    users: int = 10
    duration: int = 30
    output: str = "perf_test_report.md"


class PerfTestResponse(BaseModel):
    message: str
    total_requests: int
    avg_response_time: float
    error_rate: float
