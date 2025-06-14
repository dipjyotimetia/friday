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