"""
YAML-based test scenarios parser and validator.

This module handles parsing and validation of YAML test scenario files for browser testing.
"""

import yaml
from typing import List, Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError, HttpUrl

from friday.services.logger import get_logger

logger = get_logger(__name__)


class ViewportConfig(BaseModel):
    """Viewport configuration for browser testing"""

    width: int = Field(default=1920, description="Viewport width")
    height: int = Field(default=1080, description="Viewport height")


class DataSource(BaseModel):
    """Data source configuration for test data"""

    type: str = Field(..., description="Data source type (csv, json, api)")
    source: str = Field(..., description="Data source location (file path or URL)")
    format: Optional[str] = Field(None, description="Data format specification")


class YamlTestScenario(BaseModel):
    """Individual test scenario from YAML file"""

    name: str = Field(..., description="Test scenario name")
    requirement: str = Field(..., description="Test requirement description")
    url: HttpUrl = Field(..., description="Target URL to test")
    test_type: str = Field(default="functional", description="Type of test")
    context: Optional[str] = Field(default="", description="Additional context")
    take_screenshots: bool = Field(
        default=True, description="Whether to take screenshots"
    )
    steps: Optional[List[str]] = Field(default=[], description="Custom test steps")
    expected_outcomes: Optional[List[str]] = Field(
        default=[], description="Expected outcomes"
    )
    tags: Optional[List[str]] = Field(
        default=[], description="Test tags for categorization"
    )
    retry_count: Optional[int] = Field(
        default=0, description="Number of retry attempts"
    )
    timeout: Optional[int] = Field(default=30, description="Test timeout in seconds")
    prerequisites: Optional[List[str]] = Field(
        default=[], description="Test prerequisites (other scenario names)"
    )
    parallel: Optional[bool] = Field(
        default=False, description="Whether test can run in parallel"
    )
    browsers: Optional[List[str]] = Field(
        default=["chromium"], description="Browser types to test with"
    )
    viewport: Optional[ViewportConfig] = Field(
        default=None, description="Custom viewport configuration"
    )
    environment_variables: Optional[Dict[str, str]] = Field(
        default={}, description="Environment variables for the test"
    )
    data_sources: Optional[List[DataSource]] = Field(
        default=[], description="External data sources for test data"
    )
    wait_conditions: Optional[List[str]] = Field(
        default=[], description="Custom wait conditions"
    )
    cleanup_actions: Optional[List[str]] = Field(
        default=[], description="Actions to perform after test completion"
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "Login Test",
                "requirement": "Test user login functionality with valid credentials",
                "url": "https://example.com/login",
                "test_type": "functional",
                "context": "User should be redirected to dashboard after successful login",
                "take_screenshots": True,
                "steps": [
                    "Navigate to login page",
                    "Enter valid username and password",
                    "Click login button",
                    "Verify redirect to dashboard",
                ],
                "expected_outcomes": [
                    "Login form is visible",
                    "Credentials are accepted",
                    "User is redirected to dashboard",
                    "Dashboard displays user information",
                ],
                "tags": ["authentication", "critical"],
            }
        }


class GlobalConfig(BaseModel):
    """Global configuration for test suite"""

    max_parallel_tests: Optional[int] = Field(
        default=1, description="Maximum number of parallel tests"
    )
    default_timeout: Optional[int] = Field(
        default=30, description="Default timeout for all tests"
    )
    default_retry_count: Optional[int] = Field(
        default=0, description="Default retry count for all tests"
    )
    default_viewport: Optional[ViewportConfig] = Field(
        default=None, description="Default viewport for all tests"
    )
    setup_scripts: Optional[List[str]] = Field(
        default=[], description="Scripts to run before test suite"
    )
    teardown_scripts: Optional[List[str]] = Field(
        default=[], description="Scripts to run after test suite"
    )
    environment_variables: Optional[Dict[str, str]] = Field(
        default={}, description="Global environment variables"
    )
    reporting: Optional[Dict[str, Any]] = Field(
        default={}, description="Reporting configuration"
    )


