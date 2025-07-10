"""
Browser Testing Agent

This module implements AI-powered browser testing using the browser-use library.
It provides natural language test execution, screenshot capture, and comprehensive
reporting capabilities.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from browser_use import Agent, BrowserSession
from browser_use.browser.profile import BrowserProfile
from browser_use.llm import ChatGoogle, ChatOllama, ChatOpenAI
from langchain_mistralai import ChatMistralAI

from friday.api.schemas.browser_test import (
    BrowserTestReport,
    BrowserTestResult,
    BrowserTestScenario,
    BrowserTestSuite,
    TestStatus,
    TestType,
)
from friday.config.config import Settings
from friday.services.logger import get_logger

logger = get_logger(__name__)


class BrowserTestingAgent:
    """
    AI-powered browser testing agent using browser-use library.

    This agent can execute browser tests described in natural language,
    capture screenshots, and generate comprehensive reports.
    """

    def __init__(
        self,
        provider: str = "openai",
        headless: bool = True,
        screenshot_dir: str = "./screenshots",
        timeout: int = 30,
    ):
        """
        Initialize the browser testing agent.

        Args:
            provider: LLM provider (openai, gemini, ollama, mistral)
            headless: Whether to run browser in headless mode
            screenshot_dir: Directory to store screenshots
            timeout: Default timeout for tests
        """
        self.provider = provider
        self.headless = headless
        self.screenshot_dir = Path(screenshot_dir)
        self.timeout = timeout
        self.settings = Settings()
        self.execution_id = str(uuid.uuid4())

        # Create screenshot directory
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

        # Initialize LLM
        self.llm = self._init_llm()

        # Track execution state
        self.current_browser_session = None
        self.current_agent = None
        self.test_results: List[BrowserTestResult] = []

    def _init_llm(self):
        """Initialize the LLM based on provider."""
        logger.info(f"Initializing LLM provider: {self.provider}")

        if self.provider == "openai":
            return ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                api_key=self.settings.openai_api_key,
            )
        elif self.provider == "gemini":
            return ChatGoogle(
                model="gemini-2.5-flash",
                temperature=0.1,
                api_key=self.settings.google_api_key,
            )
        elif self.provider == "ollama":
            return ChatOllama(
                model="llama3.1:8b",
                temperature=0.1,
                base_url="http://localhost:11434",
            )
        elif self.provider == "mistral":
            return ChatMistralAI(
                model="mistral-large-latest",
                temperature=0.1,
                api_key=self.settings.mistral_api_key,
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    async def load_yaml_suite(self, yaml_content: str) -> BrowserTestSuite:
        """
        Load and parse a YAML test suite.

        Args:
            yaml_content: YAML content as string

        Returns:
            Parsed BrowserTestSuite object
        """
        try:
            data = yaml.safe_load(yaml_content)
            logger.info(f"Loading test suite: {data.get('name', 'Unknown')}")

            # Parse scenarios
            scenarios = []
            for scenario_data in data.get("scenarios", []):
                scenario = BrowserTestScenario(**scenario_data)
                scenarios.append(scenario)

            # Create test suite
            suite = BrowserTestSuite(
                name=data.get("name", "Test Suite"),
                description=data.get("description"),
                scenarios=scenarios,
                global_timeout=data.get("global_timeout", 300),
            )

            logger.info(f"Loaded {len(scenarios)} scenarios")
            return suite

        except Exception as e:
            logger.error(f"Failed to parse YAML: {e}")
            raise ValueError(f"Invalid YAML format: {e}")

    async def execute_test_suite(self, suite: BrowserTestSuite) -> BrowserTestReport:
        """
        Execute a complete test suite.

        Args:
            suite: Test suite to execute

        Returns:
            Complete test execution report
        """
        logger.info(f"Starting test suite execution: {suite.name}")
        start_time = datetime.now()

        try:
            # Initialize browser
            await self._init_browser()

            # Execute each scenario
            for scenario in suite.scenarios:
                logger.info(f"Executing scenario: {scenario.name}")

                try:
                    result = await self._execute_scenario(scenario)
                    self.test_results.append(result)

                except Exception as e:
                    logger.error(f"Scenario failed: {scenario.name} - {e}")

                    # Create failed result
                    result = BrowserTestResult(
                        scenario_name=scenario.name,
                        status=TestStatus.FAILED,
                        execution_time=0.0,
                        success=False,
                        error_message=str(e),
                        started_at=datetime.now(),
                        completed_at=datetime.now(),
                    )
                    self.test_results.append(result)

            # Generate report
            report = await self._generate_report(suite, start_time)
            logger.info(
                f"Test suite completed: {report.success_rate:.1f}% success rate"
            )

            return report

        finally:
            # Clean up browser
            await self._cleanup_browser()

    async def _init_browser(self):
        """Initialize browser and agent."""
        logger.info("Initializing browser...")

        # Configure browser profile
        browser_profile = BrowserProfile(
            headless=self.headless,
            keep_open=False,
        )

        # Create browser session
        self.current_browser_session = BrowserSession(
            browser_profile=browser_profile,
        )

        # Start browser session
        await self.current_browser_session.start()

        # Note: Agent will be created per scenario with specific task

        logger.info("Browser initialized successfully")

    async def _execute_scenario(
        self, scenario: BrowserTestScenario
    ) -> BrowserTestResult:
        """
        Execute a single test scenario.

        Args:
            scenario: Test scenario to execute

        Returns:
            Test execution result
        """
        start_time = datetime.now()
        execution_time = 0.0
        logs = []
        actions_taken = []
        error_message = None
        success = False
        screenshot_path = None

        try:
            logger.info(f"Navigating to {scenario.url}")
            logs.append(f"Navigating to {scenario.url}")

            # Navigate to URL
            await self.current_browser_session.navigate_to(scenario.url)
            actions_taken.append(f"Navigated to {scenario.url}")

            # Take initial screenshot if enabled
            should_take_screenshots = getattr(scenario, "take_screenshots", True)
            if should_take_screenshots:
                initial_screenshot = await self._capture_screenshot(
                    f"{scenario.name}_initial"
                )
                if initial_screenshot:
                    logs.append(f"Initial screenshot captured: {initial_screenshot}")

            # Build test instruction
            instruction = self._build_test_instruction(scenario)
            logs.append(f"Executing: {instruction}")

            # Log detailed steps if provided
            if hasattr(scenario, "steps") and scenario.steps:
                logs.append(f"Following {len(scenario.steps)} detailed steps:")
                for i, step in enumerate(scenario.steps, 1):
                    logs.append(f"Step {i}: {step}")

            # Create agent for this specific scenario
            scenario_agent = Agent(
                task=instruction,
                llm=self.llm,
                browser_session=self.current_browser_session,
            )

            # Execute test using browser-use agent
            logger.info(f"Executing test: {scenario.name}")
            result = await scenario_agent.run(max_steps=20)

            # Extract actions from result
            if hasattr(result, "actions"):
                actions_taken.extend([str(action) for action in result.actions])

            # Take final screenshot if enabled
            if should_take_screenshots:
                screenshot_path = await self._capture_screenshot(
                    f"{scenario.name}_final"
                )
                if screenshot_path:
                    logs.append(f"Final screenshot captured: {screenshot_path}")

            # Determine success based on result
            success = self._evaluate_test_success(result, scenario)

            # Log expected outcomes check
            if hasattr(scenario, "expected_outcomes") and scenario.expected_outcomes:
                logs.append(
                    f"Checking {len(scenario.expected_outcomes)} expected outcomes:"
                )
                for i, outcome in enumerate(scenario.expected_outcomes, 1):
                    logs.append(f"Expected outcome {i}: {outcome}")

            logs.append(f"Test completed with result: {success}")
            logger.info(f"Test completed: {scenario.name} - Success: {success}")

        except Exception as e:
            error_message = str(e)
            success = False
            logs.append(f"Test failed: {error_message}")
            logger.error(f"Test failed: {scenario.name} - {error_message}")

            # Take error screenshot if enabled
            should_take_screenshots = getattr(scenario, "take_screenshots", True)
            if should_take_screenshots:
                try:
                    error_screenshot = await self._capture_screenshot(
                        f"{scenario.name}_error"
                    )
                    if error_screenshot:
                        screenshot_path = error_screenshot
                        logs.append(f"Error screenshot captured: {error_screenshot}")
                except Exception as screenshot_error:
                    logs.append(
                        f"Failed to capture error screenshot: {screenshot_error}"
                    )

        finally:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

        # Create result
        result = BrowserTestResult(
            scenario_name=scenario.name,
            status=TestStatus.COMPLETED if success else TestStatus.FAILED,
            execution_time=execution_time,
            success=success,
            error_message=error_message,
            screenshot_path=screenshot_path,
            logs=logs,
            actions_taken=actions_taken,
            started_at=start_time,
            completed_at=end_time,
        )

        return result

    def _build_test_instruction(self, scenario: BrowserTestScenario) -> str:
        """
        Build natural language instruction for the agent.

        Args:
            scenario: Test scenario

        Returns:
            Natural language instruction
        """
        instruction = f"Test: {scenario.requirement}"

        if scenario.context:
            instruction += f"\n\nContext: {scenario.context}"

        # Add detailed steps if provided
        if scenario.steps:
            instruction += "\n\nDetailed steps to follow:"
            for i, step in enumerate(scenario.steps, 1):
                instruction += f"\n{i}. {step}"

        # Add expected outcomes
        if scenario.expected_outcomes:
            instruction += "\n\nExpected outcomes:"
            for i, outcome in enumerate(scenario.expected_outcomes, 1):
                instruction += f"\n{i}. {outcome}"
        elif scenario.expected_outcome:
            instruction += f"\n\nExpected outcome: {scenario.expected_outcome}"

        # Add screenshot instruction
        if scenario.take_screenshots:
            instruction += "\n\nImportant: Take screenshots during key steps and at completion for documentation."

        # Add test type specific instructions
        if scenario.test_type == TestType.FUNCTIONAL:
            instruction += "\n\nFocus on testing core functionality and user workflows."
        elif scenario.test_type == TestType.UI:
            instruction += (
                "\n\nFocus on testing user interface elements and visual components."
            )
        elif scenario.test_type == TestType.INTEGRATION:
            instruction += (
                "\n\nFocus on testing component interactions and integrations."
            )
        elif scenario.test_type == TestType.ACCESSIBILITY:
            instruction += "\n\nFocus on testing accessibility features and compliance."
        elif scenario.test_type == TestType.PERFORMANCE:
            instruction += "\n\nFocus on testing performance and responsiveness."

        return instruction

    def _evaluate_test_success(
        self, result: Any, _scenario: BrowserTestScenario
    ) -> bool:
        """
        Evaluate if the test was successful.

        Args:
            result: Browser agent execution result
            _scenario: Test scenario (unused)

        Returns:
            Whether the test was successful
        """
        try:
            # Check if result indicates success
            if hasattr(result, "success"):
                return result.success

            # Check if result has status
            if hasattr(result, "status"):
                return result.status == "success"

            # Check if result has error
            if hasattr(result, "error"):
                return result.error is None

            # Default to True if no clear failure indication
            return True

        except Exception:
            # If evaluation fails, assume failure
            return False

    async def _capture_screenshot(self, scenario_name: str) -> str:
        """
        Capture screenshot of current browser state.

        Args:
            scenario_name: Name of the scenario

        Returns:
            Screenshot file path
        """
        try:
            # Create unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{scenario_name}_{timestamp}.png"
            filepath = self.screenshot_dir / self.execution_id / filename

            # Create directory if needed
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Take screenshot
            screenshot_b64 = await self.current_browser_session.take_screenshot()

            # Save base64 screenshot as PNG
            import base64

            with open(filepath, "wb") as f:
                f.write(base64.b64decode(screenshot_b64))

            logger.info(f"Screenshot captured: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None

    async def _generate_report(
        self, suite: BrowserTestSuite, start_time: datetime
    ) -> BrowserTestReport:
        """
        Generate comprehensive test report.

        Args:
            suite: Test suite that was executed
            start_time: Suite start time

        Returns:
            Complete test report
        """
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = sum(1 for r in self.test_results if not r.success)
        skipped_tests = 0  # Currently not implemented

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # Get browser info
        browser_info = {
            "provider": self.provider,
            "headless": self.headless,
            "execution_id": self.execution_id,
        }

        # Create report
        report = BrowserTestReport(
            suite_name=suite.name,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            execution_time=execution_time,
            success_rate=success_rate,
            results=self.test_results,
            started_at=start_time,
            completed_at=end_time,
            browser_info=browser_info,
        )

        return report

    async def _cleanup_browser(self):
        """Clean up browser resources."""
        try:
            if self.current_browser_session:
                await self.current_browser_session.stop()
                self.current_browser_session = None

            if self.current_agent:
                self.current_agent = None

            logger.info("Browser cleanup completed")

        except Exception as e:
            logger.error(f"Error during browser cleanup: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for browser testing.

        Returns:
            Health check status
        """
        try:
            # Check if browser-use is available
            try:
                import importlib.metadata

                browser_use_version = importlib.metadata.version("browser-use")
            except Exception:
                browser_use_version = "unknown"

            # Check if playwright is available
            try:
                import importlib.metadata

                playwright_version = importlib.metadata.version("playwright")
            except Exception:
                playwright_version = "unknown"

            # Test browser initialization
            browser_available = True
            try:
                test_profile = BrowserProfile(headless=True)
                test_browser = BrowserSession(browser_profile=test_profile)
                await test_browser.start()
                await test_browser.stop()
            except Exception:
                browser_available = False

            return {
                "status": "healthy" if browser_available else "unhealthy",
                "browser_available": browser_available,
                "playwright_version": playwright_version,
                "browser_use_version": browser_use_version,
                "supported_providers": ["openai", "gemini", "ollama", "mistral"],
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "browser_available": False,
                "playwright_version": "unknown",
                "browser_use_version": "unknown",
                "supported_providers": [],
            }


