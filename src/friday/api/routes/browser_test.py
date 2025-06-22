import asyncio
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Path
from fastapi.responses import JSONResponse, FileResponse

from friday.api.schemas.browser_test import (
    BrowserTestResult,
    YamlScenarioExecuteRequest,
    YamlScenarioExecuteResponse,
    YamlScenarioUploadResponse,
    YamlTemplateSample,
)
from friday.services.browser_agent import BrowserTestingAgent
from friday.services.logger import get_logger
from friday.services.yaml_scenarios import YamlScenariosParser
from friday.services.screenshot_manager import screenshot_manager
from friday.services.browser_session_manager import browser_session_manager
from friday.services.browser_errors import browser_error_handler

logger = get_logger(__name__)

router = APIRouter(prefix="/browser-test", tags=["browser-testing"])


@router.get("/health")
async def browser_test_health():
    """
    Health check endpoint for browser testing service
    """
    try:
        # Basic health check - try to initialize the agent with default provider
        BrowserTestingAgent(provider="openai")

        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "message": "Browser testing service is operational",
                "service": "browser-testing",
                "version": "1.0.0",
            },
        )
    except Exception as e:
        error_message = str(e)
        logger.error(
            f"Browser testing service health check failed: {error_message}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": f"Browser testing service is not operational: {error_message}",
                "service": "browser-testing",
                "version": "1.0.0",
            },
        )


@router.post("/yaml/upload", response_model=YamlScenarioUploadResponse)
async def upload_yaml_scenarios(
    file: UploadFile = File(...),
    provider: str = Form(default="openai"),
    headless: bool = Form(default=True),
    execute_immediately: bool = Form(default=False),
):
    """
    Upload YAML file containing test scenarios
    """
    try:
        logger.info(f"Uploading YAML file: {file.filename}")

        # Validate file type
        if not file.filename.endswith((".yaml", ".yml")):
            raise HTTPException(
                status_code=400, detail="File must be a YAML file (.yaml or .yml)"
            )

        # Read file content
        content = await file.read()
        yaml_content = content.decode("utf-8")

        # Parse YAML content
        parser = YamlScenariosParser()
        test_suite = parser.parse_yaml_content(yaml_content)

        # Convert to browser test cases
        test_cases = parser.convert_to_browser_test_cases(test_suite)

        response_data = {
            "success": True,
            "message": f"Successfully uploaded YAML file with {len(test_cases)} scenarios",
            "test_suite_name": test_suite.name,
            "scenarios_count": len(test_cases),
            "scenarios": test_cases,
        }

        # Execute immediately if requested
        if execute_immediately:
            logger.info("Executing scenarios immediately after upload")

            # Initialize browser testing agent
            agent = BrowserTestingAgent(provider=provider)

            # Run multiple browser tests
            results = await agent.run_multiple_tests(
                test_cases=test_cases, headless=headless
            )

            # Convert results to BrowserTestResult models
            test_results = [BrowserTestResult(**result) for result in results]

            # Generate test report
            report = agent.generate_test_report(results)

            # Create summary
            total_tests = len(results)
            passed_tests = sum(1 for r in results if r.get("success", False))
            failed_tests = total_tests - passed_tests

            summary = {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests) * 100
                if total_tests > 0
                else 0,
            }

            response_data.update(
                {
                    "execution_results": test_results,
                    "report": report,
                    "summary": summary,
                    "message": f"Successfully uploaded and executed {len(test_cases)} scenarios. {passed_tests}/{total_tests} tests passed",
                }
            )

        return YamlScenarioUploadResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error uploading YAML scenarios: {error_message}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to upload YAML scenarios: {error_message}"
        )


@router.post("/yaml/execute", response_model=YamlScenarioExecuteResponse)
async def execute_yaml_scenarios(request: YamlScenarioExecuteRequest):
    """
    Execute test scenarios from YAML content
    """
    try:
        logger.info("Executing YAML scenarios from content")

        # Parse YAML content
        parser = YamlScenariosParser()
        test_suite = parser.parse_yaml_content(request.yaml_content)

        # Convert to browser test cases
        test_cases = parser.convert_to_browser_test_cases(test_suite)

        logger.info(
            f"Executing {len(test_cases)} scenarios from test suite: {test_suite.name}"
        )

        # Initialize browser testing agent
        agent = BrowserTestingAgent(provider=request.provider)

        # Run multiple browser tests
        results = await agent.run_multiple_tests(
            test_cases=test_cases, headless=request.headless
        )

        # Convert results to BrowserTestResult models
        test_results = [BrowserTestResult(**result) for result in results]

        # Generate test report
        report = agent.generate_test_report(results)

        # Create summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get("success", False))
        failed_tests = total_tests - passed_tests

        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests) * 100
            if total_tests > 0
            else 0,
        }

        return YamlScenarioExecuteResponse(
            success=True,
            message=f"Successfully executed {len(test_cases)} scenarios. {passed_tests}/{total_tests} tests passed",
            test_suite_name=test_suite.name,
            scenarios_count=len(test_cases),
            results=test_results,
            report=report,
            summary=summary,
        )

    except Exception as e:
        error_message = str(e)
        logger.error(f"Error executing YAML scenarios: {error_message}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to execute YAML scenarios: {error_message}"
        )


