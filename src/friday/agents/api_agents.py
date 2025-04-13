"""
API Test Agents Module

This module provides specialized agents for API testing based on OpenAPI specifications.
It separates the concerns of test case creation and test execution into distinct classes
for better modularity and flexibility.

Features:
- Base agent with shared functionality
- Specialized agent for test case creation
- Specialized agent for test execution
- Multiple LLM provider support
- Real-time progress logging
- Comprehensive reporting

Example:
    ```python
    # Create test cases
    async with ApiTestCreator("openapi.yaml", provider="openai") as creator:
        spec = await creator.load_spec()
        if creator.validate_spec(spec):
            test_cases = await creator.create_test_cases("/users", "GET", spec)

    # Execute tests
    async with ApiTestExecutor(provider="openai") as executor:
        await executor.execute_tests(test_cases, "http://api.example.com")
        report = await executor.generate_report()
    ```
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List

import httpx
import structlog
import yaml
from crewai import Agent, Crew, Process, Task
from tenacity import retry, stop_after_attempt, wait_exponential

from friday.llm.llm import ModelProvider, get_llm_client
from friday.services.logger import ws_logger

logger = structlog.get_logger(__name__)


class BaseApiTestAgent:
    """
    Base class for API test agents with common functionality.

    This class provides shared utilities and methods for API test agents.
    It is not meant to be instantiated directly.

    Attributes:
        max_retries (int): Maximum number of retry attempts for failed operations
        llm: Language model client for test generation
        provider (ModelProvider): LLM provider being used
    """

    def __init__(self, provider: ModelProvider = "openai"):
        """
        Initialize the base API test agent.

        Args:
            provider (ModelProvider, optional): LLM provider to use. Defaults to "openai"
        """
        self.max_retries = 3
        self.llm = get_llm_client(provider)
        self.provider = provider

    async def _send_log(self, message: str) -> None:
        """
        Send a log message through the WebSocket logger.

        Args:
            message (str): Message to be logged

        Note:
            Falls back to print if WebSocket logger is not available
        """
        try:
            if ws_logger:
                await ws_logger.broadcast(message)
            else:
                print(f"Warning: WebSocket logger not initialized: {message}")
        except Exception as e:
            print(f"Error sending log: {message} - {str(e)}")


class ApiTestCreator(BaseApiTestAgent):
    """
    Agent responsible for generating API test cases from OpenAPI specifications.

    This class handles loading and validating OpenAPI specifications and generating
    comprehensive test cases using CrewAI.

    Attributes:
        spec_path (str): Path to the OpenAPI specification file
        raw_api_spec (Dict): Raw parsed OpenAPI specification
    """

    def __init__(self, openapi_spec_path: str, provider: ModelProvider = "openai"):
        """
        Initialize the API test creator.

        Args:
            openapi_spec_path (str): Path to the OpenAPI specification file
            provider (ModelProvider, optional): LLM provider to use. Defaults to "openai"

        Raises:
            RuntimeError: If initialization fails (e.g., invalid spec file)
        """
        super().__init__(provider)
        self.spec_path = openapi_spec_path

        try:
            with open(self.spec_path) as f:
                self.raw_api_spec = yaml.safe_load(f)
        except Exception as e:
            logger.error("Failed to load API spec", error=str(e), path=self.spec_path)
            raise RuntimeError(f"Failed to initialize API test creator: {str(e)}")

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

        Args:
            spec (Dict): OpenAPI specification to validate

        Returns:
            bool: True if the specification is valid, False otherwise
        """
        required_fields = ["openapi", "info", "paths"]
        return all(field in spec for field in required_fields)

    async def create_test_cases(
        self, endpoint: str, method: str, spec: Dict
    ) -> List[Dict]:
        """
        Generate test cases for a specific API endpoint.

        This method uses CrewAI to generate comprehensive test cases covering:
        - Basic functionality
        - Edge cases
        - Error scenarios
        - Security considerations

        Args:
            endpoint (str): API endpoint path
            method (str): HTTP method (GET, POST, etc.)
            spec (Dict): OpenAPI specification

        Returns:
            List[Dict]: List of generated test cases

        Example:
            ```python
            test_cases = await creator.create_test_cases(
                "/users",
                "POST",
                spec
            )
            ```
        """
        attempts = 0
        default_test = {
            "name": f"Basic {method} {endpoint} test",
            "method": method,
            "endpoint": endpoint,
            "payload": {},
            "headers": {},
        }

        # Early validation
        if "paths" not in spec or endpoint not in spec["paths"]:
            await self._send_log(f"Endpoint {endpoint} not found in spec")
            return [default_test]

        endpoint_spec = spec["paths"][endpoint]
        if method.lower() not in endpoint_spec:
            await self._send_log(f"Method {method} not found for endpoint {endpoint}")
            return [default_test]

        while attempts < self.max_retries:
            try:
                await self._send_log(f"Generating test cases for {method} {endpoint}")

                # Create CrewAI agent for test case generation
                test_generator_agent = Agent(
                    role="API Test Case Generator",
                    goal="Generate comprehensive API test cases based on OpenAPI specifications",
                    backstory="""You are an expert in API testing with years of experience in test automation.
                    Your specialty is analyzing API specifications and creating thorough test cases that
                    cover basic functionality, edge cases, error scenarios, and security considerations.""",
                    verbose=True,
                    allow_delegation=False,
                    llm=self.llm,
                )

                # Create task for the agent
                endpoint_spec_json = json.dumps(endpoint_spec[method.lower()], indent=2)
                test_case_task = Task(
                    description=f"""
                    Generate a comprehensive set of test cases for the {method} method of the {endpoint} endpoint.
                    
                    Follow these guidelines:
                    1. Understand the OpenAPI Specification: Carefully analyze the provided specification for the endpoint and method, including request parameters, request body, headers, and expected responses.
                    2. Cover Basic Functionality: Generate test cases to validate the core functionality of the API endpoint. These tests should cover typical use cases and ensure the API behaves as expected under normal conditions.
                    3. Explore Edge Cases: Identify and create test cases for edge cases, such as boundary values, unusual input combinations, and unexpected data.
                    4. Test Error Scenarios: Develop test cases to verify how the API handles errors, such as invalid input, missing parameters, authentication failures, and server errors.
                    5. Prioritize Security: Include tests that check for common security vulnerabilities, such as injection attacks, authentication bypasses, and data breaches.
                    
                    Here is the OpenAPI specification for the {method} method of the {endpoint} endpoint:
                    ```json
                    {endpoint_spec_json}
                    ```
                    
                    Return test cases in this EXACT JSON array format:
                    [
                        {{
                            "name": "test name - be descriptive",
                            "method": "{method}",
                            "endpoint": "{endpoint}",
                            "payload": {{
                                // Add required request payload based on spec
                            }},
                            "headers": {{
                                // Add required headers based on spec
                            }}
                        }}
                    ]
                    
                    Required fields:
                    - name: Descriptive test name
                    - method: Must be {method}
                    - endpoint: Must be {endpoint} 
                    - payload: Include request body if required
                    - headers: Include required headers
                    """,
                    agent=test_generator_agent,
                    expected_output="A JSON array of test cases following the specified format",
                )

                # Create crew with the agent and task
                crew = Crew(
                    agents=[test_generator_agent],
                    tasks=[test_case_task],
                    verbose=True,
                    process=Process.sequential,
                )

                # Execute the crew to generate test cases
                result = crew.kickoff()

                # Process the results
                if not result:
                    raise ValueError("Empty response from agent")

                # Try to parse as JSON
                try:
                    if isinstance(result, str):
                        # Find JSON array in the response if it's embedded in text
                        result_text = result.strip()
                        if "[" in result_text and "]" in result_text:
                            start_idx = result_text.find("[")
                            end_idx = result_text.rfind("]") + 1
                            json_text = result_text[start_idx:end_idx]
                            parsed_result = json.loads(json_text)
                        else:
                            parsed_result = json.loads(result_text)
                    else:
                        parsed_result = result

                    if isinstance(parsed_result, dict):
                        return [parsed_result]
                    elif isinstance(parsed_result, list) and parsed_result:
                        return parsed_result
                    else:
                        raise ValueError("Invalid response structure")
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON response")

            except Exception as e:
                attempts += 1
                error_msg = f"Test generation attempt {attempts}/{self.max_retries} failed: {str(e)}"
                await self._send_log(error_msg)
                print(error_msg)

                # Sleep between retries with increasing duration
                if attempts < self.max_retries:
                    await asyncio.sleep(attempts)
                else:
                    await self._send_log("Max retries reached, using default test")
                    return [default_test]

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class ApiTestExecutor(BaseApiTestAgent):
    """
    Agent responsible for executing API tests and generating reports.

    This class handles executing test cases against a target API, collecting results,
    and generating comprehensive reports.

    Attributes:
        http_client (httpx.AsyncClient): Async HTTP client for making requests
        test_results (List): Collection of test execution results
    """

    def __init__(self, provider: ModelProvider = "openai"):
        """
        Initialize the API test executor.

        Args:
            provider (ModelProvider, optional): LLM provider to use. Defaults to "openai"
        """
        super().__init__(provider)
        self.http_client = httpx.AsyncClient(
            verify=True,
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )
        self.test_results = []

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
            await executor.execute_tests(test_cases, "http://api.example.com")
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

                    self.test_results.append(
                        {
                            "test_name": test["name"],
                            "status": "PASS"
                            if response.status_code in [200, 201]
                            else "FAIL",
                            "response_code": response.status_code,
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
            report = await executor.generate_report()
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
                report += f"Status: {result['status']}\n"
                if result["status"] == "ERROR":
                    report += f"Error: {result['error']}\n"
                else:
                    report += f"Response Code: {result['response_code']}\n"
                    report += f"Response: ```json\n{json.dumps(result['response'], indent=2)}\n```\n"

            await self._send_log("Report generation completed")
            return report
        except Exception as e:
            await self._send_log(f"Error generating report: {str(e)}")
            return f"Error generating report: {str(e)}"

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
