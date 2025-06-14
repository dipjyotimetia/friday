from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class BrowserTestRequest(BaseModel):
    """Request model for browser testing"""
    requirement: str = Field(..., description="Test requirement description")
    url: HttpUrl = Field(..., description="Target URL to test")
    test_type: str = Field(default="functional", description="Type of test (functional, ui, integration, etc.)")
    context: Optional[str] = Field(default="", description="Additional context for the test")
    headless: bool = Field(default=True, description="Run browser in headless mode")
    take_screenshots: bool = Field(default=True, description="Whether to take screenshots during execution")
    provider: Optional[str] = Field(default="openai", description="LLM provider to use (openai, gemini, ollama, mistral)")
    
    class Config:
        schema_extra = {
            "example": {
                "requirement": "Test user login functionality with valid credentials",
                "url": "https://example.com/login",
                "test_type": "functional",
                "context": "User should be redirected to dashboard after successful login",
                "headless": True,
                "take_screenshots": True
            }
        }


class BrowserTestCase(BaseModel):
    """Individual browser test case"""
    requirement: str = Field(..., description="Test requirement description")
    url: HttpUrl = Field(..., description="Target URL to test")
    test_type: str = Field(default="functional", description="Type of test")
    context: Optional[str] = Field(default="", description="Additional context")
    take_screenshots: bool = Field(default=True, description="Whether to take screenshots")


class MultipleBrowserTestRequest(BaseModel):
    """Request model for running multiple browser tests"""
    test_cases: List[BrowserTestCase] = Field(..., description="List of browser test cases")
    headless: bool = Field(default=True, description="Run browser in headless mode")
    provider: Optional[str] = Field(default="openai", description="LLM provider to use (openai, gemini, ollama, mistral)")
    
    class Config:
        schema_extra = {
            "example": {
                "test_cases": [
                    {
                        "requirement": "Test user login functionality",
                        "url": "https://example.com/login",
                        "test_type": "functional",
                        "context": "Valid user credentials should allow login"
                    },
                    {
                        "requirement": "Test navigation to dashboard",
                        "url": "https://example.com/dashboard",
                        "test_type": "ui",
                        "context": "Dashboard should display user information"
                    }
                ],
                "headless": True
            }
        }


class BrowserTestResult(BaseModel):
    """Result model for browser test execution"""
    status: str = Field(..., description="Test execution status")
    requirement: str = Field(..., description="Test requirement that was executed")
    url: str = Field(..., description="URL that was tested")
    test_type: str = Field(..., description="Type of test that was executed")
    task_description: Optional[str] = Field(None, description="Generated task description")
    execution_result: Optional[str] = Field(None, description="Detailed execution result")
    screenshots: List[str] = Field(default=[], description="List of screenshot paths/URLs")
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
                "screenshots": ["/screenshots/login_test_1.png", "/screenshots/login_test_2.png"],
                "timestamp": 1640995200.0,
                "success": True,
                "errors": []
            }
        }


class BrowserTestResponse(BaseModel):
    """Response model for browser test API"""
    success: bool = Field(..., description="Whether the API call was successful")
    message: str = Field(..., description="Response message")
    data: Optional[BrowserTestResult] = Field(None, description="Test result data")
    error: Optional[str] = Field(None, description="Error message if any")


class MultipleBrowserTestResponse(BaseModel):
    """Response model for multiple browser tests API"""
    success: bool = Field(..., description="Whether the API call was successful")
    message: str = Field(..., description="Response message")
    data: Optional[List[BrowserTestResult]] = Field(None, description="List of test results")
    report: Optional[str] = Field(None, description="Generated test report")
    summary: Optional[Dict[str, Any]] = Field(None, description="Test execution summary")
    error: Optional[str] = Field(None, description="Error message if any")


class BrowserTestReportRequest(BaseModel):
    """Request model for generating browser test report"""
    results: List[BrowserTestResult] = Field(..., description="List of browser test results")
    provider: Optional[str] = Field(default="openai", description="LLM provider to use (openai, gemini, ollama, mistral)")
    
    class Config:
        schema_extra = {
            "example": {
                "results": [
                    {
                        "status": "completed",
                        "requirement": "Test login",
                        "url": "https://example.com/login",
                        "test_type": "functional",
                        "success": True,
                        "errors": []
                    }
                ]
            }
        }


class BrowserTestReportResponse(BaseModel):
    """Response model for browser test report generation"""
    success: bool = Field(..., description="Whether the report generation was successful")
    message: str = Field(..., description="Response message")
    report: Optional[str] = Field(None, description="Generated test report")
    summary: Optional[Dict[str, Any]] = Field(None, description="Test execution summary")
    error: Optional[str] = Field(None, description="Error message if any")


class YamlScenarioUploadRequest(BaseModel):
    """Request model for uploading YAML test scenarios"""
    provider: Optional[str] = Field(default="openai", description="LLM provider to use")
    headless: bool = Field(default=True, description="Run browser in headless mode")
    execute_immediately: bool = Field(default=False, description="Execute tests immediately after upload")
    
    class Config:
        json_schema_extra = {
            "example": {
                "provider": "openai",
                "headless": True,
                "execute_immediately": False
            }
        }


class YamlScenarioUploadResponse(BaseModel):
    """Response model for YAML scenario upload"""
    success: bool = Field(..., description="Whether the upload was successful")
    message: str = Field(..., description="Response message")
    test_suite_name: Optional[str] = Field(None, description="Name of the uploaded test suite")
    scenarios_count: Optional[int] = Field(None, description="Number of scenarios found")
    scenarios: Optional[List[Dict[str, Any]]] = Field(None, description="Parsed scenarios")
    execution_results: Optional[List[BrowserTestResult]] = Field(None, description="Test results if executed immediately")
    report: Optional[str] = Field(None, description="Test report if executed immediately")
    summary: Optional[Dict[str, Any]] = Field(None, description="Test summary if executed immediately")
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
                "headless": True
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
                "description": "Sample YAML template for browser test scenarios"
            }
        }