@router.get("/yaml/template", response_model=YamlTemplateSample)
async def get_yaml_template():
    """
    Get a sample YAML template for test scenarios
    """
    try:
        parser = YamlScenariosParser()
        template_content = parser.generate_sample_yaml()

        return YamlTemplateSample(
            template_content=template_content,
            description="Sample YAML template for browser test scenarios with comprehensive examples",
        )

    except Exception as e:
        error_message = str(e)
        logger.error(f"Error generating YAML template: {error_message}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to generate YAML template: {error_message}"
        )


@router.post("/yaml/validate")
async def validate_yaml_scenarios(request: YamlScenarioExecuteRequest):
    """
    Validate YAML content without executing tests
    """
    try:
        logger.info("Validating YAML scenarios")

        # Parse YAML content
        parser = YamlScenariosParser()
        test_suite = parser.parse_yaml_content(request.yaml_content)

        # Convert to browser test cases
        test_cases = parser.convert_to_browser_test_cases(test_suite)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"YAML validation successful. Found {len(test_cases)} valid scenarios.",
                "test_suite_name": test_suite.name,
                "scenarios_count": len(test_cases),
                "scenarios": [
                    {
                        "name": case.get("scenario_name", "Unnamed"),
                        "requirement": case.get("requirement", ""),
                        "url": case.get("url", ""),
                        "test_type": case.get("test_type", "functional"),
                    }
                    for case in test_cases
                ],
            },
        )

    except Exception as e:
        error_message = str(e)
        logger.error(f"YAML validation failed: {error_message}", exc_info=True)
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": f"YAML validation failed: {error_message}",
                "errors": [error_message],
            },
        )


@router.get("/sessions")
async def get_browser_sessions():
    """
    Get information about active browser sessions
    """
    try:
        if not hasattr(browser_session_manager, "sessions"):
            await browser_session_manager.initialize()

        stats = browser_session_manager.get_session_stats()

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Browser session information retrieved",
                "stats": stats,
            },
        )

    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to get browser sessions: {error_message}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Failed to get browser sessions: {error_message}",
            },
        )


@router.get("/screenshots/{test_id}")
async def get_test_screenshots(test_id: str = Path(...)):
    """
    Get all screenshots for a specific test
    """
    try:
        screenshots = screenshot_manager.get_test_screenshots(test_id)
        metadata = screenshot_manager.get_test_metadata(test_id)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Found {len(screenshots)} screenshots for test {test_id}",
                "test_id": test_id,
                "screenshots": screenshots,
                "metadata": metadata,
            },
        )

    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to get screenshots: {error_message}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Failed to get screenshots: {error_message}",
            },
        )


@router.get("/screenshots/{test_id}/{filename}")
async def get_screenshot_file(test_id: str = Path(...), filename: str = Path(...)):
    """
    Get a specific screenshot file
    """
    try:
        screenshot_path = screenshot_manager.get_screenshot_path(test_id, filename)

        if screenshot_path and screenshot_path.exists():
            return FileResponse(
                path=str(screenshot_path), media_type="image/png", filename=filename
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Screenshot {filename} not found for test {test_id}",
            )

    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to get screenshot file: {error_message}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to get screenshot file: {error_message}"
        )


@router.get("/metrics")
async def get_test_metrics():
    """
    Get browser testing metrics and statistics
    """
    try:
        # Get session statistics
        session_stats = (
            browser_session_manager.get_session_stats()
            if hasattr(browser_session_manager, "sessions")
            else {}
        )

        # Get storage statistics
        storage_stats = screenshot_manager.get_storage_stats()

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Browser testing metrics retrieved",
                "session_stats": session_stats,
                "storage_stats": storage_stats,
                "timestamp": asyncio.get_event_loop().time(),
            },
        )

    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to get metrics: {error_message}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Failed to get metrics: {error_message}",
            },
        )


@router.delete("/screenshots/{test_id}")
async def cleanup_test_screenshots(test_id: str = Path(...)):
    """
    Clean up screenshots for a specific test
    """
    try:
        success = screenshot_manager.cleanup_test_screenshots(test_id)

        if success:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": f"Screenshots cleaned up for test {test_id}",
                },
            )
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": f"No screenshots found for test {test_id}",
                },
            )

    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to cleanup screenshots: {error_message}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Failed to cleanup screenshots: {error_message}",
            },
        )
