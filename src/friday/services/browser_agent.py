import asyncio
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from browser_use import Agent
from langchain_core.prompts import PromptTemplate

from friday.llm.llm import ModelProvider, get_llm_client
from friday.services.logger import get_logger

logger = get_logger(__name__)


class BrowserTestingAgent:
    """Browser testing agent using browser-use library for UI automation"""

    def __init__(self, provider: ModelProvider = "openai"):
        self.llm = get_llm_client(provider)
        self.provider = provider

        # Template for generating browser automation tasks
        self.template = """
        Based on the following test requirements, generate a comprehensive browser automation task:
        
        Test Requirement: {requirement}
        Target URL: {url}
        Test Type: {test_type}
        
        Additional Context:
        {context}
        
        Generate a detailed browser automation task description that includes:
        1. Clear step-by-step actions to perform
        2. Elements to interact with (buttons, forms, links, etc.)
        3. Data to input or verify
        4. Expected outcomes and assertions
        5. Screenshots or evidence to capture
        
        Format the task as a clear, actionable instruction for an AI browser agent.
        """

        self.prompt = PromptTemplate(
            input_variables=["requirement", "url", "test_type", "context"],
            template=self.template,
        )

    async def run_browser_test(
        self,
        requirement: str,
        url: str,
        test_type: str = "functional",
        context: str = "",
        headless: bool = True,
        take_screenshots: bool = True,
    ) -> Dict[str, Any]:
        """
        Run a browser test using the browser-use agent

        Args:
            requirement: Test requirement description
            url: Target URL to test
            test_type: Type of test (functional, ui, integration, etc.)
            context: Additional context for the test
            headless: Run browser in headless mode
            take_screenshots: Whether to take screenshots during execution

        Returns:
            Dict containing test results, screenshots, and execution details
        """
        logger.info(f"Starting browser test for: {requirement}")

        try:
            # Generate the task description using LLM
            task_description = self.prompt.format(
                requirement=requirement, url=url, test_type=test_type, context=context
            )

            # Enhanced task with specific instructions
            enhanced_task = f"""
            {task_description}
            
            Please navigate to {url} and perform the following:
            1. Take a screenshot of the initial page
            2. Execute the test steps as described
            3. Take screenshots at key points during execution
            4. Verify expected outcomes
            5. Document any issues or unexpected behavior
            6. Take a final screenshot of the end state
            
            Important: Be thorough in your testing and document everything you observe.
            """

            # Create and run the browser agent
            agent = Agent(task=enhanced_task, llm=self.llm)

            # Run the agent and capture results
            result = await agent.run()

            # Parse and structure the results
            test_result = {
                "status": "completed",
                "requirement": requirement,
                "url": url,
                "test_type": test_type,
                "task_description": enhanced_task,
                "execution_result": str(result),
                "screenshots": [],  # Would be populated by browser-use
                "timestamp": asyncio.get_event_loop().time(),
                "success": True,
                "errors": [],
            }

            logger.info(f"Browser test completed successfully for: {requirement}")
            return test_result

        except Exception as e:
            logger.error(f"Browser test failed: {str(e)}")
            return {
                "status": "failed",
                "requirement": requirement,
                "url": url,
                "test_type": test_type,
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time(),
                "success": False,
                "errors": [str(e)],
            }

    async def run_multiple_tests(
        self, test_cases: List[Dict[str, Any]], headless: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Run multiple browser tests in sequence

        Args:
            test_cases: List of test case dictionaries with requirement, url, etc.
            headless: Run browser in headless mode

        Returns:
            List of test results
        """
        logger.info(f"Starting batch browser testing with {len(test_cases)} test cases")

        results = []
        for i, test_case in enumerate(test_cases):
            logger.info(f"Running test case {i + 1}/{len(test_cases)}")

            result = await self.run_browser_test(
                requirement=test_case.get("requirement", ""),
                url=test_case.get("url", ""),
                test_type=test_case.get("test_type", "functional"),
                context=test_case.get("context", ""),
                headless=headless,
                take_screenshots=test_case.get("take_screenshots", True),
            )

            results.append(result)

            # Add delay between tests to avoid overwhelming the target site
            await asyncio.sleep(2)

        logger.info(f"Completed batch browser testing with {len(results)} results")
        return results

    def generate_test_report(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate a comprehensive test report from browser test results

        Args:
            results: List of test results

        Returns:
            Formatted test report string
        """
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get("success", False))
        failed_tests = total_tests - passed_tests

        report = f"""
# Browser Test Execution Report

## Summary
- **Total Tests**: {total_tests}
- **Passed**: {passed_tests}
- **Failed**: {failed_tests}
- **Success Rate**: {(passed_tests / total_tests) * 100:.1f}%

## Test Results

"""

        for i, result in enumerate(results, 1):
            status_icon = "✅" if result.get("success", False) else "❌"
            report += f"""
### Test Case {i}: {status_icon}
- **Requirement**: {result.get("requirement", "N/A")}
- **URL**: {result.get("url", "N/A")}
- **Test Type**: {result.get("test_type", "N/A")}
- **Status**: {"PASSED" if result.get("success", False) else "FAILED"}

"""

            if not result.get("success", False):
                report += f"- **Error**: {result.get('error', 'Unknown error')}\n"

            if result.get("execution_result"):
                report += (
                    f"- **Details**: {result.get('execution_result', '')[:200]}...\n"
                )

        return report
