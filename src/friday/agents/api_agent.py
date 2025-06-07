"""
API Test Generator Module

This module provides an automated API testing solution using OpenAPI specifications
and LLM-powered test case generation. It supports real-time logging via WebSocket
and comprehensive test reporting.

Features:
- Automated test case generation from OpenAPI specs
- Multiple LLM provider support
- Real-time progress logging
- Retry mechanisms for reliability
- Async HTTP client with connection pooling
- Markdown report generation
- WebSocket-based logging

Example:
    ```python
    async with ApiTestGenerator("openapi.yaml", provider="openai") as generator:
        spec = await generator.load_spec()
        if generator.validate_spec(spec):
            test_cases = await generator.create_test_cases("/users", "GET", spec)
            await generator.execute_tests(test_cases, "http://api.example.com")
            report = await generator.generate_report()
    ```
"""

import json
import logging
from datetime import datetime
from typing import Dict, List

import httpx
import yaml
from langchain_community.agent_toolkits import OpenAPIToolkit
from langchain_community.agent_toolkits.openapi.base import create_openapi_agent
from langchain_community.tools.json.tool import JsonSpec
from langchain_community.utilities import RequestsWrapper
from tenacity import retry, stop_after_attempt, wait_exponential

from friday.llm.llm import ModelProvider, get_llm_client

logger = logging.getLogger(__name__)


