"""
Browser Testing API Schemas

This module defines Pydantic models for browser testing API endpoints.
It includes schemas for test scenarios, YAML uploads, test execution,
and result reporting.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class TestType(str, Enum):
    """Test type enumeration."""
    FUNCTIONAL = "functional"
    UI = "ui"
    INTEGRATION = "integration"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"


class TestStatus(str, Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class BrowserTestScenario(BaseModel):
    """Individual test scenario definition."""
    name: str = Field(..., description="Test scenario name")
    requirement: str = Field(..., description="Test requirement in plain English")
    url: str = Field(..., description="Target URL for testing")
    test_type: TestType = Field(default=TestType.FUNCTIONAL, description="Type of test")
    context: Optional[str] = Field(None, description="Additional context for the test")
    expected_outcome: Optional[str] = Field(None, description="Expected test outcome")
    timeout: Optional[int] = Field(30, description="Test timeout in seconds")
    take_screenshots: Optional[bool] = Field(True, description="Whether to take screenshots during test")
    steps: Optional[List[str]] = Field(None, description="Detailed test steps to follow")
    expected_outcomes: Optional[List[str]] = Field(None, description="List of expected outcomes")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class BrowserTestSuite(BaseModel):
    """Complete test suite definition."""
    version: Optional[str] = Field("1.0", description="YAML schema version for backward compatibility")
    name: str = Field(..., description="Test suite name")
    description: Optional[str] = Field(None, description="Test suite description")
    scenarios: List[BrowserTestScenario] = Field(..., description="List of test scenarios")
    global_timeout: Optional[int] = Field(300, description="Global timeout for entire suite")
    global_take_screenshots: Optional[bool] = Field(True, description="Global screenshot setting for all scenarios")
    
    @field_validator('scenarios')
    @classmethod
    def validate_scenarios(cls, v: List[BrowserTestScenario]) -> List[BrowserTestScenario]:
        """Validate scenarios list."""
        if not v:
            raise ValueError('At least one scenario is required')
        return v
    
    @field_validator('version')
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate version format."""
        if not v or not v.replace('.', '').isdigit():
            raise ValueError('Version must be in format like "1.0", "2.1", etc.')
        return v


class BrowserTestResult(BaseModel):
    """Individual test result."""
    scenario_name: str = Field(..., description="Test scenario name")
    status: TestStatus = Field(..., description="Test execution status")
    execution_time: float = Field(..., description="Execution time in seconds")
    success: bool = Field(..., description="Whether test passed")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    screenshot_path: Optional[str] = Field(None, description="Screenshot file path")
    logs: List[str] = Field(default_factory=list, description="Test execution logs")
    actions_taken: List[str] = Field(default_factory=list, description="Actions performed")
    started_at: datetime = Field(..., description="Test start time")
    completed_at: Optional[datetime] = Field(None, description="Test completion time")


class BrowserTestReport(BaseModel):
    """Complete test execution report."""
    suite_name: str = Field(..., description="Test suite name")
    total_tests: int = Field(..., description="Total number of tests")
    passed_tests: int = Field(..., description="Number of passed tests")
    failed_tests: int = Field(..., description="Number of failed tests")
    skipped_tests: int = Field(..., description="Number of skipped tests")
    execution_time: float = Field(..., description="Total execution time")
    success_rate: float = Field(..., description="Success rate percentage")
    results: List[BrowserTestResult] = Field(..., description="Individual test results")
    started_at: datetime = Field(..., description="Suite start time")
    completed_at: datetime = Field(..., description="Suite completion time")
    browser_info: Dict[str, Any] = Field(default_factory=dict, description="Browser information")


class YamlUploadRequest(BaseModel):
    """YAML file upload request."""
    filename: str = Field(..., description="Original filename")
    content: str = Field(..., description="YAML file content")


class YamlUploadResponse(BaseModel):
    """YAML file upload response."""
    message: str = Field(..., description="Upload status message")
    file_id: str = Field(..., description="Unique file identifier")
    parsed_suite: BrowserTestSuite = Field(..., description="Parsed test suite")


class BrowserTestExecutionRequest(BaseModel):
    """Browser test execution request."""
    file_id: Optional[str] = Field(None, description="Uploaded file ID")
    test_suite: Optional[BrowserTestSuite] = Field(None, description="Direct test suite")
    provider: str = Field(default="openai", description="LLM provider")
    headless: bool = Field(default=True, description="Run in headless mode")
    output_format: str = Field(default="json", description="Output format")
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate LLM provider."""
        valid_providers = ['openai', 'gemini', 'ollama', 'mistral']
        if v not in valid_providers:
            raise ValueError(f'Provider must be one of: {valid_providers}')
        return v


class BrowserTestExecutionResponse(BaseModel):
    """Browser test execution response."""
    message: str = Field(..., description="Execution status message")
    execution_id: str = Field(..., description="Unique execution identifier")
    status: TestStatus = Field(..., description="Current execution status")
    report: Optional[BrowserTestReport] = Field(None, description="Test execution report")


class BrowserTestHealthResponse(BaseModel):
    """Browser testing health check response."""
    status: str = Field(..., description="Health status")
    browser_available: bool = Field(..., description="Browser availability")
    playwright_version: str = Field(..., description="Playwright version")
    browser_use_version: str = Field(..., description="Browser-use library version")
    supported_providers: List[str] = Field(..., description="Supported LLM providers")


class BrowserTestLogEntry(BaseModel):
    """Browser test log entry."""
    timestamp: datetime = Field(..., description="Log timestamp")
    level: str = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    execution_id: Optional[str] = Field(None, description="Execution ID")
    scenario_name: Optional[str] = Field(None, description="Scenario name")


class BrowserTestWebSocketMessage(BaseModel):
    """WebSocket message for real-time updates."""
    type: str = Field(..., description="Message type")
    execution_id: str = Field(..., description="Execution ID")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")