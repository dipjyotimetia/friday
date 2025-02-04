import json
from datetime import datetime
from typing import Dict, List

import requests
import yaml
from langchain_community.agent_toolkits import OpenAPIToolkit
from langchain_community.agent_toolkits.openapi.base import create_openapi_agent
from langchain_community.tools.json.tool import JsonSpec
from langchain_community.utilities import RequestsWrapper
from langchain_google_vertexai import VertexAI


class ApiTestGenerator:
    def __init__(self, openapi_spec_path: str):
        self.spec_path = openapi_spec_path
        self.max_retries = 3  # Add max retries
        self.llm = VertexAI(
            model_name="gemini-pro",
            kwargs={"temperature": 0.5, "max_tokens": 1024, "timeout": None},
        )
        self.test_results = []
        with open(self.spec_path) as f:
            raw_api_spec = yaml.safe_load(f)
        self.api_spec = JsonSpec(dict_=raw_api_spec, max_value_length=4000)
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

        # Create OpenAPI agent
        self.agent = create_openapi_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            verbose=True,
            handle_parsing_errors=True,  # Add error handling
            max_iterations=2,  # Limit iterations for safety
            return_intermediate_steps=True,  # Return intermediate steps
        )

    def load_spec(self) -> Dict:
        with open(self.spec_path) as f:
            return yaml.safe_load(f)

    def validate_spec(self, spec: Dict) -> bool:
        required_fields = ["openapi", "info", "paths"]
        return all(field in spec for field in required_fields)

    def create_test_cases(self, endpoint: str, method: str, spec: Dict) -> List[Dict]:
        attempts = 0
        default_test = {
            "name": f"Basic {method} {endpoint} test",
            "method": method,
            "endpoint": endpoint,
            "payload": {},
            "headers": {},
        }

        while attempts < self.max_retries:
            try:
                prompt = f"""Generate test cases for {method} {endpoint} with different input combinations.
                Return response as a JSON array of test cases with this structure:
                [{{"name": "test name", "method": "HTTP method", "endpoint": "path", "payload": {{}}, "headers": {{}}}}]"""

                response = self.agent.invoke(prompt)

                if not response:
                    raise ValueError("Empty response received")

                # Check if response is something like "I don't know"
                if isinstance(response, str) and "I don't know" in response:
                    raise ValueError("Agent response: 'I don't know'")

                # Try parsing the response into JSON
                if isinstance(response, dict):
                    if "output" in response:
                        response = response["output"]
                    return [response] if isinstance(response, dict) else [default_test]

                if isinstance(response, str):
                    try:
                        parsed = json.loads(response.strip())
                        return [parsed] if isinstance(parsed, dict) else parsed
                    except json.JSONDecodeError as je:
                        raise ValueError(f"Invalid JSON response: {je}")

                if isinstance(response, list):
                    if not response:
                        raise ValueError("Empty list response")
                    return response

                raise TypeError(f"Unexpected response type: {type(response)}")

            except (ValueError, TypeError, json.JSONDecodeError) as e:
                attempts += 1
                print(f"Attempt {attempts}/{self.max_retries} failed: {str(e)}")
                if attempts >= self.max_retries:
                    print(
                        f"Max retries ({self.max_retries}) reached, using default test"
                    )
                    return [default_test]

    def execute_tests(self, test_cases: List[Dict], base_url: str) -> None:
        try:
            for test in test_cases:
                try:
                    response = requests.request(
                        method=test["method"],
                        url=f"{base_url.rstrip('/')}/{test['endpoint'].lstrip('/')}",  # Fix URL joining
                        json=test.get("payload"),
                        headers=test.get("headers", {}),
                        timeout=30,
                        verify=True,
                    )

                    try:
                        response_data = response.json()
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
                    self.test_results.append(
                        {"test_name": test["name"], "status": "ERROR", "error": str(e)}
                    )
                    print(f"Test execution failed: {str(e)}")

        except Exception as e:
            print(f"Test suite execution failed: {str(e)}")

    def generate_report(self) -> str:
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

            return report
        except Exception as e:
            return f"Error generating report: {str(e)}"