class ApiTestGenerator:
    """
    A class for generating and executing API tests based on OpenAPI specifications.

    This class combines LLM capabilities with OpenAPI specifications to automatically
    generate, execute, and report on API tests. It supports multiple LLM providers
    and includes robust error handling and retry mechanisms.

    Attributes:
        spec_path (str): Path to the OpenAPI specification file
        http_client (httpx.AsyncClient): Async HTTP client for making requests
        max_retries (int): Maximum number of retry attempts for failed operations
        llm: Language model client for test generation
        test_results (List): Collection of test execution results
        api_spec (JsonSpec): Parsed OpenAPI specification
        toolkit (OpenAPIToolkit): OpenAPI toolkit for LLM integration
        agent: LLM agent for test case generation

    Example:
        ```python
        async with ApiTestGenerator("specs/api.yaml") as generator:
            spec = await generator.load_spec()
            test_cases = await generator.create_test_cases("/users", "GET", spec)
            await generator.execute_tests(test_cases, "http://api.example.com")
        ```
    """

    def __init__(self, openapi_spec_path: str, provider: ModelProvider = "openai"):
        """
        Initialize the API test generator.

        Args:
            openapi_spec_path (str): Path to the OpenAPI specification file
            provider (ModelProvider, optional): LLM provider to use. Defaults to "openai"

        Raises:
            RuntimeError: If initialization fails (e.g., invalid spec file)
        """
        self.spec_path = openapi_spec_path
        self.http_client = httpx.AsyncClient(
            verify=True,
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )
        self.max_retries = 3  # Add max retries
        self.llm = get_llm_client(provider)
        self.test_results = []
        try:
            with open(self.spec_path) as f:
                raw_api_spec = yaml.safe_load(f)
                self.api_spec = JsonSpec(dict_=raw_api_spec, max_value_length=4000)
        except Exception as e:
            logger.error("Failed to load API spec", error=str(e), path=self.spec_path)
            raise RuntimeError(f"Failed to initialize API generator: {str(e)}")
        self.requests_wrapper = RequestsWrapper(
            headers={},  # Add any default headers here
            verify=True,  # Enable SSL verification
        )

        # Initialize OpenAPI toolkit
        self.toolkit = OpenAPIToolkit.from_llm(
            llm=self.llm,
            json_spec=self.api_spec,
            requests_wrapper=self.requests_wrapper,
            allow_dangerous_requests=True,  # Allow dangerous requests
            verbose=True,
        )

        self.agent = create_openapi_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            verbose=True,
            handle_parsing_errors=True,  # Add error handling
            max_iterations=2,  # Limit iterations for safety
            return_intermediate_steps=True,  # Return intermediate steps
        )

    async def _send_log(self, message: str) -> None:
        """
        Send a log message through the WebSocket logger.

        Args:
            message (str): Message to be logged

        Note:
            Uses standard logger instead of WebSocket broadcasting
        """
        try:
            logger.info(message)
        except Exception as e:
            logger.error(f"Error logging message: {message} - {str(e)}")

    async def load_spec(self) -> Dict:
        """
        Load and parse the OpenAPI specification file.

        Returns:
            Dict: Parsed OpenAPI specification

        Raises:
            yaml.YAMLError: If the specification file is invalid
            FileNotFoundError: If the specification file doesn't exist
        """
        with open(self.spec_path) as f:
            return yaml.safe_load(f)

    def validate_spec(self, spec: Dict) -> bool:
        """
        Validate the OpenAPI specification.
        """
        required_fields = ["openapi", "info", "paths"]
        return all(field in spec for field in required_fields)

    def _extract_sample_data_from_schema(self, schema: Dict) -> Dict:
        """Extract sample data from OpenAPI schema definition."""
        if not isinstance(schema, dict):
            return {}

        if "example" in schema:
            return schema["example"]

        if "properties" in schema:
            sample = {}
            for prop, prop_schema in schema["properties"].items():
                if "example" in prop_schema:
                    sample[prop] = prop_schema["example"]
                elif prop_schema.get("type") == "string":
                    sample[prop] = f"sample_{prop}"
                elif prop_schema.get("type") == "integer":
                    sample[prop] = 123
                elif prop_schema.get("type") == "boolean":
                    sample[prop] = True
                elif prop_schema.get("type") == "array":
                    sample[prop] = []
            return sample

        # Handle schema references
        if "$ref" in schema:
            # For now, return empty dict for references
            # In a full implementation, you'd resolve the reference
            return {}

        return {}

    def _generate_test_scenarios_from_spec(
        self, endpoint: str, method: str, operation_spec: Dict
    ) -> List[Dict]:
        """Generate comprehensive test scenarios based on OpenAPI specification."""
        test_cases = []
        method_upper = method.upper()

        # Basic successful test case
        basic_test = {
            "name": f"Valid {method_upper} {endpoint} - Success",
            "method": method_upper,
            "endpoint": endpoint,
            "payload": {},
            "headers": {"Content-Type": "application/json"},
            "expected_status": [200, 201],
        }

        # Extract request body schema for POST/PUT/PATCH
        if (
            method.lower() in ["post", "put", "patch"]
            and "requestBody" in operation_spec
        ):
            request_body = operation_spec["requestBody"]
            if "content" in request_body:
                for content_type, content_spec in request_body["content"].items():
                    if "schema" in content_spec:
                        sample_payload = self._extract_sample_data_from_schema(
                            content_spec["schema"]
                        )
                        basic_test["payload"] = sample_payload
                        basic_test["headers"]["Content-Type"] = content_type
                        break

        # Extract path parameters
        path_params = {}
        if "parameters" in operation_spec:
            for param in operation_spec["parameters"]:
                if param.get("in") == "path":
                    if param.get("schema", {}).get("type") == "integer":
                        path_params[param["name"]] = 1
                    else:
                        path_params[param["name"]] = f"test_{param['name']}"

        # Replace path parameters in endpoint
        for param_name, param_value in path_params.items():
            endpoint = endpoint.replace(f"{{{param_name}}}", str(param_value))
            basic_test["endpoint"] = endpoint

        test_cases.append(basic_test)

        # Authentication/Authorization tests
        if "security" in operation_spec:
            auth_test = basic_test.copy()
            auth_test["name"] = f"Unauthorized {method_upper} {endpoint} - 401"
            auth_test["headers"] = {
                "Content-Type": "application/json"
            }  # Remove auth headers
            auth_test["expected_status"] = [401, 403]
            test_cases.append(auth_test)

        # Invalid request body test for POST/PUT/PATCH
        if method.lower() in ["post", "put", "patch"]:
            invalid_test = basic_test.copy()
            invalid_test["name"] = f"Invalid {method_upper} {endpoint} - Bad Request"
            invalid_test["payload"] = {"invalid": "data"}
            invalid_test["expected_status"] = [400]
            test_cases.append(invalid_test)

        # Not found test for operations with path parameters
        if path_params:
            not_found_test = basic_test.copy()
            not_found_test["name"] = f"Not Found {method_upper} {endpoint} - 404"
            # Use non-existent ID
            for param_name in path_params.keys():
                not_found_test["endpoint"] = not_found_test["endpoint"].replace(
                    str(path_params[param_name]), "99999"
                )
            not_found_test["expected_status"] = [404]
            test_cases.append(not_found_test)

        # Validation tests based on response schemas
        responses = operation_spec.get("responses", {})
        for status_code, response_spec in responses.items():
            if status_code.startswith("4") or status_code.startswith("5"):
                error_test = basic_test.copy()
                error_test["name"] = f"Error {method_upper} {endpoint} - {status_code}"
                error_test["expected_status"] = [int(status_code)]
                # Modify request to trigger this error
                if status_code == "400":
                    error_test["payload"] = (
                        None if method.lower() in ["post", "put", "patch"] else {}
                    )
                test_cases.append(error_test)

        return test_cases

    async def create_test_cases(
        self, endpoint: str, method: str, spec: Dict
    ) -> List[Dict]:
        """
        Generate test cases for a specific API endpoint.

        This method generates comprehensive test cases covering:
        - Basic functionality with valid data
        - Authentication/authorization scenarios
        - Input validation and error cases
        - Edge cases and boundary values
        - HTTP status code validation

        Args:
            endpoint (str): API endpoint path
            method (str): HTTP method (GET, POST, etc.)
            spec (Dict): OpenAPI specification

        Returns:
            List[Dict]: List of generated test cases

        Example:
            ```python
            test_cases = await generator.create_test_cases(
                "/users",
                "POST",
                spec
            )
            ```
        """
        await self._send_log(f"Generating test cases for {method} {endpoint}")

        # Early validation
        if "paths" not in spec or endpoint not in spec["paths"]:
            await self._send_log(f"Endpoint {endpoint} not found in spec")
            return self._generate_default_test_case(endpoint, method)

        endpoint_spec = spec["paths"][endpoint]
        if method.lower() not in endpoint_spec:
            await self._send_log(f"Method {method} not found for endpoint {endpoint}")
            return self._generate_default_test_case(endpoint, method)

        operation_spec = endpoint_spec[method.lower()]

        try:
            # Generate test scenarios from OpenAPI spec
            test_cases = self._generate_test_scenarios_from_spec(
                endpoint, method, operation_spec
            )

            await self._send_log(
                f"Generated {len(test_cases)} test cases for {method} {endpoint}"
            )
            return test_cases

        except Exception as e:
            await self._send_log(f"Error generating test cases: {str(e)}")
            return self._generate_default_test_case(endpoint, method)

    def _generate_default_test_case(self, endpoint: str, method: str) -> List[Dict]:
        """Generate a basic default test case."""
        return [
            {
                "name": f"Basic {method} {endpoint} test",
                "method": method.upper(),
                "endpoint": endpoint,
                "payload": {},
                "headers": {"Content-Type": "application/json"},
                "expected_status": [200, 201],
            }
        ]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    async def execute_tests(self, test_cases: List[Dict], base_url: str) -> None:
        """
        Execute the generated test cases against a target API.

        Features:
        - Automatic retries for failed requests
        - Real-time progress logging
        - Comprehensive result collection
        - Error handling and reporting

        Args:
            test_cases (List[Dict]): List of test cases to execute
            base_url (str): Base URL of the target API

        Example:
            ```python
            await generator.execute_tests(test_cases, "http://api.example.com")
            ```
        """
        try:
            for test in test_cases:
                await self._send_log(f"Executing test: {test['name']}")
                try:
                    response = await self.http_client.request(
                        method=test["method"],
                        url=f"{base_url.rstrip('/')}/{test['endpoint'].lstrip('/')}",
                        json=test.get("payload"),
                        headers=test.get("headers", {}),
                        timeout=30.0,
                    )

                    try:
                        response_data = response.json()
                        await self._send_log(
                            f"Test {test['name']} completed with status code {response.status_code}"
                        )
                    except ValueError:
                        response_data = {"raw": response.text}

                    # Check if response status matches expected status codes
                    expected_statuses = test.get("expected_status", [200, 201])
                    is_pass = response.status_code in expected_statuses

                    self.test_results.append(
                        {
                            "test_name": test["name"],
                            "status": "PASS" if is_pass else "FAIL",
                            "response_code": response.status_code,
                            "expected_status": expected_statuses,
                            "response": response_data,
                        }
                    )
                except Exception as e:
                    await self._send_log(
                        f"Test {test['name']} failed with error: {str(e)}"
                    )
                    self.test_results.append(
                        {"test_name": test["name"], "status": "ERROR", "error": str(e)}
                    )
                    print(f"Test execution failed: {str(e)}")

        except Exception as e:
            print(f"Test suite execution failed: {str(e)}")
            await self._send_log(f"Test suite execution failed: {str(e)}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()

    async def generate_report(self) -> str:
        """
        Generate a Markdown report of test execution results.

        The report includes:
        - Test execution timestamp
        - Summary statistics
        - Detailed results for each test case
        - Response data and error messages

        Returns:
            str: Markdown-formatted test report

        Example:
            ```python
            report = await generator.generate_report()
            with open("test_report.md", "w") as f:
                f.write(report)
            ```
        """
        await self._send_log("Generating test execution report")
        try:
            report = f"""# API Test Results
        Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        ## Summary
        - Total Tests: {len(self.test_results)}
        - Passed: {sum(1 for t in self.test_results if t["status"] == "PASS")}
        - Failed: {sum(1 for t in self.test_results if t["status"] == "FAIL")}
        - Errors: {sum(1 for t in self.test_results if t["status"] == "ERROR")}

        ## Detailed Results\n"""

            for result in self.test_results:
                report += f"\n### {result['test_name']}\n"
                report += f"Status: **{result['status']}**\n"
                if result["status"] == "ERROR":
                    report += f"Error: {result['error']}\n"
                else:
                    report += f"Response Code: {result['response_code']}\n"
                    if "expected_status" in result:
                        report += f"Expected Status: {result['expected_status']}\n"
                    report += f"Response: ```json\n{json.dumps(result['response'], indent=2)}\n```\n"

            await self._send_log("Report generation completed")
            return report
        except Exception as e:
            await self._send_log(f"Error generating report: {str(e)}")
            return f"Error generating report: {str(e)}"
