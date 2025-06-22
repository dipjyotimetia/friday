import asyncio
import uuid
from typing import Any, Dict, List, Optional

from browser_use import Agent
from langchain_core.prompts import PromptTemplate

from friday.llm.llm import ModelProvider, get_llm_client
from friday.services.logger import get_logger
from friday.services.screenshot_manager import screenshot_manager
from friday.services.browser_session_manager import browser_session_manager
from friday.services.browser_errors import browser_error_handler, BrowserTestError

logger = get_logger(__name__)


class BrowserTestingAgent:
    """Browser testing agent using browser-use library for UI automation"""

    def __init__(self, provider: ModelProvider = "openai"):
        self.llm = get_llm_client(provider)
        self.provider = provider
        self.screenshot_manager = screenshot_manager
        self.session_manager = browser_session_manager
        self.error_handler = browser_error_handler

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

    async def run_multiple_tests(
        self,
        test_cases: List[Dict[str, Any]],
        headless: bool = True,
        max_parallel: int = 1,
        respect_prerequisites: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Run multiple browser tests with enhanced features

        Args:
            test_cases: List of test case dictionaries with requirement, url, etc.
            headless: Run browser in headless mode
            max_parallel: Maximum number of parallel tests
            respect_prerequisites: Whether to respect test prerequisites

        Returns:
            List of test results
        """
        logger.info(
            f"Starting enhanced batch testing with {len(test_cases)} test cases"
        )

        # Initialize session manager if needed
        if (
            not hasattr(self.session_manager, "playwright")
            or self.session_manager.playwright is None
        ):
            await self.session_manager.initialize()

        results = []
        completed_tests = set()

        if respect_prerequisites and max_parallel == 1:
            # Sequential execution with prerequisite handling
            results = await self._run_tests_sequential_with_prerequisites(
                test_cases, headless
            )
        elif max_parallel > 1:
            # Parallel execution
            results = await self._run_tests_parallel(test_cases, headless, max_parallel)
        else:
            # Simple sequential execution
            results = await self._run_tests_sequential(test_cases, headless)

        logger.info(f"Completed batch testing with {len(results)} results")
        return results

    async def _run_tests_sequential(
        self, test_cases: List[Dict[str, Any]], headless: bool
    ) -> List[Dict[str, Any]]:
        """Run tests sequentially without prerequisite handling"""
        results = []
        for i, test_case in enumerate(test_cases):
            logger.info(
                f"Running test case {i + 1}/{len(test_cases)}: {test_case.get('scenario_name', 'Unknown')}"
            )

            result = await self.run_single_test(test_case=test_case, headless=headless)
            results.append(result)

            # Add delay between tests
            await asyncio.sleep(2)

        return results

    async def _run_tests_sequential_with_prerequisites(
        self, test_cases: List[Dict[str, Any]], headless: bool
    ) -> List[Dict[str, Any]]:
        """Run tests sequentially while respecting prerequisites"""
        results = []
        completed_tests = set()
        remaining_tests = test_cases.copy()

        while remaining_tests:
            runnable_tests = []

            for test_case in remaining_tests:
                prerequisites = test_case.get("prerequisites", [])
                if all(prereq in completed_tests for prereq in prerequisites):
                    runnable_tests.append(test_case)

            if not runnable_tests:
                # No tests can run due to unmet prerequisites
                logger.warning(
                    "Circular dependencies or missing prerequisites detected"
                )
                # Run remaining tests anyway
                runnable_tests = remaining_tests

            for test_case in runnable_tests:
                logger.info(
                    f"Running test: {test_case.get('scenario_name', 'Unknown')}"
                )

                result = await self.run_single_test(
                    test_case=test_case, headless=headless
                )
                results.append(result)
                completed_tests.add(test_case.get("scenario_name", ""))
                remaining_tests.remove(test_case)

                # Add delay between tests
                await asyncio.sleep(1)

        return results

    async def _run_tests_parallel(
        self, test_cases: List[Dict[str, Any]], headless: bool, max_parallel: int
    ) -> List[Dict[str, Any]]:
        """Run tests in parallel batches"""
        results = []

        # Filter tests that can run in parallel
        parallel_tests = [tc for tc in test_cases if tc.get("parallel", False)]
        sequential_tests = [tc for tc in test_cases if not tc.get("parallel", False)]

        # Run parallel tests in batches
        if parallel_tests:
            for i in range(0, len(parallel_tests), max_parallel):
                batch = parallel_tests[i : i + max_parallel]
                logger.info(f"Running parallel batch of {len(batch)} tests")

                tasks = [
                    self.run_single_test(test_case=test_case, headless=headless)
                    for test_case in batch
                ]

                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                for result in batch_results:
                    if isinstance(result, Exception):
                        # Handle exceptions from parallel execution
                        error_result = {
                            "status": "failed",
                            "success": False,
                            "error": str(result),
                            "timestamp": asyncio.get_event_loop().time(),
                        }
                        results.append(error_result)
                    else:
                        results.append(result)

        # Run sequential tests normally
        if sequential_tests:
            sequential_results = await self._run_tests_sequential(
                sequential_tests, headless
            )
            results.extend(sequential_results)

        return results

    async def run_single_test(
        self, test_case: Dict[str, Any], headless: bool = True
    ) -> Dict[str, Any]:
        """
        Run a single browser test case
        
        Args:
            test_case: Dictionary containing test case details
            headless: Whether to run browser in headless mode
            
        Returns:
            Dictionary with test result details
        """
        test_id = str(uuid.uuid4())
        scenario_name = test_case.get("scenario_name", "Unknown Test")
        
        logger.info(f"Starting single test: {scenario_name} (ID: {test_id})")
        
        try:
            # Extract test case details
            requirement = test_case.get("requirement", "")
            url = test_case.get("url", "")
            test_type = test_case.get("test_type", "functional")
            context = test_case.get("context", "")
            
            # Generate browser automation task using LLM prompt
            prompt_input = {
                "requirement": requirement,
                "url": url,
                "test_type": test_type,
                "context": context,
            }
            
            # Generate task description
            chain = self.prompt | self.llm
            automation_task = await chain.ainvoke(prompt_input)
            
            # Clean up task text
            if hasattr(automation_task, 'content'):
                task_description = automation_task.content
            else:
                task_description = str(automation_task)
            
            logger.info(f"Generated automation task for {scenario_name}: {task_description[:100]}...")
            
            # Initialize browser session if needed
            if not hasattr(self.session_manager, 'playwright') or self.session_manager.playwright is None:
                await self.session_manager.initialize()
            
            # Create browser context
            browser_context = await self.session_manager.create_browser_context(
                test_id=test_id,
                headless=headless
            )
            
            # Create browser-use agent
            agent = Agent(
                task=task_description,
                llm=self.llm,
                browser_context=browser_context,
                use_vision=True,
                save_conversation_path=f"logs/browser_test_{test_id}.json",
                max_failures=3,
                retry_delay=10
            )
            
            # Execute the browser automation task
            result = await agent.run(max_steps=50)
            
            # Take final screenshot
            screenshot_path = await self.screenshot_manager.capture_screenshot(
                context=browser_context,
                test_id=test_id,
                step_name="final_result"
            )
            
            # Close browser context
            await browser_context.close()
            
            # Extract result information
            success = len(result) > 0 and not any(step.is_error for step in result)
            result_summary = f"Completed {len(result)} steps"
            if result:
                last_step = result[-1]
                if hasattr(last_step, 'output') and last_step.output:
                    result_summary += f". Final result: {str(last_step.output)[:200]}"
            
            # Prepare success result
            test_result = {
                "test_id": test_id,
                "scenario_name": scenario_name,
                "requirement": requirement,
                "url": url,
                "test_type": test_type,
                "status": "completed",
                "success": success,
                "execution_result": result_summary,
                "task_description": task_description,
                "screenshot_path": str(screenshot_path) if screenshot_path else None,
                "timestamp": asyncio.get_event_loop().time(),
                "steps_executed": len(result) if result else 0,
            }
            
            logger.info(f"Successfully completed test: {scenario_name}")
            return test_result
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Test failed for {scenario_name}: {error_message}", exc_info=True)
            
            # Handle error with error handler
            handled_error = await self.error_handler.handle_test_error(
                test_id=test_id,
                error=e,
                test_case=test_case
            )
            
            # Prepare failure result
            test_result = {
                "test_id": test_id,
                "scenario_name": scenario_name,
                "requirement": test_case.get("requirement", ""),
                "url": test_case.get("url", ""),
                "test_type": test_case.get("test_type", "functional"),
                "status": "failed",
                "success": False,
                "error": error_message,
                "error_details": handled_error,
                "timestamp": asyncio.get_event_loop().time(),
            }
            
            return test_result

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
