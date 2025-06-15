from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

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
