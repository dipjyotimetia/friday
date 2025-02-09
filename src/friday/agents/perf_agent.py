import asyncio
import shlex
import statistics
import time
from typing import Dict, Union
from urllib.parse import urlparse

import httpx
import yaml


class PerfTestGenerator:
    def __init__(
        self,
        openapi_spec_path: Union[str, None] = None,
        concurrent_users: int = 10,
        duration: int = 30,
    ):
        self.spec_path = openapi_spec_path
        self.users = concurrent_users
        self.duration = duration
        self.http_client = httpx.AsyncClient(verify=True, timeout=30.0)
        self.results = []

    def parse_curl(self, curl_command: str) -> Dict:
        """Parse curl command into request components"""
        parts = shlex.split(curl_command)
        parsed = {"method": "GET", "headers": {}, "data": None, "url": None}

        i = 1  # Skip 'curl' command
        while i < len(parts):
            if parts[i] == "-H" or parts[i] == "--header":
                header = parts[i + 1]
                key, value = header.split(":", 1)
                parsed["headers"][key.strip()] = value.strip()
                i += 2
            elif parts[i] == "-X" or parts[i] == "--request":
                parsed["method"] = parts[i + 1]
                i += 2
            elif parts[i] == "-d" or parts[i] == "--data":
                parsed["data"] = parts[i + 1]
                i += 2
            elif not parts[i].startswith("-"):
                parsed["url"] = parts[i]
                i += 1
            else:
                i += 1

        return parsed

    async def load_spec(self) -> Dict:
        if not self.spec_path:
            return {"paths": {}}
        with open(self.spec_path) as f:
            return yaml.safe_load(f)

    async def run_user_session(
        self,
        endpoint: str,
        method: str,
        base_url: str,
        headers: Dict = None,
        data: str = None,
    ):
        start_time = time.time()
        try:
            response = await self.http_client.request(
                method=method,
                url=f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}",
                headers=headers,
                content=data,
            )
            end_time = time.time()
            return {
                "endpoint": endpoint,
                "method": method,
                "response_time": end_time - start_time,
                "status_code": response.status_code,
            }
        except Exception as e:
            return {"endpoint": endpoint, "method": method, "error": str(e)}

    async def execute_load_test(
        self, base_url: str = None, curl_command: str = None
    ) -> None:
        tasks = []

        if curl_command:
            # Run load test from curl command
            parsed = self.parse_curl(curl_command)
            if not base_url:
                url = urlparse(parsed["url"])
                base_url = f"{url.scheme}://{url.netloc}"
                endpoint = url.path
            else:
                endpoint = urlparse(parsed["url"]).path

            for _ in range(self.users):
                tasks.append(
                    self.run_user_session(
                        endpoint=endpoint,
                        method=parsed["method"],
                        base_url=base_url,
                        headers=parsed["headers"],
                        data=parsed["data"],
                    )
                )
        else:
            # Run load test from OpenAPI spec
            spec = await self.load_spec()
            for path, methods in spec["paths"].items():
                for method in methods.keys():
                    for _ in range(self.users):
                        tasks.append(self.run_user_session(path, method, base_url))

        self.results = await asyncio.gather(*tasks)

    def generate_report(self) -> str:
        response_times = [
            r["response_time"] for r in self.results if "response_time" in r
        ]
        errors = [r for r in self.results if "error" in r]
        total_requests = len(self.results)

        report = "# Performance Test Results\n\n"
        report += "## Summary\n"
        report += f"- Total Requests: {total_requests}\n"

        if response_times:
            report += (
                f"- Average Response Time: {statistics.mean(response_times):.2f}s\n"
            )
        else:
            report += "- Average Response Time: N/A (no successful requests)\n"

        error_rate = (len(errors) / total_requests * 100) if total_requests > 0 else 0
        report += f"- Error Rate: {error_rate:.2f}%\n\n"

        report += "## Detailed Results\n"
        for result in self.results:
            report += f"\n### {result['method']} {result['endpoint']}\n"
            if "error" in result:
                report += f"Error: {result['error']}\n"
            else:
                report += f"Response Time: {result['response_time']:.2f}s\n"
                report += f"Status Code: {result['status_code']}\n"

        return report
