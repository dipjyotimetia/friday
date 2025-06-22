from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BrowserTestResult(BaseModel):
    """Result model for browser test execution"""

    status: str = Field(..., description="Test execution status")
    requirement: str = Field(..., description="Test requirement that was executed")
    url: str = Field(..., description="URL that was tested")
    test_type: str = Field(..., description="Type of test that was executed")
    test_id: Optional[str] = Field(None, description="Unique test identifier")
    task_description: Optional[str] = Field(
        None, description="Generated task description"
    )
    execution_result: Optional[str] = Field(
        None, description="Detailed execution result"
    )
    screenshots: List[str] = Field(
        default=[], description="List of screenshot paths/URLs"
    )
    timestamp: Optional[float] = Field(None, description="Execution timestamp")
    success: bool = Field(..., description="Whether the test was successful")
    errors: List[str] = Field(default=[], description="List of errors if any")
    detailed_errors: List[Dict[str, Any]] = Field(
        default=[], description="Detailed error information with categorization"
    )
    browser_type: Optional[str] = Field(
        default="chromium", description="Browser type used for testing"
    )
    session_id: Optional[str] = Field(None, description="Browser session identifier")

    class Config:
        schema_extra = {
            "example": {
                "status": "completed",
                "requirement": "Test user login functionality",
                "url": "https://example.com/login",
                "test_type": "functional",
                "test_id": "20241219_143022_a1b2c3d4",
                "task_description": "Navigate to login page and test authentication",
                "execution_result": "Successfully logged in user and navigated to dashboard",
                "screenshots": [
                    "20241219_143022_a1b2c3d4/initial_page_20241219_143022_123.png",
                    "20241219_143022_a1b2c3d4/final_result_20241219_143025_456.png",
                ],
                "timestamp": 1640995200.0,
                "success": True,
                "errors": [],
                "detailed_errors": [],
                "browser_type": "chromium",
                "session_id": "session_123",
            }
        }


class YamlScenarioUploadRequest(BaseModel):
    """Request model for uploading YAML test scenarios"""

    provider: Optional[str] = Field(default="openai", description="LLM provider to use")
    headless: bool = Field(default=True, description="Run browser in headless mode")
    execute_immediately: bool = Field(
        default=False, description="Execute tests immediately after upload"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "openai",
                "headless": True,
                "execute_immediately": False,
            }
        }


class YamlScenarioUploadResponse(BaseModel):
    """Response model for YAML scenario upload"""

    success: bool = Field(..., description="Whether the upload was successful")
    message: str = Field(..., description="Response message")
    test_suite_name: Optional[str] = Field(
        None, description="Name of the uploaded test suite"
    )
    scenarios_count: Optional[int] = Field(
        None, description="Number of scenarios found"
    )
    scenarios: Optional[List[Dict[str, Any]]] = Field(
        None, description="Parsed scenarios"
    )
    execution_results: Optional[List[BrowserTestResult]] = Field(
        None, description="Test results if executed immediately"
    )
    report: Optional[str] = Field(
        None, description="Test report if executed immediately"
    )
    summary: Optional[Dict[str, Any]] = Field(
        None, description="Test summary if executed immediately"
    )
    error: Optional[str] = Field(None, description="Error message if any")


class YamlScenarioExecuteRequest(BaseModel):
    """Request model for executing YAML scenarios"""

    yaml_content: str = Field(..., description="YAML content containing test scenarios")
    provider: Optional[str] = Field(default="openai", description="LLM provider to use")
    headless: bool = Field(default=True, description="Run browser in headless mode")

    class Config:
        json_schema_extra = {
            "example": {
                "yaml_content": "name: 'Test Suite'\nscenarios:\n  - name: 'Homepage Test'\n    requirement: 'Test homepage loads'\n    url: 'https://example.com'",
                "provider": "openai",
                "headless": True,
            }
        }


class YamlScenarioExecuteResponse(BaseModel):
    """Response model for YAML scenario execution"""

    success: bool = Field(..., description="Whether the execution was successful")
    message: str = Field(..., description="Response message")
    test_suite_name: str = Field(..., description="Name of the executed test suite")
    scenarios_count: int = Field(..., description="Number of scenarios executed")
    results: List[BrowserTestResult] = Field(..., description="Test execution results")
    report: str = Field(..., description="Generated test report")
    summary: Dict[str, Any] = Field(..., description="Test execution summary")
    error: Optional[str] = Field(None, description="Error message if any")


class BrowserSessionStats(BaseModel):
    """Browser session statistics"""

    total_sessions: int = Field(..., description="Total number of sessions")
    active_sessions: int = Field(..., description="Number of active sessions")
    max_sessions: int = Field(..., description="Maximum allowed sessions")
    total_tests_executed: int = Field(
        ..., description="Total tests executed across all sessions"
    )
    browser_types: Dict[str, int] = Field(..., description="Breakdown by browser type")
    session_timeout: int = Field(..., description="Session timeout in seconds")


class StorageStats(BaseModel):
    """Storage statistics for screenshots and test data"""

    total_size_bytes: int = Field(..., description="Total storage size in bytes")
    total_size_mb: float = Field(..., description="Total storage size in MB")
    total_files: int = Field(..., description="Total number of files")
    test_count: int = Field(..., description="Number of test directories")
    base_path: str = Field(..., description="Base storage path")


class TestMetricsResponse(BaseModel):
    """Response model for test metrics"""

    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    session_stats: BrowserSessionStats = Field(..., description="Session statistics")
    storage_stats: StorageStats = Field(..., description="Storage statistics")
    timestamp: float = Field(..., description="Response timestamp")


class ScreenshotInfo(BaseModel):
    """Screenshot information model"""

    filename: str = Field(..., description="Screenshot filename")
    path: str = Field(..., description="Relative path to screenshot")
    size: int = Field(..., description="File size in bytes")
    created_at: str = Field(..., description="Creation timestamp")
    url: str = Field(..., description="API URL to access screenshot")


class TestScreenshotsResponse(BaseModel):
    """Response model for test screenshots"""

    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    test_id: str = Field(..., description="Test identifier")
    screenshots: List[ScreenshotInfo] = Field(..., description="List of screenshots")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Test metadata")


class ValidationResponse(BaseModel):
    """Response model for YAML validation"""

    success: bool = Field(..., description="Whether validation was successful")
    message: str = Field(..., description="Validation message")
    test_suite_name: Optional[str] = Field(None, description="Name of test suite")
    scenarios_count: Optional[int] = Field(None, description="Number of scenarios")
    scenarios: Optional[List[Dict[str, str]]] = Field(
        None, description="Scenario summaries"
    )
    errors: Optional[List[str]] = Field(None, description="Validation errors")


class YamlTemplateSample(BaseModel):
    """Sample YAML template for test scenarios"""

    template_content: str = Field(..., description="Sample YAML template content")
    description: str = Field(..., description="Template description")

    class Config:
        json_schema_extra = {
            "example": {
                "template_content": "name: 'Sample Test Suite'\nscenarios: []",
                "description": "Sample YAML template for browser test scenarios",
            }
        }