class YamlTestSuite(BaseModel):
    """Test suite containing multiple scenarios from YAML file"""

    name: str = Field(..., description="Test suite name")
    description: Optional[str] = Field(default="", description="Test suite description")
    version: str = Field(default="1.0", description="Test suite version")
    provider: str = Field(default="openai", description="LLM provider to use")
    headless: bool = Field(default=True, description="Run tests in headless mode")
    base_url: Optional[HttpUrl] = Field(
        default=None, description="Base URL for relative URLs"
    )
    global_context: Optional[str] = Field(
        default="", description="Global context for all tests"
    )
    global_config: Optional[GlobalConfig] = Field(
        default=None, description="Global configuration settings"
    )
    scenarios: List[YamlTestScenario] = Field(..., description="List of test scenarios")

    class Config:
        schema_extra = {
            "example": {
                "name": "E-commerce Website Tests",
                "description": "Comprehensive test suite for e-commerce functionality",
                "version": "1.0",
                "provider": "openai",
                "headless": True,
                "base_url": "https://example.com",
                "global_context": "Testing e-commerce platform with standard user flows",
                "scenarios": [],
            }
        }


class YamlScenariosParser:
    """Parser for YAML-based test scenarios"""

    def __init__(self):
        self.logger = logger

    def parse_yaml_file(self, file_path: str) -> YamlTestSuite:
        """
        Parse YAML file and return test suite

        Args:
            file_path: Path to YAML file

        Returns:
            YamlTestSuite object

        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML parsing fails
            ValidationError: If validation fails
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                yaml_content = yaml.safe_load(file)

            self.logger.info(f"Successfully loaded YAML file: {file_path}")
            return self._validate_yaml_content(yaml_content)

        except FileNotFoundError:
            self.logger.error(f"YAML file not found: {file_path}")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"YAML parsing error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error parsing YAML file: {str(e)}")
            raise

    def parse_yaml_content(self, yaml_content: str) -> YamlTestSuite:
        """
        Parse YAML content string and return test suite

        Args:
            yaml_content: YAML content as string

        Returns:
            YamlTestSuite object

        Raises:
            yaml.YAMLError: If YAML parsing fails
            ValidationError: If validation fails
        """
        try:
            parsed_content = yaml.safe_load(yaml_content)
            self.logger.info("Successfully parsed YAML content")
            return self._validate_yaml_content(parsed_content)

        except yaml.YAMLError as e:
            self.logger.error(f"YAML parsing error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error parsing YAML content: {str(e)}")
            raise

    def _validate_yaml_content(self, yaml_data: Dict[str, Any]) -> YamlTestSuite:
        """
        Validate YAML content against schema

        Args:
            yaml_data: Parsed YAML data

        Returns:
            YamlTestSuite object

        Raises:
            ValidationError: If validation fails
        """
        try:
            # Preprocess to handle relative URLs
            processed_data = self.preprocess_yaml_data(yaml_data)

            test_suite = YamlTestSuite(**processed_data)
            self.logger.info(f"Successfully validated test suite: {test_suite.name}")
            return test_suite

        except ValidationError as e:
            self.logger.error(f"YAML validation error: {str(e)}")
            raise

    def convert_to_browser_test_cases(
        self, test_suite: YamlTestSuite
    ) -> List[Dict[str, Any]]:
        """
        Convert YAML test suite to browser test cases format

        Args:
            test_suite: YamlTestSuite object

        Returns:
            List of browser test case dictionaries
        """
        test_cases = []

        for scenario in test_suite.scenarios:
            # Build enhanced context with steps and expected outcomes
            context_parts = []

            if test_suite.global_context:
                context_parts.append(f"Global Context: {test_suite.global_context}")

            if scenario.context:
                context_parts.append(f"Scenario Context: {scenario.context}")

            if scenario.steps:
                context_parts.append(f"Test Steps: {', '.join(scenario.steps)}")

            if scenario.expected_outcomes:
                context_parts.append(
                    f"Expected Outcomes: {', '.join(scenario.expected_outcomes)}"
                )

            enhanced_context = " | ".join(context_parts)

            # Handle relative URLs with base_url
            url = str(scenario.url)
            if test_suite.base_url and not str(scenario.url).startswith(
                ("http://", "https://")
            ):
                url = f"{str(test_suite.base_url).rstrip('/')}/{str(scenario.url).lstrip('/')}"

            test_case = {
                "requirement": scenario.requirement,
                "url": url,
                "test_type": scenario.test_type,
                "context": enhanced_context,
                "take_screenshots": scenario.take_screenshots,
                "scenario_name": scenario.name,
                "tags": scenario.tags,
                "retry_count": scenario.retry_count or 0,
                "timeout": scenario.timeout or 30,
                "prerequisites": scenario.prerequisites or [],
                "parallel": scenario.parallel or False,
                "browsers": scenario.browsers or ["chromium"],
                "viewport": scenario.viewport.dict() if scenario.viewport else None,
                "environment_variables": scenario.environment_variables or {},
                "data_sources": [ds.dict() for ds in scenario.data_sources]
                if scenario.data_sources
                else [],
                "wait_conditions": scenario.wait_conditions or [],
                "cleanup_actions": scenario.cleanup_actions or [],
            }

            test_cases.append(test_case)

        self.logger.info(f"Converted {len(test_cases)} scenarios to browser test cases")
        return test_cases

    def preprocess_yaml_data(self, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess YAML data to handle relative URLs before validation

        Args:
            yaml_data: Raw YAML data

        Returns:
            Preprocessed YAML data
        """
        if "base_url" in yaml_data and "scenarios" in yaml_data:
            base_url = yaml_data["base_url"]

            for scenario in yaml_data["scenarios"]:
                if "url" in scenario:
                    url = scenario["url"]
                    # Convert relative URLs to absolute URLs
                    if not url.startswith(("http://", "https://")):
                        scenario["url"] = f"{base_url.rstrip('/')}/{url.lstrip('/')}"

        return yaml_data

    def generate_sample_yaml(self) -> str:
        """
        Generate a comprehensive sample YAML file content for reference

        Returns:
            Sample YAML content as string
        """
        sample_yaml = """
# Enhanced Browser Test Scenarios YAML File
# This file defines comprehensive test scenarios for automated browser testing

name: "Advanced E-commerce Test Suite"
description: "Comprehensive test suite for e-commerce functionality with advanced features"
version: "2.0"
provider: "openai"  # Options: openai, gemini, ollama, mistral
headless: true
base_url: "https://example.com"
global_context: "Testing e-commerce platform with comprehensive user flows and edge cases"

# Global configuration settings
global_config:
  max_parallel_tests: 3
  default_timeout: 45
  default_retry_count: 2
  default_viewport:
    width: 1920
    height: 1080
  setup_scripts:
    - "Clear browser cache"
    - "Reset test database"
  teardown_scripts:
    - "Cleanup test data"
    - "Generate test report"
  environment_variables:
    TEST_ENV: "staging"
    DEBUG_MODE: "true"
  reporting:
    generate_html_report: true
    include_screenshots: true
    notify_on_failure: true

scenarios:
  - name: "Homepage Load Performance Test"
    requirement: "Verify homepage loads quickly and displays all key elements"
    url: "/"
    test_type: "performance"
    context: "Homepage should load within 3 seconds and display navigation, hero section, and featured products"
    take_screenshots: true
    timeout: 10
    retry_count: 1
    browsers: ["chromium", "firefox"]
    viewport:
      width: 1920
      height: 1080
    steps:
      - "Navigate to homepage"
      - "Measure page load time"
      - "Verify page title contains 'E-commerce'"
      - "Check navigation menu visibility"
      - "Verify hero section loads"
      - "Count featured products (should be >= 4)"
    expected_outcomes:
      - "Page loads within 3 seconds"
      - "Navigation menu is visible and functional"
      - "Hero section displays promotional content"
      - "At least 4 featured products are shown"
      - "No JavaScript errors in console"
    tags: ["homepage", "performance", "critical"]
    wait_conditions:
      - "DOM content loaded"
      - "All images loaded"
    cleanup_actions:
      - "Clear page cache"

  - name: "User Registration with Validation"
    requirement: "Test user registration with comprehensive input validation"
    url: "/register"
    test_type: "functional"
    context: "Test registration form with valid/invalid data, error handling, and success flow"
    take_screenshots: true
    timeout: 30
    retry_count: 2
    prerequisites: ["Homepage Load Performance Test"]
    data_sources:
      - type: "csv"
        source: "test_data/user_registration.csv"
        format: "email,password,expected_result"
    environment_variables:
      REGISTRATION_ENDPOINT: "/api/register"
    steps:
      - "Navigate to registration page"
      - "Test form validation with invalid data"
      - "Fill form with valid user data"
      - "Submit registration form"
      - "Verify success message and redirect"
    expected_outcomes:
      - "Form validation works for invalid inputs"
      - "Valid registration succeeds"
      - "Success message is displayed"
      - "User is redirected to dashboard"
      - "Confirmation email is sent"
    tags: ["registration", "authentication", "validation", "critical"]
    cleanup_actions:
      - "Delete test user account"

  - name: "Cross-browser Product Search"
    requirement: "Test product search functionality across multiple browsers"
    url: "/search"
    test_type: "functional"
    context: "Search should return relevant products and handle edge cases across different browsers"
    take_screenshots: true
    timeout: 25
    parallel: true
    browsers: ["chromium", "firefox", "webkit"]
    steps:
      - "Navigate to search page"
      - "Test empty search query"
      - "Search for 'laptop' and verify results"
      - "Test search filters"
      - "Test pagination if available"
    expected_outcomes:
      - "Empty search shows appropriate message"
      - "Search returns relevant laptop products"
      - "Filters work correctly"
      - "Pagination functions properly"
    tags: ["search", "cross-browser", "functionality"]

  - name: "Mobile Responsive Design Test"
    requirement: "Verify complete mobile responsiveness across different screen sizes"
    url: "/"
    test_type: "ui"
    context: "Test responsive design on various mobile device sizes and orientations"
    take_screenshots: true
    timeout: 20
    browsers: ["chromium"]
    viewport:
      width: 375
      height: 667
    steps:
      - "Navigate to homepage in mobile viewport"
      - "Test hamburger menu functionality"
      - "Verify touch targets are adequate (>44px)"
      - "Test form inputs on mobile"
      - "Check image scaling and loading"
      - "Test landscape orientation"
    expected_outcomes:
      - "Mobile navigation menu works smoothly"
      - "All touch targets are adequately sized"
      - "No horizontal scrolling occurs"
      - "Images scale properly"
      - "Text remains readable at all sizes"
    tags: ["responsive", "mobile", "ui", "accessibility"]

  - name: "Accessibility Compliance Test"
    requirement: "Verify WCAG 2.1 AA compliance for key pages"
    url: "/"
    test_type: "accessibility"
    context: "Test keyboard navigation, screen reader compatibility, and color contrast"
    take_screenshots: true
    timeout: 35
    steps:
      - "Navigate using only keyboard"
      - "Check color contrast ratios"
      - "Verify alt text for images"
      - "Test form labels and ARIA attributes"
      - "Check heading hierarchy"
    expected_outcomes:
      - "All interactive elements are keyboard accessible"
      - "Color contrast meets WCAG AA standards"
      - "Images have appropriate alt text"
      - "Forms are properly labeled"
      - "Heading structure is logical"
    tags: ["accessibility", "wcag", "compliance", "keyboard"]
    cleanup_actions:
      - "Reset accessibility settings"
"""
        return sample_yaml.strip()
