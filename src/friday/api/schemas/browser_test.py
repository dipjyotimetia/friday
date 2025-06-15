from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BrowserTestResult(BaseModel):
    """Result model for browser test execution"""

    status: str = Field(..., description="Test execution status")
    requirement: str = Field(..., description="Test requirement that was executed")
    url: str = Field(..., description="URL that was tested")
    test_type: str = Field(..., description="Type of test that was executed")
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

    class Config:
        schema_extra = {
            "example": {
                "status": "completed",
                "requirement": "Test user login functionality",
                "url": "https://example.com/login",
                "test_type": "functional",
                "task_description": "Navigate to login page and test authentication",
                "execution_result": "Successfully logged in user and navigated to dashboard",
                "screenshots": [
                    "/screenshots/login_test_1.png",
                    "/screenshots/login_test_2.png",
                ],
                "timestamp": 1640995200.0,
                "success": True,
                "errors": [],
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
