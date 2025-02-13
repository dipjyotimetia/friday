import asyncio
import json
from datetime import datetime
from typing import Dict, List

import httpx
import structlog
import yaml
from langchain_community.agent_toolkits import OpenAPIToolkit
from langchain_community.agent_toolkits.openapi.base import create_openapi_agent
from langchain_community.tools.json.tool import JsonSpec
from langchain_community.utilities import RequestsWrapper
from langchain_core.exceptions import OutputParserException
from langchain_google_vertexai import VertexAI
from tenacity import retry, stop_after_attempt, wait_exponential

from friday.services.logger import ws_logger

logger = structlog.get_logger(__name__)


class ApiTestGenerator:
    def __init__(self, openapi_spec_path: str):
        self.spec_path = openapi_spec_path
        self.http_client = httpx.AsyncClient(
            verify=True,
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )
        self.max_retries = 3  # Add max retries
        self.llm = VertexAI(
            model_name="gemini-pro",
            kwargs={"temperature": 0.5, "max_tokens": 1024, "timeout": None},
        )
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
        """Send log message to websocket with error handling"""
        try:
            if ws_logger:
                await ws_logger.broadcast(message)  # Call broadcast directly
            else:
                print(f"Warning: WebSocket logger not initialized: {message}")
        except Exception as e:
            print(f"Error sending log: {message} - {str(e)}")

    async def load_spec(self) -> Dict:
        with open(self.spec_path) as f:
            return yaml.safe_load(f)

    def validate_spec(self, spec: Dict) -> bool:
        required_fields = ["openapi", "info", "paths"]
        return all(field in spec for field in required_fields)

    async def create_test_cases(
        self, endpoint: str, method: str, spec: Dict
    ) -> List[Dict]:
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

                prompt = f"""
                You are an API test case generator. You will be given an OpenAPI specification and your task is to generate a comprehensive set of test cases for a specific endpoint and method. Ensure the test cases cover various scenarios, including basic functionality, edge cases, and error conditions.

                Follow these guidelines for generating test cases:

                1.  **Understand the OpenAPI Specification:** Carefully analyze the provided specification for the endpoint and method, including request parameters, request body, headers, and expected responses.
                2.  **Cover Basic Functionality:** Generate test cases to validate the core functionality of the API endpoint. These tests should cover typical use cases and ensure the API behaves as expected under normal conditions.
                3.  **Explore Edge Cases:** Identify and create test cases for edge cases, such as boundary values, unusual input combinations, and unexpected data. These tests help uncover potential issues that may not be apparent during basic testing.
                4.  **Test Error Scenarios:** Develop test cases to verify how the API handles errors, such as invalid input, missing parameters, authentication failures, and server errors. These tests should ensure the API returns appropriate error codes and messages.
                5.  **Prioritize Security:** Include tests that check for common security vulnerabilities, such as injection attacks, authentication bypasses, and data breaches.
                6.  **Output Format:** Return test cases in the EXACT JSON array format specified below.

                Here is the OpenAPI specification for the **{method}** method of the **{endpoint}** endpoint:

                ```json
                {json.dumps(endpoint_spec[method.lower()], indent=2)}

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
                - headers: Include required headers"""

                # Add structured response handling
                response = self.agent.invoke(
                    {
                        "input": prompt,
                        "action": "generate_test_cases",
                        "action_input": {
                            "method": method,
                            "endpoint": endpoint,
                            "spec": endpoint_spec[method.lower()],
                        },
                    }
                )

                # Add specific handling for OutputParserException
                if isinstance(response, OutputParserException):
                    raise ValueError(f"Parser error: {str(response)}")

                # Handle empty or "I don't know" responses
                if not response or (
                    isinstance(response, str) and "don't know" in response.lower()
                ):
                    raise ValueError("Invalid or empty response from agent")

                # Parse dict response
                if isinstance(response, dict):
                    if "output" in response:
                        response = response["output"]
                    return [response] if isinstance(response, dict) else [default_test]

                # Parse string response
                if isinstance(response, str):
                    try:
                        parsed = json.loads(response.strip())
                        if isinstance(parsed, dict):
                            return [parsed]
                        elif isinstance(parsed, list) and parsed:
                            return parsed
                        raise ValueError("Invalid response structure")
                    except json.JSONDecodeError:
                        raise ValueError("Invalid JSON response")

                # Parse list response
                if isinstance(response, list):
                    if not response:
                        raise ValueError("Empty list response")
                    return response

                raise TypeError(f"Unexpected response type: {type(response)}")

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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    async def execute_tests(self, test_cases: List[Dict], base_url: str) -> None:
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

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()

    async def generate_report(self) -> str:
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
