"""
API Test Generator Module

This module provides a backwards-compatible API testing solution that uses
the specialized ApiTestCreator and ApiTestExecutor agents internally.

This class is maintained for backward compatibility, but new code should
use the specialized agents directly.

For new implementations, please use:
- ApiTestCreator for test case generation
- ApiTestExecutor for test execution and reporting

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

from typing import Dict, List

import structlog

from friday.agents.api_agents import ApiTestCreator, ApiTestExecutor
from friday.llm.llm import ModelProvider

logger = structlog.get_logger(__name__)


class ApiTestGenerator:
    """
    A class for generating and executing API tests based on OpenAPI specifications.

    This class combines the capabilities of ApiTestCreator and ApiTestExecutor to
    provide a complete API testing solution. It is maintained for backward compatibility.

    For new implementations, consider using the specialized agents directly.

    Attributes:
        creator (ApiTestCreator): Agent for test case generation
        executor (ApiTestExecutor): Agent for test execution and reporting
        spec_path (str): Path to the OpenAPI specification file
        test_results (List): Collection of test execution results from the executor
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
        self.provider = provider
        self.creator = ApiTestCreator(openapi_spec_path, provider)
        self.executor = ApiTestExecutor(provider)

        # Bind the test_results property to the executor's test_results
        self.test_results = self.executor.test_results

    async def _send_log(self, message: str) -> None:
        """
        Send a log message through the WebSocket logger.

        Args:
            message (str): Message to be logged

        Note:
            Delegates to the creator's _send_log method
        """
        await self.creator._send_log(message)

    async def load_spec(self) -> Dict:
        """
        Load and parse the OpenAPI specification file.

        Returns:
            Dict: Parsed OpenAPI specification

        Raises:
            yaml.YAMLError: If the specification file is invalid
            FileNotFoundError: If the specification file doesn't exist
        """
        return await self.creator.load_spec()

    def validate_spec(self, spec: Dict) -> bool:
        """
        Validate the OpenAPI specification.

        Args:
            spec (Dict): OpenAPI specification to validate

        Returns:
            bool: True if the specification is valid, False otherwise
        """
        return self.creator.validate_spec(spec)

    async def create_test_cases(
        self, endpoint: str, method: str, spec: Dict
    ) -> List[Dict]:
        """
        Generate test cases for a specific API endpoint.

        Delegates to the creator's create_test_cases method.

        Args:
            endpoint (str): API endpoint path
            method (str): HTTP method (GET, POST, etc.)
            spec (Dict): OpenAPI specification

        Returns:
            List[Dict]: List of generated test cases
        """
        return await self.creator.create_test_cases(endpoint, method, spec)

    async def execute_tests(self, test_cases: List[Dict], base_url: str) -> None:
        """
        Execute the generated test cases against a target API.

        Delegates to the executor's execute_tests method.

        Args:
            test_cases (List[Dict]): List of test cases to execute
            base_url (str): Base URL of the target API
        """
        await self.executor.execute_tests(test_cases, base_url)

    async def generate_report(self) -> str:
        """
        Generate a Markdown report of test execution results.

        Delegates to the executor's generate_report method.

        Returns:
            str: Markdown-formatted test report
        """
        return await self.executor.generate_report()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.executor.http_client.aclose()
