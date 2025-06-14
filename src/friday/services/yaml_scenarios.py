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


class YamlTestScenario(BaseModel):
    """Individual test scenario from YAML file"""
    name: str = Field(..., description="Test scenario name")
    requirement: str = Field(..., description="Test requirement description")
    url: HttpUrl = Field(..., description="Target URL to test")
    test_type: str = Field(default="functional", description="Type of test")
    context: Optional[str] = Field(default="", description="Additional context")
    take_screenshots: bool = Field(default=True, description="Whether to take screenshots")
    steps: Optional[List[str]] = Field(default=[], description="Custom test steps")
    expected_outcomes: Optional[List[str]] = Field(default=[], description="Expected outcomes")
    tags: Optional[List[str]] = Field(default=[], description="Test tags for categorization")
    
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
                    "Verify redirect to dashboard"
                ],
                "expected_outcomes": [
                    "Login form is visible",
                    "Credentials are accepted",
                    "User is redirected to dashboard",
                    "Dashboard displays user information"
                ],
                "tags": ["authentication", "critical"]
            }
        }


class YamlTestSuite(BaseModel):
    """Test suite containing multiple scenarios from YAML file"""
    name: str = Field(..., description="Test suite name")
    description: Optional[str] = Field(default="", description="Test suite description")
    version: str = Field(default="1.0", description="Test suite version")
    provider: str = Field(default="openai", description="LLM provider to use")
    headless: bool = Field(default=True, description="Run tests in headless mode")
    base_url: Optional[HttpUrl] = Field(default=None, description="Base URL for relative URLs")
    global_context: Optional[str] = Field(default="", description="Global context for all tests")
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
                "scenarios": []
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
            with open(file_path, 'r', encoding='utf-8') as file:
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
    
    def convert_to_browser_test_cases(self, test_suite: YamlTestSuite) -> List[Dict[str, Any]]:
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
                context_parts.append(f"Expected Outcomes: {', '.join(scenario.expected_outcomes)}")
            
            enhanced_context = " | ".join(context_parts)
            
            # Handle relative URLs with base_url
            url = str(scenario.url)
            if test_suite.base_url and not str(scenario.url).startswith(('http://', 'https://')):
                url = f"{str(test_suite.base_url).rstrip('/')}/{str(scenario.url).lstrip('/')}"
            
            test_case = {
                "requirement": scenario.requirement,
                "url": url,
                "test_type": scenario.test_type,
                "context": enhanced_context,
                "take_screenshots": scenario.take_screenshots,
                "scenario_name": scenario.name,
                "tags": scenario.tags
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
        if 'base_url' in yaml_data and 'scenarios' in yaml_data:
            base_url = yaml_data['base_url']
            
            for scenario in yaml_data['scenarios']:
                if 'url' in scenario:
                    url = scenario['url']
                    # Convert relative URLs to absolute URLs
                    if not url.startswith(('http://', 'https://')):
                        scenario['url'] = f"{base_url.rstrip('/')}/{url.lstrip('/')}"
        
        return yaml_data
    
    def generate_sample_yaml(self) -> str:
        """
        Generate a sample YAML file content for reference
        
        Returns:
            Sample YAML content as string
        """
        sample_yaml = """
# Browser Test Scenarios YAML File
# This file defines test scenarios for automated browser testing

name: "Sample E-commerce Test Suite"
description: "Comprehensive test suite for e-commerce functionality"
version: "1.0"
provider: "openai"  # Options: openai, gemini, ollama, mistral
headless: true
base_url: "https://example.com"
global_context: "Testing e-commerce platform with standard user flows"

scenarios:
  - name: "Homepage Load Test"
    requirement: "Verify homepage loads correctly and displays key elements"
    url: "/"
    test_type: "functional"
    context: "Homepage should display navigation, hero section, and featured products"
    take_screenshots: true
    steps:
      - "Navigate to homepage"
      - "Verify page title"
      - "Check navigation menu"
      - "Verify hero section"
      - "Check featured products section"
    expected_outcomes:
      - "Page loads within 3 seconds"
      - "Navigation menu is visible"
      - "Hero section displays correctly"
      - "Featured products are shown"
    tags: ["homepage", "performance", "ui"]

  - name: "User Registration Test"
    requirement: "Test user registration with valid data"
    url: "/register"
    test_type: "functional"
    context: "User should be able to register with valid email and password"
    take_screenshots: true
    steps:
      - "Navigate to registration page"
      - "Fill in registration form"
      - "Submit form"
      - "Verify success message"
    expected_outcomes:
      - "Registration form is displayed"
      - "Form accepts valid input"
      - "Success message is shown"
      - "User is redirected appropriately"
    tags: ["registration", "authentication", "critical"]

  - name: "Product Search Test"
    requirement: "Test product search functionality"
    url: "/search"
    test_type: "functional"
    context: "Search should return relevant products for valid queries"
    take_screenshots: true
    steps:
      - "Navigate to search page"
      - "Enter search query"
      - "Click search button"
      - "Verify search results"
    expected_outcomes:
      - "Search form is accessible"
      - "Search returns relevant results"
      - "Results are properly formatted"
      - "Pagination works if applicable"
    tags: ["search", "functionality"]

  - name: "Mobile Responsive Test"
    requirement: "Verify site is mobile responsive"
    url: "/"
    test_type: "ui"
    context: "Site should adapt to mobile screen sizes"
    take_screenshots: true
    steps:
      - "Navigate to homepage"
      - "Resize viewport to mobile size"
      - "Check navigation menu"
      - "Verify content layout"
    expected_outcomes:
      - "Mobile navigation works"
      - "Content is properly sized"
      - "Touch targets are adequate"
      - "No horizontal scrolling"
    tags: ["responsive", "mobile", "ui"]
"""
        return sample_yaml.strip()