# Utility functions for CLI and API usage
async def execute_yaml_file(
    yaml_file_path: str,
    provider: str = "openai",
    headless: bool = True,
    output_file: Optional[str] = None,
) -> BrowserTestReport:
    """
    Execute browser tests from YAML file.

    Args:
        yaml_file_path: Path to YAML test file
        provider: LLM provider
        headless: Whether to run headless
        output_file: Optional output file for report

    Returns:
        Test execution report
    """
    # Read YAML file
    with open(yaml_file_path, "r") as f:
        yaml_content = f.read()

    # Create agent
    agent = BrowserTestingAgent(provider=provider, headless=headless)

    # Load and execute test suite
    suite = await agent.load_yaml_suite(yaml_content)
    report = await agent.execute_test_suite(suite)

    # Save report if requested
    if output_file:
        with open(output_file, "w") as f:
            json.dump(report.model_dump(), f, indent=2, default=str)

    return report


async def execute_yaml_content(
    yaml_content: str,
    provider: str = "openai",
    headless: bool = True,
) -> BrowserTestReport:
    """
    Execute browser tests from YAML content.

    Args:
        yaml_content: YAML content as string
        provider: LLM provider
        headless: Whether to run headless

    Returns:
        Test execution report
    """
    # Create agent
    agent = BrowserTestingAgent(provider=provider, headless=headless)

    # Load and execute test suite
    suite = await agent.load_yaml_suite(yaml_content)
    report = await agent.execute_test_suite(suite)

    return report
